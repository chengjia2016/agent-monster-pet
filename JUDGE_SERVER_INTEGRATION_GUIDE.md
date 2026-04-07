# Judge Server Integration Guide

## Overview

This guide explains the new Judge Server integration system for centralizing user data management. The system uses a hybrid approach with local caching fallback for offline operation.

## Architecture

### Data Flow

```
Application Code
    ↓
UnifiedDataManager (new)
    ├─ Local Storage (Always)
    │  └── .monster/
    │      ├── users/
    │      ├── accounts/
    │      ├── inventory/
    │      └── user_cache/
    │
    └─ Judge Server (When available)
       └─ http://agentmonster.openx.pro:10000
```

### Key Components

| Component | Purpose | Status |
|-----------|---------|--------|
| `UnifiedDataManager` | Main entry point for all data operations | ✅ Ready |
| `HybridUserDataManager` | Handles local + server sync | ✅ Ready |
| `JudgeServerUserManager` | Server API client | ✅ Ready |
| `mcp_data_manager.py` | MCP integration layer | ✅ Ready |
| `migrate_to_judge_server.py` | Migration tool | ✅ Ready |
| `test_judge_server_integration.py` | Integration tests | ✅ Ready (5/5 pass) |

## Usage

### Basic Usage

```python
from unified_data_manager import UnifiedDataManager

# Initialize manager
dm = UnifiedDataManager(".monster", enable_server_sync=True)

# Get user profile
profile = dm.get_user_profile("github_login")
print(f"Balance: {profile['balance']}")

# Update balance
dm.update_balance(user_id, 100, "reward")

# Purchase item
result = dm.purchase_item(user_id, "item_id", 1)
```

### MCP Server Integration

```python
from mcp_data_manager import get_data_manager, find_user

def cmd_user_info(github_username):
    dm = get_data_manager()
    user = find_user(github_username)
    if not user:
        return "❌ User not found"
    
    profile = dm.get_user_profile(github_username)
    return f"✓ User: {profile['github_login']}, Balance: {profile['balance']}"
```

### Error Handling

```python
from unified_data_manager import UnifiedDataManager

dm = UnifiedDataManager(".monster")

# Check server status
status = dm.get_sync_status()
print(f"Server available: {status['server_available']}")
print(f"Sync enabled: {status['server_sync_enabled']}")

# Offline mode operation (automatic fallback)
# All operations use local cache if server unavailable
balance = dm.get_balance(user_id)  # Works offline
```

## File Structure

### New Files Created

```
/root/pet/agent-monster-pet/
├── unified_data_manager.py          # Main data manager (NEW)
├── mcp_data_manager.py              # MCP integration (NEW)
├── hybrid_user_data_manager.py      # Hybrid storage (EXISTING)
├── judge_server_user_manager.py     # Server API client (EXISTING)
├── migrate_to_judge_server.py       # Migration tool (NEW)
├── test_judge_server_integration.py # Integration tests (NEW)
├── GRADUAL_MIGRATION_STRATEGY.md    # Migration strategy (NEW)
└── JUDGE_SERVER_INTEGRATION.md      # Technical spec (EXISTING)
```

## Data Models

### User Data Structure

```json
{
  "user_id": "uuid-string",
  "github_id": 123456789,
  "github_login": "username",
  "email": "user@example.com",
  "avatar_url": "https://...",
  "registered_at": "2026-04-07T10:00:00",
  "last_login": "2026-04-07T15:30:00",
  "balance": 1000.0,
  "inventory": {
    "item_id": {
      "item": { "name": "...", "price": 100, ... },
      "quantity": 5,
      "total_value": 500
    }
  },
  "transactions": [
    { "type": "purchase", "amount": -100, "timestamp": "2026-04-07T10:05:00" }
  ]
}
```

### Storage Locations

| Data | Local Storage | Server Storage |
|------|---------------|----------------|
| User Profile | `.monster/users/{user_id}.json` | `/api/users/{github_id}` |
| Account | `.monster/accounts/{user_id}.json` | `/api/users/{github_id}/account` |
| Inventory | `.monster/inventory/{user_id}.json` | `/api/users/{github_id}/items` |
| Cache | `.monster/user_cache/user_{github_id}.json` | N/A |

## Migration Guide

### Automatic Migration (Recommended)

```bash
# Dry run (shows what would be migrated)
python3 migrate_to_judge_server.py
# Then answer 'no' when prompted

# Live migration (migrates all users)
python3 migrate_to_judge_server.py
# Then answer 'yes' when prompted
```

### Manual Migration (Per-User)

```python
from migrate_to_judge_server import DataMigrationManager

migrator = DataMigrationManager()
user_data = migrator.export_user_data(user_id)
migrator.cache_user_data_locally(user_data)
success, msg = migrator.migrate_user_to_server(user_data)
```

## Testing

### Run Integration Tests

```bash
python3 test_judge_server_integration.py
```

Expected output:
```
✓ PASS: connectivity
✓ PASS: hybrid_fallback
✓ PASS: existing_data
✓ PASS: hybrid_existing
✓ PASS: api_structure

Total: 5/5 tests passed
```

### Test Specific Scenarios

```python
from test_judge_server_integration import *

# Test 1: Server connectivity
test_judge_server_connectivity()

# Test 2: Fallback mechanism
test_hybrid_data_manager_local_fallback()

# Test 3: Migration
test_hybrid_manager_with_local_data()
```

