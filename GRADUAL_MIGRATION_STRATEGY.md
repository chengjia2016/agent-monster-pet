# Gradual Judge Server Migration Strategy

## Overview
This document describes how to gradually migrate from local-only user data storage to a centralized Judge Server-based system with local caching fallback.

## Phase 1: Preparation (Current Phase - COMPLETE)
- ✅ Fix all `user.github_id` bugs in code
- ✅ Create test suite for Judge Server integration
- ✅ Create migration script for existing users
- ✅ Implement hybrid data manager with fallback

**Status**: All preparation work completed

## Phase 2: Gradual Integration (NEXT)
Implement a gradual rollout strategy:

### 2.1 Enable Hybrid Manager for New Users
- New user registrations use HybridUserDataManager
- Data saved to local cache + attempt server sync
- Fallback to local cache if server unavailable
- No impact on existing users

### 2.2 Selective User Migration
- Provide migration command for existing users
- Users can opt-in to server-based storage
- Run periodic sync to keep data current
- Monitor for any data consistency issues

### 2.3 Monitor & Validate
- Track sync success/failure rates
- Compare local vs server data
- Fix any discrepancies
- Build confidence in system

## Phase 3: Full Migration (When Judge Server APIs ready)
When the Judge Server has all required API endpoints implemented:

1. **Deploy Server Schema**
   - Create all required database tables
   - Implement all 14+ API endpoints
   - Set up data validation

2. **Bulk Migrate Existing Users**
   - Run migration script on all existing users
   - Verify data consistency
   - Enable automatic sync

3. **Switch to Server-First**
   - Update config to make server primary
   - Keep local cache for offline access
   - Monitor system health

## Phase 4: Decommission Local Storage (Optional)
Once server is proven stable:
- Archive local user data
- Remove local user files
- Keep backup for disaster recovery

## Implementation Details

### Current Architecture
```
Local Storage (Current Primary)
├── .monster/users/        (user profiles)
├── .monster/accounts/     (balance, transactions)
├── .monster/inventory/    (items owned)
└── .monster/sessions.json (active sessions)
```

### Target Architecture
```
Hybrid Storage (Recommended Long-term)
├── Judge Server (Primary)
│   ├── /api/users/{github_id}
│   ├── /api/users/{github_id}/balance
│   ├── /api/users/{github_id}/items
│   └── /api/users/{github_id}/pokemons
│
└── Local Cache (Fallback)
    └── .monster/user_cache/  (mirrored data)
```

### Fallback Mechanism
```
User Request
    ↓
Try Server (with timeout: 5s)
    ↓
├─ Success → Use server data, update cache
│
└─ Failure/Timeout → Use local cache (offline mode)
    ↓
Sync when connection restored (async)
```

## Key Design Decisions

### 1. Use GitHub Numeric ID as Primary Key
- All server storage uses `github_id` (numeric ID from GitHub)
- Local storage converted to use `github_id` for consistency
- More reliable than `user_id` (UUID) which is local-only

### 2. Local Cache Always Available
- Cache updated whenever data changes
- Survives server outages
- Users can continue playing offline
- Automatic sync when server comes back

### 3. Server Data Takes Precedence
- On conflict, server data is source of truth
- Client data overwritten on sync
- Prevents data loss from client crashes

### 4. Asynchronous Sync
- Don't block on server requests
- Background sync thread
- Configurable sync interval (default: 5 minutes)
- Queue failed operations for retry

## Testing Strategy

### Unit Tests
- Test HybridUserDataManager locally
- Test fallback when server down
- Test cache consistency

### Integration Tests
- Test end-to-end migration
- Test data integrity before/after
- Test concurrent access

### Load Tests
- Test with all 11 existing users
- Test with 100+ users (simulate growth)
- Test server response times

## Risk Mitigation

### Risk: Data Loss During Migration
**Mitigation**: 
- Always maintain local cache
- Validate checksums before/after
- Keep multiple backup versions

### Risk: Server Downtime
**Mitigation**:
- Hybrid manager automatically falls back to cache
- Operations queue up for retry
- No user impact

### Risk: Data Inconsistency
**Mitigation**:
- Implement conflict resolution policy
- Server data always wins
- Regular data validation checks

## Timeline

### Week 1: Preparation (DONE)
- Fix bugs
- Create tests
- Create migration tool

### Week 2: New User Integration
- Modify onboarding to use HybridUserDataManager
- Test with new registrations
- Verify fallback mechanism

### Week 3: Selective Migration
- Offer migration to existing users
- Run migration script
- Monitor for issues

### Week 4: Full Migration
- Migrate remaining users
- Enable server-first mode
- Monitor system health

### Week 5+: Optimization
- Fine-tune sync intervals
- Add monitoring/alerting
- Decommission old storage (optional)

## Success Criteria

- ✅ 100% of users can read/write data
- ✅ No data loss during migration
- ✅ Server uptime ≥ 99%
- ✅ Sync latency < 5 seconds
- ✅ Offline mode works seamlessly
- ✅ Zero impact on user experience

## Rollback Plan

If issues occur:

1. **Stop sync to server**: Turn off automatic sync
2. **Use local cache**: All operations use local data
3. **Investigate**: Identify root cause
4. **Fix**: Deploy fix to server
5. **Gradual restart**: Gradually re-enable sync

## Next Steps

1. **Immediate** (Next iteration):
   - Integrate HybridUserDataManager into registration flow
   - Update onboarding_manager to use hybrid manager
   - Test new user registrations

2. **Short-term** (Next 2 weeks):
   - Implement automatic sync service
   - Add data validation checks
   - Create dashboard to monitor migration status

3. **Medium-term** (Next month):
   - Run full migration of existing users
   - Deploy server-side API endpoints
   - Switch to server-primary mode

4. **Long-term** (Ongoing):
   - Monitor system performance
   - Optimize cache and sync
   - Plan for future features (cloud sync, etc.)

