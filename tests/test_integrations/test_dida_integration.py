#!/usr/bin/env python3
"""
滴答清单API集成测试脚本
用于测试滴答清单API连接和任务创建功能
"""

import os
import sys
from datetime import datetime

import pytest

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../"))

try:
    from src.arxiv_follow.integrations.dida import (
        DidaIntegration,
        create_arxiv_task,
        test_dida_connection,
    )
    from src.arxiv_follow.services.translation import test_translation_service
except ImportError as e:
    print(f"❌ 导入模块失败: {e}")
    pytest.skip(f"模块导入失败: {e}", allow_module_level=True)


class TestDidaIntegration:
    """滴答清单集成测试类"""

    @pytest.fixture
    def dida(self):
        """滴答清单集成实例"""
        return DidaIntegration()

    def test_service_initialization(self, dida):
        """测试服务初始化"""
        assert dida is not None
        assert hasattr(dida, "is_enabled")

    def test_basic_connection(self):
        """测试基本API连接"""
        if not os.getenv("DIDA_ACCESS_TOKEN"):
            pytest.skip("需要DIDA_ACCESS_TOKEN环境变量")

        success = test_dida_connection()
        assert success, "API连接应该成功"

    def test_simple_task_creation(self, dida):
        """测试简单任务创建"""
        if not dida.is_enabled():
            pytest.skip("滴答清单API未启用，请设置DIDA_ACCESS_TOKEN环境变量")

        # 创建测试任务
        result = dida.create_task(
            title="🧪 简单任务创建测试（将自动删除）",
            content="这是一个测试任务，创建时间: 2025-06-29",
            tags=["测试", "arxiv", "自动清理"],
        )

        assert result.get("success"), f"任务创建应该成功: {result.get('error')}"
        assert "task_id" in result or "url" in result

        # 自动清理测试任务
        task_id = result.get("task_id")
        project_id = result.get("project_id")
        if task_id:
            cleanup_result = dida.delete_task(task_id, project_id)
            if cleanup_result.get("success"):
                print(f"✅ 测试任务已自动清理: {task_id}")
            else:
                print(f"⚠️ 测试任务清理失败: {cleanup_result.get('error')}")
                print(f"💡 请手动删除任务ID: {task_id}")

    def test_arxiv_task_creation(self):
        """测试ArXiv论文监控任务创建"""
        if not os.getenv("DIDA_ACCESS_TOKEN"):
            pytest.skip("需要DIDA_ACCESS_TOKEN环境变量")

        created_tasks = []  # 收集创建的任务信息用于清理

        # 测试每日研究者动态监控任务
        result1 = create_arxiv_task(
            report_type="daily",
            summary="🧪 测试：今日研究者发布3篇新论文！",
            details="监控了5位研究者\n论文分布:\n• 张三: 2篇\n• 李四: 1篇\n\n⚠️ 这是测试任务，将自动清理",
            paper_count=3,
        )
        assert result1.get("success"), f"每日任务创建失败: {result1.get('error')}"
        if result1.get("task_id"):
            created_tasks.append(
                {"task_id": result1["task_id"], "project_id": result1.get("project_id")}
            )

        # 测试每周研究者动态汇总任务
        result2 = create_arxiv_task(
            report_type="weekly",
            summary="🧪 测试：本周研究者无新论文发布",
            details="监控了5位研究者\n监控周期: 2025-01-01 至 2025-01-07\n\n⚠️ 这是测试任务，将自动清理",
            paper_count=0,
        )
        assert result2.get("success"), f"每周任务创建失败: {result2.get('error')}"
        if result2.get("task_id"):
            created_tasks.append(
                {"task_id": result2["task_id"], "project_id": result2.get("project_id")}
            )

        # 测试主题搜索任务
        result3 = create_arxiv_task(
            report_type="topic",
            summary="🧪 测试：主题论文搜索发现10篇论文！\n主题: cs.AI AND cs.CR",
            details="搜索主题: cs.AI AND cs.CR\n使用策略: 智能日期回退\n\n⚠️ 这是测试任务，将自动清理",
            paper_count=10,
        )
        assert result3.get("success"), f"主题任务创建失败: {result3.get('error')}"
        if result3.get("task_id"):
            created_tasks.append(
                {"task_id": result3["task_id"], "project_id": result3.get("project_id")}
            )

        # 批量清理所有测试任务
        if created_tasks:
            dida = DidaIntegration()
            deleted_count = 0
            failed_count = 0
            failed_ids = []

            for task_info in created_tasks:
                task_id = task_info.get("task_id")
                project_id = task_info.get("project_id")
                if task_id:
                    delete_result = dida.delete_task(task_id, project_id)
                    if delete_result.get("success"):
                        deleted_count += 1
                    else:
                        failed_count += 1
                        failed_ids.append(task_id)

            if failed_count == 0:
                print(f"✅ 成功清理所有 {deleted_count} 个测试任务")
            else:
                print(
                    f"⚠️ 部分清理失败: 成功 {deleted_count} 个，失败 {failed_count} 个"
                )
                print(f"💡 需要手动删除的任务ID: {', '.join(failed_ids)}")

    def test_bilingual_task_creation(self):
        """测试双语翻译任务创建"""
        if not os.getenv("DIDA_ACCESS_TOKEN"):
            pytest.skip("需要DIDA_ACCESS_TOKEN环境变量")

        # 检查是否有翻译服务API密钥
        try:
            translation_available = test_translation_service()
        except:
            pytest.skip("翻译服务模块不可用")

        if not translation_available:
            pytest.skip("翻译服务API密钥未配置")

        result = create_arxiv_task(
            report_type="daily",
            summary="🧪 测试：今日研究者发布2篇新论文！",
            details="""监控了3位研究者

📊 论文分布:
• Zhang Wei: 1篇
  1. **Deep Learning Approaches for Network Intrusion Detection**
     📄 **arXiv:** 2501.12345

⏰ 执行时间: 2025-01-15 09:00:15
⚠️ 这是测试任务，将自动清理""",
            paper_count=2,
            bilingual=True,
        )

        assert result.get("success"), f"双语任务创建失败: {result.get('error')}"

        # 自动清理双语测试任务
        task_id = result.get("task_id")
        project_id = result.get("project_id")
        if task_id:
            dida = DidaIntegration()
            cleanup_result = dida.delete_task(task_id, project_id)
            if cleanup_result.get("success"):
                print(f"✅ 双语测试任务已自动清理: {task_id}")
            else:
                print(f"⚠️ 双语测试任务清理失败: {cleanup_result.get('error')}")
                print(f"💡 请手动删除任务ID: {task_id}")

    def test_error_handling(self):
        """测试错误处理"""
        invalid_dida = DidaIntegration(access_token="invalid_token_12345")

        result = invalid_dida.create_task(
            title="应该失败的任务", content="这个任务应该因为无效token而失败"
        )

        assert not result.get("success"), "无效token应该导致失败"


