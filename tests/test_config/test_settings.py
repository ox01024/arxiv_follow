#!/usr/bin/env python3
"""
配置模块测试
"""

import os
import sys
import pytest

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

try:
    from src.arxiv_follow.config.settings import (
        RESEARCHERS_TSV_URL,
        DEFAULT_TOPICS,
        REQUEST_TIMEOUT,
        DISPLAY_LIMIT,
        DEFAULT_DAYS_BACK,
        REPORTS_DIR,
        DIDA_API_CONFIG,
        TRANSLATION_CONFIG,
        PAPER_ANALYSIS_CONFIG,
    )
except ImportError as e:
    pytest.skip(f"配置模块导入失败: {e}", allow_module_level=True)


class TestSettings:
    """配置设置测试类"""
    
    def test_basic_settings_exist(self):
        """测试基本设置是否存在"""
        assert RESEARCHERS_TSV_URL is not None
        assert DEFAULT_TOPICS is not None
        assert REQUEST_TIMEOUT is not None
        assert DISPLAY_LIMIT is not None
        assert DEFAULT_DAYS_BACK is not None
        assert REPORTS_DIR is not None
    
    def test_researchers_tsv_url_format(self):
        """测试研究者TSV URL格式"""
        assert isinstance(RESEARCHERS_TSV_URL, str)
        assert RESEARCHERS_TSV_URL.startswith('https://')
        assert 'docs.google.com' in RESEARCHERS_TSV_URL
        assert 'export?format=tsv' in RESEARCHERS_TSV_URL
    
    def test_default_topics_format(self):
        """测试默认主题格式"""
        assert isinstance(DEFAULT_TOPICS, list)
        assert len(DEFAULT_TOPICS) > 0
        assert all(isinstance(topic, str) for topic in DEFAULT_TOPICS)
        # 检查是否包含预期的主题
        assert "cs.AI" in DEFAULT_TOPICS or "cs.CR" in DEFAULT_TOPICS
    
    def test_numeric_settings_types(self):
        """测试数值设置的类型"""
        assert isinstance(REQUEST_TIMEOUT, (int, float))
        assert isinstance(DISPLAY_LIMIT, int)
        assert isinstance(DEFAULT_DAYS_BACK, int)
        
        # 检查合理的数值范围
        assert REQUEST_TIMEOUT > 0
        assert DISPLAY_LIMIT > 0
        assert DEFAULT_DAYS_BACK > 0
    
    def test_reports_dir_setting(self):
        """测试报告目录设置"""
        assert isinstance(REPORTS_DIR, str)
        assert len(REPORTS_DIR) > 0
        assert REPORTS_DIR == "reports"
    
    def test_dida_api_config_structure(self):
        """测试滴答清单API配置结构"""
        assert isinstance(DIDA_API_CONFIG, dict)
        
        # 检查必需的配置项
        required_keys = [
            "enabled",
            "base_url", 
            "default_project_id",
            "tag_prefix",
            "priority_mapping",
            "many_papers_threshold",
            "enable_bilingual"
        ]
        
        for key in required_keys:
            assert key in DIDA_API_CONFIG, f"Missing required key: {key}"
        
        # 检查配置值类型
        assert isinstance(DIDA_API_CONFIG["enabled"], bool)
        assert isinstance(DIDA_API_CONFIG["base_url"], str)
        assert isinstance(DIDA_API_CONFIG["default_project_id"], str)
        assert isinstance(DIDA_API_CONFIG["tag_prefix"], str)
        assert isinstance(DIDA_API_CONFIG["priority_mapping"], dict)
        assert isinstance(DIDA_API_CONFIG["many_papers_threshold"], int)
        assert isinstance(DIDA_API_CONFIG["enable_bilingual"], bool)
    
    def test_translation_config_structure(self):
        """测试翻译配置结构"""
        assert isinstance(TRANSLATION_CONFIG, dict)
        
        # 检查必需的配置项
        required_keys = [
            "enabled",
            "openrouter",
            "default_settings",
            "fallback"
        ]
        
        for key in required_keys:
            assert key in TRANSLATION_CONFIG, f"Missing required key: {key}"
        
        # 检查OpenRouter配置
        openrouter_config = TRANSLATION_CONFIG["openrouter"]
        assert isinstance(openrouter_config, dict)
        assert "base_url" in openrouter_config
        assert "model" in openrouter_config
        assert "max_tokens" in openrouter_config
        assert "temperature" in openrouter_config
        assert "timeout" in openrouter_config
        
        # 检查默认设置
        default_settings = TRANSLATION_CONFIG["default_settings"]
        assert isinstance(default_settings, dict)
        assert "source_lang" in default_settings
        assert "target_lang" in default_settings
        assert "bilingual_format" in default_settings
        
        # 检查降级策略
        fallback = TRANSLATION_CONFIG["fallback"]
        assert isinstance(fallback, dict)
        assert "on_error" in fallback
        assert "retry_attempts" in fallback
    
    def test_paper_analysis_config_structure(self):
        """测试论文分析配置结构"""
        assert isinstance(PAPER_ANALYSIS_CONFIG, dict)
        
        # 检查必需的配置项
        required_keys = [
            "enable_analysis",
            "enable_content_collection",
            "analysis_mode",
            "max_papers_per_batch",
            "collection_delay",
            "llm_config",
            "collection_config",
            "report_config"
        ]
        
        for key in required_keys:
            assert key in PAPER_ANALYSIS_CONFIG, f"Missing required key: {key}"
        
        # 检查配置值类型
        assert isinstance(PAPER_ANALYSIS_CONFIG["enable_analysis"], bool)
        assert isinstance(PAPER_ANALYSIS_CONFIG["enable_content_collection"], bool)
        assert isinstance(PAPER_ANALYSIS_CONFIG["analysis_mode"], str)
        assert isinstance(PAPER_ANALYSIS_CONFIG["max_papers_per_batch"], int)
        assert isinstance(PAPER_ANALYSIS_CONFIG["collection_delay"], (int, float))
        
        # 检查LLM配置
        llm_config = PAPER_ANALYSIS_CONFIG["llm_config"]
        assert isinstance(llm_config, dict)
        assert "model" in llm_config
        assert "temperature" in llm_config
        assert "max_tokens" in llm_config
        assert "timeout" in llm_config
        
        # 检查收集配置
        collection_config = PAPER_ANALYSIS_CONFIG["collection_config"]
        assert isinstance(collection_config, dict)
        assert "try_html_version" in collection_config
        assert "include_sections" in collection_config
        
        # 检查报告配置
        report_config = PAPER_ANALYSIS_CONFIG["report_config"]
        assert isinstance(report_config, dict)
        assert "include_technical_analysis" in report_config
        assert "include_significance_analysis" in report_config
        assert "generate_daily_summary" in report_config
    
    def test_priority_mapping_values(self):
        """测试优先级映射值"""
        priority_mapping = DIDA_API_CONFIG["priority_mapping"]
        
        # 检查必需的优先级类型
        required_priorities = ["no_papers", "has_papers", "many_papers"]
        for priority_type in required_priorities:
            assert priority_type in priority_mapping
            assert isinstance(priority_mapping[priority_type], int)
            assert priority_mapping[priority_type] >= 0
    
    def test_analysis_mode_validity(self):
        """测试分析模式的有效性"""
        analysis_mode = PAPER_ANALYSIS_CONFIG["analysis_mode"]
        valid_modes = ["significance", "technical", "comprehensive"]
        assert analysis_mode in valid_modes
    
    def test_language_codes_validity(self):
        """测试语言代码的有效性"""
        default_settings = TRANSLATION_CONFIG["default_settings"]
        source_lang = default_settings["source_lang"]
        target_lang = default_settings["target_lang"]
        
        valid_langs = ["zh", "en", "zh-cn", "en-us"]
        assert source_lang in valid_langs
        assert target_lang in valid_langs
    
    def test_url_configurations(self):
        """测试URL配置的有效性"""
        # 检查滴答清单API URL
        base_url = DIDA_API_CONFIG["base_url"]
        assert base_url.startswith("https://")
        assert "dida365.com" in base_url
        
        # 检查OpenRouter URL
        openrouter_url = TRANSLATION_CONFIG["openrouter"]["base_url"]
        assert openrouter_url.startswith("https://")
        assert "openrouter.ai" in openrouter_url
    
    def test_boolean_settings_consistency(self):
        """测试布尔设置的一致性"""
        # 检查各种布尔配置
        assert isinstance(DIDA_API_CONFIG["enabled"], bool)
        assert isinstance(DIDA_API_CONFIG["enable_bilingual"], bool)
        assert isinstance(TRANSLATION_CONFIG["enabled"], bool)
        assert isinstance(TRANSLATION_CONFIG["default_settings"]["bilingual_format"], bool)
        assert isinstance(TRANSLATION_CONFIG["default_settings"]["preserve_emojis"], bool)
        assert isinstance(PAPER_ANALYSIS_CONFIG["enable_analysis"], bool)
        assert isinstance(PAPER_ANALYSIS_CONFIG["enable_content_collection"], bool) 