# Agent Monster UGC System - 完整架构设计

## 系统架构概览

```
┌─────────────────────────────────────────────────────────────────┐
│                    User Interaction Layer                       │
│  (CLI Commands, Web Interface, Mobile App - Future)            │
└────────────┬────────────────────────────────────────────────────┘
             │
┌────────────┴────────────────────────────────────────────────────┐
│                  UGC System Core Modules                        │
├──────────────┬──────────────┬──────────────┬────────────────────┤
│ Map Creator  │  Validator   │  Exporter    │ Marketplace        │
│ (在线编辑)    │  (质量检查)   │ (导出到repo) │ (社区浏览)          │
└──────────────┴──────────────┴──────────────┴────────────────────┘
             │
┌────────────┴────────────────────────────────────────────────────┐
│                 Integration Services Layer                      │
├──────────────┬──────────────┬──────────────┬────────────────────┤
│  GitHub API  │  Version Mgmt│  Notification│ Analytics          │
│  (Fork/PR)   │  (Versioning)│ (Updates)    │ (Stats/Ratings)    │
└──────────────┴──────────────┴──────────────┴────────────────────┘
             │
┌────────────┴────────────────────────────────────────────────────┐
│                      Data Layer                                 │
├──────────────┬──────────────┬──────────────┬────────────────────┤
│  Map JSON    │  Metadata DB │  User Data   │ Community Ratings  │
│  (Storage)   │  (Index)     │  (Profiles)  │ (Leaderboards)     │
└──────────────┴──────────────┴──────────────┴────────────────────┘
```

## 核心模块详解

### 1️⃣ MapValidator (map_validator.go)

**职责**: 验证和评分用户提交的Map

**功能**:
- 格式验证 (20分)
- 平衡性检查 (30分)
- 多样性检查 (25分)
- 创意性评估 (15分)
- 文档质量检查 (10分)

**输出**: ValidationResult (是否有效 + 评分)

### 2️⃣ MapExporter (map_exporter.go)

**职责**: 将验证通过的Map导出到用户GitHub仓库

**功能**:
- 本地导出为JSON
- 推送到用户Fork仓库
- 生成README文档
- 保存元数据

**输出**: 导出路径 + 仓库路径

### 3️⃣ PRGenerator (pr_generator.go)

**职责**: 自动生成并提交PR到主项目

**功能**:
- 构建PR标题和描述
- 生成分支名
- 创建GitHub PR
- 生成提交指南

**输出**: PR URL + 提交指南

### 4️⃣ MapMarketplace (map_marketplace.go)

**职责**: 社区地图市场和浏览功能

**功能**:
- 注册和更新Map
- 搜索和过滤
- 按难度/标签分类
- 评分和下载统计
- 市场分析

**输出**: Map列表 + 统计信息

### 5️⃣ 接口层 (interfaces.go)

**职责**: 定义抽象接口和基础实现

**接口**:
- Logger - 日志接口
- GitHubHelper - GitHub操作接口

**实现**:
- SimpleLogger
- SimpleGitHubHelper

## 数据流转

### Map创建到上线的完整流程

```
User Fork Main Repo
         │
         ▼
Create Local Map (CLI)
         │
         ▼
Validate Map
   ├─ Pass? ✅ → Continue
   └─ Fail? ❌ → Show errors & suggest improvements
         │
         ▼
Export to Fork Repo
   ├─ Save locally
   └─ Push to GitHub
         │
         ▼
Generate PR
   ├─ Build title & description
   ├─ Create GitHub PR
   └─ Notify user
         │
         ▼
Maintainer Review
   ├─ Approve ✅ → Merge to main
   ├─ Request changes ⚠️ → User updates
   └─ Reject ❌ → Provide feedback
         │
         ▼
Map Added to Community Marketplace
         │
         ▼
Users Browse, Download & Play
```

## 文件结构

```
agent-monster/
├── cli/pkg/ugc/                    # UGC System Package
│   ├── interfaces.go               # Logger & GitHubHelper interfaces
│   ├── map_validator.go            # Map validation & scoring
│   ├── map_exporter.go             # Export to GitHub
│   ├── pr_generator.go             # PR generation & submission
│   ├── map_marketplace.go          # Community marketplace
│   └── ugc_manager.go              # Overall orchestration (TODO)
│
├── docs/
│   ├── UGC_GUIDE.md               # Complete UGC system guide
│   └── UGC_IMPLEMENTATION_GUIDE.md # Implementation examples
│
├── maps/
│   ├── 001.json                   # Example maps
│   ├── 002.json
│   ├── exports/                   # Exported maps
│   │   └── username_map_id_timestamp.json
│   └── samples/                   # Sample community maps (TODO)
│       └── beginner_training.json
│
└── cli/cmd/
    └── agentmonster/              # Main CLI entry point
        └── map_commands.go        # Map CLI commands (TODO)
```

## API 概览

### MapValidator API

