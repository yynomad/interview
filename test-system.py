#!/usr/bin/env python3
"""
面试助手系统测试脚本
用于测试各个组件是否正常工作
"""

import requests
import json
import time
import sys

def test_backend_health():
    """测试后端健康状态"""
    try:
        print("🔍 测试后端连接...")
        response = requests.get("http://localhost:5001/health", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 后端服务正常")
            print(f"   - Gemini 可用: {data.get('gemini_available', False)}")
            return True
        else:
            print(f"❌ 后端服务异常，状态码: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端服务，请确保后端正在运行")
        return False
    except Exception as e:
        print(f"❌ 后端测试失败: {str(e)}")
        return False

def test_question_api():
    """测试问题接口"""
    try:
        print("🔍 测试问题接口...")
        
        test_question = "请介绍一下你自己"
        data = {
            "question": test_question,
            "generate_answer": True
        }
        
        response = requests.post(
            "http://localhost:5001/api/question",
            json=data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 问题接口正常")
            print(f"   - 问题: {result['conversation']['question']}")
            if result['conversation']['answer']:
                print(f"   - 回答: {result['conversation']['answer'][:100]}...")
            return True
        else:
            print(f"❌ 问题接口异常，状态码: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 问题接口测试失败: {str(e)}")
        return False



def main():
    """主测试函数"""
    print("🧪 面试助手系统测试")
    print("=" * 40)
    
    tests = [
        ("后端健康检查", test_backend_health),
        ("问题接口测试", test_question_api),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        if test_func():
            passed += 1
        time.sleep(1)
    
    print("\n" + "=" * 40)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！系统运行正常")
        print("\n📝 下一步:")
        print("1. 运行电脑端工具: cd desktop-tool && python main.py")
        print("2. 开始测试语音识别功能")
        print("3. 查看后端日志获取 AI 回答建议")
    else:
        print("⚠️  部分测试失败，请检查相关服务")
        sys.exit(1)

if __name__ == "__main__":
    main()