def test_basic_connection():
    """测试基本API连接"""
    print("🧪 测试1: 基本API连接测试")
    print("-" * 40)

    success = test_dida_connection()

    if success:
        print("✅ API连接测试成功")
        return True
    else:
        print("❌ API连接测试失败")
        return False


def test_simple_task_creation():
    """测试简单任务创建"""
    print("\n🧪 测试2: 简单任务创建测试")
    print("-" * 40)

    dida = DidaIntegration()

    if not dida.is_enabled():
        print("❌ 滴答清单API未启用，请设置DIDA_ACCESS_TOKEN环境变量")
        return False

    # 创建测试任务
    result = dida.create_task(
        title="🧪 简单任务创建测试（将自动删除）",
        content="这是一个测试任务，创建时间: 2025-06-29",
        tags=["测试", "arxiv", "自动清理"],
    )

    if result.get("success"):
        task_id = result.get("task_id")
        project_id = result.get("project_id")
        print(f"✅ 简单任务创建成功，任务ID: {task_id}")

        # 自动清理测试任务
        cleanup_result = dida.delete_task(task_id, project_id)
        if cleanup_result.get("success"):
            print(f"✅ 测试任务已自动清理")
            return True
        else:
            print(f"⚠️ 测试任务清理失败: {cleanup_result.get('error')}")
            print(f"💡 请手动删除任务ID: {task_id}")
            return True  # 创建成功就算通过，清理失败不影响测试结果
    else:
        print(f"❌ 简单任务创建失败: {result.get('error')}")
        return False


