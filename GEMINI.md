# Gemini Mandates for Agent Monster

## Strategic Mandates

1. **Natural Language First**: Always prioritize natural language interaction. If a user asks "what can I do?" or "I'm lost," immediately call `monster_guide`.
2. **Onboarding**: For first-time players, use `monster_welcome` to guide them through language selection and registration.
3. **Multilingual Support**: Respect the language preference set in the user profile. If `monster_set_language` is called, all subsequent AI guidance should match that language.
4. **Tool Orchestration**: Use `monster_status`, `inventory_view`, and `account_stats` as underlying data sources to provide a rich, narrative summary to the player.

## Tools Mapping

- **Query Status**: `monster_status`
- **What's Next?**: `monster_guide`
- **Change Language**: `monster_set_language`
- New Player Welcome: `monster_welcome`
- Fork Setup: `monster_fork_setup`
- Analyze Code Activity: `monster_analyze`

- **Battle Challenge**: `monster_duel`
- **Hatch Egg**: `monster_hatch`
- **Shop & Economy**: `shop_list`, `shop_buy`, `account_stats`
