"""Tests for CLI and config modules."""

import os
import tempfile
import pytest
import yaml

from click.testing import CliRunner

from roastmymvp.config import Config, load_config


class TestConfig:
    def test_defaults(self):
        config = Config()
        assert config.personas == 20
        assert config.output_file == "FEEDBACK-REPORT.md"
        assert config.max_concurrent == 5

    def test_frozen(self):
        config = Config()
        with pytest.raises(AttributeError):
            config.personas = 10

    def test_load_missing_file(self):
        config = load_config("/nonexistent/path.yaml")
        assert config.personas == 20

    def test_load_yaml(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump({
                "personas": 10,
                "output_file": "report.md",
                "custom_personas": ["developer", "designer"],
                "max_concurrent": 3,
            }, f)
            path = f.name

        try:
            config = load_config(path)
            assert config.personas == 10
            assert config.output_file == "report.md"
            assert len(config.custom_personas) == 2
            assert config.max_concurrent == 3
        finally:
            os.unlink(path)

    def test_load_empty_yaml(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("")
            path = f.name

        try:
            config = load_config(path)
            assert config.personas == 20  # defaults
        finally:
            os.unlink(path)


class TestCLI:
    def test_help(self):
        from roastmymvp.cli import main

        runner = CliRunner()
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "AI-simulated beta testing" in result.output

    def test_missing_all_backends(self):
        from roastmymvp.cli import main
        from unittest.mock import patch

        runner = CliRunner(env={"ANTHROPIC_API_KEY": ""})
        with patch("roastmymvp.cli.shutil.which", return_value=None):
            result = runner.invoke(main, ["https://example.com"])
        assert result.exit_code == 1
        assert "No LLM backend" in result.output

    def test_detects_claude_cli(self):
        from roastmymvp.cli import main
        from unittest.mock import patch

        runner = CliRunner(env={"ANTHROPIC_API_KEY": ""})
        # Mock claude CLI as available but don't actually run the pipeline
        with patch("roastmymvp.cli.shutil.which", return_value="/usr/local/bin/claude"):
            with patch("roastmymvp.cli.asyncio.run", side_effect=SystemExit(0)):
                result = runner.invoke(main, ["example.com"])
        assert "claude CLI backend" in result.output
