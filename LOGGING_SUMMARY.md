# 📊 日志系统实现总结

## ✅ 已完成的工作

### 1. 创建日志系统 (`cli/pkg/logger/logger.go`)
- 文件日志记录到 `~/.agent-monster/data/logs/agentmonster_YYYYMMDD_HHMMSS.log`
- 同时输出到 stderr（实时看到日志）
- 支持 DEBUG, INFO, WARN, ERROR 四个日志级别
- 线程安全的日志写入（使用 mutex）
- Session ID 用于区分不同的运行

### 2. 初始化日志系统 (`cmd/main.go`)
- CLI 启动时自动初始化日志系统
- `--debug` 标志启用 DEBUG 级别
- 默认使用 INFO 级别
- 记录启动参数和配置信息

### 3. API 客户端日志 (`pkg/api/client.go`)
- 每个 API 请求都记录方法、端点和参数
- 每个 API 响应都记录状态码
- API 错误详细记录
- 请求/响应大小限制为 200 字符（避免日志文件过大）

### 4. 新手引导日志 (`pkg/ui/onboarding.go`)

#### 关键函数添加的日志：

**GenerateOnboardingMap()**
```
- 开始地图生成
- 生成的 map_id
- API 调用参数
- 地图生成成功/失败
- 最终地图尺寸
```

**ClaimStarterPokemons()**
```
- 用户认证检查
- 用户 ID 和名称
- API 调用
- 成功/失败消息
```

**generateMapCmd()**
```
- 命令启动
- Goroutine 启动
- 超时检测
- 状态转换
```

**claimStarterPokemonsCmd()**
```
- 命令启动
- 动画屏幕显示（2秒）
- Goroutine 启动
- 完成状态
```

**HandleOnboardingInput()**
```
- 每个按键输入
- 当前步骤和按键值
```

### 5. 日志查看工具

**view_logs.sh**
- 显示最新的日志文件
- 提供过滤命令示例
- 快速定位问题

**test_onboarding.sh**
- 自动运行测试
- 分析日志输出
- 统计错误/警告/信息数量
- 提取关键事件
- 显示最终结果

### 6. 文档

**TESTING_GUIDE.md**
- 完整的测试指南
- 每一步的预期日志
- 问题排查方法
- 性能基准
- 快速参考

---

## 🎯 如何使用

### 1. 构建 CLI
```bash
cd /root/pet/agent-monster/cli
go build -o agentmonster ./cmd
```

### 2. 运行 CLI（包含日志）
```bash
# 标准模式
./agentmonster

# 调试模式（更详细的日志）
./agentmonster --debug
```

### 3. 查看日志
```bash
# 查看最新日志
/root/pet/agent-monster/view_logs.sh

# 实时监控日志
tail -f ~/.agent-monster/data/logs/agentmonster_*.log

# 过滤特定内容
grep "ERROR" ~/.agent-monster/data/logs/agentmonster_*.log
grep "API" ~/.agent-monster/data/logs/agentmonster_*.log
```

### 4. 运行自动测试
```bash
/root/pet/agent-monster/test_onboarding.sh
```

---

## 📈 日志信息分类

### 日志级别
- **DEBUG** - 详细调试信息（仅在 --debug 模式下显示）
- **INFO** - 正常流程信息
- **WARN** - 警告（操作继续但有问题）
- **ERROR** - 错误（操作失败）

### 特殊符号
```
🌐 - API 请求发送
📨 - API 响应接收
❌ - 错误标记
✅ - 成功标记
⏳ - 等待/处理中
─  - 日志区间标记
```

---

## 🔍 快速故障排查

### 问题：卡在某一步

**解决方案：**
```bash
# 查看实时日志
tail -f ~/.agent-monster/data/logs/agentmonster_*.log

# 等待，如果 15 秒内没有新日志说明真的卡住了
# 检查是否有以下日志：
# - [ERROR] 开头的错误消息
# - 超时消息
# - API 连接失败
```

### 问题：地图生成失败

**检查日志中是否有：**
```
❌ API Error at /api/maps/generate: request failed with status XXX
```

**常见状态码：**
- 400 - 请求参数错误（检查 owner_id, owner_name）
- 404 - 端点不存在
- 500 - 服务器错误

### 问题：宝可梦领取失败

**检查日志中是否有：**
```
[ERROR] User not authenticated: CurrentUser=..., ID=0
```

**原因：**
- GitHub 认证失败
- 用户 ID 未正确初始化

---

## 📊 日志文件位置

```
~/.agent-monster/data/logs/
├── agentmonster_20260409_180000.log
├── agentmonster_20260409_181500.log
└── agentmonster_20260409_183000.log
```

每次运行 CLI 都会创建一个新的日志文件。

---

## 🚀 提高调试效率的方法

### 1. 使用 grep 过滤
```bash
# 只看错误
grep "ERROR" agentmonster_*.log

# 只看 API 调用
grep "🌐\|📨" agentmonster_*.log

# 看特定步骤
grep "地图生成" agentmonster_*.log
```

### 2. 使用管道处理
```bash
# 统计某个操作出现的次数
grep "API Request" agentmonster_*.log | wc -l

# 看最后 50 行
tail -50 agentmonster_*.log
```

### 3. 对比日志
```bash
# 对比两次运行
diff <(sed 's/\[.*\]/[TIME]/' log1.log) <(sed 's/\[.*\]/[TIME]/' log2.log)
```

---

## 🔄 改进建议（未来）

1. **日志级别按模块设置** - 例如只记录 API 日志
2. **日志轮转** - 自动删除旧日志保持磁盘空间
3. **日志上传** - 远程上传用于远程调试
4. **性能指标** - 记录每个操作的执行时间
5. **Web 日志查看器** - 提供 Web 界面查看日志

---

## ✅ 验证清单

- [x] 日志系统创建
- [x] 主程序中初始化日志
- [x] API 客户端添加日志
- [x] 新手引导各步骤添加日志
- [x] 日志查看脚本
- [x] 自动测试脚本
- [x] 完整测试指南文档
- [x] 所有测试通过（74 个单元测试）
- [x] 代码编译成功

---

## 📝 提交记录

1. **06e2e80** - fix: 修正 API 参数 github_username -> github_login
2. **aa64b37** - improvement: 添加加载屏幕反馈
3. **4eb8f76** - feat: 添加日志系统
4. **176387a** - docs: 添加测试指南
5. **469fd61** - scripts: 添加自动测试脚本

---

## 🎓 学习资源

- 日志系统代码：`cli/pkg/logger/logger.go`
- 使用示例：`cli/pkg/ui/onboarding.go`
- 测试指南：`TESTING_GUIDE.md`
- 查看脚本：`view_logs.sh`，`test_onboarding.sh`

---

现在，每次测试时，你都能清楚地看到：
- ✅ 什么成功了
- ❌ 什么失败了
- 🔍 具体在哪一步失败
- 📊 失败的原因是什么

这样可以大大提高调试效率！

