package ui

import (
	"agent-monster-cli/pkg/github"
	"fmt"
	tea "github.com/charmbracelet/bubbletea"
	"strings"
)

// renderAccountSelectScreen renders the GitHub account selection screen
func (a *App) renderAccountSelectScreen() string {
	title := StyleTitle.
		Foreground(ColorWarning).
		Render("╔════════════════════════════════════════╗\n║     选择 GitHub 账户                   ║\n╚════════════════════════════════════════╝")

	if a.AccountSelectState.Loading {
		loading := StyleDim.Render("⏳ 加载账户信息中...")
		return title + "\n\n" + loading
	}

	if len(a.AccountSelectState.Accounts) == 0 {
		empty := StyleError.Render("❌ 未找到GitHub账户")
		return title + "\n\n" + empty
	}

	var content strings.Builder
	content.WriteString("检测到多个 GitHub 账户，请选择一个账户:\n\n")

	for i, account := range a.AccountSelectState.Accounts {
		status := ""
		if account.Active {
			status = " (当前)"
		}

		if i == a.AccountSelectState.SelectedIndex {
			content.WriteString(StyleMenuItemSelected.Render(
				fmt.Sprintf("  ▶ %s - %s%s\n", account.Hostname, account.Username, status)))
		} else {
			content.WriteString(StyleMenuItem.Render(
				fmt.Sprintf("    %s - %s%s\n", account.Hostname, account.Username, status)))
		}
	}

	help := StyleDim.Render("\n⬆️ ⬇️  选择账户  Enter 确认  Esc 返回")

	return title + "\n" + content.String() + help
}

// handleAccountSelect handles input on the account selection screen
func (a *App) handleAccountSelect(msg tea.KeyMsg) (*App, tea.Cmd) {
	switch msg.String() {
	case "up", "k":
		if a.AccountSelectState.SelectedIndex > 0 {
			a.AccountSelectState.SelectedIndex--
		}

	case "down", "j":
		if a.AccountSelectState.SelectedIndex < len(a.AccountSelectState.Accounts)-1 {
			a.AccountSelectState.SelectedIndex++
		}

	case "enter":
		// Switch to selected account
		if a.AccountSelectState.SelectedIndex < len(a.AccountSelectState.Accounts) {
			selected := a.AccountSelectState.Accounts[a.AccountSelectState.SelectedIndex]
			a.AccountSelectState.Loading = true

			// Try to switch account (this is async in real implementation)
			go func() {
				err := github.SwitchAccount(selected.Hostname, selected.Username)
				if err != nil {
					a.AccountSelectState.Error = fmt.Sprintf("切换账户失败: %v", err)
				} else {
					// Reinitialize GitHub client with new account
					ghClient, err := github.NewGitHubClient()
					if err == nil {
						a.GitHub = ghClient
						// Get the new user info
						user, err := ghClient.GetCurrentUser()
						if err == nil {
							a.CurrentUser = user
							a.AccountSelectState.Message = fmt.Sprintf("已切换到账户: %s", user.Login)

							// Sync with server
							if user.ID > 0 {
								a.Client.CreateOrGetUserAccount(user.ID, user.Login)
							}

							// Update profile
							if a.UserManager != nil {
								a.UserManager.GetOrCreateProfile(user.Login, 0)
								a.UserProfile, _ = a.UserManager.GetProfile(user.Login)
							}

							// Move to main menu
							a.CurrentScreen = MainMenuScreen
							a.SelectedIndex = 0
						}
					}
				}
				a.AccountSelectState.Loading = false
			}()
		}

	case "esc":
		// Return to login screen
		a.CurrentScreen = LoginScreen
		a.SelectedIndex = 0
		a.AccountSelectState.SelectedIndex = 0
	}

	return a, nil
}
