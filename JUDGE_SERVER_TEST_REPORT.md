# Judge Server API Test Report

**Test Date**: 2026-04-07  
**Test Environment**: localhost:10000  
**Database**: PostgreSQL agent_monster  
**Overall Success Rate**: 70.6% (12/17 tests passed)

## Test Summary

| Category | Tests | Passed | Failed | Status |
|----------|-------|--------|--------|--------|
| Health Check | 1 | 1 | 0 | ✓ |
| User Account Management | 1 | 0 | 1 | ✗ |
| Farm Management | 2 | 2 | 0 | ✓ |
| Cookie Management | 3 | 1 | 2 | ⚠️ |
| Egg Management | 2 | 1 | 1 | ⚠️ |
| Shop Management | 3 | 2 | 1 | ⚠️ |
| Validation Endpoints | 5 | 5 | 0 | ✓ |
| **Total** | **17** | **12** | **5** | **70.6%** |

## Detailed Test Results

### ✓ Working Endpoints

1. **Health Check** (GET /health)
   - Status: ✓ Healthy
   - Response: `{"status":"healthy"}`

2. **Farm Management**
   - Create Farm: ✓ Working
   - Search Farms: ✓ Working

3. **Shop Management (Partial)**
   - List Shop Items: ✓ Working
   - Shop Statistics: ✓ Working

4. **Validation Endpoints (All Working)**
   - Validate Pet: ✓ Working
   - Validate Battle: ✓ Working
   - Validate Food: ✓ Working
   - Record Food: ✓ Working
   - Record Growth: ✓ Working

### ✗ Issues Found

#### 1. User Account Creation - Status Code Issue
**Endpoint**: POST /api/users/create  
**Issue**: Returns 201 (Created) instead of 200 (OK)  
**Expected**: 200  
**Actual**: 201  
**Severity**: Low (Functional, just wrong status code)  
**Fix**: Update expected status code to 201

```json
{
  "message": "User account created",
  "success": true,
  "user": {
    "id": 4,
    "github_id": 890535,
    "github_login": "",
    "email": "",
    "avatar_url": "",
    "balance": 0,
    "created_at": "2026-04-07T16:55:12.637016Z"
  }
}
```

#### 2. Register Cookie - 500 Server Error
**Endpoint**: POST /api/cookies/register  
**Issue**: Internal Server Error  
**Error**: `{"error":"Failed to register cookie","success":false}`  
**Severity**: High (API broken)  
**Cause**: Likely database constraint or data validation issue  
**Investigation Needed**: 
- Check cookies table schema
- Verify register cookie handler implementation
- Check for NULL constraint violations

#### 3. Scan Cookies - Missing Parameter
**Endpoint**: GET /api/cookies/scan  
**Issue**: Missing required `player_id` parameter  
**Error**: `{"error":"Missing player_id parameter","success":false}`  
**Severity**: Medium (API working as designed, but needs better documentation)  
**Fix**: Add `player_id` parameter to requests: `GET /api/cookies/scan?player_id=testuser`

#### 4. Create Egg - Duplicate Key Constraint
**Endpoint**: POST /api/eggs/create  
**Issue**: Duplicate egg_id error  
**Error**: `pq: duplicate key value violates unique constraint "eggs_egg_id_key"`  
**Severity**: High (API broken)  
**Cause**: UUID/ID generation issue or concurrent requests  
**Investigation Needed**:
- Check egg_id generation logic
- Verify UUID uniqueness
- Check if database has existing test data

#### 5. Transaction History - 500 Server Error
**Endpoint**: GET /api/shop/transactions?player_id=testuser  
**Issue**: Internal Server Error  
**Error**: `{"error":"Failed to get transactions","success":false}`  
**Severity**: High (API broken)  
**Investigation Needed**:
- Check transaction query implementation
- Verify player_id exists in database
- Check for NULL/empty data handling

## Database Issues Detected

1. **Eggs table**: Constraint violation on egg_id (duplicate key)
   - Suggest: Rebuild test data or implement better UUID generation

2. **Cookies table**: Register operation failing
   - Suggest: Verify schema and data types

3. **Transactions table**: Query operation failing
   - Suggest: Check query implementation and data existence

## Recommendations

### Priority 1 (Critical)
- [ ] Fix Cookie registration 500 error
- [ ] Fix Egg creation duplicate key error
- [ ] Fix Transaction history 500 error
- [ ] Debug database constraints

### Priority 2 (Important)
- [ ] Update API documentation for parameter requirements
- [ ] Add player_id to Scan Cookies endpoint documentation
- [ ] Review error messages for clarity

### Priority 3 (Nice to Have)
- [ ] Consider using 201 for POST endpoints that create resources
- [ ] Add more descriptive error messages
- [ ] Implement request validation middleware

## Test Data Issues

- Egg creation fails with "duplicate key" error
- Possible causes:
  1. Test data from previous runs not cleaned up
  2. UUID generation not unique
  3. Database constraints too strict

**Suggestion**: Clear test data between runs or use unique identifiers

## Next Steps

1. Check Judge Server logs for detailed error messages
2. Inspect database schema for constraints
3. Review handler implementations for error handling
4. Run database integrity checks
5. Consider adding database reset/cleanup for tests

## Conclusion

Judge Server is **partially functional** with a **70.6% success rate**. 

**Key Issues**:
- Core validation endpoints work perfectly (100%)
- Farm management works well (100%)
- Cookie and egg management have issues (50% success rate)
- Transaction history needs investigation

**Recommendation**: Debug the database constraint and error handling issues before using in production.

