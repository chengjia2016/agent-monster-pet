# 🧬 Enhanced Egg Incubator - GitHub Reputation Gene Inheritance

## 概述

Agent Monster 的增强版蛋孵化系统结合了两个核心数据源来生成更强大的宠物：

1. **提交历史分析** (60% 权重) - 基于 Git 提交中的语言分布
2. **GitHub 声誉指标** (40% 权重) - 基于项目在 GitHub 上的评价

这种混合方法允许开发者通过以下方式获得更好的基因：
- ⭐ 拥有高星标的优质项目
- 🔀 Fork 流行的其他项目
- 📈 维护活跃的项目（好的 Issue 解决率）
- 👥 建立个人影响力（followers）

---

## 🌟 三大基因类型

### Logic Gene（逻辑基因）🧠
**衡量**: 代码质量与复杂度
- **提交源**: Go, Rust, Python, Java, C++, C, TypeScript, JavaScript 等
- **GitHub 源**: Stars（开发者认可度）+ Issue 解决率
- **属性加成**: HP、Attack、Defense

### Creative Gene（创意基因）🎨
**衡量**: 社区参与与创意表达
- **提交源**: 文档、样式表、HTML、Vue、JSX、TSX
- **GitHub 源**: PR 活动、Issues 参与、Watchers
- **属性加成**: Speed、Armor、Quota

### Speed Gene（速度基因）⚡
**衡量**: 生态影响力与实际应用
- **提交源**: Shell 脚本、配置文件、API、SQL
- **GitHub 源**: Forks（被采用程度）+ Owner Followers
- **属性加成**: Attack、Speed

---

## 📊 GitHub 声誉评分系统

### Star 等级 (代码质量)

| 等级 | Stars | 描述 | 示例项目 |
|------|-------|------|--------|
| 🔴 LEGENDARY | 5,000+ | 传奇级项目 | TensorFlow, PyTorch, Django |
| 🟠 EPIC | 1,000-4,999 | 史诗级项目 | 知名开源项目 |
| 🟡 RARE | 100-999 | 稀有项目 | 受欢迎的中型项目 |
| 🟢 UNCOMMON | 10-99 | 不常见项目 | 一般质量项目 |
| ⚪ COMMON | 1-9 | 普通项目 | 小型个人项目 |

### Fork 等级 (生态影响)

| 等级 | Forks | 描述 |
|------|-------|------|
| 🟢 DOMINANT | 500+ | 主导级 - 被大量分支和扩展 |
| 🟡 STRONG | 100-499 | 强大 - 被广泛采用 |
| 🟡 MODERATE | 20-99 | 中等 - 中等采用 |
| ⚪ LIGHT | 5-19 | 轻度 - 少量采用 |
| ⚫ NONE | 0-4 | 无分支 |

### 社区健康度评估

| 等级 | Issue 解决率 | 描述 |
|------|------------|------|
| 🟢 EXCELLENT | ≥80% | 活跃维护 |
| 🟡 GOOD | 60-79% | 良好维护 |
| 🟠 FAIR | 40-59% | 中等维护 |
| 🔴 POOR | <40% | 维护不足 |

---

## 🧬 基因计算示例

### 例子 1: 高质量项目 (TensorFlow-like)

**项目指标:**
- Stars: 185,000 (LEGENDARY)
- Forks: 42,000 (DOMINANT)
- Issues: 8,500 已解决 / 1,500 开放 (85% 解决率)
- PRs: 5,000
- Owner Followers: 15,000

**计算结果:**
```
Logic Gene (逻辑): 24.83%    ████████████████████████
Creative Gene:     6.09%    ██████
Speed Gene:        6.49%    ███████
```

**属性加成** (相比基础属性):
```
HP:       +1   (51)
Attack:   +1   (51)
Defense:  +2   (52)
Speed:    +0   (50)
Armor:    +0   (30)
Quota:    +1   (101)
```

### 例子 2: 中等项目

**项目指标:**
- Stars: 500 (RARE)
- Forks: 80 (MODERATE)
- Issues: 200 已解决 / 30 开放 (87% 解决率)

**计算结果:**
```
Logic Gene:       23.67%
Creative Gene:    5.72%
Speed Gene:       7.45%
```

### 例子 3: Fork 项目 (70% 声誉加成)

**项目指标:**
- 是 Fork: ✓ (70% 加成)
- Stars: 250
- Forks: 45

**计算结果:**
```
Logic Gene:       27.78%    (略高于原始权重)
Creative Gene:    5.55%
Speed Gene:       5.55%
Note: Fork 项目会被适当降低评分，但不失有效性
```

---

## 🎯 如何获得更好的基因

### 策略 1: 提升自己的项目质量

**增加 Stars:**
- 写优质代码
- 发布到 Product Hunt、Hacker News
- 改进 README 和文档
- 维护活跃的社区

**增加 Forks:**
- 设计可扩展的架构
- 提供良好的扩展点
- 创建示例和教程
- 响应用户需求

**改进社区健康度:**
- 及时关闭已解决的 Issues
- 与贡献者互动
- 维护良好的 PR 响应时间

