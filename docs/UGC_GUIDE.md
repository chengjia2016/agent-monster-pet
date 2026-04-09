# Agent Monster UGC (User Generated Content) System

## 概述

Agent Monster UGC系统允许用户创建、验证、共享和管理自己设计的地图。这个社区驱动的内容生态系统让玩家能够：

- 📍 **创建** 独特的游戏地图
- ✅ **验证** 地图质量和平衡性
- 📤 **导出** 地图到个人GitHub仓库
- 🔀 **提交** PR到主项目获取社区认可
- 🏪 **浏览** 社区创建的地图市场
- ⭐ **评分** 和下载其他玩家的地图

## 核心功能

### 1. Map创建 & 设计

```bash
# 创建新的map
./agentmonster map create \
  --title "我的精彩地图" \
  --description "一个充满挑战的冒险地图" \
  --difficulty hard \
  --tags "adventure,challenging,pokemon"
```

### 2. Map验证 & 评分

系统自动验证每个Map：

**格式验证 (20分)**
- ✅ 所有必要字段完整
- ✅ Map ID唯一
- ✅ JSON格式正确

**平衡性检查 (30分)**
- ✅ 野生Pokemon: 30-50%
- ✅ 食物: 20-30%
- ✅ 障碍物: 15-25%
- ✅ NPC/其他: 5-10%

**多样性检查 (25分)**
- ✅ 至少3种不同Pokemon
- ✅ 至少2种不同食物
- ✅ 多样化的地形

**创意性评估 (15分)**
- 独特的设计
- 有趣的布局
- 良好的可玩性

**文档质量 (10分)**
- 清晰的描述
- 合适的标签
- 版本信息

### 3. Map导出到GitHub

```bash
# 导出map到你的fork仓库
./agentmonster map export <map_id>

# 这会创建以下结构：
# your-repo/
# └── maps/
#     └── my_map_id/
#         ├── map.json        # 地图数据
#         ├── metadata.json   # 元数据
#         └── README.md       # 说明文档
```

### 4. 提交PR到主项目

```bash
# 系统自动生成PR，包含：
# - Map元数据
# - 验证评分
# - 作者信息
# - 许可证声明

# 维护者审查后，合并到主项目
# 你的Map现在对所有玩家可用!
```

### 5. 社区地图市场

```bash
# 列出所有社区地图
./agentmonster marketplace list

# 搜索地图
./agentmonster marketplace search "adventure"

# 按难度浏览
./agentmonster marketplace filter --difficulty hard

# 查看最受欢迎的地图
./agentmonster marketplace top 10

# 下载并使用地图
./agentmonster map load <map_id>
```

## 工作流程详解

### 完整的Map贡献流程

```
1. Fork主仓库
   ↓
2. 创建新Map (本地)
   ↓
3. 验证Map质量
   ↓
4. 如果评分 < 70 → 返回修改
   ↓
5. 导出Map到你的Fork
   ↓
6. 提交PR到主仓库
   ↓
7. 维护者审查
   ↓
8. 如果需要改进 → 返回修改
   ↓
9. PR合并到主项目
   ↓
10. Map出现在社区市场!
```

## 文件结构

### 导出的Map包结构

```json
{
  "metadata": {
    "map_id": "my_awesome_map",
    "title": "My Awesome Map",
    "description": "...",
    "owner_id": 12345,
    "owner_username": "myusername",
    "difficulty": "hard",
    "tags": ["adventure", "pokemon", "challenging"],
    "version": "1.0.0",
    "created_at": "2026-04-09T18:00:00Z",
    "downloads": 0,
    "rating": 0,
    "reviews": 0
  },
  "map_data": {
    "version": "1.0",
    "width": 30,
    "height": 40,
    "terrain": [...],
    "elements": [
      {
        "id": "wild_001",
        "type": "wild_pokemon",
        "x": 10,
        "y": 15,
        "data": {...}
      },
      ...
    ]
  },
  "license": "CC-BY-4.0",
  "authors": ["myusername"],
  "changelog": "Initial version"
}
```

## Map设计最佳实践

### 1. 地图大小选择

| 大小 | 推荐用途 | 难度 |
|-----|--------|------|
| 10x10 | 教程/快速试玩 | Easy |
| 20x20 | 标准游戏体验 | Easy-Medium |
| 30x40 | 长篇冒险 | Medium-Hard |
| 50x50+ | 史诗级探险 | Hard |

### 2. 难度平衡

