# 🔧 OpenCode MCP 连接错误 - 根本原因和修复

## 问题诊断

**错误信息**: `PaMCP • agent-monster MCP error -32000: Connection closed`

### 根本原因

OpenCode 配置文件 (`~/.config/opencode/opencode.json`) 中指向了错误的路径：

```json
// ❌ 错误的配置
"command": ["python3", "/root/pet/agent-monster-pet/mcp_server.py", "mcp"]
```

问题：
- 路径指向 `/root/pet/agent-monster-pet/` (不存在)
- 应该指向 `/root/pet/agent-monster/` (实际路径)
- 使用过时的 `mcp_server.py` 而不是改进的 `mcp_server_fix.py`

## 解决方案

### 已修复的配置

```json
// ✅ 正确的配置
"command": ["python3", "/root/pet/agent-monster/mcp_server_fix.py", "mcp"]
```

**变更内容**:
1. 修正路径: `agent-monster-pet` → `agent-monster`
2. 更新脚本: `mcp_server.py` → `mcp_server_fix.py` (改进版本)

### 配置文件位置

```
~/.config/opencode/opencode.json
```

## 验证步骤

✅ **已验证**:
- 配置文件正确指向实际脚本
- 脚本文件存在且可执行
- MCP 服务器成功响应初始化请求
- 返回有效的 JSON-RPC 协议响应

## 修复后的操作

1. **重启 OpenCode** - 使新配置生效
2. **测试连接** - 使用任何 `/monster` 命令测试
3. **验证功能** - 应该能正常调用 MCP 工具

## 使用示例

修复后，所有 `/monster` 命令应该正常工作：

```
/monster init        ✅ 初始化宠物
/monster status      ✅ 查看状态
/monster duel        ✅ 发起对战
/monster analyze     ✅ 分析仓库
```

## 技术细节

### 改进的 MCP 服务器 (`mcp_server_fix.py`)

相比原始版本的改进：

1. **优雅的信号处理**
   ```python
   signal.signal(signal.SIGTERM, signal_handler)
   signal.signal(signal.SIGINT, signal_handler)
   ```

2. **行缓冲 I/O**
   ```python
   sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', buffering=1)
   sys.stderr = os.fdopen(sys.stderr.fileno(), 'w', buffering=1)
   ```

3. **连接错误处理**
   ```python
   try:
       mcp_server.mcp_loop()
   except BrokenPipeError:
       sys.exit(0)  # OpenCode 关闭连接
   ```

## 相关文件

| 文件 | 状态 | 用途 |
|------|------|------|
| `~/.config/opencode/opencode.json` | ✅ 已修复 | OpenCode 配置 |
| `/root/pet/agent-monster/mcp_server_fix.py` | ✅ 可用 | 改进的 MCP 服务器 |
| `/root/pet/agent-monster/mcp_server.py` | ✅ 保留 | 原始 MCP 服务器 |

## 如果问题仍然存在

1. **清除 OpenCode 缓存**
   ```bash
   rm -rf ~/.config/opencode/cache
   rm -rf ~/.cache/opencode
   ```

2. **完全重启 OpenCode**
   - 关闭 OpenCode
   - 等待 30 秒
   - 重新启动

3. **检查配置有效性**
   ```bash
   cat ~/.config/opencode/opencode.json | jq '.mcp'
   ```

4. **手动测试 MCP 服务器**
   ```bash
   cd /root/pet/agent-monster
   python3 mcp_server_fix.py mcp
   # 然后输入: {"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}
   ```

## 预期结果

修复后，OpenCode 应该：
- ✅ 正确连接到 agent-monster MCP 服务器
- ✅ 加载所有 30+ 个可用工具
- ✅ 响应 `/monster` 斜杠命令
- ✅ 无 "Connection closed" 错误

---

**修复日期**: 2026-04-07  
**配置版本**: 1.1  
**状态**: ✅ 已验证可用
