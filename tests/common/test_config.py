"""Tests for AgentConfig configuration model."""

import pytest
from pydantic import ValidationError

from src.common.config import AgentConfig


class TestAgentConfig:
    """Test suite for the AgentConfig model."""

    def test_config_creation_with_defaults(self):
        """Test creating config with all default values."""
        config = AgentConfig()
        assert config.system_prompt is None
        assert config.model is None
        assert config.temperature == 0.7
        assert config.max_tokens is None
        assert config.api_key is None
        assert config.timeout == 30
        assert config.retry_attempts == 3

    def test_config_creation_with_all_fields(self):
        """Test creating config with all fields specified."""
        config = AgentConfig(
            system_prompt="You are a helpful assistant",
            model="gpt-4",
            temperature=0.5,
            max_tokens=2000,
            api_key="sk-test-key",
            timeout=60,
            retry_attempts=5
        )
        assert config.system_prompt == "You are a helpful assistant"
        assert config.model == "gpt-4"
        assert config.temperature == 0.5
        assert config.max_tokens == 2000
        assert config.api_key == "sk-test-key"
        assert config.timeout == 60
        assert config.retry_attempts == 5

    def test_config_creation_partial(self):
        """Test creating config with some fields specified."""
        config = AgentConfig(
            system_prompt="Custom prompt",
            model="claude-3-5-sonnet-20241022"
        )
        assert config.system_prompt == "Custom prompt"
        assert config.model == "claude-3-5-sonnet-20241022"
        assert config.temperature == 0.7  # Default
        assert config.max_tokens is None  # Default

    def test_config_temperature_validation_min(self):
        """Test that temperature must be >= 0.0."""
        with pytest.raises(ValidationError) as exc_info:
            AgentConfig(temperature=-0.1)

        assert "temperature" in str(exc_info.value).lower()

    def test_config_temperature_validation_max(self):
        """Test that temperature must be <= 1.0."""
        with pytest.raises(ValidationError) as exc_info:
            AgentConfig(temperature=1.1)

        assert "temperature" in str(exc_info.value).lower()

    def test_config_temperature_boundary_values(self):
        """Test temperature at boundary values (0.0 and 1.0)."""
        config_min = AgentConfig(temperature=0.0)
        assert config_min.temperature == 0.0

        config_max = AgentConfig(temperature=1.0)
        assert config_max.temperature == 1.0

    def test_config_timeout_validation(self):
        """Test that timeout must be > 0."""
        with pytest.raises(ValidationError) as exc_info:
            AgentConfig(timeout=0)

        assert "timeout" in str(exc_info.value).lower()

        with pytest.raises(ValidationError) as exc_info:
            AgentConfig(timeout=-1)

        assert "timeout" in str(exc_info.value).lower()

    def test_config_timeout_positive_value(self):
        """Test timeout with valid positive value."""
        config = AgentConfig(timeout=120)
        assert config.timeout == 120

    def test_config_retry_attempts_validation(self):
        """Test that retry_attempts must be >= 0."""
        with pytest.raises(ValidationError) as exc_info:
            AgentConfig(retry_attempts=-1)

        assert "retry_attempts" in str(exc_info.value).lower()

    def test_config_retry_attempts_zero(self):
        """Test retry_attempts can be zero (no retries)."""
        config = AgentConfig(retry_attempts=0)
        assert config.retry_attempts == 0

    def test_config_retry_attempts_large_value(self):
        """Test retry_attempts with large value."""
        config = AgentConfig(retry_attempts=10)
        assert config.retry_attempts == 10

    def test_config_max_tokens_none(self):
        """Test max_tokens can be None (no limit)."""
        config = AgentConfig(max_tokens=None)
        assert config.max_tokens is None

    def test_config_max_tokens_positive(self):
        """Test max_tokens with positive value."""
        config = AgentConfig(max_tokens=4000)
        assert config.max_tokens == 4000

    def test_config_api_key_none(self):
        """Test api_key can be None."""
        config = AgentConfig(api_key=None)
        assert config.api_key is None

    def test_config_api_key_string(self):
        """Test api_key with string value."""
        config = AgentConfig(api_key="sk-1234567890")
        assert config.api_key == "sk-1234567890"

    def test_config_system_prompt_none(self):
        """Test system_prompt can be None."""
        config = AgentConfig(system_prompt=None)
        assert config.system_prompt is None

    def test_config_system_prompt_long_text(self):
        """Test system_prompt with long text."""
        long_prompt = "You are a helpful assistant. " * 100
        config = AgentConfig(system_prompt=long_prompt)
        assert config.system_prompt == long_prompt
        assert len(config.system_prompt) > 1000

    def test_config_model_none(self):
        """Test model can be None."""
        config = AgentConfig(model=None)
        assert config.model is None

    def test_config_model_various_names(self):
        """Test model with various model names."""
        model_names = [
            "gpt-4",
            "gpt-3.5-turbo",
            "claude-3-5-sonnet-20241022",
            "claude-3-opus-20240229",
            "mistral-large",
            "llama-2-70b"
        ]

        for model_name in model_names:
            config = AgentConfig(model=model_name)
            assert config.model == model_name

    def test_config_serialization(self):
        """Test config can be serialized to dict."""
        config = AgentConfig(
            system_prompt="Test prompt",
            model="gpt-4",
            temperature=0.8,
            max_tokens=1500,
            api_key="test-key",
            timeout=45,
            retry_attempts=2
        )

        data = config.model_dump()
        assert data["system_prompt"] == "Test prompt"
        assert data["model"] == "gpt-4"
        assert data["temperature"] == 0.8
        assert data["max_tokens"] == 1500
        assert data["api_key"] == "test-key"
        assert data["timeout"] == 45
        assert data["retry_attempts"] == 2

    def test_config_json_serialization(self):
        """Test config can be serialized to JSON."""
        config = AgentConfig(
            model="gpt-4",
            temperature=0.7,
            max_tokens=2000
        )

        json_str = config.model_dump_json()
        assert "gpt-4" in json_str
        assert "0.7" in json_str
        assert "2000" in json_str

    def test_config_deserialization(self):
        """Test config can be created from dict."""
        data = {
            "system_prompt": "You are an AI assistant",
            "model": "gpt-4",
            "temperature": 0.6,
            "max_tokens": 1000,
            "api_key": "sk-test",
            "timeout": 60,
            "retry_attempts": 4
        }

        config = AgentConfig(**data)
        assert config.system_prompt == data["system_prompt"]
        assert config.model == data["model"]
        assert config.temperature == data["temperature"]
        assert config.max_tokens == data["max_tokens"]
        assert config.api_key == data["api_key"]
        assert config.timeout == data["timeout"]
        assert config.retry_attempts == data["retry_attempts"]

    def test_config_with_exclude_none_serialization(self):
        """Test serialization excluding None values."""
        config = AgentConfig(
            model="gpt-4",
            temperature=0.7
            # system_prompt, max_tokens, api_key are None
        )

        data = config.model_dump(exclude_none=True)
        assert "model" in data
        assert "temperature" in data
        assert "timeout" in data
        assert "retry_attempts" in data
        assert "system_prompt" not in data
        assert "max_tokens" not in data
        assert "api_key" not in data

    def test_config_update_via_copy(self):
        """Test updating config via model_copy."""
        original = AgentConfig(
            model="gpt-3.5-turbo",
            temperature=0.5
        )

        updated = original.model_copy(update={"model": "gpt-4", "temperature": 0.8})

        # Original unchanged
        assert original.model == "gpt-3.5-turbo"
        assert original.temperature == 0.5

        # Updated has new values
        assert updated.model == "gpt-4"
        assert updated.temperature == 0.8

    def test_config_empty_string_values(self):
        """Test config with empty strings (should be allowed)."""
        config = AgentConfig(
            system_prompt="",
            model="",
            api_key=""
        )
        assert config.system_prompt == ""
        assert config.model == ""
        assert config.api_key == ""


