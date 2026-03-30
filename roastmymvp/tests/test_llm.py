"""Tests for LLM client — uses mock to avoid real API/CLI calls."""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from roastmymvp.llm.models import LLMRequest, LLMResponse, ModelTier


class TestLLMModels:
    def test_request_defaults(self):
        req = LLMRequest(prompt="Hello")
        assert req.model_tier == ModelTier.DEEP
        assert req.max_tokens == 4096
        assert req.temperature == 0.7

    def test_request_fast_tier(self):
        req = LLMRequest(prompt="Rate this", model_tier=ModelTier.FAST)
        assert req.model_tier == ModelTier.FAST

    def test_response_frozen(self):
        resp = LLMResponse(
            content="Hello",
            model="claude-sonnet-4-6",
            input_tokens=10,
            output_tokens=5,
            cost_usd=0.001,
        )
        with pytest.raises(AttributeError):
            resp.content = "Changed"


class TestLLMClientAPI:
    """Tests for the Anthropic API backend."""

    @pytest.mark.asyncio
    async def test_send_returns_response(self):
        from roastmymvp.llm.client import LLMClient

        mock_message = MagicMock()
        mock_message.content = [MagicMock(text="Test response")]
        mock_message.model = "claude-sonnet-4-6"
        mock_message.usage.input_tokens = 100
        mock_message.usage.output_tokens = 50

        mock_anthropic = MagicMock()
        mock_anthropic.messages.create = AsyncMock(return_value=mock_message)

        client = LLMClient(backend="api", anthropic_client=mock_anthropic)
        req = LLMRequest(prompt="Hello")
        resp = await client.send(req)

        assert isinstance(resp, LLMResponse)
        assert resp.content == "Test response"
        assert resp.input_tokens == 100

    @pytest.mark.asyncio
    async def test_deep_uses_sonnet(self):
        from roastmymvp.llm.client import LLMClient

        mock_message = MagicMock()
        mock_message.content = [MagicMock(text="Response")]
        mock_message.model = "claude-sonnet-4-6"
        mock_message.usage.input_tokens = 10
        mock_message.usage.output_tokens = 5

        mock_anthropic = MagicMock()
        mock_anthropic.messages.create = AsyncMock(return_value=mock_message)

        client = LLMClient(backend="api", anthropic_client=mock_anthropic)
        req = LLMRequest(prompt="Analyze", model_tier=ModelTier.DEEP)
        await client.send(req)

        call_kwargs = mock_anthropic.messages.create.call_args[1]
        assert "sonnet" in call_kwargs["model"]

    @pytest.mark.asyncio
    async def test_fast_uses_haiku(self):
        from roastmymvp.llm.client import LLMClient

        mock_message = MagicMock()
        mock_message.content = [MagicMock(text="Response")]
        mock_message.model = "claude-haiku-4-5-20251001"
        mock_message.usage.input_tokens = 10
        mock_message.usage.output_tokens = 5

        mock_anthropic = MagicMock()
        mock_anthropic.messages.create = AsyncMock(return_value=mock_message)

        client = LLMClient(backend="api", anthropic_client=mock_anthropic)
        req = LLMRequest(prompt="Rate", model_tier=ModelTier.FAST)
        await client.send(req)

        call_kwargs = mock_anthropic.messages.create.call_args[1]
        assert "haiku" in call_kwargs["model"]

    @pytest.mark.asyncio
    async def test_cost_calculation(self):
        from roastmymvp.llm.client import LLMClient

        mock_message = MagicMock()
        mock_message.content = [MagicMock(text="Response")]
        mock_message.model = "claude-sonnet-4-6"
        mock_message.usage.input_tokens = 1000
        mock_message.usage.output_tokens = 500

        mock_anthropic = MagicMock()
        mock_anthropic.messages.create = AsyncMock(return_value=mock_message)

        client = LLMClient(backend="api", anthropic_client=mock_anthropic)
        req = LLMRequest(prompt="Analyze")
        resp = await client.send(req)

        assert resp.cost_usd > 0

    @pytest.mark.asyncio
    async def test_system_prompt_passed(self):
        from roastmymvp.llm.client import LLMClient

        mock_message = MagicMock()
        mock_message.content = [MagicMock(text="Response")]
        mock_message.model = "claude-sonnet-4-6"
        mock_message.usage.input_tokens = 10
        mock_message.usage.output_tokens = 5

        mock_anthropic = MagicMock()
        mock_anthropic.messages.create = AsyncMock(return_value=mock_message)

        client = LLMClient(backend="api", anthropic_client=mock_anthropic)
        req = LLMRequest(prompt="Hello", system="You are a tester")
        await client.send(req)

        call_kwargs = mock_anthropic.messages.create.call_args[1]
        assert call_kwargs["system"] == "You are a tester"


