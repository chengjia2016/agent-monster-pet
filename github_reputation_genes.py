#!/usr/bin/env python3
"""
Agent Monster - GitHub Reputation Based Gene Calculator

根据项目在 GitHub 上的评价（Star、Fork、Issue、PR）计算和改进宠物基因
This module calculates gene bonuses based on project reputation metrics.

Star ⭐: 项目代码质量评价
Fork 🔀: 项目被采用和复用的程度
Followers: 开发者影响力
"""

import json
import math
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class GitHubMetrics:
    """GitHub 项目指标"""
    stars: int
    forks: int
    watchers: int
    open_issues: int
    closed_issues: int
    pull_requests: int
    language: str
    is_fork: bool
    owner_followers: int = 0
    
    def __post_init__(self):
        """数据验证"""
        self.stars = max(0, self.stars)
        self.forks = max(0, self.forks)
        self.watchers = max(0, self.watchers)
        self.open_issues = max(0, self.open_issues)
        self.closed_issues = max(0, self.closed_issues)
        self.pull_requests = max(0, self.pull_requests)
        self.owner_followers = max(0, self.owner_followers)


class ReputationGeneCalculator:
    """
    基于 GitHub 声誉的基因计算器
    
    基因三大类：
    - logic: 代码质量（Stars → 开发者认可）
    - creative: 社区参与（Issues/PRs → 社区关注）
    - speed: 生态影响（Forks → 实际应用）
    """
    
    # 基因权重配置
    GENE_WEIGHTS = {
        "logic": 0.5,      # 代码质量权重
        "creative": 0.25,  # 创意和社区权重
        "speed": 0.25,     # 生态影响权重
    }
    
    # 星标评级阈值 (基于知名度)
    STAR_TIERS = {
        "legendary": 5000,   # 传奇 (Django, TensorFlow 级别)
        "epic": 1000,        # 史诗 (知名项目)
        "rare": 100,         # 稀有 (受欢迎项目)
        "uncommon": 10,      # 不常见 (一般项目)
        "common": 1,         # 普通 (小项目)
    }
    
    # Fork 评级阈值 (基于被采用程度)
    FORK_TIERS = {
        "dominant": 500,     # 主导级 (被大量分支)
        "strong": 100,       # 强大 (被广泛采用)
        "moderate": 20,      # 中等 (中等采用)
        "light": 5,          # 轻度 (少量采用)
        "none": 0,          # 无
    }
    
    # 最多可应用的项目质量倍数
    MAX_QUALITY_MULTIPLIER = 3.0
    
    # 基因属性改进配置
    GENE_IMPROVEMENTS = {
        "logic": {
            "hp": 5,          # 逻辑基因→健康度
            "attack": 8,      # 逻辑基因→攻击力
            "defense": 10,    # 逻辑基因→防御力
            "speed": 3,
            "armor": 2,
            "quota": 5,
        },
        "creative": {
            "hp": 3,
            "attack": 5,
            "defense": 3,
            "speed": 8,       # 创意基因→速度
            "armor": 10,      # 创意基因→护甲
            "quota": 15,      # 创意基因→配额
        },
        "speed": {
            "hp": 2,
            "attack": 12,     # 速度基因→攻击力
            "defense": 2,
            "speed": 15,      # 速度基因→速度
            "armor": 5,
            "quota": 8,
        },
    }
    
    def __init__(self):
        pass
    
    def calculate_gene_bonus(self, metrics: GitHubMetrics) -> Tuple[Dict[str, float], Dict[str, str]]:
        """
        计算基于项目声誉的基因加成
        
        返回：
        - gene_bonuses: 基因权重加成 {gene_type: bonus_weight}
        - reputation_analysis: 声誉分析说明
        """
        
        # 计算各个维度的评分
        logic_score = self._calculate_logic_score(metrics)  # 代码质量
        creative_score = self._calculate_creative_score(metrics)  # 社区参与
        speed_score = self._calculate_speed_score(metrics)  # 生态影响
        
        # 标准化评分 (0-1)
        total_score = logic_score + creative_score + speed_score
        if total_score == 0:
            total_score = 1
        
        gene_bonuses = {
            "logic": logic_score / total_score * 0.5,
            "creative": creative_score / total_score * 0.25,
            "speed": speed_score / total_score * 0.25,
        }
        
        # 生成分析说明
        reputation_analysis = self._generate_analysis(metrics, logic_score, creative_score, speed_score)
        
        return gene_bonuses, reputation_analysis
    
    def _calculate_logic_score(self, metrics: GitHubMetrics) -> float:
        """
        计算逻辑基因评分（代码质量）
        基于：Stars（开发者认可度）
        """
        # 对数转换 Stars
        if metrics.stars == 0:
            stars_score = 0
        else:
            stars_score = math.log(metrics.stars + 1) / math.log(10)  # log10 scale
            stars_score = min(stars_score, 5)  # Cap at 5
        
        # Issue 质量指标 (解决率)
        total_issues = metrics.open_issues + metrics.closed_issues
        if total_issues == 0:
            issue_health = 0.5
        else:
            resolution_rate = metrics.closed_issues / total_issues
            issue_health = min(resolution_rate * 1.5, 1.0)
        
        logic_score = (stars_score * 0.7 + issue_health * 3.0)
        return logic_score
    
    def _calculate_creative_score(self, metrics: GitHubMetrics) -> float:
        """
        计算创意基因评分（社区参与）
        基于：PR 活动、Issues、Community Engagement
        """
        # PR 活动指标
        total_pr = metrics.pull_requests
        if total_pr == 0:
            pr_score = 0
        else:
            pr_score = math.log(total_pr + 1) / math.log(10) * 2
            pr_score = min(pr_score, 3.0)
        
        # Issues 指标（高活动=社区参与）
        total_issues = metrics.open_issues + metrics.closed_issues
        if total_issues == 0:
            issue_engagement = 0
        else:
            issue_engagement = math.log(total_issues + 1) / math.log(10)
        
        # Watchers 指标
        watchers_score = math.log(metrics.watchers + 1) / math.log(10) * 0.5
        
        creative_score = (pr_score * 0.4 + issue_engagement * 0.4 + watchers_score * 0.2)
        return creative_score
    
    def _calculate_speed_score(self, metrics: GitHubMetrics) -> float:
        """
        计算速度基因评分（生态影响）
        基于：Forks（被采用程度）和 Owner Followers（开发者影响力）
        """
        # Fork 评分（对数转换）
        if metrics.forks == 0:
            fork_score = 0
        else:
            fork_score = math.log(metrics.forks + 1) / math.log(10) * 2
            fork_score = min(fork_score, 4.0)
        
        # Owner followers 评分（开发者影响力）
        if metrics.owner_followers == 0:
            follower_score = 0
        else:
            follower_score = math.log(metrics.owner_followers + 1) / math.log(10) * 0.5
            follower_score = min(follower_score, 2.0)
        
        # Fork 倍数 (如果是 fork 项目，评分降低)
        fork_penalty = 1.0
        if metrics.is_fork:
            fork_penalty = 0.7  # Fork 项目获得 70% 的评分
        
        speed_score = (fork_score * 0.7 + follower_score * 0.3) * fork_penalty
        return speed_score
    
    def _generate_analysis(self, metrics: GitHubMetrics, logic: float, creative: float, speed: float) -> Dict[str, str]:
        """生成声誉分析"""
        analysis = {
            "stars_tier": self._get_star_tier(metrics.stars),
            "fork_tier": self._get_fork_tier(metrics.forks),
            "logic_score": f"{logic:.2f}",
            "creative_score": f"{creative:.2f}",
            "speed_score": f"{speed:.2f}",
            "project_type": "Fork" if metrics.is_fork else "Original",
            "community_health": self._assess_community_health(metrics),
        }
        return analysis
    
    def _get_star_tier(self, stars: int) -> str:
        """根据 Stars 获取项目等级"""
        for tier, threshold in sorted(self.STAR_TIERS.items(), key=lambda x: -x[1]):
            if stars >= threshold:
                return tier.upper()
        return "COMMON"
    
    def _get_fork_tier(self, forks: int) -> str:
        """根据 Forks 获取采用等级"""
        for tier, threshold in sorted(self.FORK_TIERS.items(), key=lambda x: -x[1]):
            if forks >= threshold:
                return tier.upper()
        return "NONE"
    
    def _assess_community_health(self, metrics: GitHubMetrics) -> str:
        """评估社区健康度"""
        total_issues = metrics.open_issues + metrics.closed_issues
        if total_issues == 0:
            return "INACTIVE"
        
        resolution_rate = metrics.closed_issues / total_issues
        if resolution_rate >= 0.8:
            return "EXCELLENT"
        elif resolution_rate >= 0.6:
            return "GOOD"
        elif resolution_rate >= 0.4:
            return "FAIR"
        else:
            return "POOR"
    
    def apply_gene_improvements(self, base_stats: Dict[str, int], gene_bonuses: Dict[str, float]) -> Dict[str, int]:
        """
        应用基因加成到基础属性
        
        参数：
        - base_stats: 基础属性字典 {stat_name: value}
        - gene_bonuses: 基因加成 {gene_type: bonus_weight}
        
        返回：
        - 改进后的属性字典
        """
        improved_stats = base_stats.copy()
        
        for gene_type, bonus_weight in gene_bonuses.items():
            if bonus_weight == 0:
                continue
            
            improvements = self.GENE_IMPROVEMENTS.get(gene_type, {})
            for stat_name, improvement_value in improvements.items():
                if stat_name in improved_stats:
                    # 应用改进（基于基因权重）
                    bonus = improvement_value * bonus_weight
                    improved_stats[stat_name] = int(improved_stats[stat_name] + bonus)
        
        return improved_stats
    
    def get_reputation_summary(self, metrics: GitHubMetrics) -> str:
        """生成项目声誉总结"""
        star_tier = self._get_star_tier(metrics.stars)
        fork_tier = self._get_fork_tier(metrics.forks)
        community = self._assess_community_health(metrics)
        
        summary = f"""
🏆 Project Reputation Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⭐ Code Quality (Stars): {star_tier} ({metrics.stars} stars)
🔀 Ecosystem Impact (Forks): {fork_tier} ({metrics.forks} forks)
👥 Community Health: {community}
📊 Watchers: {metrics.watchers}
🐛 Issues: {metrics.closed_issues} resolved / {metrics.open_issues} open
🔄 PRs: {metrics.pull_requests}
"""
        if metrics.is_fork:
            summary += "📌 Note: This is a fork project (70% reputation bonus)\n"
        
        summary += f"👤 Owner Followers: {metrics.owner_followers}\n"
        
        return summary


