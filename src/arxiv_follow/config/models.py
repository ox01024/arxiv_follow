"""
模型配置常量 - 统一管理所有LLM模型配置
"""

import os
from typing import Dict, Any

# 默认模型配置
DEFAULT_LLM_MODEL = "google/gemini-2.0-flash-001"

# 支持的模型列表
SUPPORTED_MODELS = {
    "gemini-flash": "google/gemini-2.0-flash-001",
    "gemini-flash-lite": "google/gemini-2.0-flash-lite-001",
    "gemini-flash-exp": "google/gemini-2.0-flash-exp",
    "claude-haiku": "anthropic/claude-3-haiku",
    "gpt-4o-mini": "openai/gpt-4o-mini",
    "llama-3.1": "meta-llama/llama-3.1-8b-instruct",
}

# 模型参数配置
MODEL_CONFIG = {
    "temperature": 0.3,
    "max_tokens": 2000,
    "timeout": 60.0,
    "top_p": 0.9,
}


def get_default_model() -> str:
    """
    获取默认模型名称

    支持通过环境变量 ARXIV_FOLLOW_DEFAULT_MODEL 覆盖
    """
    env_model = os.getenv("ARXIV_FOLLOW_DEFAULT_MODEL")
    if env_model:
        # 如果是简短名称，转换为完整名称
        if env_model in SUPPORTED_MODELS:
            return SUPPORTED_MODELS[env_model]
        # 如果是完整名称，直接返回
        return env_model

    return DEFAULT_LLM_MODEL


def get_model_config(model_name: str = None) -> Dict[str, Any]:
    """
    获取模型配置

    Args:
        model_name: 模型名称，如果不提供则使用默认模型

    Returns:
        包含模型名称和参数的配置字典
    """
    if model_name is None:
        model_name = get_default_model()

    config = MODEL_CONFIG.copy()
    config["model"] = model_name

    return config


def get_translation_config() -> Dict[str, Any]:
    """获取翻译服务配置"""
    return {
        "enabled": True,
        "openrouter": {
            "base_url": "https://openrouter.ai/api/v1",
            **get_model_config(),
        },
        "default_settings": {
            "source_lang": "zh",
            "target_lang": "en",
            "bilingual_format": True,
            "preserve_emojis": True,
            "preserve_format": True,
        },
        "fallback": {
            "on_error": "original",
            "retry_attempts": 2,
            "timeout_handling": "skip",
        },
    }


def get_analysis_config() -> Dict[str, Any]:
    """获取论文分析配置"""
    return {
        "enable_analysis": False,
        "enable_content_collection": False,
        "analysis_mode": "comprehensive",
        "max_papers_per_batch": 5,
        "collection_delay": 1.0,
        "llm_config": get_model_config(),
        "collection_config": {
            "try_html_version": True,
            "include_sections": True,
            "user_agent": "ArXiv-Follow-Collector/1.0",
        },
        "report_config": {
            "include_technical_analysis": True,
            "include_significance_analysis": True,
            "generate_daily_summary": True,
            "max_summary_papers": 10,
        },
    }
