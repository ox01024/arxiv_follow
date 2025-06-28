"""
滴答清单API集成模块
支持OAuth认证和任务创建功能
"""

import httpx
import os
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DidaIntegration:
    """滴答清单API集成类"""
    
    def __init__(self, access_token: Optional[str] = None):
        """
        初始化滴答清单API客户端
        
        Args:
            access_token: 访问令牌，如果不提供会从环境变量读取
        """
        self.access_token = access_token or os.getenv('DIDA_ACCESS_TOKEN')
        self.base_url = "https://api.dida365.com/open/v1"
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "User-Agent": "ArXiv-Follow-Bot/1.0"
        }
        
        if not self.access_token:
            logger.warning("未找到滴答清单访问令牌，API功能将被禁用")
    
    def is_enabled(self) -> bool:
        """检查API是否可用"""
        return bool(self.access_token)
    
    def create_task(self, 
                   title: str, 
                   content: str = "", 
                   project_id: str = "inbox", 
                   due_date: Optional[str] = None,
                   priority: int = 0,
                   tags: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        创建滴答清单任务
        
        Args:
            title: 任务标题
            content: 任务内容描述
            project_id: 项目ID，默认为收集箱("inbox")
            due_date: 截止日期，格式：YYYY-MM-DD
            priority: 优先级 (0-3，0为无，3为高)
            tags: 标签列表
            
        Returns:
            API响应结果
        """
        if not self.is_enabled():
            logger.warning("滴答清单API未启用，跳过任务创建")
            return {"success": False, "error": "API未启用"}
        
        # 构建任务数据（使用简化格式）
        task_data = {
            "title": title
        }
        
        # 添加内容（如果有的话，作为描述）
        if content:
            task_data["content"] = content
        
        # 添加优先级（如果不是默认值）
        if priority > 0:
            task_data["priority"] = priority
        
        # 添加截止日期
        if due_date:
            task_data["dueDate"] = f"{due_date}T23:59:59.000+0000"
        
        # 添加标签
        if tags:
            task_data["tags"] = tags
        
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(
                    f"{self.base_url}/task",
                    headers=self.headers,
                    json=task_data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"成功创建滴答清单任务: {title}")
                    return {
                        "success": True,
                        "task_id": result.get("id"),
                        "title": title,
                        "url": f"https://dida365.com/webapp/#/task/{result.get('id')}"
                    }
                else:
                    logger.error(f"创建任务失败: {response.status_code} - {response.text}")
                    return {
                        "success": False,
                        "error": f"HTTP {response.status_code}: {response.text}"
                    }
                    
        except httpx.RequestError as e:
            logger.error(f"网络请求错误: {e}")
            return {"success": False, "error": f"网络错误: {e}"}
        except Exception as e:
            logger.error(f"创建任务时发生未知错误: {e}")
            return {"success": False, "error": f"未知错误: {e}"}
    
    def create_report_task(self, 
                          report_type: str, 
                          summary: str, 
                          details: str = "",
                          paper_count: int = 0) -> Dict[str, Any]:
        """
        创建论文监控报告任务
        
        Args:
            report_type: 报告类型 (daily/weekly/topic)
            summary: 报告摘要
            details: 详细内容
            paper_count: 论文数量
            
        Returns:
            API响应结果
        """
        if not self.is_enabled():
            return {"success": False, "error": "API未启用"}
        
        # 构建任务标题
        type_map = {
            "daily": "📄 每日论文监控",
            "weekly": "📚 周报论文汇总", 
            "topic": "🎯 主题论文搜索"
        }
        
        title = f"{type_map.get(report_type, '📄 论文监控')} - {datetime.now().strftime('%Y-%m-%d')}"
        
        # 构建任务内容
        content_parts = [summary]
        
        if paper_count > 0:
            content_parts.append(f"\n📊 共发现 {paper_count} 篇论文")
        
        if details:
            content_parts.append(f"\n\n📝 详细信息:\n{details}")
        
        content_parts.append(f"\n⏰ 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        content_parts.append(f"\n🤖 由 ArXiv Follow 系统自动生成")
        
        content = "".join(content_parts)
        
        # 设置标签
        tags = ["arxiv", "论文监控", report_type]
        
        # 设置优先级（有论文时为中等优先级）
        priority = 1 if paper_count > 0 else 0
        
        return self.create_task(
            title=title,
            content=content,
            tags=tags,
            priority=priority
        )
    
    def get_user_info(self) -> Dict[str, Any]:
        """
        测试API连接（通过创建一个简单的测试任务）
        
        Returns:
            连接测试结果
        """
        if not self.is_enabled():
            return {"success": False, "error": "API未启用"}
        
        try:
            # 使用创建任务来测试连接（因为open/v1版本没有用户信息接口）
            test_task_data = {
                "title": "🧪 API连接测试任务（将自动删除）"
            }
            
            with httpx.Client(timeout=30.0) as client:
                response = client.post(
                    f"{self.base_url}/task",
                    headers=self.headers,
                    json=test_task_data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    task_id = result.get("id")
                    logger.info("滴答清单API连接测试成功")
                    
                    # 尝试删除测试任务（清理）
                    try:
                        delete_response = client.delete(
                            f"{self.base_url}/task/{task_id}",
                            headers=self.headers
                        )
                        if delete_response.status_code == 200:
                            logger.info("测试任务已自动清理")
                    except:
                        logger.warning("测试任务清理失败，请手动删除")
                    
                    return {
                        "success": True,
                        "message": "API连接正常",
                        "test_task_id": task_id
                    }
                else:
                    logger.error(f"API连接测试失败: {response.status_code} - {response.text}")
                    return {
                        "success": False,
                        "error": f"HTTP {response.status_code}: {response.text}"
                    }
                    
        except Exception as e:
            logger.error(f"API连接测试时发生错误: {e}")
            return {"success": False, "error": str(e)}


# 创建全局实例
dida_client = DidaIntegration()


def create_arxiv_task(report_type: str, 
                     summary: str, 
                     details: str = "",
                     paper_count: int = 0) -> Dict[str, Any]:
    """
    便捷函数：创建ArXiv论文监控任务
    
    Args:
        report_type: 报告类型
        summary: 报告摘要  
        details: 详细内容
        paper_count: 论文数量
        
    Returns:
        任务创建结果
    """
    return dida_client.create_report_task(
        report_type=report_type,
        summary=summary,
        details=details,
        paper_count=paper_count
    )


def test_dida_connection() -> bool:
    """
    测试滴答清单API连接
    
    Returns:
        连接是否成功
    """
    result = dida_client.get_user_info()
    if result.get("success"):
        logger.info(f"滴答清单API连接成功")
        return True
    else:
        logger.warning(f"滴答清单API连接失败：{result.get('error', '未知错误')}")
        return False


if __name__ == "__main__":
    # 测试连接
    print("🧪 测试滴答清单API连接...")
    if test_dida_connection():
        print("✅ 连接成功!")
        
        # 创建测试任务
        print("\n🧪 创建测试任务...")
        result = create_arxiv_task(
            report_type="daily",
            summary="这是一个测试任务，用于验证滴答清单API集成功能",
            paper_count=0
        )
        
        if result.get("success"):
            print(f"✅ 测试任务创建成功! 任务ID: {result.get('task_id')}")
        else:
            print(f"❌ 测试任务创建失败: {result.get('error')}")
    else:
        print("❌ 连接失败!")
        print("💡 请确保已设置 DIDA_ACCESS_TOKEN 环境变量") 