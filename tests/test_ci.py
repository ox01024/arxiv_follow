#!/usr/bin/env python3
"""
CI测试脚本 - 验证环境和依赖是否正确安装
"""

import sys
import os
from datetime import datetime

def test_imports():
    """测试必要的导入"""
    try:
        import httpx
        print("✅ httpx 导入成功")
        
        import csv
        print("✅ csv 导入成功")
        
        import json
        print("✅ json 导入成功")
        
        import re
        print("✅ re 导入成功")
        
        from urllib.parse import urlencode
        print("✅ urllib.parse 导入成功")
        
        return True
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return False

def test_directories():
    """测试目录结构"""
    try:
        # 检查reports目录
        if not os.path.exists("reports"):
            os.makedirs("reports")
            print("✅ 创建了 reports 目录")
        else:
            print("✅ reports 目录已存在")
        
        # 测试写入权限
        test_file = "reports/test_write.txt"
        with open(test_file, 'w') as f:
            f.write("测试写入")
        os.remove(test_file)
        print("✅ reports 目录写入权限正常")
        
        return True
    except Exception as e:
        print(f"❌ 目录测试失败: {e}")
        return False

def test_network():
    """测试网络连接"""
    try:
        import httpx
        with httpx.Client(timeout=10.0) as client:
            response = client.get("https://httpbin.org/status/200")
            if response.status_code == 200:
                print("✅ 网络连接正常")
                return True
            else:
                print(f"❌ 网络测试失败，状态码: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ 网络测试异常: {e}")
        return False

def main():
    """主测试函数"""
    print("🧪 CI环境测试")
    print("="*50)
    print(f"🕐 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🐍 Python版本: {sys.version}")
    print(f"📁 工作目录: {os.getcwd()}")
    print("="*50)
    
    tests_passed = 0
    total_tests = 3
    
    # 测试导入
    print("\n📦 测试模块导入...")
    if test_imports():
        tests_passed += 1
    
    # 测试目录
    print("\n📁 测试目录结构...")
    if test_directories():
        tests_passed += 1
    
    # 测试网络
    print("\n🌐 测试网络连接...")
    if test_network():
        tests_passed += 1
    
    print("\n" + "="*50)
    print(f"📊 测试结果: {tests_passed}/{total_tests} 通过")
    
    if tests_passed == total_tests:
        print("🎉 所有测试通过！CI环境准备就绪")
        return True
    else:
        print("❌ 部分测试失败，请检查CI配置")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 