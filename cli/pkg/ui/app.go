package ui

import (
	"agent-monster-cli/pkg/api"
	"agent-monster-cli/pkg/github"
	"agent-monster-cli/pkg/user"
	"fmt"
	tea "github.com/charmbracelet/bubbletea"
	"strings"
)

type Screen int

const (
	LoginScreen Screen = iota
	AccountSelectScreen
	MainMenuScreen
	PokemonListScreen
	BattleScreen
	DefenseScreen
	WildPokemonScreen
	DetailScreen
	GitHubScreen
	ProfileScreen
	GitHubReposScreen
	GitHubIssuesScreen
	GitHubPullRequestsScreen
	MapScreen
	MapInputScreen
	OnboardingScreen
)

// GitHubScreenState tracks GitHub screen state
type GitHubScreenState struct {
	Repositories []github.Repository
	Issues       []github.Issue
	PullRequests []github.PullRequest
	CurrentRepo  string
	IssueState   string // "open" or "closed"
	PRState      string // "open" or "closed"
}

// AccountSelectState tracks account selection state
type AccountSelectState struct {
	Accounts      []github.AuthAccount
	SelectedIndex int
	Loading       bool
	Error         string
	Message       string
}

// MapState tracks map screen state
type MapState struct {
	CurrentMap       *api.MapData
	PlayerX          int
	PlayerY          int
	InputBuffer      string // For GitHub link or map ID input
	TargetRepoURL    string // GitHub repository URL
	SelectedMapIndex int
	AllMaps          []api.MapData
}

// App 是主应用模型
type App struct {
	Client             *api.Client
	GitHub             *github.GitHubClient
	UserManager        *user.Manager
	CurrentScreen      Screen
	Width              int
	Height             int
	SelectedIndex      int
	Loading            bool
	Error              string
	Message            string
	CurrentUser        *github.User
	UserProfile        *user.UserProfile
	GitHubState        *GitHubScreenState
	MapState           *MapState
	PreviousScreen     Screen
	OnboardingState    *OnboardingState
	AccountSelectState *AccountSelectState
}

// NewApp 创建新应用实例
func NewApp(client *api.Client, userDir string) *App {
	return &App{
		Client:        client,
		UserManager:   user.NewManager(userDir),
		CurrentScreen: LoginScreen,
		SelectedIndex: 0,
		Loading:       false,
		GitHubState:   &GitHubScreenState{},
		MapState: &MapState{
			PlayerX: 0,
			PlayerY: 0,
		},
		OnboardingState: &OnboardingState{
			CurrentStep:      0,
			SelectedTemplate: 0,
			SelectedNPCs:     make([]bool, 0),
			InputBuffer:      "",
		},
		AccountSelectState: &AccountSelectState{
			Accounts:      make([]github.AuthAccount, 0),
			SelectedIndex: 0,
			Loading:       false,
		},
	}
}

// Init 初始化应用
func (a *App) Init() tea.Cmd {
	return nil
}