**Easy (容易)**
- Pokemon 等级: 1-5
- Pokemon数量: 20-30% 元素
- 障碍物: 10% 元素
- 食物丰富

**Medium (中等)**
- Pokemon 等级: 5-15
- Pokemon数量: 35% 元素
- 障碍物: 20% 元素
- 适度食物

**Hard (困难)**
- Pokemon 等级: 15-30
- Pokemon数量: 45% 元素
- 障碍物: 25% 元素
- 有限食物

### 3. 内容多样性

- **Pokemon**: 使用5+ 种不同的Pokemon物种
- **食物**: 至少3种不同的食物类型
- **地形**: 混合多种地形 (草地40%, 森林30%, 水域20%, 山地10%)
- **特殊元素**: 添加NPC、宝箱、传送点等

## 评分系统详解

### 评分计算

```
总分 = 格式(20) + 平衡(30) + 多样(25) + 创意(15) + 文档(10)
```

### 评级等级

| 分数 | 等级 | 状态 | 操作 |
|------|------|------|------|
| 90-100 | S | ✅ 优秀 | 直接合并 |
| 70-89 | A | ✅ 良好 | 可能需要小改进 |
| 50-69 | B | ⚠️ 需要改进 | 建议修改后重新提交 |
| < 50 | C | ❌ 不符合要求 | 需要大幅修改 |

### 改进建议获取

```bash
# 查看详细的验证报告
./agentmonster map validate <map_id> --detailed

# 输出:
# ✅ 格式验证: 通过 (20/20分)
# ⚠️  平衡性检查: 需要改进 (18/30分)
#     - Pokemon数量过多 (60%, 建议30-50%)
#     - 食物不足 (15%, 建议20-30%)
# ⚠️  多样性检查: 可以改进 (20/25分)
#     - Pokemon类型过少 (只有2种, 建议3+种)
# ✅ 创意性: 好 (12/15分)
# ✅ 文档质量: 完美 (10/10分)
#
# 总评分: 80/100 - A级 (良好)
```

## 许可证和归属

### CC-BY-4.0 许可证

所有社区地图使用 CC-BY-4.0 许可证，意味着：

✅ **允许**
- 使用和修改地图
- 商业用途
- 分发和改编

⚠️ **要求**
- 必须给予原作者署名
- 使用相同许可证

### 版权归属

```
Map: My Awesome Map
Author: @username
License: CC-BY-4.0
URL: https://github.com/username/agent-monster/maps/my_awesome_map
```

## 常见问题 (FAQ)

**Q: 我可以修改已上传的Map吗?**
A: 是的! 提交新的PR，标题注明 "Update: Map名称"。

**Q: 如何处理Map版本冲突?**
A: 使用语义化版本 (1.0.0)。更新时递增版本号。

**Q: 我的Map被拒绝了怎么办?**
A: 查看评分报告，根据建议修改。可以多次重新提交。

**Q: 我可以删除我的Map吗?**
A: 联系维护者。但已有下载的Map版本会保留。

**Q: Map会被修改吗?**
A: 可能进行轻微调整。重大修改会先征求你的意见。

## API参考

### MapValidator API

```go
validator := NewMapValidator(logger)

// 验证地图
result := validator.ValidateMap(mapData, metadata)

if result.IsValid {
    fmt.Printf("Map质量评分: %d/100\n", result.Score)
} else {
    fmt.Println("验证失败:")
    for _, err := range result.Errors {
        fmt.Println(" -", err)
    }
}
```

### MapExporter API

```go
exporter := NewMapExporter(outputDir, github, logger)

// 导出map
localPath, repoPath, err := exporter.ExportMap(mapData, metadata)
if err != nil {
    log.Fatal(err)
}

fmt.Printf("导出成功: %s\n", localPath)
```

### MapMarketplace API

```go
marketplace := NewMapMarketplace(logger)

// 搜索地图
results := marketplace.SearchMaps("adventure")

// 按难度过滤
hardMaps := marketplace.FilterByDifficulty("hard")

// 获取热门地图
topMaps := marketplace.GetTopMaps(10)

// 查看统计
stats := marketplace.GetStatistics()
```

## 贡献者社区

感谢所有为 Agent Monster 社区做出贡献的创意者!

当你的第一个Map被接受时，你将获得：
- 🏆 **贡献者徽章** 在Profile中显示
- 📊 **Map统计** 追踪你的Map受欢迎程度
- 💬 **社区认可** 在项目中被列为贡献者

---

**开始创建你的第一个Map吧!** 🎮🗺️
