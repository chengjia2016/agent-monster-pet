"""
GitHub Farm Explorer Module
Provides functionality to discover and explore Agent Monster farms across GitHub.
"""

import os
import json
import requests
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime
import yaml


@dataclass
class FarmInfo:
    """Information about a discovered farm"""
    owner: str
    repository: str
    url: str
    farm_url: str
    file_path: str
    planted_at: Optional[datetime] = None
    foods_count: int = 0
    last_checked: Optional[datetime] = None


@dataclass
class FarmFood:
    """Food information from a farm"""
    id: str
    type: str
    emoji: str
    quantity: int = 0
    max_quantity: int = 0
    regeneration_hours: int = 0
    last_eaten_at: Optional[datetime] = None
    seed: str = ""


class GitHubFarmExplorer:
    """Discovers and explores Agent Monster farms on GitHub"""

    def __init__(self, github_token: Optional[str] = None):
        """
        Initialize the farm explorer.

        Args:
            github_token: GitHub personal access token for authenticated requests
        """
        self.github_token = github_token or os.getenv("GITHUB_TOKEN", "")
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
        }
        if self.github_token:
            self.headers["Authorization"] = f"token {self.github_token}"

    def search_farms(self, query: str = "", per_page: int = 30, page: int = 1) -> List[Dict[str, Any]]:
        """
        Search for repositories with Agent Monster farms.

        Args:
            query: Additional search terms
            per_page: Results per page (max 100)
            page: Page number

        Returns:
            List of repository information matching the search
        """
        search_query = "filename:.monster/farm.yaml"
        if query:
            search_query += f" {query}"

        url = f"{self.base_url}/search/repositories"
        params = {
            "q": search_query,
            "sort": "updated",
            "order": "desc",
            "per_page": min(per_page, 100),
            "page": page,
        }

        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get("items", [])
        except requests.RequestException as e:
            print(f"Error searching farms: {e}")
            return []

    def discover_farms(self, limit: int = 50) -> List[FarmInfo]:
        """
        Discover available farms on GitHub.

        Args:
            limit: Maximum number of farms to discover

        Returns:
            List of discovered farm information
        """
        farms = []
        page = 1
        items_found = 0

        while items_found < limit:
            repos = self.search_farms(per_page=min(30, limit - items_found), page=page)
            if not repos:
                break

            for repo in repos:
                if items_found >= limit:
                    break

                farm_info = self._extract_farm_info(repo)
                if farm_info:
                    farms.append(farm_info)
                    items_found += 1

            page += 1

        return farms

    def get_farm_content(self, owner: str, repo: str, path: str = ".monster/farm.yaml") -> Optional[Dict[str, Any]]:
        """
        Retrieve the farm.yaml content from a repository.

        Args:
            owner: Repository owner
            repo: Repository name
            path: Path to farm.yaml file

        Returns:
            Parsed farm data or None if not found
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/contents/{path}"

        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if "content" not in data:
                return None

            # Decode base64 content
            import base64
            content = base64.b64decode(data["content"]).decode("utf-8")
            
            # Parse YAML
            farm_data = yaml.safe_load(content)
            return farm_data
        except requests.RequestException as e:
            print(f"Error fetching farm content for {owner}/{repo}: {e}")
            return None
        except (yaml.YAMLError, ValueError) as e:
            print(f"Error parsing farm YAML for {owner}/{repo}: {e}")
            return None

    def explore_farm(self, owner: str, repo: str) -> Optional[Dict[str, Any]]:
        """
        Explore a specific farm.

        Args:
            owner: Repository owner
            repo: Repository name

        Returns:
            Farm information including available foods or None if not found
        """
        farm_content = self.get_farm_content(owner, repo)
        if not farm_content:
            return None

        # Structure the farm data
        farm_data = farm_content.get("farm", {})
        foods = []

        for food_entry in farm_data.get("foods", []):
            food = FarmFood(
                id=food_entry.get("id", ""),
                type=food_entry.get("type", ""),
                emoji=food_entry.get("emoji", ""),
                quantity=food_entry.get("quantity", 0),
                max_quantity=food_entry.get("max_quantity", 0),
                regeneration_hours=food_entry.get("regeneration_hours", 0),
                last_eaten_at=self._parse_datetime(food_entry.get("last_eaten_at")),
                seed=food_entry.get("seed", ""),
            )
            if food.quantity > 0:  # Only include available food
                foods.append(food.__dict__)

        return {
            "owner": farm_data.get("owner", owner),
            "repository": farm_data.get("repository", repo),
            "url": farm_data.get("url", f"https://github.com/{owner}/{repo}"),
            "planted_at": farm_data.get("planted_at"),
            "available_foods": foods,
            "total_available": len(foods),
        }

    def get_favorites(self, favorites_file: str = ".monster/favorites.json") -> List[str]:
        """
        Load favorite farms from a local file.

        Args:
            favorites_file: Path to favorites JSON file

        Returns:
            List of favorite farm URLs
        """
        try:
            if os.path.exists(favorites_file):
                with open(favorites_file, "r") as f:
                    data = json.load(f)
                    return data.get("favorites", [])
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error reading favorites file: {e}")
        return []

    def save_favorites(self, farms: List[str], favorites_file: str = ".monster/favorites.json") -> bool:
        """
        Save favorite farms to a local file.

        Args:
            farms: List of farm URLs to save
            favorites_file: Path to favorites JSON file

        Returns:
            True if successful, False otherwise
        """
        try:
            os.makedirs(os.path.dirname(favorites_file) or ".", exist_ok=True)
            with open(favorites_file, "w") as f:
                json.dump({"favorites": farms}, f, indent=2)
            return True
        except IOError as e:
            print(f"Error saving favorites file: {e}")
            return False

    def _extract_farm_info(self, repo: Dict[str, Any]) -> Optional[FarmInfo]:
        """Extract farm information from a repository object."""
        try:
            owner = repo.get("owner", {}).get("login", "")
            name = repo.get("name", "")
            
            if not owner or not name:
                return None

            return FarmInfo(
                owner=owner,
                repository=name,
                url=repo.get("html_url", f"https://github.com/{owner}/{name}"),
                farm_url=f"https://raw.githubusercontent.com/{owner}/{name}/main/.monster/farm.yaml",
                file_path=".monster/farm.yaml",
                last_checked=datetime.now(),
            )
        except (KeyError, TypeError):
            return None

    def _parse_datetime(self, dt_str: Optional[str]) -> Optional[datetime]:
        """Parse datetime string to datetime object."""
        if not dt_str:
            return None
        try:
            # Handle ISO 8601 format
            if "T" in dt_str:
                return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
            return None
        except (ValueError, AttributeError):
            return None

    def get_farm_leaderboard(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get a leaderboard of farms with the most available food.

        Args:
            limit: Maximum number of farms to return

        Returns:
            List of farms sorted by available food count
        """
        farms = self.discover_farms(limit=100)
        leaderboard = []

        for farm in farms:
            farm_data = self.explore_farm(farm.owner, farm.repository)
            if farm_data:
                leaderboard.append({
                    "owner": farm.owner,
                    "repository": farm.repository,
                    "available_foods": farm_data["total_available"],
                    "url": farm.url,
                })

        # Sort by available foods
        leaderboard.sort(key=lambda x: x["available_foods"], reverse=True)
        return leaderboard[:limit]


if __name__ == "__main__":
    # Example usage
    explorer = GitHubFarmExplorer()
    
    # Discover farms
    print("Discovering farms...")
    farms = explorer.discover_farms(limit=5)
    
    for farm in farms:
        print(f"\nFarm: {farm.owner}/{farm.repository}")
        farm_data = explorer.explore_farm(farm.owner, farm.repository)
        if farm_data:
            print(f"  Available foods: {farm_data['total_available']}")
            for food in farm_data['available_foods'][:3]:
                print(f"    - {food['emoji']} {food['type']}: {food['quantity']}/{food['max_quantity']}")