// Update 处理事件更新
func (a *App) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	switch msg := msg.(type) {
	case OnboardingOperationMsg:
		// Handle onboarding operation result
		a.OnboardingState.Loading = false

		if !msg.Success {
			a.OnboardingState.Error = msg.Error
			return a, nil
		}

		// Handle successful operations
		switch msg.Operation {
		case "fork":
			a.OnboardingState.RepoForked = true
			a.OnboardingState.Message = "✅ Fork 成功！"
			a.OnboardingState.CurrentStep = int(OnboardingBaseScreen)
		case "createbase":
			a.OnboardingState.BaseCreated = true
			a.OnboardingState.Message = "✅ 基地创建成功！"
			a.OnboardingState.CurrentStep = int(OnboardingTemplateScreen)
		case "generatemap":
			a.OnboardingState.CurrentStep = int(OnboardingClaimingScreen)
			// Trigger the claiming operation in a command
			return a, claimStarterPokemonsCmd(a)
		case "claiming":
			// Claiming operation completed, move to complete screen
			a.OnboardingState.PokemonsClaimed = true
			a.OnboardingState.CurrentStep = int(OnboardingCompleteScreen)
			a.OnboardingState.Message = "✅ 宝可梦领取成功！"
		}
		return a, nil

	case SwitchAccountMsg:
		// Handle account switch result
		a.AccountSelectState.Loading = false

		if msg.Error != "" {
			a.AccountSelectState.Error = msg.Error
			return a, nil
		}

		if msg.User != nil {
			a.CurrentUser = msg.User
			a.AccountSelectState.Message = fmt.Sprintf("已切换到账户: %s", msg.User.Login)

			// Reinitialize GitHub client for new account
			ghClient, err := github.NewGitHubClient()
			if err == nil {
				a.GitHub = ghClient
			}

			// Sync with server
			if msg.User.ID > 0 {
				_, err := a.Client.CreateOrGetUserAccount(msg.User.ID, msg.User.Login)
				// Handle duplicate account error gracefully
				if err != nil && !strings.Contains(err.Error(), "duplicate key") && !strings.Contains(err.Error(), "already exists") {
					a.AccountSelectState.Error = fmt.Sprintf("同步账户失败: %v", err)
					return a, nil
				}
			}

			// Update profile with correct GitHub ID
			if a.UserManager != nil {
				a.UserManager.GetOrCreateProfile(msg.User.Login, msg.User.ID)
				a.UserProfile, _ = a.UserManager.GetProfile(msg.User.Login)
			}

			// Reset account selection state
			a.AccountSelectState = &AccountSelectState{
				Accounts:      make([]github.AuthAccount, 0),
				SelectedIndex: 0,
				Loading:       false,
			}

			// Move to main menu
			a.CurrentScreen = MainMenuScreen
			a.SelectedIndex = 0
		}
		return a, nil

	case tea.KeyMsg:
		// Handle account select screen separately
		if a.CurrentScreen == AccountSelectScreen {
			return a.handleAccountSelect(msg)
		}

		// Handle map input screen separately
		if a.CurrentScreen == MapInputScreen {
			return a.HandleMapInputScreenInput(msg)
		}

		// Handle map screen navigation
		if a.CurrentScreen == MapScreen {
			cmd := a.HandleMapInput(msg)
			return a, cmd
		}

		// Handle onboarding screen
		if a.CurrentScreen == OnboardingScreen {
			return a.handleOnboarding(msg)
		}

		// Regular menu navigation
		switch msg.String() {
		case "ctrl+c", "q":
			return a, tea.Quit

		case "up", "k":
			maxIndex := a.getMaxMenuIndex()
			if a.SelectedIndex > 0 {
				a.SelectedIndex--
			} else {
				// Wrap to last item
				a.SelectedIndex = maxIndex
			}

		case "down", "j":
			maxIndex := a.getMaxMenuIndex()
			if a.SelectedIndex < maxIndex {
				a.SelectedIndex++
			} else {
				// Wrap to first item
				a.SelectedIndex = 0
			}

		case "enter", "l":
			return a.handleMenuSelect()

		case "esc", "h", "backspace":
			// BackSpace key to go back to main menu
			if a.CurrentScreen != MainMenuScreen && a.CurrentScreen != LoginScreen {
				a.CurrentScreen = MainMenuScreen
				a.SelectedIndex = 0
			}
		}

	case tea.WindowSizeMsg:
		a.Width = msg.Width
		a.Height = msg.Height
	}
	return a, nil
}