class TestLLMClientCLI:
    """Tests for the claude CLI backend."""

    @pytest.mark.asyncio
    async def test_cli_send_returns_response(self):
        from roastmymvp.llm.client import LLMClient

        mock_proc = AsyncMock()
        mock_proc.communicate = AsyncMock(return_value=(
            b'{"would_download": true, "narrative": "Great product"}',
            b"",
        ))
        mock_proc.returncode = 0

        with patch("roastmymvp.llm.client.asyncio.create_subprocess_exec", return_value=mock_proc):
            client = LLMClient(backend="cli")
            req = LLMRequest(prompt="Test prompt")
            resp = await client.send(req)

        assert isinstance(resp, LLMResponse)
        assert "would_download" in resp.content
        assert resp.cost_usd == 0.0
        assert "cli" in resp.model

    @pytest.mark.asyncio
    async def test_cli_passes_model_flag(self):
        from roastmymvp.llm.client import LLMClient

        mock_proc = AsyncMock()
        mock_proc.communicate = AsyncMock(return_value=(b"response", b""))
        mock_proc.returncode = 0

        with patch("roastmymvp.llm.client.asyncio.create_subprocess_exec", return_value=mock_proc) as mock_exec:
            client = LLMClient(backend="cli")
            req = LLMRequest(prompt="Test", model_tier=ModelTier.FAST)
            await client.send(req)

        # Check that --model haiku was passed
        call_args = mock_exec.call_args[0]
        assert "haiku" in call_args

    @pytest.mark.asyncio
    async def test_cli_deep_uses_sonnet(self):
        from roastmymvp.llm.client import LLMClient

        mock_proc = AsyncMock()
        mock_proc.communicate = AsyncMock(return_value=(b"response", b""))
        mock_proc.returncode = 0

        with patch("roastmymvp.llm.client.asyncio.create_subprocess_exec", return_value=mock_proc) as mock_exec:
            client = LLMClient(backend="cli")
            req = LLMRequest(prompt="Test", model_tier=ModelTier.DEEP)
            await client.send(req)

        call_args = mock_exec.call_args[0]
        assert "sonnet" in call_args

    @pytest.mark.asyncio
    async def test_cli_includes_system_in_prompt(self):
        from roastmymvp.llm.client import LLMClient

        mock_proc = AsyncMock()
        mock_proc.communicate = AsyncMock(return_value=(b"response", b""))
        mock_proc.returncode = 0

        with patch("roastmymvp.llm.client.asyncio.create_subprocess_exec", return_value=mock_proc) as mock_exec:
            client = LLMClient(backend="cli")
            req = LLMRequest(prompt="Hello", system="You are a tester")
            await client.send(req)

        # System prompt should be included in stdin
        stdin_data = mock_proc.communicate.call_args[1]["input"].decode()
        assert "You are a tester" in stdin_data
        assert "Hello" in stdin_data

    @pytest.mark.asyncio
    async def test_cli_error_raises(self):
        from roastmymvp.llm.client import LLMClient

        mock_proc = AsyncMock()
        mock_proc.communicate = AsyncMock(return_value=(b"", b"Error: auth failed"))
        mock_proc.returncode = 1

        with patch("roastmymvp.llm.client.asyncio.create_subprocess_exec", return_value=mock_proc):
            client = LLMClient(backend="cli")
            req = LLMRequest(prompt="Test")
            with pytest.raises(RuntimeError, match="claude CLI error"):
                await client.send(req)


class TestBackendDetection:
    def test_api_key_prefers_api(self):
        from roastmymvp.llm.client import _detect_backend

        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-test"}):
            assert _detect_backend() == "api"

    def test_cli_fallback(self):
        from roastmymvp.llm.client import _detect_backend

        with patch.dict("os.environ", {}, clear=True):
            with patch("roastmymvp.llm.client.shutil.which", return_value="/usr/local/bin/claude"):
                assert _detect_backend() == "cli"

    def test_no_backend_falls_to_api(self):
        from roastmymvp.llm.client import _detect_backend

        with patch.dict("os.environ", {}, clear=True):
            with patch("roastmymvp.llm.client.shutil.which", return_value=None):
                assert _detect_backend() == "api"
