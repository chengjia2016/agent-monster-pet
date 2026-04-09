# 🚀 快速参考 - 日志和测试

## 📦 构建

```bash
cd /root/pet/agent-monster/cli
go build -o agentmonster ./cmd
```

## 🏃 运行

```bash
# 标准运行
./agentmonster

# 调试模式（更多日志）
./agentmonster --debug

# 指定服务器（默认 http://127.0.0.1:10000）
./agentmonster --server=http://localhost:10000
```

## 📋 查看日志

```bash
# 查看最新日志摘要
/root/pet/agent-monster/view_logs.sh

# 实时跟踪日志
tail -f ~/.agent-monster/data/logs/agentmonster_*.log

# 只看错误
grep "ERROR\|❌" ~/.agent-monster/data/logs/agentmonster_*.log

# 只看 API 调用
grep "🌐\|📨" ~/.agent-monster/data/logs/agentmonster_*.log

# 看特定部分
grep "地图生成\|领取" ~/.agent-monster/data/logs/agentmonster_*.log
```

## 🧪 自动测试

```bash
# 运行自动测试（显示完整日志分析）
/root/pet/agent-monster/test_onboarding.sh

# 运行单元测试
cd /root/pet/agent-monster/cli
go test ./pkg/ui -v
```

## 🔍 调试技巧

### 问题：卡在某一步

```bash
# 查看实时日志，等待新信息出现
tail -f ~/.agent-monster/data/logs/agentmonster_*.log

# 如果 15 秒内没有新日志，说明卡住了
```

### 问题：地图生成失败

```bash
# 查看 API 错误
grep "API Error\|Status\|failed" ~/.agent-monster/data/logs/agentmonster_*.log

# 可能的问题：
# - Status 400 = 参数错误
# - Status 404 = 端点不存在  
# - Status 500 = 服务器错误
# - timeout = 网络太慢或服务器没响应
```

### 问题：宝可梦领取失败

```bash
# 查看用户认证
grep "User not authenticated\|user_id\|github_id" ~/.agent-monster/data/logs/agentmonster_*.log

# 可能的问题：
# - github_id=0 = 用户账户未初始化
# - ID=0 = GitHub 认证失败
```

## 📊 日志位置

```
~/.agent-monster/data/logs/agentmonster_YYYYMMDD_HHMMSS.log
```

## 🎯 关键日志消息

| 消息 | 含义 |
|------|------|
| `[INFO] Starting Agent Monster CLI` | CLI 启动成功 |
| `[INFO] 🌐 API Request: POST /api/...` | API 请求发送 |
| `[INFO] 📨 API Response: Status 201` | API 响应成功 |
| `[ERROR] ❌ API Error at ...` | API 请求失败 |
| `[INFO] Map generated successfully` | 地图生成成功 |
| `[INFO] Successfully claimed starter pokemons` | 宝可梦领取成功 |
| `[ERROR] Map generation timeout (30 seconds)` | 地图生成超时 |

## ✅ 测试清单

- [ ] CLI 能正常启动
- [ ] 按 Enter 进入 Fork 屏幕
- [ ] Fork 成功
- [ ] 选择地图模板
- [ ] 选择 NPC
- [ ] 按 Enter 生成地图，看到加载界面
- [ ] 地图生成成功
- [ ] 自动进入领取屏幕
- [ ] 宝可梦领取成功
- [ ] 显示完成屏幕

## 📚 文档

| 文档 | 用途 |
|------|------|
| `TESTING_GUIDE.md` | 完整的测试指南 |
| `LOGGING_SUMMARY.md` | 日志系统总结 |
| `README.md` | 项目概览 |

## 🔗 相关命令

```bash
# 清理旧日志（保留最近 5 个）
ls -t ~/.agent-monster/data/logs/agentmonster_*.log | tail -n +6 | xargs rm

# 查看日志统计
wc -l ~/.agent-monster/data/logs/agentmonster_*.log

# 导出日志到文本
cat ~/.agent-monster/data/logs/agentmonster_*.log > /tmp/export.log

# 对比两次运行
diff log1.log log2.log | head -50
```

## 💡 提示

- 每次运行会创建新的日志文件
- 日志文件不会自动删除（考虑定期清理）
- DEBUG 模式会产生更多日志（约 10 倍大小）
- 日志既写入文件也输出到终端
- 所有时间戳都是本地时间

---

**需要帮助？** 查看详细指南：`cat TESTING_GUIDE.md`
