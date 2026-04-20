"""
LLM Gateway — the SINGLE swap point for all LLM calls.

Change LLM_PROVIDER and LLM_MODEL in your .env to switch models:
  - gemini   → LLM_MODEL=gemini/gemini-2.0-flash
  - ollama   → LLM_MODEL=ollama/mistral
  - claude   → LLM_MODEL=claude-3-5-sonnet-20241022
  - openai   → LLM_MODEL=gpt-4o-mini

All application code calls LLMGateway.generate() — never talks to
a specific provider directly.
"""

import logging
from dataclasses import dataclass

import litellm

from backend.app.config import get_settings

logger = logging.getLogger(__name__)

# Silence litellm's noisy logs
litellm.suppress_debug_info = True


@dataclass
class LLMResponse:
    """Wrapper around LLM provider responses."""
    content: str
    model: str
    usage: dict | None = None


class LLMGateway:
    """Unified interface to any LLM provider via LiteLLM."""

    def __init__(self):
        self.settings = get_settings()
        self._configure_api_keys()

    def _configure_api_keys(self):
        """Inject the correct API key based on active provider."""
        provider = self.settings.LLM_PROVIDER.lower()

        if provider == "gemini":
            litellm.api_key = self.settings.GEMINI_API_KEY
            # LiteLLM reads GEMINI_API_KEY from env automatically,
            # but we set it explicitly for clarity.
            import os
            os.environ["GEMINI_API_KEY"] = self.settings.GEMINI_API_KEY
        elif provider == "openai":
            litellm.api_key = self.settings.OPENAI_API_KEY
        elif provider == "claude" or provider == "anthropic":
            import os
            os.environ["ANTHROPIC_API_KEY"] = self.settings.ANTHROPIC_API_KEY
        elif provider == "ollama":
            litellm.api_base = self.settings.OLLAMA_BASE_URL
        else:
            logger.warning(f"Unknown LLM provider: {provider}")

    async def generate(
        self,
        prompt: str,
        system_message: str | None = None,
        temperature: float = 0.3,
        max_tokens: int = 2048,
        json_mode: bool = False,
    ) -> LLMResponse:
        """
        Send a prompt to the configured LLM and return the response.

        Args:
            prompt: The user message / prompt text.
            system_message: Optional system prompt.
            temperature: Creativity control (0.0 = deterministic, 1.0 = creative).
            max_tokens: Maximum response length.
            json_mode: If True, request JSON output (model-dependent support).

        Returns:
            LLMResponse with content, model name, and token usage.
        """
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})

        model = self.settings.LLM_MODEL

        try:
            kwargs = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }

            if json_mode:
                kwargs["response_format"] = {"type": "json_object"}

            response = await litellm.acompletion(**kwargs)

            content = response.choices[0].message.content or ""
            usage = None
            if response.usage:
                usage = {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                }

            logger.info(f"LLM [{model}] responded — tokens: {usage}")
            return LLMResponse(content=content, model=model, usage=usage)

        except Exception as e:
            logger.error(f"LLM call failed [{model}]: {e}")

            # Try fallback if configured
            fallback_model = self.settings.LLM_FALLBACK_MODEL
            if fallback_model:
                logger.info(f"Trying fallback model: {fallback_model}")
                try:
                    kwargs["model"] = fallback_model
                    response = await litellm.acompletion(**kwargs)
                    content = response.choices[0].message.content or ""
                    return LLMResponse(content=content, model=fallback_model)
                except Exception as fe:
                    logger.error(f"Fallback also failed [{fallback_model}]: {fe}")

            raise RuntimeError(f"LLM generation failed: {e}") from e

    async def generate_with_history(
        self,
        messages: list[dict],
        system_message: str | None = None,
        temperature: float = 0.3,
        max_tokens: int = 2048,
    ) -> LLMResponse:
        """
        Send a full conversation history to the LLM.

        Args:
            messages: List of {"role": "user"|"assistant", "content": "..."} dicts.
            system_message: Optional system prompt (prepended).
        """
        full_messages = []
        if system_message:
            full_messages.append({"role": "system", "content": system_message})
        full_messages.extend(messages)

        model = self.settings.LLM_MODEL

        try:
            response = await litellm.acompletion(
                model=model,
                messages=full_messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            content = response.choices[0].message.content or ""
            return LLMResponse(content=content, model=model)

        except Exception as e:
            logger.error(f"LLM call with history failed [{model}]: {e}")
            raise RuntimeError(f"LLM generation failed: {e}") from e


# ── Module-level singleton ──────────────────────────────────────────
_gateway: LLMGateway | None = None


def get_llm_gateway() -> LLMGateway:
    """Return a shared LLMGateway instance."""
    global _gateway
    if _gateway is None:
        _gateway = LLMGateway()
    return _gateway
