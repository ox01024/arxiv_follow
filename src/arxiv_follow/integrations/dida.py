"""
滴答清单API集成模块
支持任务创建、删除和测试连接功能
"""

import logging
import os
import time
from datetime import datetime
from typing import Any

import httpx

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 导入翻译服务
try:
    from ..services.translation import translate_arxiv_task
except ImportError:
    logger.warning("无法导入翻译服务模块，翻译功能将被禁用")

    def translate_arxiv_task(*_args, **_kwargs):
        return {"success": False, "error": "翻译模块未导入"}


class DidaIntegration:
    """滴答清单API集成类"""

    def __init__(self, access_token: str | None = None):
        """
        初始化滴答清单API客户端

        Args:
            access_token: 访问令牌，如果不提供会从环境变量读取
        """
        self.access_token = access_token or os.getenv("DIDA_ACCESS_TOKEN")
        self.base_url = "https://api.dida365.com/open/v1"
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "User-Agent": "ArXiv-Follow-Bot/1.0",
        }

        if not self.access_token:
            logger.warning("未找到滴答清单访问令牌，API功能将被禁用")

    def is_enabled(self) -> bool:
        """检查API是否可用"""
        return bool(self.access_token)

    def _make_request(self, method: str, url: str, **kwargs) -> dict[str, Any]:
        """
        统一的HTTP请求处理

        Args:
            method: HTTP方法
            url: 请求URL
            **kwargs: 其他请求参数

        Returns:
            请求结果
        """
        if not self.is_enabled():
            return {"success": False, "error": "API未启用"}

        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.request(method, url, headers=self.headers, **kwargs)

                if response.status_code in [200, 204]:
                    return {
                        "success": True,
                        "data": response.json() if response.content else {},
                        "status_code": response.status_code
                    }
                else:
                    error_msg = f"HTTP {response.status_code}: {response.text}"
                    logger.error(f"API请求失败: {error_msg}")
                    return {"success": False, "error": error_msg}

        except httpx.RequestError as e:
            error_msg = f"网络请求错误: {e}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
        except Exception as e:
            error_msg = f"未知错误: {e}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}

    def create_task(
        self,
        title: str,
        content: str = "",
        due_date: str | None = None,
        priority: int = 0,
        tags: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        创建滴答清单任务

        Args:
            title: 任务标题
            content: 任务内容描述
            due_date: 截止日期，格式：YYYY-MM-DD
            priority: 优先级 (0-3，0为无，3为高)
            tags: 标签列表

        Returns:
            API响应结果
        """
        if not self.is_enabled():
            logger.warning("滴答清单API未启用，跳过任务创建")
            return {"success": False, "error": "API未启用"}

        # 构建任务数据
        task_data = {"title": title}

        if content:
            task_data["content"] = content
        if priority > 0:
            task_data["priority"] = priority
        if due_date:
            task_data["dueDate"] = f"{due_date}T23:59:59.000+0000"
        if tags:
            task_data["tags"] = tags

        result = self._make_request("POST", f"{self.base_url}/task", json=task_data)

        if result.get("success"):
            data = result["data"]
            logger.info(f"成功创建滴答清单任务: {title}")
            return {
                "success": True,
                "task_id": data.get("id"),
                "project_id": data.get("projectId"),
                "title": title,
                "url": f"https://dida365.com/webapp/#/task/{data.get('id')}",
            }

        return result

    def delete_task(self, task_id: str, project_id: str = None) -> dict[str, Any]:
        """
        删除滴答清单任务
        
        ⚠️ 注意：滴答清单删除API存在问题，可能总是返回成功但实际未删除任务
        建议在API调用后手动检查任务是否真的被删除
        
        根据官方API文档：DELETE /open/v1/project/{projectId}/task/{taskId}
        成功响应：200 OK 或 201 Created
        失败响应：401 Unauthorized, 403 Forbidden, 404 Not Found

        Args:
            task_id: 任务ID
            project_id: 项目ID（必需）

        Returns:
            删除结果（注意：success=True不保证任务真的被删除）
        """
        if not self.is_enabled():
            return {"success": False, "error": "API未启用"}

        # 根据官方文档，必须使用项目路径
        if not project_id:
            logger.warning("删除任务时未提供project_id，删除将失败")
            return {
                "success": False,
                "error": "删除任务需要提供project_id",
                "task_id": task_id
            }

        url = f"{self.base_url}/project/{project_id}/task/{task_id}"
        logger.info(f"删除任务: {task_id} (项目: {project_id})")

        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.delete(url, headers=self.headers)
                
                # 根据官方文档，200和201都表示成功
                if response.status_code in [200, 201]:
                    logger.warning(f"删除API返回成功 (状态码: {response.status_code})，但可能需要手动确认删除")
                    logger.warning(f"请在滴答清单App中检查任务 {task_id} 是否真的被删除")
                    return {
                        "success": True, 
                        "task_id": task_id, 
                        "status_code": response.status_code,
                        "warning": "删除API可能不可靠，请手动确认删除"
                    }
                elif response.status_code == 404:
                    # 任务不存在
                    logger.info(f"任务不存在: {task_id}")
                    return {"success": True, "task_id": task_id, "status_code": 404, "note": "任务不存在"}
                elif response.status_code == 401:
                    error_msg = "访问令牌无效或已过期"
                    logger.error(f"删除任务失败: {error_msg}")
                    return {"success": False, "error": error_msg, "task_id": task_id}
                elif response.status_code == 403:
                    error_msg = "没有权限删除此任务"
                    logger.error(f"删除任务失败: {error_msg}")
                    return {"success": False, "error": error_msg, "task_id": task_id}
                else:
                    error_msg = f"HTTP {response.status_code}: {response.text}"
                    logger.error(f"删除任务失败: {error_msg}")
                    return {"success": False, "error": error_msg, "task_id": task_id}

        except httpx.RequestError as e:
            error_msg = f"网络请求错误: {e}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg, "task_id": task_id}
        except Exception as e:
            error_msg = f"未知错误: {e}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg, "task_id": task_id}

    def test_connection(self) -> dict[str, Any]:
        """
        测试API连接
        
        ⚠️ 注意：此方法会创建测试任务，但删除API不可靠，可能需要手动清理

        Returns:
            连接测试结果
        """
        # 创建测试任务
        test_title = "🧪 API连接测试（请手动删除）"
        create_result = self.create_task(title=test_title)

        if not create_result.get("success"):
            return {
                "success": False,
                "error": f"连接测试失败: {create_result.get('error')}"
            }

        task_id = create_result.get("task_id")
        project_id = create_result.get("project_id")
        logger.info("滴答清单API连接测试成功")

        # 尝试自动清理测试任务（但很可能不会真正删除）
        logger.warning("⚠️ 滴答清单删除API存在问题，可能无法自动清理测试任务")
        logger.warning(f"请在滴答清单App中手动删除测试任务，ID: {task_id}")
        logger.warning(f"任务标题: {test_title}")
        
        delete_result = self.delete_task(task_id, project_id)
        
        return {
            "success": True,
            "message": "API连接正常",
            "test_task_id": task_id,
            "warning": "测试任务需要手动删除",
            "manual_cleanup_needed": True
        }

    def create_report_task(
        self,
        report_type: str,
        summary: str,
        details: str = "",
        paper_count: int = 0,
        bilingual: bool = False,
    ) -> dict[str, Any]:
        """
        创建论文监控报告任务

        Args:
            report_type: 报告类型 (daily/weekly/topic)
            summary: 报告摘要
            details: 详细内容
            paper_count: 论文数量
            bilingual: 是否生成双语版本

        Returns:
            任务创建结果
        """
        if not self.is_enabled():
            return {"success": False, "error": "API未启用"}

        # 构建任务标题
        type_map = {
            "daily": "📄 每日研究者动态监控",
            "weekly": "📚 每周研究者动态汇总",
            "topic": "🎯 主题论文搜索",
        }
        title = f"{type_map.get(report_type, '📄 论文监控')} - {datetime.now().strftime('%Y-%m-%d')}"

        # 构建任务内容
        content_parts = [summary]
        if paper_count > 0:
            content_parts.append(f"\n📊 共发现 {paper_count} 篇论文")
        if details:
            content_parts.append(f"\n\n📝 详细信息:\n{details}")

        content_parts.extend([
            f"\n⏰ 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "\n🤖 由 ArXiv Follow 系统自动生成"
        ])
        content = "".join(content_parts)

        # 处理双语翻译（如果启用）
        final_title, final_content = title, content
        translation_info = {}

        if bilingual:
            translation_result = self._generate_bilingual_content(title, content)
            if translation_result.get("success"):
                final_title = translation_result["title"]
                final_content = translation_result["content"]
                translation_info = {
                    "translation_success": True,
                    "model_used": translation_result.get("model_used")
                }
            else:
                translation_info = {
                    "translation_success": False,
                    "translation_error": translation_result.get("error")
                }

        # 创建任务
        task_result = self.create_task(
            title=final_title,
            content=final_content,
            tags=["arxiv", "论文监控", report_type],
            priority=1 if paper_count > 0 else 0
        )

        # 添加翻译信息
        task_result.update(translation_info)
        return task_result

    def _generate_bilingual_content(self, title: str, content: str) -> dict[str, Any]:
        """
        生成双语内容

        Args:
            title: 原始标题
            content: 原始内容

        Returns:
            翻译结果
        """
        try:
            from ..services.translation import translate_arxiv_task

            logger.info("开始生成智能双语版本任务...")
            result = translate_arxiv_task(title, content, bilingual=True, smart_mode=True)

            if result.get("success") and "bilingual" in result:
                bilingual_data = result["bilingual"]

                # 检查翻译质量
                if self._is_translation_valid(bilingual_data):
                    return {
                        "success": True,
                        "title": bilingual_data["title"],
                        "content": bilingual_data["content"],
                        "model_used": result.get("model_used")
                    }
                else:
                    return {"success": False, "error": "翻译质量异常，包含格式残留"}

            return {"success": False, "error": result.get("error", "翻译失败")}

        except ImportError:
            return {"success": False, "error": "翻译模块未导入"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _is_translation_valid(self, bilingual_data: dict) -> bool:
        """检查翻译是否有效"""
        title = bilingual_data.get("title", "")
        content = bilingual_data.get("content", "")

        # 检查是否包含JSON格式残留
        invalid_patterns = ["```json", '"translated_']
        return not any(pattern in title or pattern in content for pattern in invalid_patterns)


# 全局实例
_dida_client = DidaIntegration()


# 简化的便捷函数
def create_arxiv_task(
    report_type: str,
    summary: str,
    details: str = "",
    paper_count: int = 0,
    bilingual: bool = False,
) -> dict[str, Any]:
    """创建ArXiv论文监控任务"""
    return _dida_client.create_report_task(
        report_type=report_type,
        summary=summary,
        details=details,
        paper_count=paper_count,
        bilingual=bilingual,
    )


def test_dida_connection() -> bool:
    """测试滴答清单API连接，返回简单的成功/失败状态"""
    result = _dida_client.test_connection()
    success = result.get("success", False)

    if success:
        logger.info("滴答清单API连接成功")
        if result.get("manual_cleanup_needed"):
            logger.warning(f"需要手动清理测试任务，ID: {result.get('test_task_id')}")
    else:
        logger.warning(f"滴答清单API连接失败：{result.get('error', '未知错误')}")

    return success


def test_dida_connection_detailed() -> dict[str, Any]:
    """测试滴答清单API连接，返回详细结果"""
    return _dida_client.test_connection()


def delete_dida_task(task_id: str, project_id: str = None) -> dict[str, Any]:
    """删除滴答清单任务"""
    return _dida_client.delete_task(task_id, project_id)


# 保持向后兼容的别名
dida_client = _dida_client
