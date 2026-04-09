package ui

import (
	"agent-monster-cli/pkg/github"
	"fmt"
	tea "github.com/charmbracelet/bubbletea"
	"strings"
)

// SwitchAccountMsg is sent when account switch is complete
type SwitchAccountMsg struct {
	Account github.AuthAccount
	Error   string
	User    *github.User
}

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

		line := fmt.Sprintf("%s - %s%s", account.Hostname, account.Username, status)

		if i == a.AccountSelectState.SelectedIndex {
			// Selected item - simple styling without borders
			content.WriteString("  ▶ " + StyleSuccess.Background(ColorAccent).Render(line) + "\n")
		} else {
			// Unselected item
			content.WriteString("    " + line + "\n")
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
		// Switch to selected account using Bubble Tea command
		if a.AccountSelectState.SelectedIndex < len(a.AccountSelectState.Accounts) {
			selected := a.AccountSelectState.Accounts[a.AccountSelectState.SelectedIndex]
			a.AccountSelectState.Loading = true

			// Return a command that will handle the account switch
			return a, switchAccountCmd(selected, a.Client, a.UserManager)
		}

	case "esc":
		// Return to login screen
		a.CurrentScreen = LoginScreen
		a.SelectedIndex = 0
		a.AccountSelectState.SelectedIndex = 0
	}

	return a, nil
}

// switchAccountCmd returns a Bubble Tea command that switches accounts
func switchAccountCmd(account github.AuthAccount, client interface{}, userMgr interface{}) tea.Cmd {
	return func() tea.Msg {
		// Switch to the selected account
		err := github.SwitchAccount(account.Hostname, account.Username)
		if err != nil {
			return SwitchAccountMsg{
				Account: account,
				Error:   fmt.Sprintf("切换账户失败: %v", err),
			}
		}

		// Reinitialize GitHub client with new account
		ghClient, err := github.NewGitHubClient()
		if err != nil {
			return SwitchAccountMsg{
				Account: account,
				Error:   fmt.Sprintf("初始化GitHub客户端失败: %v", err),
			}
		}

		// Get the new user info
		user, err := ghClient.GetCurrentUser()
		if err != nil {
			return SwitchAccountMsg{
				Account: account,
				Error:   fmt.Sprintf("获取用户信息失败: %v", err),
			}
		}

		return SwitchAccountMsg{
			Account: account,
			User:    user,
			Error:   "",
		}
	}
}
