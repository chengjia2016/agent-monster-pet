#!/usr/bin/env python3
"""
Test Enhanced Egg Incubator with GitHub Reputation Integration
测试基于 GitHub 声誉的增强蛋孵化系统
"""

import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from github_reputation_genes import (
    GitHubMetrics,
    ReputationGeneCalculator,
    HybridGeneCalculator,
)


def test_reputation_calculator():
    """测试声誉计算器"""
    print("\n" + "=" * 70)
    print("TEST 1: GitHub Reputation Calculator")
    print("=" * 70)
    
    calc = ReputationGeneCalculator()
    
    # Test Case 1: High-quality project (like TensorFlow)
    print("\n📊 Test Case 1: High-Quality Project (TensorFlow-like)")
    print("-" * 70)
    
    tf_metrics = GitHubMetrics(
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
    
    bonuses, analysis = calc.calculate_gene_bonus(tf_metrics)
    
    print(f"🧬 Gene Bonuses:")
    total = sum(bonuses.values())
    for gene_type, bonus in sorted(bonuses.items(), key=lambda x: -x[1]):
        bar = "█" * int(bonus * 50)
        print(f"   {gene_type:10}: {bonus:6.2%} {bar}")
    
    print(f"\n📈 Analysis:")
    for key, value in analysis.items():
        if key != "score":
            print(f"   {key:20}: {value}")
    
    print(f"\n📝 Reputation Summary:")
    print(calc.get_reputation_summary(tf_metrics))
    
    # Test Case 2: Medium project
    print("\n📊 Test Case 2: Medium Project")
    print("-" * 70)
    
    medium_metrics = GitHubMetrics(
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
    
    bonuses, analysis = calc.calculate_gene_bonus(medium_metrics)
    
    print(f"🧬 Gene Bonuses:")
    for gene_type, bonus in sorted(bonuses.items(), key=lambda x: -x[1]):
        bar = "█" * int(bonus * 50)
        print(f"   {gene_type:10}: {bonus:6.2%} {bar}")
    
    # Test Case 3: Fork project
    print("\n📊 Test Case 3: Fork Project (70% reputation)")
    print("-" * 70)
    
    fork_metrics = GitHubMetrics(
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
    
    bonuses, analysis = calc.calculate_gene_bonus(fork_metrics)
    
    print(f"🧬 Gene Bonuses (with Fork penalty):")
    for gene_type, bonus in sorted(bonuses.items(), key=lambda x: -x[1]):
        bar = "█" * int(bonus * 50)
        print(f"   {gene_type:10}: {bonus:6.2%} {bar}")
    
    print(f"   Note: Fork projects receive 70% of reputation bonus")


def test_gene_improvements():
    """测试基因属性改进"""
    print("\n" + "=" * 70)
    print("TEST 2: Gene Improvements (Attribute Bonuses)")
    print("=" * 70)
    
    calc = ReputationGeneCalculator()
    
    # Base stats
    base_stats = {
        "hp": 50,
        "attack": 50,
        "defense": 50,
        "speed": 50,
        "armor": 30,
        "quota": 100,
    }
    
    print(f"\n📌 Base Stats (without reputation):")
    for stat, value in base_stats.items():
        print(f"   {stat:10}: {value}")
    
    # High-quality project
    tf_metrics = GitHubMetrics(
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
    
    bonuses, _ = calc.calculate_gene_bonus(tf_metrics)
    improved_stats = calc.apply_gene_improvements(base_stats, bonuses)
    
    print(f"\n✨ Improved Stats (with TensorFlow-like reputation):")
    for stat in base_stats:
        base = base_stats[stat]
        improved = improved_stats[stat]
        bonus = improved - base
        print(f"   {stat:10}: {base} → {improved} (+{bonus})")


def test_hybrid_calculator():
    """测试混合基因计算器"""
    print("\n" + "=" * 70)
    print("TEST 3: Hybrid Gene Calculator (Commit + Reputation)")
    print("=" * 70)
    
    # Simulated commit genes
    commit_genes = {
        "logic": 0.4,
        "creative": 0.3,
        "speed": 0.3,
    }
    
    print(f"\n📝 Commit History Genes (60% weight):")
    for gene_type, weight in commit_genes.items():
        bar = "█" * int(weight * 40)
        print(f"   {gene_type:10}: {weight:6.2%} {bar}")
    
    # GitHub metrics
    github_metrics = GitHubMetrics(
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
    
    hybrid_calc = HybridGeneCalculator()
    hybrid_genes = hybrid_calc.calculate_hybrid_genes(commit_genes, github_metrics)
    
    print(f"\n🌟 GitHub Reputation Genes (40% weight):")
    rep_calc = ReputationGeneCalculator()
    rep_bonuses, _ = rep_calc.calculate_gene_bonus(github_metrics)
    for gene_type, weight in rep_bonuses.items():
        bar = "█" * int(weight * 40)
        print(f"   {gene_type:10}: {weight:6.2%} {bar}")
    
    print(f"\n🧬 Final Hybrid Genes (combined):")
    for gene_type, weight in hybrid_genes.items():
        bar = "█" * int(weight * 40)
        print(f"   {gene_type:10}: {weight:6.2%} {bar}")


def test_star_tiers():
    """测试星标等级"""
    print("\n" + "=" * 70)
    print("TEST 4: Star Tiers and Fork Tiers")
    print("=" * 70)
    
    calc = ReputationGeneCalculator()
    
    star_counts = [0, 5, 50, 150, 1000, 5000, 10000, 50000, 100000, 200000]
    
    print("\n⭐ Star Tiers:")
    for stars in star_counts:
        tier = calc._get_star_tier(stars)
        print(f"   {stars:>6} stars → {tier}")
    
    fork_counts = [0, 3, 8, 25, 100, 300, 500, 1000]
    
    print("\n🔀 Fork Tiers:")
    for forks in fork_counts:
        tier = calc._get_fork_tier(forks)
        print(f"   {forks:>4} forks → {tier}")


def test_community_health():
    """测试社区健康度评估"""
    print("\n" + "=" * 70)
    print("TEST 5: Community Health Assessment")
    print("=" * 70)
    
    calc = ReputationGeneCalculator()
    
    test_cases = [
        ("Active, Well-Maintained", GitHubMetrics(
            stars=1000, forks=200, watchers=300,
            open_issues=50, closed_issues=500,
            pull_requests=100, language="Python",
            is_fork=False, owner_followers=1000
        )),
        ("Low Activity", GitHubMetrics(
            stars=100, forks=20, watchers=30,
            open_issues=20, closed_issues=50,
            pull_requests=10, language="Python",
            is_fork=False, owner_followers=100
        )),
        ("Stalled Project", GitHubMetrics(
            stars=500, forks=50, watchers=100,
            open_issues=200, closed_issues=100,
            pull_requests=5, language="Python",
            is_fork=False, owner_followers=300
        )),
    ]
    
    for name, metrics in test_cases:
        health = calc._assess_community_health(metrics)
        total_issues = metrics.open_issues + metrics.closed_issues
        resolution_rate = metrics.closed_issues / total_issues if total_issues > 0 else 0
        
        print(f"\n📊 {name}")
        print(f"   Community Health: {health}")
        print(f"   Resolution Rate: {resolution_rate:.1%} ({metrics.closed_issues}/{total_issues})")


def main():
    """运行所有测试"""
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  Agent Monster - Enhanced Egg Incubator Test Suite  ".center(68) + "║")
    print("║" + "  GitHub Reputation Based Gene Inheritance".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "═" * 68 + "╝")
    
    try:
        test_reputation_calculator()
        test_gene_improvements()
        test_hybrid_calculator()
        test_star_tiers()
        test_community_health()
        
        print("\n" + "=" * 70)
        print("✅ All Tests Completed Successfully!")
        print("=" * 70 + "\n")
        
        return 0
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
