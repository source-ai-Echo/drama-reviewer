from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Literal

from agents import OpenAIChatCompletionsModel, OpenAIResponsesModel, RunConfig
from openai import AsyncOpenAI

from config import load_local_env


load_local_env()


ProviderName = Literal["openai", "compatible", "local"]
ApiMode = Literal["responses", "chat_completions"]


@dataclass(frozen=True)
class ProviderConfig:
    provider: ProviderName = "openai"
    model: str = "gpt-5-mini"
    base_url: str | None = None
    api_key_env: str = "OPENAI_API_KEY"
    api_mode: ApiMode = "responses"
    tools_enabled: bool = True
    api_key: str | None = field(default=None, repr=False, compare=False)

    @classmethod
    def from_environment(
        cls,
        *,
        provider: str | None = None,
        model: str | None = None,
        base_url: str | None = None,
        api_key_env: str | None = None,
        api_mode: str | None = None,
    ) -> "ProviderConfig":
        selected = (provider or os.getenv("DRAMA_PROVIDER") or "openai").strip().lower()
        if selected not in {"openai", "compatible", "local"}:
            raise ValueError("模型厂商类型只支持 openai、compatible 或 local。")

        defaults = {
            "openai": {
                "model": "gpt-5-mini",
                "base_url": None,
                "api_key_env": "OPENAI_API_KEY",
                "api_mode": "responses",
                "tools_enabled": True,
            },
            "compatible": {
                "model": "",
                "base_url": None,
                "api_key_env": "DRAMA_API_KEY",
                "api_mode": "chat_completions",
                "tools_enabled": False,
            },
            "local": {
                "model": "",
                "base_url": "http://127.0.0.1:11434/v1",
                "api_key_env": "",
                "api_mode": "chat_completions",
                "tools_enabled": False,
            },
        }[selected]

        chosen_model = (model or os.getenv("DRAMA_MODEL") or defaults["model"]).strip()
        chosen_base_url = (base_url or os.getenv("DRAMA_API_BASE") or defaults["base_url"] or "").strip() or None
        chosen_key_env = (api_key_env or os.getenv("DRAMA_API_KEY_ENV") or defaults["api_key_env"]).strip()
        chosen_mode = (api_mode or os.getenv("DRAMA_API_MODE") or defaults["api_mode"]).strip().lower()
        if chosen_mode not in {"responses", "chat_completions"}:
            raise ValueError("接口模式只支持 responses 或 chat_completions。")

        tools_setting = os.getenv("DRAMA_MODEL_TOOLS")
        tools_enabled = defaults["tools_enabled"] if tools_setting is None else tools_setting.strip().lower() in {"1", "true", "yes", "on"}
        config = cls(
            provider=selected,  # type: ignore[arg-type]
            model=chosen_model,
            base_url=chosen_base_url,
            api_key_env=chosen_key_env,
            api_mode=chosen_mode,  # type: ignore[arg-type]
            tools_enabled=tools_enabled,
        )
        config.validate_shape()
        return config

    def validate_shape(self) -> None:
        if not self.model:
            raise ValueError("请指定模型名称（DRAMA_MODEL 或 --model）。")
        if self.provider == "compatible" and not self.base_url:
            raise ValueError("兼容接口需要填写服务地址（DRAMA_API_BASE 或 --base-url）。")
        if self.provider != "openai" and self.api_mode == "responses":
            raise ValueError("兼容接口和本地模型默认应使用 chat_completions 模式。")

    def resolve_api_key(self) -> str:
        if self.provider == "local":
            return "local-model-no-secret"
        if self.api_key and self.api_key.strip():
            return self.api_key.strip()
        if not self.api_key_env:
            raise ValueError("未配置 API Key 环境变量名称。")
        value = os.getenv(self.api_key_env, "").strip()
        if not value:
            raise ValueError(f"没有找到 {self.api_key_env}，请由使用者配置自己的 API Key。")
        return value

    def safe_summary(self) -> dict[str, object]:
        key_ready = self.provider == "local" or bool(self.api_key and self.api_key.strip()) or bool(
            self.api_key_env and os.getenv(self.api_key_env, "").strip()
        )
        return {
            "provider": self.provider,
            "model": self.model,
            "api_mode": self.api_mode,
            "base_url": self.base_url,
            "api_key_env": self.api_key_env or None,
            "api_key_ready": key_ready,
            "tools_enabled": self.tools_enabled,
            "tracing": False,
        }


@dataclass
class ModelRuntime:
    model: OpenAIResponsesModel | OpenAIChatCompletionsModel
    run_config: RunConfig
    client: AsyncOpenAI
    tools_enabled: bool

    async def close(self) -> None:
        await self.client.close()


def build_model_runtime(config: ProviderConfig) -> ModelRuntime:
    api_key = config.resolve_api_key()
    client_options: dict[str, object] = {"api_key": api_key}
    if config.base_url:
        client_options["base_url"] = config.base_url
    client = AsyncOpenAI(**client_options)

    if config.api_mode == "responses":
        model = OpenAIResponsesModel(model=config.model, openai_client=client)
    else:
        model = OpenAIChatCompletionsModel(
            model=config.model,
            openai_client=client,
            buffer_streamed_tool_calls=True,
        )
    return ModelRuntime(
        model=model,
        run_config=RunConfig(
            tracing_disabled=True,
            trace_include_sensitive_data=False,
            workflow_name="Drama Reviewer",
        ),
        client=client,
        tools_enabled=config.tools_enabled,
    )


def provider_catalog() -> list[dict[str, str]]:
    return [
        {
            "id": "openai",
            "label": "OpenAI",
            "protocol": "Responses API",
            "credential": "OPENAI_API_KEY",
            "notes": "支持结构化输出与工具调用；模型名称可替换。",
        },
        {
            "id": "compatible",
            "label": "OpenAI兼容接口",
            "protocol": "Chat Completions",
            "credential": "DRAMA_API_KEY（可改名）",
            "notes": "适合提供 /v1/chat/completions 的第三方服务；需逐个验证结构化输出。",
        },
        {
            "id": "local",
            "label": "本地模型",
            "protocol": "Chat Completions",
            "credential": "不需要",
            "notes": "默认连接本机兼容地址；模型必须支持足够长上下文和 JSON 输出。",
        },
    ]
