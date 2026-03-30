"""CLI entry point for ai-beta-test."""

import asyncio
import os
import shutil
import sys

import click

from roastmymvp.browser.explorer import explore_url
from roastmymvp.context.builder import build_product_context
from roastmymvp.config import load_config
from roastmymvp.llm.client import LLMClient
from roastmymvp.personas.depth_analyst import run_deep_analysis
from roastmymvp.personas.generator import (
    generate_custom_persona,
    generate_default_personas,
    generate_persona_variants,
)
from roastmymvp.report.builder import build_report
from roastmymvp.report.stats import calculate_pmf_signals
from roastmymvp.research.scraper import research_product
from roastmymvp.research.persona_enricher import enrich_personas
from roastmymvp.research.persona_factory import build_personas_from_research
from roastmymvp.founder.scraper import research_founder
from roastmymvp.evolution.apply import get_evolved_vc_panel
from roastmymvp.evolution.genes import GenePool
from roastmymvp.vc.analyst import run_vc_panel
from roastmymvp.vc.report import build_vc_report
from roastmymvp.gauntlet import (
    build_gauntlet_report,
    determine_certification,
    CertificationLevel,
)


async def _explore_and_context(url: str):
    """Shared browser exploration step."""
    click.echo(f"🔍 Exploring {url}...")
    browser_ctx = await explore_url(url)
    click.echo(f"   Found {len(browser_ctx.elements)} interactive elements, "
               f"{len(browser_ctx.errors)} errors")
    product_context = build_product_context(browser_ctx)
    return browser_ctx, product_context


