"""
LLM翻译服务模块 - 使用OpenRouter API进行中英双语翻译
支持Gemini 2.0模型，对Task信息进行智能翻译
"""

import json
import logging
import os
from typing import Any

from openai import OpenAI

from ..config.models import get_default_model

# 配置日志
logger = logging.getLogger(__name__)


class TranslationService:
    """LLM翻译服务类"""

    def __init__(self, api_key: str | None = None, model: str | None = None):
        """
        初始化翻译服务客户端

        Args:
            api_key: OpenRouter API密钥，如果不提供会从环境变量读取
            model: 使用的模型名称，如果不提供会使用默认模型
        """
        from ..config.models import SUPPORTED_MODELS

        self.api_key = api_key or os.getenv("OPEN_ROUTE_API_KEY")
        self.base_url = "https://openrouter.ai/api/v1"

        # 处理模型名称，支持别名转换
        if model:
            if model in SUPPORTED_MODELS:
                self.model = SUPPORTED_MODELS[model]
            else:
                self.model = model
        else:
            self.model = get_default_model()

        # 初始化OpenAI客户端，配置为使用OpenRouter
        if self.api_key:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                default_headers={
                    "HTTP-Referer": "https://github.com/arxiv-follow",  # 可选：用于OpenRouter统计
                    "X-Title": "ArXiv Follow Translation Service",  # 可选：用于OpenRouter统计
                },
            )
        else:
            self.client = None
            logger.warning("未找到OpenRouter API密钥，翻译功能将被禁用")
            logger.info("请设置环境变量: OPEN_ROUTE_API_KEY")

    def is_enabled(self) -> bool:
        """检查翻译服务是否可用"""
        return bool(self.api_key and self.client)

    def translate_task_content(
        self, title: str, content: str, source_lang: str = "zh", target_lang: str = "en"
    ) -> dict[str, Any]:
        """
        翻译任务内容（标题和内容）

        Args:
            title: 任务标题
            content: 任务内容
            source_lang: 源语言 (zh/en)
            target_lang: 目标语言 (en/zh)

        Returns:
            翻译结果包含 translated_title 和 translated_content
        """
        if not self.is_enabled():
            logger.warning("翻译服务未启用，跳过翻译")
            return {
                "success": False,
                "error": "翻译服务未启用",
                "translated_title": title,
                "translated_content": content,
            }

        try:
            # 构建翻译提示
            lang_names = {"zh": "中文", "en": "English"}
            source_name = lang_names.get(source_lang, source_lang)
            target_name = lang_names.get(target_lang, target_lang)

            prompt = f"""请将以下{source_name}内容翻译为{target_name}。这是一个ArXiv论文监控系统的任务信息，请保持技术术语的准确性和格式的完整性。

任务标题：
{title}

任务内容：
{content}

请直接返回纯JSON格式的翻译结果，不要包含代码块标记或任何其他文本：
{{
    "translated_title": "翻译后的标题",
    "translated_content": "翻译后的内容"
}}

注意事项：
1. 保持emoji表情符号不变
2. 保持时间格式不变
3. 保持技术术语（如ArXiv、paper、citation等）的准确性
4. 保持列表和段落格式
5. 论文标题可以保持英文原文或提供中文翻译，以可读性为准
6. 输出必须是有效的JSON格式，不要使用```json代码块包围
7. JSON字符串中的换行符请用\\n表示
8. 保持原始内容的完整性，不要省略任何信息"""

            # 使用OpenAI SDK发送请求
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=2000,
                    temperature=0.3,  # 较低的温度以确保翻译一致性
                    top_p=0.9,
                    timeout=60.0,
                )

                translated_text = response.choices[0].message.content.strip()

                # 尝试解析JSON结果
                try:
                    # 清理和提取JSON部分
                    cleaned_text = translated_text.strip()

                    # 移除可能的代码块标记
                    if "```json" in cleaned_text:
                        json_start = cleaned_text.find("```json") + 7
                        json_end = cleaned_text.find("```", json_start)
                        if json_end == -1:
                            json_end = len(cleaned_text)
                        json_text = cleaned_text[json_start:json_end].strip()
                    elif cleaned_text.startswith("```") and cleaned_text.endswith(
                        "```"
                    ):
                        # 处理只有```包围的情况
                        json_text = cleaned_text[3:-3].strip()
                    elif "{" in cleaned_text and "}" in cleaned_text:
                        # 提取JSON对象
                        json_start = cleaned_text.find("{")
                        json_end = cleaned_text.rfind("}") + 1
                        json_text = cleaned_text[json_start:json_end]
                    else:
                        json_text = cleaned_text

                    # 再次清理可能的前后缀
                    json_text = json_text.strip()
                    if json_text.startswith("json"):
                        json_text = json_text[4:].strip()

                    logger.debug(f"准备解析的JSON文本: {json_text[:200]}...")
                    translation_result = json.loads(json_text)

                    # 验证结果格式
                    if not isinstance(translation_result, dict):
                        raise ValueError("翻译结果不是有效的JSON对象")

                    # 确保有必要的字段
                    translated_title = translation_result.get("translated_title", title)
                    translated_content = translation_result.get(
                        "translated_content", content
                    )

                    logger.info(f"成功翻译任务内容: {title[:30]}...")

                    return {
                        "success": True,
                        "translated_title": translated_title,
                        "translated_content": translated_content,
                        "model_used": self.model,
                        "source_lang": source_lang,
                        "target_lang": target_lang,
                    }

                except (json.JSONDecodeError, ValueError) as e:
                    logger.warning(f"翻译结果JSON解析失败: {e}")
                    logger.warning(f"原始响应内容: {translated_text[:500]}...")

                    # 降级处理：清理可能存在的JSON格式标记
                    cleaned_text = translated_text

                    # 移除JSON代码块标记
                    if "```json" in cleaned_text:
                        cleaned_text = cleaned_text.replace("```json", "").replace(
                            "```", ""
                        )

                    # 移除JSON格式字符串
                    if (
                        '"translated_title":' in cleaned_text
                        or '"translated_content":' in cleaned_text
                    ):
                        # 尝试提取可能的标题和内容
                        lines = [
                            line.strip()
                            for line in cleaned_text.split("\n")
                            if line.strip()
                        ]

                        # 过滤掉JSON格式行
                        content_lines = []
                        for line in lines:
                            if not (
                                line.startswith("{")
                                or line.startswith('"')
                                or line.startswith("}")
                                or line.endswith(",")
                                or '"translated_' in line
                            ):
                                content_lines.append(line)

                        if content_lines:
                            translated_title = (
                                content_lines[0] if content_lines else title
                            )
                            translated_content = (
                                "\n".join(content_lines[1:])
                                if len(content_lines) > 1
                                else content_lines[0] if content_lines else content
                            )
                        else:
                            # 如果无法提取，则返回失败
                            logger.error("无法从JSON解析失败的响应中提取有效内容")
                            return {
                                "success": False,
                                "error": f"JSON解析失败且无法提取有效内容: {e}",
                                "translated_title": title,
                                "translated_content": content,
                            }
                    else:
                        # 普通文本处理
                        lines = cleaned_text.split("\n")
                        translated_title = lines[0] if lines else title
                        translated_content = (
                            "\n".join(lines[1:]) if len(lines) > 1 else cleaned_text
                        )

                    # 最后验证结果不包含JSON格式
                    if (
                        '"translated_title":' in translated_title
                        or '"translated_content":' in translated_title
                    ):
                        logger.error("降级处理后标题仍包含JSON格式，翻译失败")
                        return {
                            "success": False,
                            "error": f"JSON解析失败且降级处理无效: {e}",
                            "translated_title": title,
                            "translated_content": content,
                        }

                    return {
                        "success": True,
                        "translated_title": translated_title,
                        "translated_content": translated_content,
                        "model_used": self.model,
                        "source_lang": source_lang,
                        "target_lang": target_lang,
                        "note": "使用降级解析",
                    }

            except Exception as e:
                logger.error(f"API调用失败: {e}")
                return {
                    "success": False,
                    "error": f"API调用失败: {e}",
                    "translated_title": title,
                    "translated_content": content,
                }

        except Exception as e:
            logger.error(f"翻译时发生未知错误: {e}")
            return {
                "success": False,
                "error": f"未知错误: {e}",
                "translated_title": title,
                "translated_content": content,
            }

    def translate_to_bilingual(self, title: str, content: str) -> dict[str, Any]:
        """
        生成中英双语版本的任务内容

        Args:
            title: 原始任务标题（假设为中文）
            content: 原始任务内容（假设为中文）

        Returns:
            包含中英双语版本的结果
        """
        if not self.is_enabled():
            return {
                "success": False,
                "error": "翻译服务未启用",
                "chinese": {"title": title, "content": content},
                "english": {"title": title, "content": content},
                "bilingual": {"title": title, "content": content},
            }

        # 翻译为英文
        translation_result = self.translate_task_content(
            title=title, content=content, source_lang="zh", target_lang="en"
        )

        if translation_result.get("success"):
            english_title = translation_result["translated_title"]
            english_content = translation_result["translated_content"]

            # 生成双语版本
            bilingual_title = f"{title} / {english_title}"
            bilingual_content = f"""中文版本 / Chinese Version:
{content}

---

English Version:
{english_content}"""

            return {
                "success": True,
                "chinese": {"title": title, "content": content},
                "english": {"title": english_title, "content": english_content},
                "bilingual": {"title": bilingual_title, "content": bilingual_content},
                "model_used": translation_result.get("model_used"),
            }
        else:
            logger.warning(f"翻译失败，返回原始内容: {translation_result.get('error')}")
            return {
                "success": False,
                "error": translation_result.get("error"),
                "chinese": {"title": title, "content": content},
                "english": {"title": title, "content": content},
                "bilingual": {"title": title, "content": content},
            }

    def translate_mixed_content_to_bilingual(
        self, title: str, content: str
    ) -> dict[str, Any]:
        """
        生成中英双语版本的任务内容，智能处理包含英文论文信息的中文报告

        Args:
            title: 原始任务标题（中文）
            content: 原始任务内容（包含英文论文信息的中文报告）

        Returns:
            包含中英双语版本的结果
        """
        if not self.is_enabled():
            return {
                "success": False,
                "error": "翻译服务未启用",
                "chinese": {"title": title, "content": content},
                "english": {"title": title, "content": content},
                "bilingual": {"title": title, "content": content},
            }

        # 首先创建中文版本 - 将论文信息翻译为中文，但保持研究者名字不变
        chinese_result = self._translate_to_chinese_with_preserved_names(title, content)

        if not chinese_result.get("success"):
            logger.warning(f"中文版本生成失败: {chinese_result.get('error')}")
            chinese_title = title
            chinese_content = content
        else:
            chinese_title = chinese_result["translated_title"]
            chinese_content = chinese_result["translated_content"]

        # 然后创建英文版本
        english_result = self.translate_task_content(
            title=chinese_title,
            content=chinese_content,
            source_lang="zh",
            target_lang="en",
        )

        if english_result.get("success"):
            english_title = english_result["translated_title"]
            english_content = english_result["translated_content"]

            # 生成双语版本
            bilingual_title = f"{chinese_title} / {english_title}"
            bilingual_content = f"""中文版本 / Chinese Version:
{chinese_content}

---

English Version:
{english_content}"""

            return {
                "success": True,
                "chinese": {"title": chinese_title, "content": chinese_content},
                "english": {"title": english_title, "content": english_content},
                "bilingual": {"title": bilingual_title, "content": bilingual_content},
                "model_used": english_result.get("model_used"),
                "translation_mode": "mixed_content",
            }
        else:
            logger.warning(f"英文翻译失败，返回中文版本: {english_result.get('error')}")
            return {
                "success": True,
                "chinese": {"title": chinese_title, "content": chinese_content},
                "english": {"title": chinese_title, "content": chinese_content},
                "bilingual": {"title": chinese_title, "content": chinese_content},
                "translation_mode": "chinese_only",
                "english_translation_error": english_result.get("error"),
            }

    def _translate_to_chinese_with_preserved_names(
        self, title: str, content: str
    ) -> dict[str, Any]:
        """
        将包含英文论文信息的中文报告翻译为完全中文版本，但保持研究者名字不变

        Args:
            title: 原始标题
            content: 原始内容（包含英文论文信息）

        Returns:
            翻译结果
        """
        prompt = f"""请将以下论文监控报告中的英文论文信息翻译为中文，但保持以下要求：

1. 保持研究者的姓名不变（如 Zhang Wei, Li Ming 等人名保持英文）
2. 将论文标题翻译为中文
3. 将论文摘要翻译为中文
4. 将其他英文内容翻译为中文
5. 保持原有的格式和结构
6. 保持 emoji 表情符号不变
7. 保持 arXiv ID、链接等技术信息不变

请直接返回翻译后的内容，不要添加任何额外的说明。

标题: {title}

内容:
{content}

请提供翻译后的结果，格式为JSON：
{{
    "translated_title": "翻译后的标题",
    "translated_content": "翻译后的内容"
}}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=3000,
                temperature=0.3,
                timeout=60.0,
            )

            translated_text = response.choices[0].message.content.strip()

            # 尝试解析JSON结果
            try:
                # 清理和提取JSON部分
                cleaned_text = translated_text.strip()

                # 移除可能的代码块标记
                if "```json" in cleaned_text:
                    json_start = cleaned_text.find("```json") + 7
                    json_end = cleaned_text.find("```", json_start)
                    if json_end == -1:
                        json_end = len(cleaned_text)
                    json_text = cleaned_text[json_start:json_end].strip()
                elif cleaned_text.startswith("```") and cleaned_text.endswith("```"):
                    json_text = cleaned_text[3:-3].strip()
                elif "{" in cleaned_text and "}" in cleaned_text:
                    json_start = cleaned_text.find("{")
                    json_end = cleaned_text.rfind("}") + 1
                    json_text = cleaned_text[json_start:json_end]
                else:
                    json_text = cleaned_text

                # 再次清理可能的前后缀
                json_text = json_text.strip()
                if json_text.startswith("json"):
                    json_text = json_text[4:].strip()

                logger.debug(f"准备解析的JSON文本: {json_text[:200]}...")
                translation_result = json.loads(json_text)

                if isinstance(translation_result, dict):
                    return {
                        "success": True,
                        "translated_title": translation_result.get(
                            "translated_title", title
                        ),
                        "translated_content": translation_result.get(
                            "translated_content", content
                        ),
                        "model": self.model,
                    }
                else:
                    logger.error("翻译结果不是有效的字典格式")
                    return {"success": False, "error": "翻译结果格式无效"}

            except json.JSONDecodeError as e:
                logger.error(f"JSON解析失败: {e}")
                logger.error(f"响应内容: {translated_text[:500]}...")
                return {"success": False, "error": f"JSON解析失败: {e}"}

        except Exception as e:
            logger.error(f"中文翻译过程中发生错误: {e}")
            return {"success": False, "error": f"翻译过程错误: {e}"}

    def test_connection(self) -> dict[str, Any]:
        """
        测试与OpenRouter API的连接

        Returns:
            连接测试结果
        """
        if not self.is_enabled():
            return {"success": False, "error": "翻译服务未启用"}

        try:
            # 使用简单的翻译任务测试连接
            test_result = self.translate_task_content(
                title="测试标题",
                content="这是一个连接测试。",
                source_lang="zh",
                target_lang="en",
            )

            if test_result.get("success"):
                logger.info("OpenRouter API连接测试成功")
                return {
                    "success": True,
                    "message": "API连接正常",
                    "model": self.model,
                    "test_translation": test_result.get("translated_title"),
                }
            else:
                return {
                    "success": False,
                    "error": f"连接测试失败: {test_result.get('error')}",
                }

        except Exception as e:
            logger.error(f"连接测试时发生错误: {e}")
            return {"success": False, "error": f"连接测试错误: {e}"}


# 创建全局实例
translation_service = TranslationService()


def translate_arxiv_task(
    title: str, content: str, bilingual: bool = True, smart_mode: bool = True
) -> dict[str, Any]:
    """
    便捷函数：翻译ArXiv论文监控任务内容

    Args:
        title: 任务标题
        content: 任务内容
        bilingual: 是否生成双语版本
        smart_mode: 是否使用智能翻译模式（处理包含英文论文信息的中文报告）

    Returns:
        翻译结果
    """
    if bilingual:
        if smart_mode:
            return translation_service.translate_mixed_content_to_bilingual(
                title, content
            )
        else:
            return translation_service.translate_to_bilingual(title, content)
    else:
        return translation_service.translate_task_content(title, content)


def test_translation_service() -> bool:
    """
    测试翻译服务连接

    Returns:
        测试是否成功
    """
    result = translation_service.test_connection()
    if result.get("success"):
        print("✅ OpenRouter翻译服务连接成功")
        print(f"🤖 使用模型: {result.get('model')}")
        print(f"🧪 测试翻译: {result.get('test_translation')}")
        return True
    else:
        print(f"❌ OpenRouter翻译服务连接失败: {result.get('error')}")
        return False


if __name__ == "__main__":
    # 测试翻译服务
    print("🧪 测试OpenRouter翻译服务连接...")

    if test_translation_service():
        print("\n🧪 测试双语翻译功能...")

        test_title = "📄 每日论文监控 - 2025-01-15"
        test_content = """🎉 今日发现 3 篇新论文！

📊 共发现 3 篇论文

📝 详细信息:
监控了 5 位研究者

📊 论文分布:
• Zhang Wei: 2 篇
  1. Deep Learning Approaches for Cybersecurity...
  2. Federated Learning Privacy Protection...
• Li Ming: 1 篇
  1. AI-Powered Network Security Framework...

⏰ 生成时间: 2025-01-15 09:00:15
🤖 由 ArXiv Follow 系统自动生成"""

        result = translate_arxiv_task(test_title, test_content, bilingual=True)

        if result.get("success"):
            print("✅ 双语翻译测试成功!")
            print(f"\n📋 双语标题: {result['bilingual']['title']}")
            print(f"\n📝 双语内容:\n{result['bilingual']['content'][:300]}...")
        else:
            print(f"❌ 双语翻译测试失败: {result.get('error')}")
    else:
        print("❌ 翻译服务连接失败!")
        print("💡 请确保已设置 OPEN_ROUTE_API_KEY 环境变量")
