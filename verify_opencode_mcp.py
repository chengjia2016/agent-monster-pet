#!/usr/bin/env python3
"""
OpenCode MCP Connection Verification Script
验证 OpenCode MCP 连接是否正常工作
"""

import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

def print_header(title):
    """打印章节标题"""
    print(f"\n{'═' * 70}")
    print(f"  {title}")
    print(f"{'═' * 70}")

def print_step(step_num, title):
    """打印步骤标题"""
    print(f"\n{step_num}️⃣  {title}")
    print(f"  {'-' * 66}")

def verify_config():
    """验证 OpenCode 配置"""
    print_step("1", "验证 OpenCode 配置")
    
    config_path = Path.home() / ".config" / "opencode" / "opencode.json"
    
    if not config_path.exists():
        print(f"  ❌ 配置文件不存在: {config_path}")
        return False
    
    try:
        with open(config_path) as f:
            config = json.load(f)
        
        mcp_config = config.get("mcp", {}).get("agent-monster", {})
        
        if not mcp_config:
            print(f"  ❌ 没有找到 agent-monster MCP 配置")
            return False
        
        print(f"  ✅ 配置文件存在")
        print(f"     Type: {mcp_config.get('type')}")
        print(f"     Enabled: {mcp_config.get('enabled')}")
        
        command = mcp_config.get("command", [])
        if isinstance(command, list) and len(command) >= 2:
            print(f"     Command: {' '.join(command)}")
            return True
        else:
            print(f"  ❌ 配置命令格式错误: {command}")
            return False
    
    except json.JSONDecodeError as e:
        print(f"  ❌ JSON 解析错误: {e}")
        return False
    except Exception as e:
        print(f"  ❌ 错误: {e}")
        return False

def verify_script():
    """验证 MCP 脚本文件"""
    print_step("2", "验证 MCP 脚本")
    
    script_path = Path("/root/pet/agent-monster/mcp_server_fix.py")
    
    if not script_path.exists():
        print(f"  ❌ 脚本不存在: {script_path}")
        return False
    
    print(f"  ✅ 脚本存在")
    
    # 检查可执行性
    is_exec = script_path.stat().st_mode & 0o111
    if is_exec:
        print(f"  ✅ 脚本可执行")
    else:
        print(f"  ⚠️  脚本不可执行（但可以用 python3 运行）")
    
    print(f"     大小: {script_path.stat().st_size} 字节")
    
    return True

def test_mcp_connection():
    """测试 MCP 服务器连接"""
    print_step("3", "测试 MCP 服务器连接")
    
    script_path = "/root/pet/agent-monster/mcp_server_fix.py"
    
    # 测试初始化请求
    test_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "opencode",
                "version": "1.0"
            }
        }
    }
    
    test_input = json.dumps(test_request) + "\n"
    
    try:
        result = subprocess.run(
            [sys.executable, script_path, "mcp"],
            input=test_input.encode(),
            capture_output=True,
            timeout=5
        )
        
        if result.returncode != 0:
            print(f"  ❌ 脚本返回错误代码: {result.returncode}")
            stderr = result.stderr.decode()
            if stderr:
                print(f"     Error: {stderr[:200]}")
            return False
        
        print(f"  ✅ 脚本成功运行")
        
        response_text = result.stdout.decode().strip()
        if not response_text:
            print(f"  ❌ 没有收到响应")
            return False
        
        print(f"  ✅ 收到响应 ({len(response_text)} 字节)")
        
        try:
            response = json.loads(response_text)
            
            if "error" in response:
                print(f"  ❌ MCP 错误: {response['error']['message']}")
                return False
            
            if "result" not in response:
                print(f"  ❌ 响应格式错误: {response_text[:100]}")
                return False
            
            print(f"  ✅ 有效的 JSON-RPC 响应")
            
            result_data = response.get("result", {})
            protocol = result_data.get("protocolVersion")
            print(f"     Protocol: {protocol}")
            
            return True
        
        except json.JSONDecodeError as e:
            print(f"  ❌ JSON 解析错误: {e}")
            print(f"     Response: {response_text[:100]}")
            return False
    
    except subprocess.TimeoutExpired:
        print(f"  ❌ 脚本执行超时 (5 秒)")
        return False
    except Exception as e:
        print(f"  ❌ 异常: {e}")
        return False

def test_tools_list():
    """测试工具列表请求"""
    print_step("4", "测试工具列表")
    
    script_path = "/root/pet/agent-monster/mcp_server_fix.py"
    
    test_request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {}
    }
    
    test_input = json.dumps(test_request) + "\n"
    
    try:
        result = subprocess.run(
            [sys.executable, script_path, "mcp"],
            input=test_input.encode(),
            capture_output=True,
            timeout=5
        )
        
        if result.returncode != 0:
            print(f"  ❌ 脚本返回错误代码: {result.returncode}")
            return False
        
        response_text = result.stdout.decode().strip()
        
        try:
            response = json.loads(response_text)
            
            if "error" in response:
                print(f"  ❌ MCP 错误: {response['error']['message']}")
                return False
            
            tools = response.get("result", {}).get("tools", [])
            print(f"  ✅ 成功获取工具列表")
            print(f"     工具数量: {len(tools)}")
            
            if len(tools) > 0:
                print(f"     示例工具: {tools[0].get('name')}")
            
            return len(tools) > 0
        
        except json.JSONDecodeError:
            print(f"  ❌ JSON 解析错误")
            return False
    
    except subprocess.TimeoutExpired:
        print(f"  ❌ 执行超时")
        return False
    except Exception as e:
        print(f"  ❌ 异常: {e}")
        return False

def main():
    """主验证流程"""
    print_header("🔍 OpenCode MCP 连接验证")
    print(f"\n  验证时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {
        "配置验证": verify_config(),
        "脚本验证": verify_script(),
        "连接测试": test_mcp_connection(),
        "工具列表": test_tools_list(),
    }
    
    # 总结
    print_header("📊 验证结果总结")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name:20} {status}")
    
    print(f"\n  总体: {passed}/{total} 通过")
    
    print_header("🎯 建议")
    
    if all(results.values()):
        print("""
  ✅ 所有检查都通过了！
  
  OpenCode MCP 连接应该正常工作。
  请按以下步骤操作：
  
  1. 重启 OpenCode（完全关闭后重新打开）
  2. 在 OpenCode 中尝试使用 /monster 命令
  3. 例如: /monster status
  
  如果仍有问题，请检查 OpenCode 的输出日志。
        """)
    else:
        print("""
  ⚠️  某些检查失败
  
  请按以下步骤排查：
  
  1. 确保 /root/pet/agent-monster/ 目录存在
  2. 确保 mcp_server_fix.py 文件存在
  3. 验证 ~/.config/opencode/opencode.json 配置
  4. 尝试手动运行脚本进行测试
  5. 查看 OPENCODE_MCP_FIX.md 获取详细帮助
        """)
    
    print_header("✨ 验证完成")
    
    return 0 if all(results.values()) else 1

if __name__ == "__main__":
    sys.exit(main())
