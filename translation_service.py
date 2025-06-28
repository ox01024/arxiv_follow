"""
LLM翻译服务模块 - 使用OpenRouter API进行中英双语翻译
支持Gemini 2.0 Flash Lite模型，对Task信息进行智能翻译
"""

import httpx
import os
import json
from typing import Dict, Any, Optional
import logging

# 配置日志
logger = logging.getLogger(__name__)

class TranslationService:
    """LLM翻译服务类"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化翻译服务客户端
        
        Args:
            api_key: OpenRouter API密钥，如果不提供会从环境变量读取
        """
        self.api_key = api_key or os.getenv('OPEN_ROUTE_API_KEY')
        self.base_url = "https://openrouter.ai/api/v1"
        self.model = "google/gemini-2.0-flash-lite-001"
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/arxiv-follow",  # 可选：用于OpenRouter统计
            "X-Title": "ArXiv Follow Translation Service"  # 可选：用于OpenRouter统计
        }
        
        if not self.api_key:
            logger.warning("未找到OpenRouter API密钥，翻译功能将被禁用")
            logger.info("请设置环境变量: OPEN_ROUTE_API_KEY")
    
    def is_enabled(self) -> bool:
        """检查翻译服务是否可用"""
        return bool(self.api_key)
    
    def translate_task_content(self, 
                             title: str, 
                             content: str, 
                             source_lang: str = "zh",
                             target_lang: str = "en") -> Dict[str, Any]:
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
                "translated_content": content
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

请按以下JSON格式返回翻译结果：
{{
    "translated_title": "翻译后的标题",
    "translated_content": "翻译后的内容"
}}

注意事项：
1. 保持emoji表情符号不变
2. 保持时间格式不变  
3. 保持技术术语（如ArXiv、paper、citation等）的准确性
4. 保持列表和段落格式
5. 论文标题可以保持英文原文或提供中文翻译，以可读性为准"""

            # 构建API请求
            request_data = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 2000,
                "temperature": 0.3,  # 较低的温度以确保翻译一致性
                "top_p": 0.9
            }
            
            # 发送请求
            with httpx.Client(timeout=60.0) as client:
                response = client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=request_data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    translated_text = result["choices"][0]["message"]["content"].strip()
                    
                    # 尝试解析JSON结果
                    try:
                        # 提取JSON部分（可能包含在代码块中）
                        if "```json" in translated_text:
                            json_start = translated_text.find("```json") + 7
                            json_end = translated_text.find("```", json_start)
                            json_text = translated_text[json_start:json_end].strip()
                        elif "{" in translated_text and "}" in translated_text:
                            json_start = translated_text.find("{")
                            json_end = translated_text.rfind("}") + 1
                            json_text = translated_text[json_start:json_end]
                        else:
                            json_text = translated_text
                        
                        translation_result = json.loads(json_text)
                        
                        # 验证结果格式
                        if not isinstance(translation_result, dict):
                            raise ValueError("翻译结果不是有效的JSON对象")
                        
                        # 确保有必要的字段
                        translated_title = translation_result.get("translated_title", title)
                        translated_content = translation_result.get("translated_content", content)
                        
                        logger.info(f"成功翻译任务内容: {title[:30]}...")
                        
                        return {
                            "success": True,
                            "translated_title": translated_title,
                            "translated_content": translated_content,
                            "model_used": self.model,
                            "source_lang": source_lang,
                            "target_lang": target_lang
                        }
                        
                    except (json.JSONDecodeError, ValueError) as e:
                        logger.warning(f"翻译结果JSON解析失败: {e}")
                        # 降级处理：直接使用翻译文本
                        lines = translated_text.split('\n')
                        translated_title = lines[0] if lines else title
                        translated_content = '\n'.join(lines[1:]) if len(lines) > 1 else translated_text
                        
                        return {
                            "success": True,
                            "translated_title": translated_title,
                            "translated_content": translated_content,
                            "model_used": self.model,
                            "source_lang": source_lang,
                            "target_lang": target_lang,
                            "note": "使用降级解析"
                        }
                
                else:
                    error_msg = f"API调用失败: {response.status_code}"
                    try:
                        error_detail = response.json()
                        error_msg += f" - {error_detail.get('error', {}).get('message', response.text)}"
                    except:
                        error_msg += f" - {response.text}"
                    
                    logger.error(error_msg)
                    return {
                        "success": False,
                        "error": error_msg,
                        "translated_title": title,
                        "translated_content": content
                    }
                    
        except httpx.RequestError as e:
            logger.error(f"网络请求错误: {e}")
            return {
                "success": False, 
                "error": f"网络错误: {e}",
                "translated_title": title,
                "translated_content": content
            }
        except Exception as e:
            logger.error(f"翻译时发生未知错误: {e}")
            return {
                "success": False, 
                "error": f"未知错误: {e}",
                "translated_title": title,
                "translated_content": content
            }
    
    def translate_to_bilingual(self, 
                               title: str, 
                               content: str) -> Dict[str, Any]:
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
                "bilingual": {"title": title, "content": content}
            }
        
        # 翻译为英文
        translation_result = self.translate_task_content(
            title=title,
            content=content,
            source_lang="zh",
            target_lang="en"
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
                "chinese": {
                    "title": title,
                    "content": content
                },
                "english": {
                    "title": english_title,
                    "content": english_content
                },
                "bilingual": {
                    "title": bilingual_title,
                    "content": bilingual_content
                },
                "model_used": translation_result.get("model_used")
            }
        else:
            logger.warning(f"翻译失败，返回原始内容: {translation_result.get('error')}")
            return {
                "success": False,
                "error": translation_result.get("error"),
                "chinese": {"title": title, "content": content},
                "english": {"title": title, "content": content},
                "bilingual": {"title": title, "content": content}
            }
    
    def test_connection(self) -> Dict[str, Any]:
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
                target_lang="en"
            )
            
            if test_result.get("success"):
                logger.info("OpenRouter API连接测试成功")
                return {
                    "success": True,
                    "message": "API连接正常",
                    "model": self.model,
                    "test_translation": test_result.get("translated_title")
                }
            else:
                return {
                    "success": False,
                    "error": f"连接测试失败: {test_result.get('error')}"
                }
                
        except Exception as e:
            logger.error(f"连接测试时发生错误: {e}")
            return {"success": False, "error": f"连接测试错误: {e}"}


# 创建全局实例
translation_service = TranslationService()


def translate_arxiv_task(title: str, content: str, bilingual: bool = True) -> Dict[str, Any]:
    """
    便捷函数：翻译ArXiv论文监控任务内容
    
    Args:
        title: 任务标题
        content: 任务内容
        bilingual: 是否生成双语版本
        
    Returns:
        翻译结果
    """
    if bilingual:
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