// View 渲染UI
func (a *App) View() string {
	content := ""

	switch a.CurrentScreen {
	case LoginScreen:
		content = a.renderLoginScreen()
	case AccountSelectScreen:
		content = a.renderAccountSelectScreen()
	case MainMenuScreen:
		content = a.mainMenuView()
	case PokemonListScreen:
		content = a.RenderPokemonList()
	case BattleScreen:
		content = a.RenderBattleScreen()
	case DefenseScreen:
		content = a.RenderDefenseScreen()
	case WildPokemonScreen:
		content = a.RenderWildPokemonScreen()
	case DetailScreen:
		content = a.RenderDetailScreen()
	case GitHubScreen:
		content = a.renderGitHubScreen()
	case ProfileScreen:
		content = a.renderProfileScreen()
	case GitHubReposScreen:
		content = a.renderGitHubReposScreen()
	case GitHubIssuesScreen:
		content = a.renderGitHubIssuesScreen()
	case GitHubPullRequestsScreen:
		content = a.renderGitHubPullRequestsScreen()
	case MapInputScreen:
		content = a.renderMapInputScreen()
	case MapScreen:
		content = a.renderMapScreen()
	case OnboardingScreen:
		content = a.renderOnboarding()
	}

	// 添加加载状态
	if a.Loading {
		content += "\n" + StyleDim.Render("⏳ 加载中...")
	}

	// 添加错误或消息显示
	if a.Error != "" {
		content += "\n" + StyleError.Render("❌ 错误: "+a.Error)
	}
	if a.Message != "" {
		content += "\n" + StyleSuccess.Render("✅ "+a.Message)
	}

	return content
}

func (a *App) getMaxMenuIndex() int {
	switch a.CurrentScreen {
	case MainMenuScreen:
		return 8 // 9个菜单项 (0-8)
	case BattleScreen:
		return 3 // 4个选项
	case DefenseScreen:
		return 4 // 5个选项
	case WildPokemonScreen:
		return 3 // 4个精灵
	case PokemonListScreen:
		return 2 // 3只宠物
	case GitHubScreen:
		return 3 // 4个选项
	case GitHubReposScreen:
		if len(a.GitHubState.Repositories) > 0 {
			return len(a.GitHubState.Repositories) - 1
		}
		return 0
	case GitHubIssuesScreen:
		if len(a.GitHubState.Issues) > 0 {
			return len(a.GitHubState.Issues) - 1
		}
		return 0
	case GitHubPullRequestsScreen:
		if len(a.GitHubState.PullRequests) > 0 {
			return len(a.GitHubState.PullRequests) - 1
		}
		return 0
	default:
		return 0
	}
}