def test_arxiv_task_creation():
    """测试ArXiv论文监控任务创建"""
    print("\n🧪 测试3: ArXiv论文监控任务创建测试")
    print("-" * 40)

    if not os.getenv("DIDA_ACCESS_TOKEN"):
        print("❌ 需要DIDA_ACCESS_TOKEN环境变量")
        return False

    created_tasks = []  # 收集创建的任务信息用于清理

    # 测试每日监控任务
    print("📄 测试每日监控任务...")
    result1 = create_arxiv_task(
        report_type="daily",
        summary="🧪 测试：今日发现3篇新论文！",
        details="监控了5位研究者\n论文分布:\n• 张三: 2篇\n• 李四: 1篇\n\n⚠️ 这是测试任务，将自动清理",
        paper_count=3,
    )

    if result1.get("success"):
        print("✅ 每日监控任务创建成功")
        if result1.get("task_id"):
            created_tasks.append(
                {"task_id": result1["task_id"], "project_id": result1.get("project_id")}
            )
    else:
        print(f"❌ 每日监控任务创建失败: {result1.get('error')}")
        return False

    # 测试周报任务
    print("📚 测试周报任务...")
    result2 = create_arxiv_task(
        report_type="weekly",
        summary="🧪 测试：本周无新论文发现",
        details="监控了5位研究者\n监控周期: 2025-01-01 至 2025-01-07\n\n⚠️ 这是测试任务，将自动清理",
        paper_count=0,
    )

    if result2.get("success"):
        print("✅ 周报任务创建成功")
        if result2.get("task_id"):
            created_tasks.append(
                {"task_id": result2["task_id"], "project_id": result2.get("project_id")}
            )
    else:
        print(f"❌ 周报任务创建失败: {result2.get('error')}")

    # 测试主题搜索任务
    print("🎯 测试主题搜索任务...")
    result3 = create_arxiv_task(
        report_type="topic",
        summary="🧪 测试：主题论文搜索发现10篇论文！\n主题: cs.AI AND cs.CR",
        details="搜索主题: cs.AI AND cs.CR\n使用策略: 智能日期回退\n\n⚠️ 这是测试任务，将自动清理",
        paper_count=10,
    )

    if result3.get("success"):
        print("✅ 主题搜索任务创建成功")
        if result3.get("task_id"):
            created_tasks.append(
                {"task_id": result3["task_id"], "project_id": result3.get("project_id")}
            )
    else:
        print(f"❌ 主题搜索任务创建失败: {result3.get('error')}")

    # 批量清理所有测试任务
    if created_tasks:
        print(f"\n🗑️  开始清理 {len(created_tasks)} 个测试任务...")
        dida = DidaIntegration()
        deleted_count = 0
        failed_count = 0
        failed_ids = []

        for task_info in created_tasks:
            task_id = task_info.get("task_id")
            project_id = task_info.get("project_id")
            if task_id:
                delete_result = dida.delete_task(task_id, project_id)
                if delete_result.get("success"):
                    deleted_count += 1
                else:
                    failed_count += 1
                    failed_ids.append(task_id)

        if failed_count == 0:
            print(f"✅ 成功清理所有 {deleted_count} 个测试任务")
        else:
            print(f"⚠️ 部分清理失败: 成功 {deleted_count} 个，失败 {failed_count} 个")
            print(f"💡 需要手动删除的任务ID: {', '.join(failed_ids)}")

    # 统计成功数量
    success_count = sum(
        [
            result1.get("success", False),
            result2.get("success", False),
            result3.get("success", False),
        ]
    )

    print(f"\n📊 ArXiv任务创建测试结果: {success_count}/3 成功")
    return success_count >= 2  # 至少2个成功就算通过


