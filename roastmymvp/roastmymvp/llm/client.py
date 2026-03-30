"""LLM client with multiple backends: claude CLI (default), Anthropic API (optional)."""

import asyncio
import json
import os
import shutil
import logging

from roastmymvp.llm.models import LLMRequest, LLMResponse, ModelTier

logger = logging.getLogger(__name__)

# Model IDs for API backend
_API_MODELS = {
    ModelTier.DEEP: "claude-sonnet-4-6",
    ModelTier.FAST: "claude-haiku-4-5-20251001",
}

# Model flags for claude CLI backend
_CLI_MODELS = {
    ModelTier.DEEP: "sonnet",
    ModelTier.FAST: "haiku",
}

# Cost per million tokens (USD) — for tracking only
_PRICING = {
    "claude-sonnet-4-6": {"input": 3.0, "output": 15.0},
    "claude-haiku-4-5-20251001": {"input": 0.80, "output": 4.0},
    "claude-cli": {"input": 0.0, "output": 0.0},  # Included in subscription
}


def _extract_json(text: str) -> str:
    """Extract JSON from text that may be wrapped in markdown code blocks."""
    import re

    # Try to find JSON in ```json ... ``` blocks
    match = re.search(r'```(?:json)?\s*\n?([\s\S]*?)\n?```', text)
    if match:
        return match.group(1).strip()

    # Try to find raw JSON object
    match = re.search(r'(\{[\s\S]*\})', text)
    if match:
        return match.group(1).strip()

    return text


def _calculate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    pricing = _PRICING.get(model, {"input": 0.0, "output": 0.0})
    input_cost = (input_tokens / 1_000_000) * pricing["input"]
    output_cost = (output_tokens / 1_000_000) * pricing["output"]
    return round(input_cost + output_cost, 6)


def _detect_backend() -> str:
    """Detect which backend to use: 'cli' if claude is installed, else 'api'."""
    if os.environ.get("ANTHROPIC_API_KEY"):
        return "api"
    if shutil.which("claude"):
        return "cli"
    return "api"  # Will fail with clear error message


class LLMClient:
    """LLM client supporting both claude CLI and Anthropic API backends.

    Priority:
    1. Explicit backend passed to constructor
    2. ANTHROPIC_API_KEY set → API backend
    3. claude CLI installed → CLI backend (uses your Claude Code subscription)
    """

    def __init__(self, backend: str | None = None, anthropic_client=None):
        self._backend = backend or _detect_backend()
        self._anthropic_client = anthropic_client

    async def send(self, request: LLMRequest) -> LLMResponse:
        if self._backend == "cli":
            return await self._send_cli(request)
        else:
            return await self._send_api(request)

    async def _send_cli(self, request: LLMRequest) -> LLMResponse:
        """Send request via claude -p CLI (uses Claude Code subscription)."""
        model_flag = _CLI_MODELS[request.model_tier]

        # Build the full prompt with system context
        full_prompt = request.prompt
        if request.system:
            full_prompt = f"[System: {request.system}]\n\n{request.prompt}"

        # Run claude -p with the prompt piped to stdin
        cmd = ["claude", "-p", "--model", model_flag]

        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await proc.communicate(input=full_prompt.encode())

        if proc.returncode != 0:
            error_msg = stderr.decode().strip() or f"claude CLI exited with code {proc.returncode}"
            raise RuntimeError(f"claude CLI error: {error_msg}")

        content = stdout.decode().strip()

        # Claude CLI often wraps JSON in markdown code blocks — extract it
        content = _extract_json(content)

        # Estimate tokens (rough: 1 token ≈ 4 chars)
        est_input = len(full_prompt) // 4
        est_output = len(content) // 4

        return LLMResponse(
            content=content,
            model=f"claude-cli-{model_flag}",
            input_tokens=est_input,
            output_tokens=est_output,
            cost_usd=0.0,  # Included in subscription
        )

    async def _send_api(self, request: LLMRequest) -> LLMResponse:
        """Send request via Anthropic API (requires ANTHROPIC_API_KEY)."""
        client = self._get_api_client()
        model = _API_MODELS[request.model_tier]

        kwargs = {
            "model": model,
            "max_tokens": request.max_tokens,
            "temperature": request.temperature,
            "messages": [{"role": "user", "content": request.prompt}],
            "system": request.system,
        }

        message = await client.messages.create(**kwargs)

        content = message.content[0].text
        input_tokens = message.usage.input_tokens
        output_tokens = message.usage.output_tokens

        return LLMResponse(
            content=content,
            model=message.model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=_calculate_cost(model, input_tokens, output_tokens),
        )

    def _get_api_client(self):
        if self._anthropic_client is None:
            import anthropic
            self._anthropic_client = anthropic.AsyncAnthropic()
        return self._anthropic_client