class TestAgentConfigUseCases:
    """Test realistic use cases for AgentConfig."""

    def test_openai_agent_config(self):
        """Test typical OpenAI agent configuration."""
        config = AgentConfig(
            system_prompt="You are a data analysis assistant.",
            model="gpt-4-turbo-preview",
            temperature=0.7,
            max_tokens=4000,
            api_key="sk-openai-key",
            timeout=60,
            retry_attempts=3
        )

        assert config.model == "gpt-4-turbo-preview"
        assert config.max_tokens == 4000

    def test_anthropic_agent_config(self):
        """Test typical Anthropic (Claude) agent configuration."""
        config = AgentConfig(
            system_prompt="You are Claude, an AI assistant.",
            model="claude-3-5-sonnet-20241022",
            temperature=0.5,
            max_tokens=8000,
            api_key="sk-ant-key",
            timeout=120,
            retry_attempts=2
        )

        assert config.model == "claude-3-5-sonnet-20241022"
        assert config.max_tokens == 8000

    def test_minimal_config_for_testing(self):
        """Test minimal config suitable for testing."""
        config = AgentConfig()
        # Should work with all defaults
        assert config.temperature == 0.7
        assert config.timeout == 30
        assert config.retry_attempts == 3

    def test_config_for_fast_responses(self):
        """Test config optimized for fast responses."""
        config = AgentConfig(
            model="gpt-3.5-turbo",
            temperature=0.3,
            max_tokens=500,
            timeout=10,
            retry_attempts=1
        )

        assert config.timeout == 10
        assert config.max_tokens == 500
        assert config.retry_attempts == 1

    def test_config_for_creative_tasks(self):
        """Test config optimized for creative tasks."""
        config = AgentConfig(
            system_prompt="You are a creative writing assistant.",
            temperature=0.9,
            max_tokens=2000
        )

        assert config.temperature == 0.9
        assert config.max_tokens == 2000

    def test_config_for_deterministic_tasks(self):
        """Test config optimized for deterministic tasks."""
        config = AgentConfig(
            system_prompt="You are a precise technical analyst.",
            temperature=0.0,
            max_tokens=1000
        )

        assert config.temperature == 0.0
        assert config.max_tokens == 1000