### 策略 2: Fork 流行项目

**选择高质量项目:**
- Fork TensorFlow, PyTorch 等知名项目 (+40-50% 属性加成)
- Fork 你关注的成熟项目
- 虽然分数会降低到 70%，但仍能获得显著加成

**示例:**
```
Fork TensorFlow (185,000 stars, 42,000 forks)
→ 获得 185k × 0.7 ≈ 129.5k "有效星标"
→ 相比小项目有显著优势
```

### 策略 3: 建立个人影响力

**增加 Followers:**
- 发布高质量的工具和库
- 参与开源社区
- 写技术博客
- 在会议上演讲

**Owner followers 的影响:**
- 影响 Speed Gene 计算
- 体现开发者的整体影响力

---

## 📈 混合基因计算流程

```
┌─────────────────────────────────────────────────────┐
│        提交历史分析 (60% 权重)                      │
│                                                       │
│  分析 Git 提交中的语言分布                          │
│  → Logic: 40%  Creative: 30%  Speed: 30%           │
└─────────────────────────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────┐
│        GitHub 声誉评分 (40% 权重)                   │
│                                                       │
│  计算 Stars、Forks、Issues、PRs                   │
│  → Logic: 24%  Creative: 6%  Speed: 7%            │
└─────────────────────────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────┐
│           混合计算 (Normalization)                  │
│                                                       │
│  最终基因 = Commit × 0.6 + GitHub × 0.4           │
│  → Logic: 45%  Creative: 27%  Speed: 27%          │
└─────────────────────────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────┐
│           应用属性加成                              │
│                                                       │
│  基于最终基因权重改进宠物属性                       │
│  HP+、Attack+、Defense+ 等                        │
└─────────────────────────────────────────────────────┘
```

---

## 🔄 向后兼容性

**如果无法获取 GitHub 数据:**
- 系统自动回退到纯提交历史模式
- 宠物仍然会正常孵化，但使用 60% 的权重
- `inheritance_method` 字段会标记为 "commit_history_only"

---

## 🛠️ 使用新的孵化系统

### 方式 1: 使用增强孵化器

```bash
python3 enhanced_egg_incubator.py
```

**需要:**
- Git 仓库
- 可选: `GITHUB_TOKEN` 环境变量 (用于 API 速率限制)

**输出:**
- `.monster/pet.soul` 文件
- 包含完整的基因和声誉信息

### 方式 2: 编程接口

```python
from github_reputation_genes import GitHubMetrics, ReputationGeneCalculator

# 创建项目指标
metrics = GitHubMetrics(
    stars=5000,
    forks=800,
    watchers=500,
    open_issues=100,
    closed_issues=500,
    pull_requests=300,
    language="Python",
    is_fork=False,
    owner_followers=2000
)

# 计算基因加成
calc = ReputationGeneCalculator()
bonuses, analysis = calc.calculate_gene_bonus(metrics)

# 应用属性改进
base_stats = {"hp": 50, "attack": 50, ...}
improved_stats = calc.apply_gene_improvements(base_stats, bonuses)
```

---

## 📊 测试验证

运行完整的测试套件:

```bash
python3 test_enhanced_incubator.py
```

**测试覆盖:**
1. ✅ GitHub 声誉计算器
2. ✅ 基因属性改进
3. ✅ 混合基因计算
4. ✅ Star/Fork 等级分类
5. ✅ 社区健康度评估

所有测试均通过 ✅

---

## 🎮 游戏平衡考虑

### 等级平衡

| 项目类型 | 属性加成 | 基因权重变化 | 竞争力 |
|---------|--------|-----------|-------|
| LEGENDARY | +++++ | +30-40% | 最强 |
| EPIC | ++++ | +20-30% | 强 |
| RARE | +++ | +15-20% | 中上 |
| UNCOMMON | ++ | +5-15% | 中 |
| COMMON | + | +0-5% | 基础 |
| Fork(70%) | ++ | +5-25% | 中 |

### 设计目标

1. **鼓励质量** - 高星标项目获得显著加成
2. **激励多样性** - Fork 项目也有合理奖励
3. **奖励投入** - Issue 解决率影响评分
4. **尊重规模** - 使用对数尺度避免过度差异

---

## 📝 相关文件

- `github_reputation_genes.py` - 核心算法实现
- `enhanced_egg_incubator.py` - 增强版孵化器
- `test_enhanced_incubator.py` - 完整测试套件
- `.monster/pet.soul` - 生成的宠物数据

---

## 🚀 未来改进

计划中的增强：

- [ ] 多仓库基因融合 (跨项目继承)
- [ ] 时间加权评分 (最近活动权重更高)
- [ ] 贡献者基因继承 (多人项目)
- [ ] 实时评分更新 (定期刷新 GitHub 数据)
- [ ] 基因突变系统 (特殊事件触发)

---

**版本**: 2.0 (Enhanced with GitHub Reputation)
**最后更新**: 2026-04-07
**维护者**: Agent Monster Team