## Offline Mode

### How It Works

1. **Request Made**: User performs action (e.g., purchase item)
2. **Server Try**: System attempts to reach Judge Server (5s timeout)
3. **Fallback**: If server unavailable, uses local cache
4. **User Notification**: Shows which mode is active
5. **Auto Sync**: When server returns, syncs queued operations

### Example

```python
# User is offline but can still play
dm = UnifiedDataManager(".monster")

# This works even without server
inventory = dm.get_inventory(user_id)
balance = dm.get_balance(user_id)

# This queues for sync when server returns
dm.update_balance(user_id, 50)

# Check status
status = dm.get_sync_status()
print(f"Mode: {status['mode']}")  # "offline"
```

## Configuration

### Environment Variables

```bash
# Disable server sync (offline mode)
export JUDGE_SERVER_SYNC=false

# Server URL override
export JUDGE_SERVER_URL=http://localhost:10000

# Sync interval (seconds)
export SYNC_INTERVAL=300
```

### Programmatic Configuration

```python
# Offline mode
dm = UnifiedDataManager(".monster", enable_server_sync=False)

# Enable/disable dynamically
dm.enable_server_mode(False)  # Switch to offline
dm.enable_server_mode(True)   # Switch to online
```

## Troubleshooting

### Problem: "Server unavailable"

**Solution**: The system automatically falls back to local cache. Check:
1. Is Judge Server running?
2. Network connectivity OK?
3. Firewall allowing connections?

### Problem: "Data mismatch"

**Solution**: Server data always wins. To manually sync:
```python
dm = UnifiedDataManager(".monster")
# Force re-sync of specific user
profile = dm.get_user_profile(github_login)
dm.sync_user_to_server(profile['github_id'], profile)
```

### Problem: "Migration failed"

**Solution**: Check migration log:
```bash
# View migration report
cat .monster/migration_report.json | jq .

# Retry migration for failed users
python3 migrate_to_judge_server.py
```

## Performance Considerations

### Latency

| Operation | Local | Server | Hybrid |
|-----------|-------|--------|--------|
| Get Balance | < 1ms | 100-500ms | < 1ms (cache) |
| Update Balance | < 5ms | 200-600ms | < 5ms (cache) + async sync |
| List Inventory | < 10ms | 300-700ms | < 10ms (cache) + async sync |

### Optimization Tips

1. **Cache Warm-up**: Pre-load user data on startup
2. **Batch Operations**: Group multiple updates into one sync
3. **Async Sync**: Don't block on server responses
4. **Connection Pool**: Reuse HTTP connections

## Security Considerations

### Data Protection

- ✅ Local data encrypted at rest (recommended)
- ✅ HTTPS for server communication (when deployed)
- ✅ Server data is source of truth
- ✅ User can access own data only

### Recommended Practices

```python
# Always validate user ownership
def purchase_item(current_user_id, target_user_id, ...):
    if current_user_id != target_user_id:
        raise PermissionError("Can only modify own account")
```

## API Reference

### UnifiedDataManager Methods

#### User Profile
- `get_user_profile(github_login: str) -> Dict`
- `find_user_by_login(github_login: str) -> User`
- `list_users() -> List[User]`
- `get_user_by_id(user_id: str) -> User`

#### Account Management
- `get_account(user_id: str) -> Account`
- `get_balance(user_id: str) -> float`
- `update_balance(user_id: str, amount: float, reason: str) -> bool`

#### Inventory
- `get_inventory(user_id: str) -> Dict`
- `add_item(user_id: str, item_id: str, quantity: int) -> bool`
- `remove_item(user_id: str, item_id: str, quantity: int) -> bool`

#### Economy
- `purchase_item(user_id: str, item_id: str, quantity: int) -> Dict`

#### Sync
- `sync_user_to_server(github_id: int, user_data: Dict) -> bool`
- `enable_server_mode(enabled: bool)`
- `get_sync_status() -> Dict`

## Next Steps

### Immediate (Next Iteration)
1. Test UnifiedDataManager in production
2. Update onboarding to use new manager
3. Monitor sync performance

### Short-term (1-2 weeks)
1. Deploy server-side API endpoints
2. Enable server sync for new users
3. Run migration of existing users

### Medium-term (1 month)
1. Switch to server-primary mode
2. Archive local storage
3. Monitor system health

## Support

### Debug Logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)
dm = UnifiedDataManager(".monster")
# Now all operations are logged
```

### Check System Status

```python
dm = UnifiedDataManager(".monster")

# Status report
status = dm.get_sync_status()
print(f"Server Sync: {status['server_sync_enabled']}")
print(f"Server Available: {status['server_available']}")
print(f"Mode: {status['mode']}")

# List all users
users = dm.list_users()
print(f"Total Users: {len(users)}")

# Check user data
profile = dm.get_user_profile("username")
print(json.dumps(profile, indent=2))
```

## References

- [GRADUAL_MIGRATION_STRATEGY.md](./GRADUAL_MIGRATION_STRATEGY.md) - Migration plan
- [JUDGE_SERVER_INTEGRATION.md](./JUDGE_SERVER_INTEGRATION.md) - Technical spec
- [HybridUserDataManager](./hybrid_user_data_manager.py) - Hybrid storage implementation
- [JudgeServerUserManager](./judge_server_user_manager.py) - Server API client

