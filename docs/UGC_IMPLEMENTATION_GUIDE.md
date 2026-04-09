# Agent Monster UGC - 实现示例和指南

## 快速开始

### 1. 完整的Map创建和提交流程示例

```bash
#!/bin/bash

# 步骤 1: Fork主项目
gh repo fork chengjia2016/agent-monster
cd agent-monster

# 步骤 2: 创建新Map (在CLI中)
./agentmonster map create \
  --title "Crystal Cave Adventure" \
  --description "A mysterious cave filled with rare Pokemon and treasures" \
  --difficulty medium \
  --tags "cave,adventure,rare-pokemon" \
  --output-id crystal_cave_01

# 步骤 3: 验证Map质量
./agentmonster map validate crystal_cave_01 --detailed

# 输出示例:
# ✅ Format Validation: PASS (20/20)
# ⚠️  Balance Check: GOOD (28/30)
#     - Warning: Food slightly low (19%, suggested 20-30%)
# ✅ Diversity Check: EXCELLENT (25/25)
# ✅ Creativity: GOOD (13/15)
# ✅ Documentation: PERFECT (10/10)
# ➖➖➖➖➖➖➖➖➖➖➖
# TOTAL SCORE: 96/100 ⭐⭐⭐⭐⭐

# 步骤 4: 导出到你的Fork仓库
./agentmonster map export crystal_cave_01 \
  --target-repo https://github.com/your-username/agent-monster

# 步骤 5: 提交PR到主项目
gh pr create \
  --title "Map Submission: [Medium] Crystal Cave Adventure" \
  --body "User-generated map: Crystal Cave Adventure\n\nQuality Score: 96/100\nAuthor: @your-username"

# 步骤 6: 等待审查和合并
# 维护者会审查你的map并合并到主项目
```

## Python/Go 集成示例

### Go 集成示例

```go
package main

import (
	"agent-monster-cli/pkg/ugc"
	"log"
)

func main() {
	// 初始化日志
	logger := ugc.NewSimpleLogger(true)

	// 1. 创建validator
	validator := ugc.NewMapValidator(logger)

	// 模拟map数据
	mapData := map[string]interface{}{
		"version": "1.0",
		"width": 30,
		"height": 40,
		"elements": []map[string]interface{}{
			{
				"type": "wild_pokemon",
				"x": 10,
				"y": 15,
				"data": map[string]interface{}{
					"pokemon_name": "Pikachu",
					"level": 5,
				},
			},
			// ... more elements
		},
	}

	// 创建元数据
	metadata := ugc.MapMetadata{
		MapID:       "crystal_cave_01",
		OwnerID:     12345,
		OwnerName:   "john_doe",
		Title:       "Crystal Cave Adventure",
		Description: "A mysterious cave filled with rare Pokemon",
		Version:     "1.0.0",
		Difficulty:  "medium",
		Tags:        []string{"cave", "adventure", "rare-pokemon"},
	}

	// 2. 验证map
	result := validator.ValidateMap(mapData, metadata)
	validator.PrintResult(result)

	if result.IsValid && result.Score >= 70 {
		// 3. 创建exporter
		github := ugc.NewSimpleGitHubHelper(
			"your-github-token",
			"john_doe",
			"agent-monster",
			logger,
		)
		exporter := ugc.NewMapExporter(
			"./exports",
			github,
			logger,
		)

		// 4. 导出map
		localPath, repoPath, err := exporter.ExportMap(mapData, metadata)
		if err != nil {
			log.Fatalf("Export failed: %v", err)
		}

		log.Printf("Map exported successfully!")
		log.Printf("Local: %s", localPath)
		log.Printf("Repo:  %s", repoPath)

		// 5. 生成PR
		prGenerator := ugc.NewPRGenerator(
			"https://github.com/chengjia2016/agent-monster",
			github,
			validator,
			logger,
		)

		prInfo, err := prGenerator.GeneratePR(metadata, result.Score)
		if err != nil {
			log.Fatalf("PR generation failed: %v", err)
		}

		log.Printf("PR created: %s", prInfo.Title)
		log.Printf("Branch: %s", prInfo.Branch)
	}
}
```

## Map设计工作表

### Map规划模板

```
项目: ________________________
作者: ________________________
创建日期: ____________________

[ ] 基本信息
  - [ ] Map ID: _______________
  - [ ] 标题: ________________
  - [ ] 描述完整 (50-500字)
  - [ ] 难度选择: ☐Easy ☐Medium ☐Hard
  - [ ] 版本号: ______________

[ ] 地图规划
  - [ ] 宽度: _____ (建议: 20-40)
  - [ ] 高度: _____ (建议: 20-40)
  - [ ] 总元素数: _____ (建议: 50-200)

[ ] 元素平衡性
  - [ ] 野生Pokemon数: _____ (目标: 30-50%)
  - [ ] 食物数: _____ (目标: 20-30%)
  - [ ] 障碍物: _____ (目标: 15-25%)
  - [ ] 其他元素: _____ (目标: 5-10%)

[ ] 内容多样性
  - [ ] 不同Pokemon物种数: _____ (最少: 3)
  - [ ] 不同食物类型数: _____ (最少: 2)
  - [ ] 地形多样性:
      - [ ] 草地: ______%
      - [ ] 森林: ______%
      - [ ] 水域: ______%
      - [ ] 山地: ______%

[ ] 标签和分类
  - [ ] 标签1: _______________
  - [ ] 标签2: _______________
  - [ ] 标签3: _______________
  - [ ] 标签4: _______________
  - [ ] 标签5: _______________

[ ] 质量检查
  - [ ] 没有重复的元素ID
  - [ ] 所有坐标在范围内
  - [ ] 元素数据完整
  - [ ] 没有坏数据

[ ] 文档完整性
  - [ ] README.md已编写
  - [ ] 元数据JSON完整
  - [ ] 截图/预览已添加
  - [ ] 许可证声明已添加

```