class HybridGeneCalculator:
    """混合基因计算器：结合提交历史和 GitHub 声誉"""
    
    def __init__(self):
        self.reputation_calc = ReputationGeneCalculator()
    
    def calculate_hybrid_genes(self, commit_genes: Dict[str, float], 
                              github_metrics: GitHubMetrics) -> Dict[str, float]:
        """
        结合提交历史基因和 GitHub 声誉计算混合基因
        
        参数：
        - commit_genes: 从提交历史计算的基因权重
        - github_metrics: GitHub 项目指标
        
        返回：
        - 混合基因权重
        """
        repo_bonuses, _ = self.reputation_calc.calculate_gene_bonus(github_metrics)
        
        # 加权混合
        commit_weight = 0.6  # 提交历史权重 60%
        reputation_weight = 0.4  # GitHub 声誉权重 40%
        
        hybrid_genes = {}
        for gene_type in ["logic", "creative", "speed"]:
            commit_val = commit_genes.get(gene_type, 0)
            repo_val = repo_bonuses.get(gene_type, 0)
            hybrid_genes[gene_type] = (commit_val * commit_weight + 
                                       repo_val * reputation_weight)
        
        # 正规化
        total = sum(hybrid_genes.values())
        if total > 0:
            hybrid_genes = {k: v / total for k, v in hybrid_genes.items()}
        
        return hybrid_genes