async def _run_community(
    url: str, product_context: str, browser_ctx,
    persona_descriptions: tuple[str, ...], persona_count: int,
    config, llm_client: LLMClient,
    competitors: tuple[str, ...] = (), skip_research: bool = False,
    use_real_personas: bool = False, subreddits: tuple[str, ...] = (),
    topics: tuple[str, ...] = (),
):
    """Run community testing (Stage 2 / standalone)."""
    count = persona_count or config.personas

    if use_real_personas:
        # Build personas FROM real social media users
        from urllib.parse import urlparse
        product_name = urlparse(url).netloc.replace("www.", "").split(".")[0]
        click.echo(f"📡 Scraping real users from Reddit/HN for '{product_name}'...")
        try:
            personas = await build_personas_from_research(
                product_name, count=count,
                competitors=competitors, subreddits=subreddits,
                topics=topics,
            )
            click.echo(f"👥 Built {len(personas)} personas from real social media users")
            if personas:
                real_count = sum(1 for p in personas if "Real user from" in p.background)
                click.echo(f"   {real_count} from real comments, {len(personas) - real_count} variants")
        except Exception as e:
            click.echo(f"   Research failed ({e}), falling back to defaults")
            personas = generate_default_personas()[:count]
    elif persona_descriptions:
        # Custom persona descriptions
        personas_list = []
        for desc in persona_descriptions:
            base = generate_custom_persona(desc)
            variants = generate_persona_variants(base, count=max(1, count // len(persona_descriptions)))
            personas_list.extend(variants)
        personas = tuple(personas_list[:count])
        click.echo(f"👥 Generated {len(personas)} custom personas")
    else:
        # Default personas, optionally enriched with research
        personas = generate_default_personas()
        if count < 20:
            personas = personas[:count]
        click.echo(f"👥 Using {len(personas)} default personas")

        if not skip_research:
            from urllib.parse import urlparse
            product_name = urlparse(url).netloc.replace("www.", "").split(".")[0]
            click.echo(f"📡 Researching real user feedback for '{product_name}'...")
            try:
                research = await research_product(product_name, competitors=competitors)
                click.echo(f"   Found {len(research.signals)} signals from Reddit/HN")
                if research.signals:
                    personas = enrich_personas(personas, research)
                    click.echo(f"   Enriched with real user data")
            except Exception as e:
                click.echo(f"   Research skipped ({e})")

    # Deep analysis
    click.echo(f"🧠 Running community test with {len(personas)} personas...")
    feedbacks = await run_deep_analysis(
        personas=personas,
        product_context=product_context,
        llm_client=llm_client,
        max_concurrent=config.max_concurrent,
    )

    pmf = calculate_pmf_signals(feedbacks)
    browser_errors = tuple(e.message for e in browser_ctx.errors)
    report = build_report(url, feedbacks, pmf, browser_errors)

    return pmf, report


async def _run_vc(
    url: str, product_context: str, llm_client: LLMClient, pitch: str = "",
    github_url: str = "", linkedin_url: str = "", twitter_url: str = "",
):
    """Run VC roast (Stage 1) with optional founder research."""
    # Research the founder before roasting
    founder_summary = ""
    if github_url or linkedin_url or twitter_url:
        click.echo(f"🔍 Researching founder...")
        founder = await research_founder(
            github_url=github_url,
            linkedin_url=linkedin_url,
            twitter_url=twitter_url,
            pitch_text=pitch,
        )
        founder_summary = founder.summary

        if founder.bluff_count > 0:
            click.echo(f"   ⚠️  Found {founder.bluff_count} bluff(s) — VCs will use this against you")
        credibility_pct = int(founder.overall_credibility * 100)
        click.echo(f"   Founder credibility: {credibility_pct}%")
        for check in founder.credibility_checks:
            icon = "✅" if check.flag.value == "verified" else "⚠️" if check.flag.value == "suspicious" else "🚨" if check.flag.value == "bluff" else "❓"
            click.echo(f"   {icon} {check.claim}: {check.flag.value}")

    # Use evolved VCs if gene pool exists
    pool = GenePool()
    pool_stats = pool.stats()
    if pool_stats["total"] > 0 and pool_stats["max_generation"] > 0:
        panel = get_evolved_vc_panel()
        click.echo(f"\n🧬 Using EVOLVED VC panel (gen {pool_stats['max_generation']}, {pool_stats['alive']} alive)")
    else:
        panel = None  # Use defaults
        click.echo("")

    click.echo(f"🔥 STAGE 1: VC ROAST PANEL 🔥")
    click.echo(f"   {len(panel) if panel else 5} VCs are about to destroy your prototype...\n")

    kwargs = {"product_context": product_context, "llm_client": llm_client,
              "pitch_text": pitch, "founder_summary": founder_summary}
    if panel:
        kwargs["panel"] = panel
    gate = await run_vc_panel(**kwargs)

    # Print live results
    click.echo(gate.summary_roast)

    if gate.passed:
        click.echo(f"\n😤 You SURVIVED the VC panel. Score: {gate.score}/100")
    else:
        click.echo(f"\n💀 DESTROYED. Score: {gate.score}/100")
        click.echo(f"   Fix these before trying again:")
        for fix in gate.must_fix:
            click.echo(f"   • {fix}")

    # Save run for later feedback
    import time
    from roastmymvp.evolution.feedback import save_run_results
    run_id = str(int(time.time()))
    verdicts_data = [
        {"persona_id": v.vc.name, "kill_shot": v.kill_shot, "score": v.score}
        for v in gate.verdicts
    ]
    save_run_results(run_id, url, "vc", verdicts_data)
    click.echo(f"\n   Run saved. Rate critiques with: roastmymvp feedback {run_id}")

    return gate


async def _run_mode(
    url: str, mode: str, persona_descriptions: tuple[str, ...],
    persona_count: int, output: str, config_path: str | None,
    competitors: tuple[str, ...], skip_research: bool, pitch: str,
    use_real_personas: bool = False, subreddits: tuple[str, ...] = (),
    topics: tuple[str, ...] = (),
    github_url: str = "", linkedin_url: str = "", twitter_url: str = "",
) -> None:
    config = load_config(config_path)
    llm_client = LLMClient()

    browser_ctx, product_context = await _explore_and_context(url)

    if mode == "vc":
        # VC-only mode
        gate = await _run_vc(url, product_context, llm_client, pitch, github_url, linkedin_url, twitter_url)
        report = build_vc_report(url, gate)
        output_path = output or "VC-ROAST-REPORT.md"
        with open(output_path, "w") as f:
            f.write(report)
        click.echo(f"\n📊 VC report saved to {output_path}")

    elif mode == "gauntlet":
        # Full gauntlet: VC → Community → Certification
        click.echo("=" * 60)
        click.echo("  THE GAUNTLET: VC GATE → COMMUNITY GATE → CERTIFICATION")
        click.echo("=" * 60)

        # Stage 1: VC Gate
        gate = await _run_vc(url, product_context, llm_client, pitch, github_url, linkedin_url, twitter_url)

        if not gate.passed:
            click.echo(f"\n🚫 VC GATE FAILED — Community testing LOCKED.")
            click.echo(f"   Fix the issues and try again.\n")
            result = determine_certification(gate)
            report = build_gauntlet_report(result, url)
        else:
            click.echo(f"\n✅ VC GATE PASSED — Unlocking Community Testing...\n")

            # Stage 2: Community Gate
            click.echo("=" * 60)
            click.echo("  STAGE 2: COMMUNITY TEST")
            click.echo("=" * 60)

            pmf, community_report = await _run_community(
                url, product_context, browser_ctx,
                persona_descriptions, persona_count,
                config, llm_client, competitors, skip_research,
                use_real_personas, subreddits, topics,
            )

            result = determine_certification(gate, pmf)
            report = build_gauntlet_report(result, url)

            # Print final certification
            click.echo(f"\n{'=' * 60}")
            if result.certification == CertificationLevel.CERTIFIED_GREAT:
                click.echo("  🏆 CERTIFIED GREAT PROJECT 🏆")
            elif result.certification == CertificationLevel.CERTIFIED_GOOD:
                click.echo("  ✅ CERTIFIED GOOD PROJECT ✅")
            else:
                click.echo("  😤 PASSED VC, FAILED COMMUNITY 😤")
            click.echo(f"  Final Score: {result.final_score}/100")
            click.echo(f"{'=' * 60}")

        output_path = output or "GAUNTLET-REPORT.md"
        with open(output_path, "w") as f:
            f.write(report)
        click.echo(f"\n📊 Gauntlet report saved to {output_path}")

    else:
        # Default: community-only mode
        pmf, report = await _run_community(
            url, product_context, browser_ctx,
            persona_descriptions, persona_count,
            config, llm_client, competitors, skip_research,
            use_real_personas, subreddits, topics,
        )
        output_path = output or config.output_file
        with open(output_path, "w") as f:
            f.write(report)
        click.echo(f"\n📊 Report saved to {output_path}")
        click.echo(f"   Verdict: {pmf.verdict}")
        click.echo(f"   Download: {pmf.download_rate:.0%} | Pay: {pmf.pay_rate:.0%} | Return: {pmf.return_rate:.0%}")


@click.command()
@click.argument("url")
@click.option("--mode", "-m", default="community", type=click.Choice(["community", "vc", "gauntlet"]),
              help="Testing mode: community (default), vc (roast only), gauntlet (VC → community)")
@click.option("--personas", "-n", default=0, help="Number of personas (default: 20)")
@click.option("--persona", "-p", multiple=True, help="Custom persona description (repeatable)")
@click.option("--output", "-o", default="", help="Output file path")
@click.option("--config", "-c", default=None, help="Path to .ai-beta-test.yaml config file")
@click.option("--competitor", multiple=True, help="Competitor name for research (repeatable)")
@click.option("--skip-research", is_flag=True, help="Skip Reddit/HN research")
@click.option("--pitch", default="", help="Pitch text or elevator pitch for VC mode")
@click.option("--real", is_flag=True, help="Build personas from real Reddit/HN users instead of defaults")
@click.option("--subreddit", "-s", multiple=True, help="Specific subreddits to scrape (repeatable)")
@click.option("--topic", "-t", multiple=True, help="Search terms for finding real users (repeatable)")
@click.option("--github", default="", help="Founder's GitHub URL (VCs will research you)")
@click.option("--linkedin", default="", help="Founder's LinkedIn URL")
@click.option("--twitter", default="", help="Founder's Twitter/X URL")
def main(url: str, mode: str, personas: int, persona: tuple[str, ...], output: str,
         config: str | None, competitor: tuple[str, ...], skip_research: bool, pitch: str,
         real: bool, subreddit: tuple[str, ...], topic: tuple[str, ...],
         github: str, linkedin: str, twitter: str) -> None:
    """AI-simulated beta testing with real user personas.

    Three modes:

      community  — AI personas test your product (default)

      vc         — Brutal VC panel roasts your prototype

      gauntlet   — Must pass VC gate to unlock community testing

    Examples:

        roastmymvp https://your-app.com --real -n 20

        roastmymvp https://your-app.com --real -n 50 -s actuary -s math

        roastmymvp https://your-app.com --mode vc --pitch "Uber for dogs"

        roastmymvp https://your-app.com --mode gauntlet --real
    """
    if not url.startswith(("http://", "https://")):
        url = f"https://{url}"

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    has_claude_cli = shutil.which("claude") is not None

    if not api_key and not has_claude_cli:
        click.echo("Error: No LLM backend available.", err=True)
        click.echo("Either:", err=True)
        click.echo("  1. Install Claude Code (claude CLI) — uses your subscription", err=True)
        click.echo("  2. Set ANTHROPIC_API_KEY environment variable", err=True)
        sys.exit(1)

    if has_claude_cli and not api_key:
        click.echo("Using claude CLI backend (your Claude Code subscription)")

    asyncio.run(_run_mode(url, mode, persona, personas, output, config, competitor, skip_research, pitch, real, subreddit, topic, github, linkedin, twitter))


@click.command("evolve")
def evolve_cmd():
    """Run an evolution cycle on the persona gene pool.

    Mutates low-performing personas, breeds top performers,
    and kills consistently bad critics. Run this after giving feedback.
    """
    from roastmymvp.evolution.genes import GenePool

    pool = GenePool()
    stats_before = pool.stats()

    if stats_before["total"] == 0:
        click.echo("Gene pool is empty. Initializing from defaults...")
        from roastmymvp.evolution.feedback import initialize_gene_pool_from_defaults
        init_stats = initialize_gene_pool_from_defaults()
        click.echo(f"Seeded {init_stats['total']} personas into gene pool")
        return

    click.echo(f"Gene pool: {stats_before['alive']} alive, gen {stats_before['max_generation']}")
    mutations = pool.evolve()

    if mutations:
        click.echo(f"\n🧬 Evolution cycle complete — {len(mutations)} changes:")
        for m in mutations:
            click.echo(f"   {m}")
    else:
        click.echo("\nNo mutations this cycle. Need more feedback data.")

    stats_after = pool.stats()
    click.echo(f"\nPool: {stats_after['alive']} alive, avg fitness {stats_after['avg_fitness']:.2f}, gen {stats_after['max_generation']}")


@click.command("feedback")
@click.argument("run_id", default="latest")
def feedback_cmd(run_id: str):
    """Rate the usefulness of critiques from a run.

    This drives evolution — good critiques survive, bad ones die.

    Example: roastmymvp feedback latest
    """
    from roastmymvp.evolution.feedback import FEEDBACK_DIR, collect_feedback_for_run
    import json

    # Find the run file
    if run_id == "latest":
        files = sorted(FEEDBACK_DIR.glob("run_*.json"), key=lambda f: f.stat().st_mtime, reverse=True)
        if not files:
            click.echo("No runs found. Run a roast first.")
            return
        run_file = files[0]
    else:
        run_file = FEEDBACK_DIR / f"run_{run_id}.json"

    if not run_file.exists():
        click.echo(f"Run file not found: {run_file}")
        return

    run_data = json.loads(run_file.read_text())
    click.echo(f"Rating run: {run_data['url']} ({run_data['mode']} mode)\n")

    ratings = {}
    for v in run_data.get("verdicts", []):
        persona_id = v.get("persona_id", v.get("vc_name", "unknown"))
        kill_shot = v.get("kill_shot", v.get("top_issue", ""))
        click.echo(f"  {persona_id}: \"{kill_shot[:80]}...\"")
        score = click.prompt(f"  Rate (0=useless, 5=ok, 10=killer insight)", type=float, default=5.0)
        ratings[persona_id] = score / 10.0

    result = collect_feedback_for_run(run_data["run_id"], ratings)

    # Mark as collected
    run_data["feedback_collected"] = True
    run_file.write_text(json.dumps(run_data, indent=2))

    click.echo(f"\nFeedback applied to {result['ratings_applied']} personas")
    if result["evolved"]:
        click.echo(f"🧬 Evolution triggered! {len(result['mutations'])} mutations:")
        for m in result["mutations"]:
            click.echo(f"   {m}")
    else:
        click.echo(f"Next evolution in {5 - (result['total_sessions'] % 5)} more feedback sessions")


@click.command("pool")
def pool_cmd():
    """Show the current state of the persona gene pool."""
    from roastmymvp.evolution.genes import GenePool

    pool = GenePool()
    stats = pool.stats()

    if stats["total"] == 0:
        click.echo("Gene pool is empty. Run 'roastmymvp evolve' to initialize.")
        return

    click.echo(f"🧬 Gene Pool Status")
    click.echo(f"   Total personas: {stats['total']}")
    click.echo(f"   Alive: {stats['alive']}")
    click.echo(f"   Dead: {stats['dead']}")
    click.echo(f"   Avg fitness: {stats['avg_fitness']:.2f}")
    click.echo(f"   Max generation: {stats['max_generation']}")
    click.echo(f"   Total mutations: {stats['total_mutations']}")

    click.echo(f"\n   Top performers:")
    alive = sorted(pool.all_alive(), key=lambda g: g.avg_usefulness, reverse=True)[:5]
    for g in alive:
        click.echo(f"   {'🔥' if g.avg_usefulness > 0.7 else '  '} {g.persona_id}: "
                   f"fitness {g.avg_usefulness:.2f}, gen {g.generation}, "
                   f"{g.total_runs} runs")


@click.group()
def cli():
    """RoastMyMVP — AI-simulated beta testing with evolving personas."""
    pass


cli.add_command(main, "run")
cli.add_command(evolve_cmd, "evolve")
cli.add_command(feedback_cmd, "feedback")
cli.add_command(pool_cmd, "pool")


if __name__ == "__main__":
    cli()
