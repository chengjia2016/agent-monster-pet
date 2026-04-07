#!/usr/bin/env python3
"""
Agent Monster - Enhanced Egg Incubator (Phase 2+)
结合 Git 提交历史和 GitHub 声誉的蛋孵化器
Combines commit history analysis and GitHub reputation for superior gene inheritance
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timedelta
from collections import defaultdict
from pathlib import Path
from typing import Dict, Optional, Tuple

# Import our reputation calculator
try:
    from github_reputation_genes import (
        GitHubMetrics, 
        ReputationGeneCalculator, 
        HybridGeneCalculator
    )
except ImportError:
    print("Warning: Could not import github_reputation_genes module")
    GitHubMetrics = None
    ReputationGeneCalculator = None
    HybridGeneCalculator = None

# 项目根目录
PROJECT_ROOT = Path(__file__).parent
MONSTER_DIR = PROJECT_ROOT / ".monster"
SOUL_FILE = MONSTER_DIR / "pet.soul"

# 基因类型定义
GENE_TYPES = {
    "logic": ["go", "rs", "py", "java", "cpp", "c", "ts", "js"],  # 代码行/复杂算法
    "creative": ["md", "css", "html", "scss", "vue", "jsx", "tsx"],  # 文档/注释/UI
    "speed": ["sh", "yml", "yaml", "json", "toml", "sql"],  # 脚本/配置/API
}

# 语言到基因类型的映射
LANGUAGE_GENE_MAP = {}
for gene_type, langs in GENE_TYPES.items():
    for lang in langs:
        LANGUAGE_GENE_MAP[lang] = gene_type


def get_git_config(key):
    """获取 git 配置"""
    try:
        result = subprocess.run(
            ["git", "config", "--get", key], capture_output=True, text=True, timeout=5
        )
        return result.stdout.strip() or None
    except Exception:
        return None


def get_commit_history(hours=72, limit=50):
    """获取最近 N 小时的提交历史"""
    try:
        since = (datetime.now() - timedelta(hours=hours)).strftime("%Y-%m-%d")
        result = subprocess.run(
            [
                "git",
                "log",
                f"--since={since}",
                f"-n{limit}",
                "--pretty=format:%H|%an|%ae|%at|%s",
                "--",
            ],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=PROJECT_ROOT,
        )
        if result.returncode != 0:
            return []

        commits = []
        for line in result.stdout.strip().split("\n"):
            if not line:
                continue
            parts = line.split("|")
            if len(parts) >= 5:
                commits.append(
                    {
                        "hash": parts[0],
                        "author": parts[1],
                        "email": parts[2],
                        "timestamp": int(parts[3]),
                        "message": parts[4],
                    }
                )
        return commits
    except Exception as e:
        print(f"Warning: Could not read git history: {e}")
        return []


def analyze_commit_diffs(commits):
    """分析提交的 diff 特征，统计语言分布"""
    language_counts = defaultdict(int)
    gene_weights = defaultdict(float)

    for commit in commits:
        try:
            result = subprocess.run(
                ["git", "show", "--stat", "--format=", commit["hash"]],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=PROJECT_ROOT,
            )

            for line in result.stdout.strip().split("\n"):
                # 统计文件扩展名
                for ext in LANGUAGE_GENE_MAP:
                    if f".{ext}" in line.lower():
                        lang = ext
                        gene_type = LANGUAGE_GENE_MAP.get(lang, "logic")
                        language_counts[lang] += 1
                        gene_weights[gene_type] += 1
                        break
        except Exception:
            continue

    return language_counts, gene_weights


def calculate_ivs(commits):
    """计算个体值 (IVs) - 基于提交特征的随机种子"""
    import hashlib

    if not commits:
        # 默认值
        return {
            stat: 15 for stat in ["hp", "attack", "defense", "speed", "armor", "quota"]
        }

    # 使用所有提交 hash 的组合作为种子
    seed_data = "".join(c["hash"] for c in commits[:10])
    seed = int(hashlib.md5(seed_data.encode()).hexdigest()[:8], 16)

    ivs = {}
    stat_names = ["hp", "attack", "defense", "speed", "armor", "quota"]
    for i, stat in enumerate(stat_names):
        ivs[stat] = (seed >> (i * 5)) % 32

    return ivs


def fetch_github_metrics(owner: str, repo: str, github_token: Optional[str] = None) -> Optional[GitHubMetrics]:
    """
    从 GitHub API 获取项目指标
    
    参数：
    - owner: GitHub 用户名或组织
    - repo: 仓库名称
    - github_token: GitHub Personal Access Token (可选)
    
    返回：
    - GitHubMetrics 对象或 None
    """
    if GitHubMetrics is None:
        print("Warning: GitHub metrics unavailable (module not imported)")
        return None
    
    try:
        import requests
        
        headers = {}
        if github_token:
            headers["Authorization"] = f"token {github_token}"
        
        # 获取仓库信息
        url = f"https://api.github.com/repos/{owner}/{repo}"
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            print(f"Warning: Failed to fetch GitHub metrics (status: {response.status_code})")
            return None
        
        data = response.json()
        
        # 获取 Issue 统计
        issues_url = f"https://api.github.com/repos/{owner}/{repo}/issues?state=all&per_page=1"
        issues_response = requests.get(issues_url, headers=headers, timeout=10)
        total_issues = 0
        if issues_response.status_code == 200:
            link_header = issues_response.headers.get("Link", "")
            if "last" in link_header:
                # 从 Link header 提取总数
                parts = link_header.split(',')
                for part in parts:
                    if 'rel="last"' in part:
                        # 提取 page= 参数
                        import re
                        match = re.search(r'page=(\d+)', part)
                        if match:
                            total_issues = int(match.group(1))
        
        # 估算开放和已关闭的 issue
        open_issues = data.get("open_issues_count", 0)
        closed_issues = max(0, total_issues - open_issues)
        
        # 获取 PR 统计
        pulls_url = f"https://api.github.com/repos/{owner}/{repo}/pulls?state=all&per_page=1"
        pulls_response = requests.get(pulls_url, headers=headers, timeout=10)
        total_prs = 0
        if pulls_response.status_code == 200:
            link_header = pulls_response.headers.get("Link", "")
            if "last" in link_header:
                parts = link_header.split(',')
                for part in parts:
                    if 'rel="last"' in part:
                        import re
                        match = re.search(r'page=(\d+)', part)
                        if match:
                            total_prs = int(match.group(1))
        
        # 获取 Owner 信息
        owner_followers = 0
        try:
            owner_url = data.get("owner", {}).get("url")
            if owner_url:
                owner_response = requests.get(owner_url, headers=headers, timeout=10)
                if owner_response.status_code == 200:
                    owner_followers = owner_response.json().get("followers", 0)
        except Exception:
            pass
        
        metrics = GitHubMetrics(
            stars=data.get("stargazers_count", 0),
            forks=data.get("forks_count", 0),
            watchers=data.get("watchers_count", 0),
            open_issues=open_issues,
            closed_issues=closed_issues,
            pull_requests=total_prs,
            language=data.get("language", "Unknown"),
            is_fork=data.get("fork", False),
            owner_followers=owner_followers
        )
        
        return metrics
        
    except ImportError:
        print("Warning: requests library not available")
        return None
    except Exception as e:
        print(f"Warning: Failed to fetch GitHub metrics: {e}")
        return None


def generate_enhanced_soul(
    commits, 
    language_counts, 
    commit_genes,
    owner_email,
    github_metrics: Optional[GitHubMetrics] = None
):
    """
    生成增强的 pet.soul 文件，结合提交历史和 GitHub 声誉
    """
    
    total_commits = len(commits)
    if total_commits == 0:
        total_commits = 1

    # 计算最终基因权重
    if github_metrics and ReputationGeneCalculator:
        # 使用混合计算器
        hybrid_calc = HybridGeneCalculator()
        final_genes = hybrid_calc.calculate_hybrid_genes(commit_genes, github_metrics)
        reputation_calc = ReputationGeneCalculator()
        improved_stats_bonus = reputation_calc.apply_gene_improvements(
            {stat: 0 for stat in ["hp", "attack", "defense", "speed", "armor", "quota"]},
            final_genes
        )
    else:
        # 仅使用提交历史
        total_weight = sum(commit_genes.values()) or 1
        final_genes = {
            gene: weight / total_weight for gene, weight in commit_genes.items()
        }
        improved_stats_bonus = {stat: 0 for stat in ["hp", "attack", "defense", "speed", "armor", "quota"]}

    # 确定物种类型
    max_gene = max(final_genes.items(), key=lambda x: x[1])
    if max_gene[1] > 0.5:
        species = {
            "logic": "Logic",
            "creative": "Creative", 
            "speed": "Speed"
        }.get(max_gene[0], "Hybrid")
    else:
        species = "Hybrid"

    # 生成基础属性（基于基因权重）
    base_stats = {
        "hp": 50 + int(final_genes.get("logic", 0.33) * 50),
        "attack": 50 + int(final_genes.get("speed", 0.33) * 50),
        "defense": 50 + int(final_genes.get("logic", 0.33) * 30),
        "speed": 50 + int(final_genes.get("speed", 0.33) * 50),
        "armor": 30 + int(final_genes.get("creative", 0.33) * 40),
        "quota": 100 + int(final_genes.get("creative", 0.33) * 100),
    }
    
    # 应用 GitHub 声誉加成
    for stat in base_stats:
        base_stats[stat] += improved_stats_bonus.get(stat, 0)

    # 计算 IVs
    ivs = calculate_ivs(commits)

    # 构建 soul 数据结构
    soul = {
        "metadata": {
            "name": f"CodePet-{datetime.now().strftime('%Y%m%d')}",
            "species": species,
            "birth_time": datetime.now().isoformat(),
            "owner": owner_email,
            "generation": 1,
            "evolution_stage": 1,
            "avatar": get_ascii_avatar(1),
            "inheritance_method": "hybrid" if github_metrics else "commit_history_only",
        },
        "stats": {},
        "genes": {
            "logic": {
                "weight": final_genes.get("logic", 0.33),
                "source_commits": [],
            },
            "creative": {
                "weight": final_genes.get("creative", 0.33),
                "source_commits": [],
            },
            "speed": {
                "weight": final_genes.get("speed", 0.33),
                "source_commits": [],
            },
        },
        "github_reputation": None,
        "battle_history": [],
        "signature": {
            "algorithm": "RSA-SHA256",
            "value": "",
            "keyid": get_git_config("user.signingkey") or "",
        },
    }

    # 添加 GitHub 声誉信息
    if github_metrics:
        reputation_calc = ReputationGeneCalculator()
        bonuses, analysis = reputation_calc.calculate_gene_bonus(github_metrics)
        soul["github_reputation"] = {
            "stars": github_metrics.stars,
            "forks": github_metrics.forks,
            "watchers": github_metrics.watchers,
            "analysis": analysis,
            "boosted": True,
        }

    # 构建 stats
    for stat_name, base in base_stats.items():
        soul["stats"][stat_name] = {
            "base": base,
            "iv": ivs.get(stat_name, 15),
            "ev": 0,
            "exp": 0,
        }

    # 添加基因来源提交
    for commit in commits[:10]:
        gene_type = LANGUAGE_GENE_MAP.get("py", "logic")  # 默认
        for lang, gt in LANGUAGE_GENE_MAP.items():
            if lang in commit.get("message", "").lower():
                gene_type = gt
                break
        soul["genes"][gene_type]["source_commits"].append(commit["hash"])

    return soul


def get_ascii_avatar(stage):
    """获取 ASCII 头像"""
    avatars = {
        1: r"""
     ╭───╮
    │ ◕  │
    ╰───╯
   ╭──────╮
  │  ♪ ♪  │
  ╰──────╯
        """,
        2: r"""
    ╭───────────╮
   │   ╭═══╮   │
   │  ◕  ◕  │ 
   │   ╰═══╯   │
   ╰───────────╯
  ╭─────────────╮
 │   ══════════│