def demo():
    """演示基因计算"""
    
    # 示例 1: 高质量项目 (如 TensorFlow)
    tensorflow_metrics = GitHubMetrics(
        stars=185000,
        forks=42000,
        watchers=8200,
        open_issues=1500,
        closed_issues=8500,
        pull_requests=5000,
        language="Python",
        is_fork=False,
        owner_followers=15000
    )
    
    # 示例 2: 中等项目
    medium_project = GitHubMetrics(
        stars=500,
        forks=80,
        watchers=150,
        open_issues=30,
        closed_issues=200,
        pull_requests=50,
        language="Go",
        is_fork=False,
        owner_followers=500
    )
    
    # 示例 3: Fork 项目
    fork_project = GitHubMetrics(
        stars=250,
        forks=45,
        watchers=80,
        open_issues=5,
        closed_issues=30,
        pull_requests=20,
        language="Rust",
        is_fork=True,
        owner_followers=200
    )
    
    calc = ReputationGeneCalculator()
    
    print("=" * 60)
    print("Agent Monster - Gene Reputation Calculator Demo")
    print("=" * 60)
    
    for name, metrics in [("TensorFlow-like", tensorflow_metrics),
                          ("Medium Project", medium_project),
                          ("Fork Project", fork_project)]:
        print(f"\n📌 {name}")
        print(calc.get_reputation_summary(metrics))
        
        bonuses, analysis = calc.calculate_gene_bonus(metrics)
        print("Gene Bonuses:")
        for gene_type, bonus in bonuses.items():
            print(f"  {gene_type}: {bonus:.2%}")
        
        print("\nReputation Analysis:")
        for key, value in analysis.items():
            print(f"  {key}: {value}")


if __name__ == "__main__":
    demo()