func (a *App) handleMenuSelect() (*App, tea.Cmd) {
	switch a.CurrentScreen {
	case LoginScreen:
		// Clear any previous errors
		a.Error = ""
		a.Message = ""

		// When Enter is pressed on login screen, move to main menu
		if a.GitHub == nil {
			ghClient, err := github.NewGitHubClient()
			if err != nil {
				a.Error = fmt.Sprintf("GitHub 客户端初始化失败: %v", err)
				return a, nil
			}
			a.GitHub = ghClient
		}

		// Check if there are multiple GitHub accounts logged in
		accounts, err := github.GetAuthAccounts()
		if err == nil && len(accounts) > 1 {
			// Multiple accounts found, show selection screen
			a.AccountSelectState.Accounts = accounts
			a.AccountSelectState.SelectedIndex = 0
			a.CurrentScreen = AccountSelectScreen
			a.SelectedIndex = 0
			return a, nil
		}

		// Get current user info
		currentUser, err := a.GitHub.GetCurrentUser()
		if err == nil {
			a.CurrentUser = currentUser

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

			// Save or create user profile
			if a.UserManager != nil {
				_, err := a.UserManager.GetOrCreateProfile(currentUser.Login, 0)
				if err != nil {
					a.Error = fmt.Sprintf("保存用户资料失败: %v", err)
					return a, nil
				}
				a.UserProfile, _ = a.UserManager.GetProfile(currentUser.Login)
			}
		} else {
			a.Error = fmt.Sprintf("获取用户信息失败: %v", err)
			return a, nil
		}
		if a.Message == "" {
			a.Message = fmt.Sprintf("欢迎, %s!", currentUser.Login)
		}
		a.CurrentScreen = MainMenuScreen
		a.SelectedIndex = 0

	case MainMenuScreen:
		switch a.SelectedIndex {
		case 0:
			// 开始新手引导
			a.CurrentScreen = OnboardingScreen
			a.OnboardingState.CurrentStep = 0
			a.OnboardingState.RepoForked = false
			a.OnboardingState.BaseCreated = false
			a.OnboardingState.SelectedTemplate = 0
			a.OnboardingState.SelectedNPCs = make([]bool, 0)
		case 1:
			a.CurrentScreen = PokemonListScreen
		case 2:
			a.CurrentScreen = BattleScreen
		case 3:
			a.CurrentScreen = DefenseScreen
		case 4:
			a.CurrentScreen = WildPokemonScreen
		case 5:
			// 开始进入地图模式
			a.MapState.InputBuffer = ""
			a.CurrentScreen = MapInputScreen
			a.SelectedIndex = 0
		case 6:
			a.CurrentScreen = GitHubScreen
		case 7:
			a.CurrentScreen = ProfileScreen
		case 8:
			return a, tea.Quit
		}

	case PokemonListScreen:
		a.CurrentScreen = DetailScreen

	case BattleScreen:
		switch a.SelectedIndex {
		case 0:
			// 选择对手进行PvP战斗
			a.Message = "选择对手功能将在下一版本实现"
		case 1:
			// 查看战斗记录
			a.Message = "战斗记录功能将在下一版本实现"
		case 2:
			// 战斗统计
			a.Message = "战斗统计功能将在下一版本实现"
		case 3:
			// 返回主菜单
			a.CurrentScreen = MainMenuScreen
		}

	case DefenseScreen:
		if a.SelectedIndex == 4 {
			a.CurrentScreen = MainMenuScreen
		} else {
			a.Message = fmt.Sprintf("防守操作: %d", a.SelectedIndex)
		}

	case WildPokemonScreen:
		a.Message = fmt.Sprintf("尝试捕获精灵 %d", a.SelectedIndex)
		// In a full implementation, this would call the API to attempt capture

	case DetailScreen:
		a.CurrentScreen = PokemonListScreen

	case GitHubScreen:
		switch a.SelectedIndex {
		case 0:
			// 查看仓库 - 加载数据
			a.PreviousScreen = GitHubScreen
			a.CurrentScreen = GitHubReposScreen
			a.SelectedIndex = 0
			a.Loading = true
			// Load repositories in background
			go func() {
				if err := a.LoadGitHubRepositories(); err != nil {
					a.Error = fmt.Sprintf("加载仓库失败: %v", err)
				}
				a.Loading = false
			}()
		case 1:
			// 查看Issues - 加载数据
			a.PreviousScreen = GitHubScreen
			a.CurrentScreen = GitHubIssuesScreen
			a.SelectedIndex = 0
			a.Loading = true
			// Load issues in background
			go func() {
				if err := a.LoadGitHubRepositories(); err == nil {
					if err := a.LoadGitHubIssues(); err != nil {
						a.Error = fmt.Sprintf("加载Issues失败: %v", err)
					}
				} else {
					a.Error = fmt.Sprintf("加载仓库失败: %v", err)
				}
				a.Loading = false
			}()
		case 2:
			// 查看Pull Requests - 加载数据
			a.PreviousScreen = GitHubScreen
			a.CurrentScreen = GitHubPullRequestsScreen
			a.SelectedIndex = 0
			a.Loading = true
			// Load PRs in background
			go func() {
				if err := a.LoadGitHubRepositories(); err == nil {
					if err := a.LoadGitHubPullRequests(); err != nil {
						a.Error = fmt.Sprintf("加载PRs失败: %v", err)
					}
				} else {
					a.Error = fmt.Sprintf("加载仓库失败: %v", err)
				}
				a.Loading = false
			}()
		case 3:
			// 返回主菜单
			a.CurrentScreen = MainMenuScreen
		}

	case ProfileScreen:
		a.CurrentScreen = MainMenuScreen

	case GitHubReposScreen:
		// 返回GitHub菜单
		a.CurrentScreen = GitHubScreen
		a.SelectedIndex = 0

	case GitHubIssuesScreen:
		// 返回GitHub菜单
		a.CurrentScreen = GitHubScreen
		a.SelectedIndex = 0

	case GitHubPullRequestsScreen:
		// 返回GitHub菜单
		a.CurrentScreen = GitHubScreen
		a.SelectedIndex = 0
	}

	// Reset selected index for menu
	a.SelectedIndex = 0
	return a, nil
}