```go
type ValidationResult struct {
    IsValid  bool          // 是否通过验证
    Errors   []string      // 错误列表
    Warnings []string      // 警告列表
    Score    int           // 0-100评分
}

func (mv *MapValidator) ValidateMap(mapData interface{}, metadata MapMetadata) *ValidationResult
func (mv *MapValidator) PrintResult(result *ValidationResult)
```

### MapExporter API

```go
type MapExportPackage struct {
    Metadata MapMetadata   // 元数据
    MapData  interface{}   // Map数据
    License  string        // 许可证
    Authors  []string      // 作者列表
    Changelog string       // 更新日志
}

func (me *MapExporter) ExportMap(mapData interface{}, metadata MapMetadata) (string, string, error)
func (me *MapExporter) ListExportedMaps() ([]string, error)
```

### PRGenerator API

```go
type PullRequestInfo struct {
    Title           string
    Description     string
    Branch          string
    MapID           string
    ValidationScore int
}

func (pg *PRGenerator) GeneratePR(metadata MapMetadata, validationScore int) (*PullRequestInfo, error)
func (pg *PRGenerator) SubmitPR(prInfo *PullRequestInfo) (string, error)
```

### MapMarketplace API

```go
type MapListing struct {
    MapID       string
    Title       string
    Difficulty  string
    Rating      float64
    Downloads   int
    Tags        []string
}

func (mm *MapMarketplace) RegisterMap(listing *MapListing) error
func (mm *MapMarketplace) SearchMaps(query string) []*MapListing
func (mm *MapMarketplace) FilterByDifficulty(difficulty string) []*MapListing
func (mm *MapMarketplace) GetTopMaps(count int) []*MapListing
```

## 集成点

### 与现有系统的集成

```
现有系统              →  UGC系统
────────────────────────────────────
Map生成器             →  MapValidator
GitHub OAuth          →  GitHubHelper
API Server            →  MapMarketplace (Registry)
User Profile          →  Marketplace (Author Info)
Rating System         →  Marketplace (Ratings/Reviews)
Notification System   →  PR Generator (Notifications)
```

## 配置和扩展

### 验证评分权重配置

```go
// 可配置的评分权重
type ValidationConfig struct {
    FormatWeight      int = 20  // 格式验证
    BalanceWeight     int = 30  // 平衡性
    DiversityWeight   int = 25  // 多样性
    CreativityWeight  int = 15  // 创意性
    DocumentationWeight int = 10 // 文档
}
```

### Marketplace配置

```go
type MarketplaceConfig struct {
    MaxMapsPerUser    int = 100
    ApprovalRequired  bool = true
    AutoPublish       bool = false
    RatingSystem      string = "5-star"
    ArchiveOldVersions bool = true
}
```

## 后续改进计划

### Phase 2: 高级功能

- [ ] Web-based Map Editor (可视化编辑)
- [ ] Version Control & Rollback (版本回滚)
- [ ] Collaborative Editing (协作编辑)
- [ ] Fork & Remix (衍生和混搭)
- [ ] Community Reviews & Comments (社区评论)

### Phase 3: 社区功能

- [ ] Creator Leaderboards (创作者排行)
- [ ] Map Collections & Playlists (合集/播放列表)
- [ ] Trending Maps (热门地图)
- [ ] Creator Profiles & Portfolio (创作者档案)
- [ ] Community Events & Contests (社区活动和竞赛)

### Phase 4: 高级分析

- [ ] Map Statistics & Analytics (Map统计分析)
- [ ] Player Behavior Analysis (玩家行为分析)
- [ ] Difficulty Metrics (难度指标)
- [ ] Engagement Tracking (参与度追踪)
- [ ] Recommendation Engine (推荐引擎)

## 许可和贡献

所有社区提交的Map使用 **CC-BY-4.0** 许可证:

```
Attribution 4.0 International (CC BY 4.0)
- 允许商业和非商业使用
- 允许修改和衍生
- 要求署名原作者
- 使用相同许可证
```

## 社区治理

### 审核政策

1. **自动验证** - 格式和平衡性检查
2. **社区投票** - 用户可以对Map评分
3. **维护者审核** - 最终批准权在维护者
4. **定期清理** - 删除低质量或违反规则的Map

### 贡献奖励

```
✅ 第一个被接受的Map  → 🏆 Contributor Badge
✨ 100+下载          → ⭐ Featured Badge
🌟 3.5+ 平均评分      → 🎖️ Quality Creator Badge
🏅 10个Map被接受      → 👑 Elite Creator Badge
```

---

## 总结

Agent Monster UGC系统将游戏转变为**社区创意平台**：

```
单个游戏 → 社区创意生态系统
User Owned Content → Democratic Content Approval
Developer-only → Community Empowered
Limited Content → Infinite Possibilities
```

这个系统使任何玩家都可以：
1. 🎨 **创作** 自己的Map
2. ✅ **验证** 质量标准
3. 📤 **分享** 到社区
4. 🌟 **获得** 认可和奖励
5. 💡 **激发** 其他创作者

---

**让Agent Monster成为每个玩家的创意舞台!** 🎮✨