## 社区地图示例

### 示例1: 初级训练地图

```json
{
  "metadata": {
    "map_id": "beginner_training_01",
    "title": "Beginner Training Grounds",
    "description": "Perfect for new trainers! A safe area to catch your first Pokemon and learn the basics.",
    "difficulty": "easy",
    "tags": ["beginner", "tutorial", "safe"],
    "version": "1.0.0"
  },
  "statistics": {
    "total_wild_pokemon": 15,
    "total_food": 12,
    "total_obstacles": 3,
    "total_elements": 30
  },
  "design_notes": {
    "pokemon_distribution": "40% (mostly common species)",
    "recommended_level": 1-5,
    "expected_playtime": "10-15 minutes"
  }
}
```

### 示例2: 高级探险地图

```json
{
  "metadata": {
    "map_id": "dragon_mountain_01",
    "title": "Dragon Mountain Peak",
    "description": "Challenging ascent to the summit. Face powerful Pokemon and collect rare items.",
    "difficulty": "hard",
    "tags": ["mountain", "legendary", "challenge", "dragons"],
    "version": "1.0.0"
  },
  "statistics": {
    "total_wild_pokemon": 45,
    "total_food": 18,
    "total_obstacles": 32,
    "total_elements": 95
  },
  "design_notes": {
    "pokemon_distribution": "47% (including rare species)",
    "recommended_level": 20-35,
    "expected_playtime": "45-60 minutes",
    "special_features": ["Rare Dragon-types", "Hidden treasure rooms", "Summit boss"]
  }
}
```

## 最佳实践

### DO ✅

1. **多样化Pokemon种类**
   - 使用5+种不同的Pokemon
   - 混合常见和稀有物种
   - 考虑类型平衡 (水、火、草等)

2. **创意性地图设计**
   - 使用不同的地形创造视觉多样性
   - 添加自然的流动和线路
   - 创建有趣的"热点"区域

3. **平衡的资源分配**
   - 确保食物足够但不过多
   - 战略性放置障碍物
   - 创建挑战但不会令人沮丧的路线

4. **清晰的文档**
   - 写详细的描述
   - 解释设计理念
   - 列出特殊特性

### DON'T ❌

1. **避免重复和单调**
   - ❌ 所有Pokemon都是同一物种
   - ❌ 整个地图都是同一地形
   - ❌ 没有变化的难度

2. **避免不平衡**
   - ❌ Pokemon数量过多 (>60%)
   - ❌ 食物过少 (<15%)
   - ❌ 障碍物阻挡大部分地图

3. **避免低质量**
   - ❌ 不完整的数据字段
   - ❌ 无效的坐标
   - ❌ 错误的JSON格式

4. **避免误导**
   - ❌ 难度标记错误
   - ❌ 过度夸大描述
   - ❌ 隐藏真实内容

## 审核清单

提交前检查:

```
[ ] 基本要求
  [ ] Map ID唯一且有效
  [ ] 标题不超过100字符
  [ ] 描述50-1000字
  [ ] 选择了正确的难度

[ ] 验证通过
  [ ] 格式验证通过
  [ ] 没有关键错误
  [ ] 评分 >= 70

[ ] 内容质量
  [ ] Pokemon多样化 (3+种)
  [ ] 食物多样化 (2+种)
  [ ] 地形多样化
  [ ] 布局有意思

[ ] 文档完整
  [ ] README完整
  [ ] 元数据正确
  [ ] 许可证声明
  [ ] 版本号正确

[ ] 最终检查
  [ ] 没有重复元素
  [ ] 所有坐标有效
  [ ] JSON格式正确
  [ ] 可以在游戏中加载
```

## 故障排除

### 常见问题

**Q: Map验证失败"Pokemon数量不平衡"**
A: 减少或增加wild_pokemon元素，确保占比在30-50%

**Q: "Food数量不足"警告**
A: 添加更多食物元素到地图，确保占比20-30%

**Q: 导出到GitHub失败**
A: 检查:
  - GitHub token有效
  - Fork仓库存在
  - 网络连接正常

**Q: PR自动生成但没有合并**
A: 维护者可能有改进建议，查看PR评论并调整

---

**祝你设计愉快!** 🎮✨