// LoadGitHubRepositories loads GitHub repositories asynchronously
func (a *App) LoadGitHubRepositories() error {
	if a.GitHub == nil {
		return fmt.Errorf("GitHub client not initialized")
	}

	repos, err := a.GitHub.ListUserRepositories()
	if err != nil {
		return err
	}

	a.GitHubState.Repositories = repos
	return nil
}

// LoadGitHubIssues loads GitHub issues asynchronously
func (a *App) LoadGitHubIssues() error {
	if a.GitHub == nil {
		return fmt.Errorf("GitHub client not initialized")
	}

	if len(a.GitHubState.Repositories) == 0 {
		return fmt.Errorf("no repositories loaded")
	}

	// Get issues from the first repository
	repo := a.GitHubState.Repositories[0]
	parts := strings.Split(repo.FullName, "/")
	if len(parts) < 2 {
		return fmt.Errorf("invalid repository name")
	}

	issues, err := a.GitHub.ListIssues(parts[0], parts[1], "open")
	if err != nil {
		return err
	}

	a.GitHubState.Issues = issues
	return nil
}

// LoadGitHubPullRequests loads GitHub pull requests asynchronously
func (a *App) LoadGitHubPullRequests() error {
	if a.GitHub == nil {
		return fmt.Errorf("GitHub client not initialized")
	}

	if len(a.GitHubState.Repositories) == 0 {
		return fmt.Errorf("no repositories loaded")
	}

	// Get PRs from the first repository
	repo := a.GitHubState.Repositories[0]
	parts := strings.Split(repo.FullName, "/")
	if len(parts) < 2 {
		return fmt.Errorf("invalid repository name")
	}

	prs, err := a.GitHub.ListPullRequests(parts[0], parts[1], "open")
	if err != nil {
		return err
	}

	a.GitHubState.PullRequests = prs
	return nil
}

func (a *App) mainMenuView() string {
	menuItems := []string{
		"🎓 新手引导 (Onboarding)",
		"🐾 我的宠物",
		"⚔️  发起战斗",
		"🏰 防守基地",
		"🌍 捕获精灵",
		"🗺️  探索地图",
		"💻 GitHub 集成",
		"👤 个人资料",
		"❌ 退出游戏",
	}

	title := StyleTitle.
		Foreground(ColorWarning).
		Render("╔══════════════════════════════════════╗\n║  Agent Monster - 怪兽对战系统  ║\n╚══════════════════════════════════════╝")

	var menu string
	for i, item := range menuItems {
		if i == a.SelectedIndex {
			menu += StyleMenuItemSelected.Render(fmt.Sprintf("  ▶ %s", item)) + "\n"
		} else {
			menu += StyleMenuItem.Render(fmt.Sprintf("    %s", item)) + "\n"
		}
	}

	footer := StyleDim.Render("\n⬆️ ⬇️  K/J 上下  Enter 选择  BackSpace 返回  Ctrl+C 退出")

	return title + "\n\n" + menu + footer
}
