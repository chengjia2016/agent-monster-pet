# Agent Monster CLI Map Commands

Complete guide for the map command-line interface in Agent Monster.

## Overview

The `map` command provides a powerful CLI interface for creating, validating, and sharing maps. Users can build custom game maps without using the graphical onboarding flow.

## Installation & Setup

### Running Map Commands

```bash
./agentmonster map <command> [options]
```

### Environment Setup

Set your GitHub token for easy access:

```bash
export GITHUB_TOKEN=your_token_here
```

## Available Commands

### 1. Map Create

Create a new map from templates or custom designs.

**Usage:**
```bash
./agentmonster map create [--title <title>] [--template <template>] [--difficulty <level>]
```

**Options:**
- `--title <title>` - Map title (required)
- `--template <template>` - Map template to use
  - `starter` - Basic 20x20 map with 1 Pokemon and 1 food
  - `advanced` - Complex map with multiple Pokemon and obstacles
  - `custom` - Empty map for complete customization
- `--difficulty <level>` - Difficulty level
  - `easy` - Beginner-friendly
  - `medium` - Standard difficulty
  - `hard` - Challenging

**Examples:**
```bash
./agentmonster map create --title "Forest Adventure" --template starter --difficulty easy
./agentmonster map create --title "Mountain Quest" --template advanced --difficulty hard
```

**Output:**
Shows the created map ID and local storage location. Provides next steps for validation and export.

---

### 2. Map Validate

Validate a map and receive a quality score (0-100).

**Usage:**
```bash
./agentmonster map validate <map_id>
```

**Validation Checks:**
1. **Format Validation (20 points)**
   - Required fields present (version, map_id, statistics)
   - Proper JSON structure
   - Field value constraints

2. **Balance Check (30 points)**
   - Pokemon distribution (30-50%)
   - Food distribution (20-30%)
   - Obstacles (15-25%)
   - Element overlap detection

3. **Diversity Check (25 points)**
   - Minimum 3 different Pokemon species
   - Minimum 2 different food types
   - Varied terrain distribution
   - Element type variety

4. **Creativity (15 points)**
   - Original layout design
   - Unique element combinations
   - Interesting gameplay flow

5. **Documentation (10 points)**
   - Map title and description quality
   - Tags and metadata completeness
   - Version information

**Output:**
- Overall score (0-100)
- Component scores breakdown
- List of critical issues
- Suggestions for improvement

**Example:**
```bash
./agentmonster map validate map_1775802116_2361877
```

**Sample Output:**
```
📊 Validation Results:

  Overall Score: 72/100
  Valid: true

💡 Suggestions:
  - Pokemon type diversity could be improved
  - Consider adding more obstacles for balance
```

---

### 3. Map List

List available maps from local or community sources.

**Usage:**
```bash
./agentmonster map list [--source <source>] [--difficulty <level>]
```

**Options:**
- `--source <source>` - Data source (default: `local`)
  - `local` - Maps on your computer
  - `community` - Shared maps from the community
- `--difficulty <level>` - Filter by difficulty
  - `easy`, `medium`, `hard`

**Examples:**
```bash
./agentmonster map list
./agentmonster map list --source community --difficulty hard
./agentmonster map list --difficulty easy
```

**Output:**
- List of map IDs with basic info
- Difficulty and creator information
- Download/play options

---

### 4. Map Export

Export a map to GitHub for community submission.

**Usage:**
```bash
./agentmonster map export [--token <token>] [--user <username>] <map_id>
```

