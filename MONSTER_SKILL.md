# Agent Monster Skill (代码怪兽)

Agent Monster is an AI-powered RPG where your GitHub repository becomes a digital pet. You can interact with your monster using natural language and receive AI-driven guidance.

## Mandates

- **Natural Language First**: Always interpret user requests as natural language actions in the game.
- **AI Guidance**: If the user is unsure what to do, call `monster_guide` to provide multilingual suggestions.
- **Language Preference**: Respect the user's language choice (defaulting to Chinese if unspecified).
- **Proactive Onboarding**: If no user is found, suggest calling `monster_welcome`.

## Core Tools

- `monster_welcome`: Start the journey and choose language.
- `monster_set_language`: Change your preferred language.
- `monster_guide`: Get AI-driven suggestions based on your current game state.
- `monster_fork_setup`: Automatically setup base and map for a forked repository.
- `monster_status`: View your monster's stats and level.
- `monster_init`: Initialize your repository's monster.
- `user_register`: Create your player account.

## Workflow

1. **New Players**: Start with `monster_welcome` -> `monster_set_language` -> `user_register`.
2. **Gameplay**: Use `monster_guide` to see available actions (buying items, battling, hatching eggs).
3. **Exploration**: Use `monster_explore` and `monster_farm` to manage your resources.
4. **Combat**: Use `monster_duel` or `monster_battle` to gain experience.

## Language Support

- **中文**: 默认支持，提供完整的任务引导和状态查询。
- **English**: Fully supported, can be toggled via `monster_set_language`.
