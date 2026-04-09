# Duplicate User Account Error Fix

## Problem
When users with existing GitHub accounts in the database tried to login, they received a 500 error:
```
❌ 错误: 同步用户账户失败: request failed with status 500: 
{"error":"Failed to create user account: pq: duplicate key value violates 
unique constraint \"user_accounts_github_id_key\""}
```

## Root Cause
The `CreateOrGetUserAccount` endpoint in the judge-server was attempting to INSERT a new user record without checking if the account already existed. This violated the unique constraint on `github_id`.

## Solution
Implemented graceful error handling in the CLI login flow to handle duplicate account errors:

1. **Login Screen** (`app.go`):
   - Catch errors from `CreateOrGetUserAccount` call
   - Check if error contains "duplicate key" or "already exists"
   - If duplicate error: Continue gracefully with a welcome-back message
   - If other error: Display actual error and return to login

2. **Account Selection Screen** (`account_select.go`):
   - Apply same logic when switching between accounts
   - Handle duplicate account errors when syncing selected account
   - Allow account switch to proceed even if sync returns duplicate error

## Implementation Details

### Login Flow (app.go)
```go
// Create or sync user account with judge-server
if a.CurrentUser.ID > 0 {
    _, err := a.Client.CreateOrGetUserAccount(a.CurrentUser.ID, a.CurrentUser.Login)
    if err != nil {
        // Check if error is due to duplicate account (account already exists)
        if strings.Contains(err.Error(), "duplicate key") || strings.Contains(err.Error(), "already exists") {
            // Account already exists, continue (this is not an error)
            a.Message = fmt.Sprintf("欢迎回来, %s!", a.CurrentUser.Login)
        } else {
            // Different error occurred
            a.Error = fmt.Sprintf("同步用户账户失败: %v", err)
            return a, nil
        }
    }
}
```

### Account Switch Flow (account_select.go)
```go
// Sync with server
if user.ID > 0 {
    _, err := a.Client.CreateOrGetUserAccount(user.ID, user.Login)
    // Handle duplicate account error gracefully
    if err != nil && !strings.Contains(err.Error(), "duplicate key") && !strings.Contains(err.Error(), "already exists") {
        a.AccountSelectState.Error = fmt.Sprintf("同步账户失败: %v", err)
        a.AccountSelectState.Loading = false
        return
    }
}
```

## User Experience

### Before Fix
1. User enters CLI
2. Presses Enter on login screen
3. Gets error: "同步用户账户失败: duplicate key..."
4. Cannot proceed to main menu

### After Fix
1. User enters CLI
2. Presses Enter on login screen
3. If account exists: Shows "欢迎回来, username!" and proceeds
4. User can now access the main menu

## Scenarios Handled

✅ **First-time login**: Account gets created, user proceeds
✅ **Returning user**: Account already exists, duplicate error is ignored, user proceeds
✅ **Account switching**: Duplicate errors handled during account switch
✅ **Other errors**: Non-duplicate errors are still reported to user

## Files Modified

- `cli/pkg/ui/app.go` - Enhanced error handling in login flow
- `cli/pkg/ui/account_select.go` - Enhanced error handling in account switch

## Testing

### Test Scenario 1: First-time Login
```
User with no existing account in database
→ Login → Account created → Main menu ✅
```

### Test Scenario 2: Returning User
```
User with existing account in database
→ Login → Duplicate error caught → "欢迎回来" message → Main menu ✅
```

### Test Scenario 3: Account Switching
```
Multiple accounts, one has existing record
→ Select account → Duplicate error caught → Account switched ✅
```

### Test Scenario 4: Actual Server Errors
```
Server returns different error
→ Login → Error displayed → Can retry ✅
```

## Commit Information
- Hash: `51f53d3`
- Message: "fix: handle duplicate user account error gracefully"

## Long-term Solution

For a more robust solution, consider:

1. **Backend Enhancement**: 
   - Modify `/api/users/create` endpoint to truly be "CreateOrGet"
   - Check if account exists before creating
   - Return existing account if it does exist
   - Only create if it doesn't exist

2. **Database-level Solution**:
   - Use `INSERT ... ON CONFLICT DO UPDATE` (PostgreSQL)
   - Or `UPSERT` functionality if available

3. **New Endpoint**:
   - Create dedicated `/api/users/sync` endpoint
   - Specifically handles account synchronization
   - Always returns account (creates if needed)

## Impact

✅ Users with existing accounts can now login successfully
✅ Multiple account switching works properly  
✅ Better error messages and user experience
✅ Graceful handling of duplicate account scenarios
✅ No breaking changes to existing code

## Status
✅ **RESOLVED** - Users can now login and switch accounts without duplicate key errors