**Options:**
- `--token <token>` - GitHub personal access token
  - Can be set via `GITHUB_TOKEN` environment variable
  - [Generate token here](https://github.com/settings/tokens)
- `--user <username>` - Your GitHub username

**Prerequisites:**
- Valid GitHub token with `repo` scope
- Map passes validation (score ≥ 50)

**Examples:**
```bash
./agentmonster map export --user myusername map_1775802116_2361877
export GITHUB_TOKEN=ghp_xxxxxxxxxxxx
./agentmonster map export my_map
```

**What Gets Exported:**
- `map.json` - Map data and metadata
- `metadata.json` - Complete map information
- `README.md` - Map documentation
- Git commit with proper attribution

**Next Steps:**
After export, visit your repository to:
1. Review the exported files
2. Create a pull request to the main project
3. Contribute to the community

---

### 5. Map Info

Display detailed information about a map.

**Usage:**
```bash
./agentmonster map info <map_id>
```

**Shows:**
- Complete map data structure
- Terrain configuration
- All elements (Pokemon, food, obstacles)
- Element positions and properties

**Examples:**
```bash
./agentmonster map info map_1775802116_2361877
```

---

### 6. Map Help

Display comprehensive help information.

**Usage:**
```bash
./agentmonster map help
```

---

## Map Data Format

### JSON Structure

```json
{
  "terrain": {
    "width": 20,
    "height": 20,
    "type": "grass"
  },
  "elements": [
    {
      "type": "wild_pokemon",
      "x": 5,
      "y": 5,
      "data": {
        "species": "Psyduck",
        "level": 1
      }
    },
    {
      "type": "food",
      "x": 10,
      "y": 10,
      "data": {
        "kind": "apple"
      }
    },
    {
      "type": "obstacle",
      "x": 15,
      "y": 5,
      "data": {
        "kind": "rock"
      }
    }
  ],
  "version": "1.0.0",
  "map_id": "map_1775802116_2361877",
  "statistics": {
    "total_elements": 3,
    "pokemon_count": 1,
    "food_count": 1,
    "obstacle_count": 1
  }
}
```

### Element Types

**wild_pokemon**
- `species` - Pokemon species name
- `level` - Pokemon level (1-100)
- `rarity` (optional) - Rarity level

**food**
- `kind` - Food type (apple, berry, potion, etc.)
- `effect` (optional) - Special effect

**obstacle**
- `kind` - Obstacle type (rock, tree, wall, etc.)
- `passable` (optional) - Whether players can pass through

**npc** (future)
- `name` - NPC name
- `dialogue` (optional) - NPC dialogue

---

## Workflow Examples

### Example 1: Create and Share a Simple Map

```bash
# Step 1: Create a map
./agentmonster map create --title "Beginner's Garden" --template starter --difficulty easy

# Step 2: Validate the map
./agentmonster map validate map_1775802116_2361877

# Step 3: View map details
./agentmonster map info map_1775802116_2361877

# Step 4: Export to GitHub
export GITHUB_TOKEN=ghp_xxxxxxxxxxxx
./agentmonster map export --user myusername map_1775802116_2361877

# Step 5: Create PR on GitHub to share with community
# Visit: https://github.com/yourfork/agent-monster/pull/new/main
```

### Example 2: Create Advanced Map with Custom Elements

```bash
# Step 1: Create from advanced template
./agentmonster map create --title "Dragon's Castle" --template advanced --difficulty hard

# Step 2: Get current map data
./agentmonster map info map_xyz

# Step 3: Edit map JSON file
nano ~/.agent-monster/data/maps/map_xyz.json

# Step 4: Validate changes
./agentmonster map validate map_xyz

# Step 5: Export when ready
./agentmonster map export --user myusername map_xyz
```

### Example 3: Browse and Study Community Maps

```bash
# List all community maps
./agentmonster map list --source community

# Filter by difficulty
./agentmonster map list --source community --difficulty hard

# Study an interesting map
./agentmonster map info community_map_001
```

---

## Tips & Best Practices

### Map Design

1. **Balance** - Distribute elements evenly across the map
2. **Variety** - Use multiple Pokemon species and item types
3. **Challenge** - Adjust difficulty through Pokemon levels and obstacle density
4. **Story** - Consider narrative flow when placing elements
5. **Navigation** - Ensure paths are accessible without excessive obstacles

### Naming & Documentation

1. **Clear Title** - Use descriptive, memorable names
2. **Good Description** - Help others understand the map's theme
3. **Appropriate Tags** - Use tags like "adventure", "boss", "puzzle"
4. **Version Management** - Increment version after changes

### Community Contribution

1. **Quality First** - Aim for scores above 70 before sharing
2. **Unique Content** - Create original maps, not duplicates
3. **Respect License** - Follow CC-BY-4.0 license terms
4. **Engage** - Review others' maps and provide feedback

---

## Troubleshooting

### Map Validation Fails

**Issue:** "缺少必要字段" (Missing required fields)

**Solution:** Ensure your map JSON includes:
- `version` - Semantic version (e.g., "1.0.0")
- `map_id` - Unique identifier
- `statistics` - Element count summary

**Issue:** "元素过少" (Too few elements)

**Solution:** Add at least 5 elements (Pokemon, food, obstacles total)

### Export Fails

**Issue:** "GitHub token required"

**Solution:** Set token via environment:
```bash
export GITHUB_TOKEN=your_token_here
./agentmonster map export --user myusername map_id
```

**Issue:** "Permission denied"

**Solution:** Ensure token has `repo` scope:
1. Go to https://github.com/settings/tokens
2. Create new token with `repo` scope
3. Use generated token

### Map File Not Found

**Issue:** "Map not found: map_xyz"

**Solution:** Check map location:
```bash
ls ~/.agent-monster/data/maps/
```

Map files must be `.json` format in the maps directory.

---

## GitHub Token Setup

### Generate Personal Access Token

1. Visit https://github.com/settings/tokens/new
2. Set token name (e.g., "agent-monster-cli")
3. Select required scopes:
   - ✓ repo (full control of private repositories)
   - ✓ public_repo (for public repositories)
4. Generate and copy token
5. Set environment variable:
   ```bash
   export GITHUB_TOKEN=ghp_xxxxxxxxxxxx
   ```

### Token Security

- Never commit tokens to version control
- Use environment variables for temporary use
- Store in secure credential manager for permanent use
- Rotate tokens regularly
- Delete unused tokens

---

## Advanced Usage

### Batch Operations (Future)

```bash
# Validate all local maps
./agentmonster map validate-all

# Export all validated maps
./agentmonster map export-all
```

### Map Templates (Future)

```bash
# Create custom template
./agentmonster map template create --name "my_template"

# Use custom template
./agentmonster map create --template my_template
```

### Collaborative Editing (Future)

```bash
# Download community map for editing
./agentmonster map download community_map_001

# Edit locally
./agentmonster map edit map_001

# Submit changes as PR
./agentmonster map export map_001
```

---

## Related Commands

See also:
- `./agentmonster` - Launch interactive onboarding
- `./agentmonster -auto` - Run automated onboarding
- `./agentmonster -debug` - Enable debug logging

---

## File Locations

- **Maps Directory:** `~/.agent-monster/data/maps/`
- **Logs:** `~/.agent-monster/data/logs/`
- **Exported Maps:** `~/.agent-monster/data/maps/exports/`

---

## Contributing

Have ideas for the map CLI? Report issues or suggest features:
- GitHub Issues: https://github.com/chengjia2016/agent-monster/issues
- Discussions: https://github.com/chengjia2016/agent-monster/discussions

---

**Version:** 1.0.0
**Last Updated:** April 2026
