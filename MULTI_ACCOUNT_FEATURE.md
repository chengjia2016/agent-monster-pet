# GitHub Multi-Account Selection Feature

## Overview

Successfully implemented support for selecting between multiple GitHub accounts when multiple accounts are logged into `gh` CLI.

## Features Added

### 1. **Multiple Account Detection**
- Automatically detects when user has multiple GitHub accounts logged in via `gh auth`
- Uses `gh auth status` command to retrieve account information
- Parses account hostname and username from CLI output

### 2. **Account Selection Screen**
- New `AccountSelectScreen` in CLI navigation flow
- Display all available GitHub accounts with hostnames and usernames
- Show current/active account status
- Navigate with arrow keys (↑/↓ or K/J)
- Select with Enter key

### 3. **Account Switching**
- Users can switch between GitHub accounts seamlessly
- Automatically reinitializes GitHub client with new account
- Updates current user information
- Syncs with backend judge-server
- Updates user profile in local storage

## Implementation Details

### New Components

#### 1. `cli/pkg/github/client.go` - Updated
- Added `AuthAccount` struct to represent GitHub accounts
- Added `GetAuthAccounts()` function to parse `gh auth status` output
- Added `SwitchAccount()` function to switch between accounts
- Both functions interact with GitHub CLI

```go
type AuthAccount struct {
    Hostname string
    Username string
    Active   bool
}

func GetAuthAccounts() ([]AuthAccount, error)
func SwitchAccount(hostname, username string) error
```

#### 2. `cli/pkg/ui/account_select.go` - New File
- `renderAccountSelectScreen()` - Renders the account selection UI
- `handleAccountSelect()` - Handles keyboard input for account selection
- Full state management for account selection flow

#### 3. `cli/pkg/ui/app.go` - Updated
- Added `AccountSelectScreen` constant to Screen enum
- Added `AccountSelectState` struct to track selection state
- Added `AccountSelectState` field to App struct
- Updated `NewApp()` to initialize account state
- Updated `Update()` to handle account selection input
- Updated `View()` to render account selection screen
- Updated login flow to detect and prompt for multiple accounts

## User Flow

### Single Account (Existing Behavior)
```
Login Screen → GitHub Client Init → Get Current User → Main Menu
```

### Multiple Accounts (New Behavior)
```
Login Screen → Detect Multiple Accounts → Account Selection Screen
    ↓
Select Account → Switch to Selected Account → Get User Info → Main Menu
```

## Keyboard Controls

On Account Selection Screen:
- **↑ / K** - Move selection up
- **↓ / J** - Move selection down
- **Enter** - Confirm selection and switch to account
- **Esc** - Return to login screen

## Display Format

```
╔════════════════════════════════════════╗
║     选择 GitHub 账户                   ║
╚════════════════════════════════════════╝

检测到多个 GitHub 账户，请选择一个账户:

  ▶ github.com - username1 (当前)
    github.com - username2
    github.com - username3

⬆️ ⬇️  选择账户  Enter 确认  Esc 返回
```

## Technical Implementation

### Account Detection Logic
1. Run `gh auth status --show-token` command
2. Parse output for "Logged in to" lines
3. Extract hostname and username from each line
4. Build list of `AuthAccount` objects
5. Return list to UI layer

### Account Switching Logic
1. Execute `gh auth switch -h [hostname]` command
2. Reinitialize GitHub client with new credentials
3. Fetch current user information
4. Update application state
5. Sync with backend
6. Proceed to main menu

### Error Handling
- If account switch fails, display error message
- Allow user to retry or return to login
- Graceful fallback if no accounts found

## State Management

### AccountSelectState Structure
```go
type AccountSelectState struct {
    Accounts        []github.AuthAccount  // Available accounts
    SelectedIndex   int                   // Currently selected account
    Loading         bool                  // Loading indicator
    Error           string                // Error message
    Message         string                // Status message
}
```

## Integration Points

1. **Login Flow**: Modified LoginScreen handler to check for multiple accounts
2. **GitHub Client**: Uses existing GitHub CLI infrastructure
3. **User Management**: Integrates with existing user profile system
4. **Main Menu**: Seamlessly transitions to main menu after account selection

## Benefits

✅ **User Choice**: Users can work with multiple GitHub accounts
✅ **Seamless Switching**: Quick account switching without re-authentication
✅ **Automatic Detection**: No configuration needed
✅ **Backward Compatible**: Single account flow unchanged
✅ **Data Sync**: Automatically syncs with backend

## Future Enhancements

1. **Account Management Screen**: Allow adding/removing accounts from CLI
2. **Quick Switch Command**: Direct command to switch accounts
3. **Account Favorites**: Mark preferred account for quick access
4. **Session Persistence**: Remember last used account
5. **Multi-Account Operations**: Support operations across accounts

## Testing Scenarios

### Scenario 1: Single Account
- Only one GitHub account logged in
- Login → Get User → Main Menu (no account selection screen)

### Scenario 2: Two Accounts
- Two GitHub accounts logged in
- Login → Account Selection → Select Account → Main Menu

### Scenario 3: Multiple Accounts
- 3+ GitHub accounts logged in
- Login → Account Selection (with scrolling) → Select Account → Main Menu

### Scenario 4: Account Switch Error
- Try to switch to account
- Error occurs in switch process
- Error message displayed
- User can retry

## Files Modified/Created

```
cli/pkg/github/
├── client.go                      [MODIFIED]
│   ├── AuthAccount struct
│   ├── GetAuthAccounts() function
│   └── SwitchAccount() function

cli/pkg/ui/
├── app.go                         [MODIFIED]
│   ├── AccountSelectScreen constant
│   ├── AccountSelectState struct
│   ├── handleAccountSelect() in Update
│   └── Account selection screen in View()
├── account_select.go              [NEW]
│   ├── renderAccountSelectScreen()
│   └── handleAccountSelect()
```

## Compilation Status

✅ **Build Successful** - All code compiles without errors
✅ **No New Dependencies** - Uses existing Go standard library
✅ **Integration Complete** - Seamlessly integrated with existing code
✅ **Backward Compatible** - No breaking changes to existing flow

## Summary

The multi-account selection feature enables users to work with multiple GitHub accounts in the Agent Monster CLI. When multiple accounts are detected, users are presented with a simple selection interface to choose which account to use. The implementation is clean, efficient, and fully integrated into the existing authentication flow.