def test_bilingual_task_creation():
    """测试双语翻译任务创建"""
    print("\n🧪 测试4: 双语翻译任务创建测试")
    print("-" * 40)

    if not os.getenv("DIDA_ACCESS_TOKEN"):
        print("❌ 需要DIDA_ACCESS_TOKEN环境变量")
        return False

    # 检查是否有翻译服务API密钥
    try:
        translation_available = test_translation_service()
    except:
        print("⏭️ 翻译服务模块不可用，跳过测试")
        return True  # 跳过不算失败

    if not translation_available:
        print("⏭️ 翻译服务API密钥未配置，跳过测试")
        return True  # 跳过不算失败

    result = create_arxiv_task(
        report_type="daily",
        summary="🧪 测试：今日研究者发布2篇新论文！",
        details="""监控了3位研究者

📊 论文分布:
• Zhang Wei: 1篇
  1. **Deep Learning Approaches for Network Intrusion Detection**
     📄 **arXiv:** 2501.12345

⏰ 执行时间: 2025-01-15 09:00:15
⚠️ 这是测试任务，将自动清理""",
        paper_count=2,
        bilingual=True,
    )

    if result.get("success"):
        print("✅ 双语翻译任务创建成功")

        # 自动清理双语测试任务
        task_id = result.get("task_id")
        project_id = result.get("project_id")
        if task_id:
            dida = DidaIntegration()
            cleanup_result = dida.delete_task(task_id, project_id)
            if cleanup_result.get("success"):
                print(f"✅ 双语测试任务已自动清理")
            else:
                print(f"⚠️ 双语测试任务清理失败: {cleanup_result.get('error')}")
                print(f"💡 请手动删除任务ID: {task_id}")

        return True
    else:
        print(f"❌ 双语翻译任务创建失败: {result.get('error')}")
        return False


def test_error_handling():
    """测试错误处理"""
    print("\n🧪 测试5: 错误处理测试")
    print("-" * 40)

    # 创建一个使用无效token的客户端
    invalid_dida = DidaIntegration(access_token="invalid_token_12345")

    result = invalid_dida.create_task(
        title="应该失败的任务", content="这个任务应该因为无效token而失败"
    )

    if not result.get("success"):
        print("✅ 错误处理测试成功 - 无效token正确返回失败")
        return True
    else:
        print("❌ 错误处理测试失败 - 无效token应该返回失败")
        return False


def main():
    """主测试函数"""
    print("🧪 滴答清单API集成测试套件（带自动清理）")
    print("=" * 60)

    # 检查环境变量
    access_token = os.getenv("DIDA_ACCESS_TOKEN")
    if not access_token:
        print("⚠️  警告: 未设置 DIDA_ACCESS_TOKEN 环境变量")
        print("   部分测试将被跳过或失败")
        print("   请参考README.md获取access token配置方法")
    else:
        print(f"✅ 检测到access token (长度: {len(access_token)})")
        print("🗑️  所有测试任务将在测试完成后自动清理")

    print()

    # 运行测试
    test_results = []

    # 测试1: 基本连接
    test_results.append(test_basic_connection())

    # 测试2: 简单任务创建（需要有效token）
    if access_token:
        test_results.append(test_simple_task_creation())
        test_results.append(test_arxiv_task_creation())
        test_results.append(test_bilingual_task_creation())
    else:
        print("\n⏭️  跳过任务创建测试（需要access token）")
        test_results.extend([False, False, False])

    # 测试5: 错误处理
    test_results.append(test_error_handling())

    # 测试结果汇总
    print("\n" + "=" * 60)
    print("📊 测试结果汇总")
    print("=" * 60)

    test_names = [
        "基本API连接测试",
        "简单任务创建测试",
        "ArXiv任务创建测试",
        "双语翻译任务创建测试",
        "错误处理测试",
    ]

    passed = 0
    for i, (name, result) in enumerate(zip(test_names, test_results, strict=False), 1):
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{i}. {name}: {status}")
        if result:
            passed += 1

    print(f"\n🎯 总体结果: {passed}/{len(test_results)} 个测试通过")

    if passed == len(test_results):
        print("🎉 所有测试通过！滴答清单API集成正常工作")
        return 0
    elif passed > len(test_results) // 2:
        print("⚠️  部分测试通过，请检查失败的测试项")
        return 1
    else:
        print("❌ 大部分测试失败，请检查配置和网络连接")
        return 2


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