╰───────────────╯
        """,
        3: r"""
    ╭═══════════════════╮
   │   ╭═══════════╮   │
   │  │ ╭═══════╮ │   │
   │  │ │ ◕  ◕ │ │   │
   │  │ ╰═══════╯ │   │
   │   ╰═══════════╯   │
   ╰═══════════════════╯
  ╭═════════════════════╮
 │ ════════════════════ │
╰════════───────────────╯
        """,
    }
    return avatars.get(stage, avatars[1])


def main():
    """主函数"""
    # Windows 控制台 Unicode 兼容
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

    print("🥚 Agent Monster - Enhanced Egg Incubator")
    print("=" * 60)
    print("结合 Git 提交历史和 GitHub 声誉的蛋孵化器")
    print("=" * 60)

    # 确保 .monster 目录存在
    MONSTER_DIR.mkdir(exist_ok=True)

    # 获取用户信息
    owner_email = get_git_config("user.email") or "unknown@localhost"
    print(f"\n👤 Owner: {owner_email}")

    # 获取 GitHub 信息 (可选)
    github_owner = get_git_config("user.name") or None
    github_repo = None
    github_url = get_git_config("remote.origin.url") or ""
    
    print(f"\n📍 Repository: {github_url}")
    
    # 尝试从 GitHub URL 解析所有者和仓库
    if "github.com" in github_url:
        try:
            # 处理 git@github.com:owner/repo.git 格式
            parts = github_url.split(":")[-1].split("/")
            if len(parts) >= 2:
                github_owner = parts[-2]
                github_repo = parts[-1].replace(".git", "")
        except Exception:
            pass

    github_metrics = None
    if github_owner and github_repo:
        print(f"\n🔍 Fetching GitHub metrics for {github_owner}/{github_repo}...")
        github_token = os.getenv("GITHUB_TOKEN")
        github_metrics = fetch_github_metrics(github_owner, github_repo, github_token)
        
        if github_metrics:
            print("✅ GitHub metrics fetched successfully")
            print(f"   ⭐ Stars: {github_metrics.stars}")
            print(f"   🔀 Forks: {github_metrics.forks}")
            print(f"   👁️ Watchers: {github_metrics.watchers}")
        else:
            print("ℹ️  Could not fetch GitHub metrics")

    # 获取提交历史
    commits = get_commit_history(hours=72, limit=50)
    print(f"\n📝 Analyzing {len(commits)} commits (last 72h)...")

    # 分析语言分布
    language_counts, commit_genes = analyze_commit_diffs(commits)

    print("\n📊 Language Distribution:")
    for lang, count in sorted(language_counts.items(), key=lambda x: -x[1])[:10]:
        gene = LANGUAGE_GENE_MAP.get(lang, "logic")
        print(f"  {lang:8} -> {gene:8} : {count}")

    print("\n🧬 Commit Gene Weights:")
    total_weight = sum(commit_genes.values()) or 1
    for gene in ["logic", "creative", "speed"]:
        weight = commit_genes.get(gene, 0)
        bar = "█" * int(weight / max(commit_genes.values()) * 20) if total_weight > 0 else ""
        print(f"  {gene:8}: {weight/total_weight:.2%} {bar}")

    # 生成增强的 soul 文件
    soul = generate_enhanced_soul(
        commits, language_counts, commit_genes, owner_email, github_metrics
    )

    # 写入文件
    with open(SOUL_FILE, "w", encoding="utf-8") as f:
        json.dump(soul, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Created: {SOUL_FILE}")
    print(f"   种族 Species: {soul['metadata']['species']}")
    print(f"   阶段 Stage: {soul['metadata']['evolution_stage']}")
    print(f"   继承方式: {soul['metadata']['inheritance_method']}")

    if github_metrics:
        print(f"\n🏆 GitHub Reputation Boost Applied!")
        rep_info = soul.get("github_reputation", {})
        if rep_info:
            print(f"   ⭐ Stars: {rep_info.get('stars', 0)}")
            print(f"   🔀 Forks: {rep_info.get('forks', 0)}")

    print("\n" + soul["metadata"]["avatar"])

    return 0


if __name__ == "__main__":
    sys.exit(main())
