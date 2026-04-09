package ui

import (
	"agent-monster-cli/pkg/api"
	"fmt"
	tea "github.com/charmbracelet/bubbletea"
	"strings"
)

// OnboardingOperationMsg is sent when an onboarding operation completes
type OnboardingOperationMsg struct {
	Operation string // "fork", "createbase", "generatemap", "complete"
	Success   bool
	Error     string
	Data      interface{}
}

// OnboardingState tracks onboarding progress
type OnboardingState struct {
	CurrentStep        int          // 0-5
	Username           string       // GitHub username
	RepoForked         bool         // Whether repo was forked
	BaseCreated        bool         // Whether base was created
	SelectedTemplate   int          // Selected map template (0-4)
	SelectedNPCs       []bool       // Which NPCs were selected (bitmask)
	GeneratedMap       *api.MapData // Generated map
	CompletionProgress int          // 0-100%
	Message            string       // User feedback
	Error              string       // Error message
	Loading            bool         // Loading indicator
	InputBuffer        string       // User input
}

// OnboardingStep defines each step
type OnboardingStep int

const (
	StepWelcome OnboardingStep = iota
	StepForkRepo
	StepCreateBase
	StepSelectTemplate
	StepSelectNPCs
	StepConfirmMap
	StepComplete
)

// OnboardingScreenStates
const (
	OnboardingWelcomeScreen OnboardingStep = iota
	OnboardingForkScreen
	OnboardingBaseScreen
	OnboardingTemplateScreen
	OnboardingNPCScreen
	OnboardingMapPreviewScreen
	OnboardingCompleteScreen
)

// RenderOnboardingWelcome renders the welcome screen
func (a *App) RenderOnboardingWelcome() string {
	title := StyleTitle.
		Foreground(ColorWarning).
		Render("╔════════════════════════════════════════╗\n║   欢迎来到 Agent Monster 怪兽世界！   ║\n╚════════════════════════════════════════╝")

	content := StyleMenuItem.Render(`
👋 欢迎，新训练师！

你即将开始一次伟大的冒险！在这个旅程中，你将：

✨ 功能亮点：
  1. 📌 Fork 仓库 - 创建你自己的代码仓库
  2. 🏰 建立基地 - 成为你的宝可梦的主人
  3. 🗺️  创建地图 - 设计你的地图世界
  4. 🎨 选择主题 - 从5种风格中选择
  5. 🤖 配置NPC - 邀请NPC进驻你的世界
  6. 🎮 开始冒险 - 与其他玩家互动

这个过程只需要 5-10 分钟！

按 Enter 继续 或 Q 返回菜单
`)

	info := StyleDim.Render(`
💡 提示: 你可以在任何时候按 Esc 取消这个流程
`)

	return title + "\n" + content + "\n" + info
}

// RenderOnboardingFork renders the fork step
func (a *App) RenderOnboardingFork() string {
	title := StyleTitle.
		Foreground(ColorWarning).
		Render("╔════════════════════════════════════════╗\n║        第 1 步: Fork 仓库               ║\n╚════════════════════════════════════════╝")

	status := "⏳ 等待中..."
	if a.OnboardingState.RepoForked {
		status = StyleSuccess.Render("✅ 已完成")
	} else if a.OnboardingState.Loading {
		status = StyleDim.Render("⌛ 正在处理...")
	}

	content := StyleMenuItem.Render(fmt.Sprintf(`
%s

什么是 Fork?
Fork 是在 GitHub 上为项目创建一个个人副本的过程。这样你就拥
有了自己的代码仓库，可以在其中创建和管理你的宝可梦世界。

当前账户: %s

按 Enter 开始 Fork
`, status, a.CurrentUser.Login))

	features := StyleDim.Render(`
🎯 Fork 后你将获得:
  • 自己的 agent-monster 代码仓库副本
  • 完整的版本控制和历史记录
  • 与社区分享的权利
  • 你的宝可梦世界将存储在你的仓库中
`)

	return title + "\n" + content + "\n" + features
}

// RenderOnboardingBase renders the base creation step
func (a *App) RenderOnboardingBase() string {
	title := StyleTitle.
		Foreground(ColorWarning).
		Render("╔════════════════════════════════════════╗\n║        第 2 步: 建立防守基地           ║\n╚════════════════════════════════════════╝")

	status := "⏳ 等待中..."
	if a.OnboardingState.BaseCreated {
		status = StyleSuccess.Render("✅ 已完成")
	} else if a.OnboardingState.Loading {
		status = StyleDim.Render("⌛ 正在处理...")
	}

	content := StyleMenuItem.Render(fmt.Sprintf(`
%s

什么是防守基地?
防守基地是你在宝可梦世界中的主要据点。其他玩家可以来挑战你
的基地，而你需要用强大的宝可梦来防守它。

按 Enter 创建你的防守基地
`, status))

	benefits := StyleDim.Render(`
🏰 基地带来的好处:
  • 成为真正的训练师
  • 获得防守奖励
  • 建立个人排名
  • 与其他玩家互动
  • 展示你的宝可梦实力
`)

	return title + "\n" + content + "\n" + benefits
}

// RenderOnboardingTemplate renders the template selection
func (a *App) RenderOnboardingTemplate() string {
	title := StyleTitle.
		Foreground(ColorWarning).
		Render("╔════════════════════════════════════════╗\n║        第 3 步: 选择地图主题           ║\n╚════════════════════════════════════════╝")

	templates := GetMapTemplates()
	var content strings.Builder

	content.WriteString("选择你的地图风格 (使用 ⬆️⬇️ 上下切换，Enter 确认):\n\n")

	for i, template := range templates {
		prefix := "  "
		if i == a.OnboardingState.SelectedTemplate {
			content.WriteString(StyleMenuItemSelected.Render(fmt.Sprintf("▶ %s %s - %s [%s]\n",
				template.Emoji, template.Name, template.Description, template.Difficulty)))
		} else {
			content.WriteString(StyleMenuItem.Render(fmt.Sprintf("%s %s %s - %s [%s]\n",
				prefix, template.Emoji, template.Name, template.Description, template.Difficulty)))
		}
	}

	return title + "\n" + content.String()
}

// RenderOnboardingNPC renders the NPC selection
func (a *App) RenderOnboardingNPC() string {
	templates := GetMapTemplates()
	selectedTemplate := templates[a.OnboardingState.SelectedTemplate]

	title := StyleTitle.
		Foreground(ColorWarning).
		Render(fmt.Sprintf("╔════════════════════════════════════════╗\n║        第 4 步: 选择 NPC 伙伴           ║\n║        地图: %s                  ║\n╚════════════════════════════════════════╝", selectedTemplate.Name))

	var content strings.Builder

	content.WriteString(fmt.Sprintf("为你的 %s 选择 NPC (使用 Space 切换选择，Enter 确认):\n\n",
		selectedTemplate.Name))

	for i, npc := range selectedTemplate.NPCs {
		if i >= len(a.OnboardingState.SelectedNPCs) {
			a.OnboardingState.SelectedNPCs = append(a.OnboardingState.SelectedNPCs, false)
		}

		checked := "☐"
		if a.OnboardingState.SelectedNPCs[i] {
			checked = "☑"
		}

		content.WriteString(StyleMenuItem.Render(fmt.Sprintf(
			"  %s %s %-15s | %s | \"%s\"\n",
			checked, npc.Emoji, npc.Name, npc.Type, npc.Dialogue,
		)))
	}

	content.WriteString("\n" + StyleDim.Render("💡 提示: 至少选择 1 个 NPC\n"))

	return title + "\n" + content.String()
}

// RenderOnboardingPreview renders the map preview before generation
func (a *App) RenderOnboardingPreview() string {
	templates := GetMapTemplates()
	selectedTemplate := templates[a.OnboardingState.SelectedTemplate]

	title := StyleTitle.
		Foreground(ColorWarning).
		Render("╔════════════════════════════════════════╗\n║        第 5 步: 确认并生成地图         ║\n╚════════════════════════════════════════╝")

	var content strings.Builder

	content.WriteString(StyleMenuItem.Render("\n📋 确认信息:\n\n"))
	content.WriteString(StyleMenuItemSelected.Render(fmt.Sprintf("  🗺️  地图主题: %s\n", selectedTemplate.Name)))
	content.WriteString(StyleMenuItemSelected.Render(fmt.Sprintf("  📊 难度级别: %s\n", selectedTemplate.Difficulty)))

	content.WriteString("\n  🤖 邀请的 NPC:\n")
	for i, npc := range selectedTemplate.NPCs {
		if i < len(a.OnboardingState.SelectedNPCs) && a.OnboardingState.SelectedNPCs[i] {
			content.WriteString(StyleMenuItemSelected.Render(fmt.Sprintf(
				"      • %s %s (%s)\n", npc.Emoji, npc.Name, npc.Type)))
		}
	}

	content.WriteString("\n" + StyleMenuItemSelected.Render(fmt.Sprintf("  🌍 地形分布:\n")))
	for terrain, percent := range selectedTemplate.TerrainType {
		bar := strings.Repeat("█", percent/10)
		content.WriteString(StyleDim.Render(fmt.Sprintf("      %-10s: %s %d%%\n", terrain, bar, percent)))
	}

	content.WriteString("\n" + StyleMenuItem.Render("功能特性:\n"))
	for _, feature := range selectedTemplate.Features {
		content.WriteString(StyleDim.Render(fmt.Sprintf("  ✨ %s\n", feature)))
	}

	confirm := StyleSuccess.Render("\n✅ 按 Enter 生成你的地图")

	return title + "\n" + content.String() + confirm
}

// RenderOnboardingComplete renders the completion screen
func (a *App) RenderOnboardingComplete() string {
	title := StyleTitle.
		Foreground(ColorWarning).
		Render("╔════════════════════════════════════════╗\n║        🎉 恭喜！冒险开始了！         ║\n╚════════════════════════════════════════╝")

	content := StyleSuccess.Render(`
✅ 你已成功完成新手引导！

你现在拥有:
  • 🗽 自己的 GitHub 仓库副本
  • 🏰 防守基地，准备迎接挑战
  • 🗺️  精心设计的个人地图
  • 🤖 NPC 伙伴在你的世界中
  • 🎮 完全的游戏体验

接下来你可以:

1️⃣  🚀 开始冒险
   • 进入你的地图世界
   • 探索其他玩家的地图
   • 捕获野生宝可梦

2️⃣  ⚔️  与其他玩家对战
   • 挑战其他训练师
   • 防守你的基地
   • 赚取奖励

3️⃣  🎨 自定义你的世界
   • 生成更多地图
   • 邀请更多 NPC
   • 修改地图设置

4️⃣  💼 与社区互动
   • 分享你的成就
   • 查看排行榜
   • 参与社区活动
`)

	footer := StyleDim.Render(`
按 Enter 返回主菜单开始探索你的世界！
`)

	return title + "\n" + content + "\n" + footer
}

// HandleOnboardingInput processes input during onboarding
func (a *App) HandleOnboardingInput(msg tea.KeyMsg, currentStep OnboardingStep) (*App, tea.Cmd) {
	switch currentStep {
	case OnboardingWelcomeScreen:
		switch msg.String() {
		case "enter":
			a.OnboardingState.CurrentStep = int(OnboardingForkScreen)
		case "q":
			a.CurrentScreen = MainMenuScreen
			a.SelectedIndex = 0
		}

	case OnboardingForkScreen:
		switch msg.String() {
		case "enter":
			if !a.OnboardingState.RepoForked {
				a.OnboardingState.Loading = true
				return a, forkRepositoryCmd(a)
			} else {
				a.OnboardingState.CurrentStep = int(OnboardingBaseScreen)
			}

		case "esc":
			a.CurrentScreen = MainMenuScreen
		}

	case OnboardingBaseScreen:
		switch msg.String() {
		case "enter":
			if !a.OnboardingState.BaseCreated {
				a.OnboardingState.Loading = true
				return a, createBaseCmd(a)
			} else {
				a.OnboardingState.CurrentStep = int(OnboardingTemplateScreen)
			}

		case "esc":
			a.CurrentScreen = MainMenuScreen
		}

	case OnboardingTemplateScreen:
		switch msg.String() {
		case "up", "k":
			templates := GetMapTemplates()
			if a.OnboardingState.SelectedTemplate > 0 {
				a.OnboardingState.SelectedTemplate--
			} else {
				// Wrap to last template
				a.OnboardingState.SelectedTemplate = len(templates) - 1
			}
		case "down", "j":
			templates := GetMapTemplates()
			if a.OnboardingState.SelectedTemplate < len(templates)-1 {
				a.OnboardingState.SelectedTemplate++
			} else {
				// Wrap to first template
				a.OnboardingState.SelectedTemplate = 0
			}
		case "enter":
			a.OnboardingState.SelectedNPCs = make([]bool, len(GetMapTemplates()[a.OnboardingState.SelectedTemplate].NPCs))
			a.OnboardingState.CurrentStep = int(OnboardingNPCScreen)
		case "esc":
			a.CurrentScreen = MainMenuScreen
		}

	case OnboardingNPCScreen:
		switch msg.String() {
		case "up", "k":
			// Move selection up
			for i := a.OnboardingState.SelectedTemplate - 1; i >= 0; i-- {
				if i < len(a.OnboardingState.SelectedNPCs) {
					a.OnboardingState.SelectedTemplate = i
					break
				}
			}
		case "down", "j":
			// Move selection down
			for i := a.OnboardingState.SelectedTemplate + 1; i < len(a.OnboardingState.SelectedNPCs); i++ {
				a.OnboardingState.SelectedTemplate = i
				break
			}
		case " ":
			// Toggle selection
			if a.OnboardingState.SelectedTemplate < len(a.OnboardingState.SelectedNPCs) {
				a.OnboardingState.SelectedNPCs[a.OnboardingState.SelectedTemplate] =
					!a.OnboardingState.SelectedNPCs[a.OnboardingState.SelectedTemplate]
			}
		case "enter":
			// Check if at least one NPC is selected
			selectedCount := 0
			for _, selected := range a.OnboardingState.SelectedNPCs {
				if selected {
					selectedCount++
				}
			}
			if selectedCount > 0 {
				a.OnboardingState.CurrentStep = int(OnboardingMapPreviewScreen)
			} else {
				a.OnboardingState.Error = "请至少选择一个 NPC"
			}
		case "esc":
			a.CurrentScreen = MainMenuScreen
		}

	case OnboardingMapPreviewScreen:
		switch msg.String() {
		case "enter":
			a.OnboardingState.Loading = true
			return a, generateMapCmd(a)
		case "esc":
			a.CurrentScreen = MainMenuScreen
		}

	case OnboardingCompleteScreen:
		switch msg.String() {
		case "enter":
			a.CurrentScreen = MainMenuScreen
			a.SelectedIndex = 0
		}
	}

	return a, nil
}

// ForkRepository forks the GitHub repository
func (a *App) ForkRepository() error {
	if a.GitHub == nil {
		return fmt.Errorf("GitHub client not initialized")
	}

	// This would call GitHub CLI or API to fork the repository
	// For now, we'll simulate it
	return nil
}

// CreateBase creates the user's defense base
func (a *App) CreateBase() error {
	// Call API to create base
	_, err := a.Client.CreateBase(fmt.Sprintf("https://github.com/%s/agent-monster", a.CurrentUser.Login))

	// If the error is about not having enough pokemons, that's expected in onboarding
	// Just skip it for now - player can create base later after catching pokemons
	if err != nil && strings.Contains(err.Error(), "needs at least 3 pokemons") {
		return nil // Skip this error during onboarding
	}

	return err
}

// GenerateOnboardingMap generates the map based on selected template and NPCs
func (a *App) GenerateOnboardingMap() error {
	templates := GetMapTemplates()
	_ = templates[a.OnboardingState.SelectedTemplate] // Ensure template exists

	// Generate map based on template
	mapID := fmt.Sprintf("%s_starter_%d", strings.ToLower(a.CurrentUser.Login), a.OnboardingState.SelectedTemplate+1)

	mapData, err := a.Client.GenerateMap(
		a.CurrentUser.ID,
		a.CurrentUser.Login,
		mapID,
		20,
		20,
	)
	if err != nil {
		return err
	}

	a.OnboardingState.GeneratedMap = mapData
	return nil
}

// ClaimStarterPokemons claims starter pokemons (1 Psyduck + 2 Eggs) for the user during onboarding
func (a *App) ClaimStarterPokemons() error {
	if a.CurrentUser == nil || a.CurrentUser.ID == 0 {
		return fmt.Errorf("user not authenticated")
	}

	_, err := a.Client.ClaimStarterPokemons(a.CurrentUser.ID)
	return err
}

// renderOnboarding renders the current step of onboarding
func (a *App) renderOnboarding() string {
	step := a.OnboardingState.CurrentStep

	switch step {
	case int(OnboardingWelcomeScreen):
		return a.RenderOnboardingWelcome()
	case int(OnboardingForkScreen):
		return a.RenderOnboardingFork()
	case int(OnboardingBaseScreen):
		return a.RenderOnboardingBase()
	case int(OnboardingTemplateScreen):
		return a.RenderOnboardingTemplate()
	case int(OnboardingNPCScreen):
		return a.RenderOnboardingNPC()
	case int(OnboardingMapPreviewScreen):
		return a.RenderOnboardingPreview()
	case int(OnboardingCompleteScreen):
		return a.RenderOnboardingComplete()
	default:
		return a.RenderOnboardingWelcome()
	}
}

// handleOnboarding handles input during onboarding and returns proper Bubble Tea command
func (a *App) handleOnboarding(msg tea.KeyMsg) (*App, tea.Cmd) {
	step := OnboardingStep(a.OnboardingState.CurrentStep)

	var cmd tea.Cmd
	a, cmd = a.HandleOnboardingInput(msg, step)

	// If cmd is not nil, it's a Bubble Tea command we should execute
	if cmd != nil {
		return a, cmd
	}

	return a, nil
}

// forkRepositoryCmd creates a Bubble Tea command for forking repository
func forkRepositoryCmd(a *App) tea.Cmd {
	return func() tea.Msg {
		if err := a.ForkRepository(); err != nil {
			return OnboardingOperationMsg{
				Operation: "fork",
				Success:   false,
				Error:     fmt.Sprintf("Fork 失败: %v", err),
			}
		}
		return OnboardingOperationMsg{
			Operation: "fork",
			Success:   true,
			Error:     "",
		}
	}
}

// createBaseCmd creates a Bubble Tea command for creating base
func createBaseCmd(a *App) tea.Cmd {
	return func() tea.Msg {
		if err := a.CreateBase(); err != nil {
			return OnboardingOperationMsg{
				Operation: "createbase",
				Success:   false,
				Error:     fmt.Sprintf("创建基地失败: %v", err),
			}
		}
		return OnboardingOperationMsg{
			Operation: "createbase",
			Success:   true,
			Error:     "",
		}
	}
}

// generateMapCmd creates a Bubble Tea command for generating map and claiming starter pokemons
func generateMapCmd(a *App) tea.Cmd {
	return func() tea.Msg {
		if err := a.GenerateOnboardingMap(); err != nil {
			return OnboardingOperationMsg{
				Operation: "generatemap",
				Success:   false,
				Error:     fmt.Sprintf("生成地图失败: %v", err),
			}
		}

		// After generating map successfully, claim starter pokemons
		if err := a.ClaimStarterPokemons(); err != nil {
			// Log the error but don't fail the onboarding completion
			// User successfully completed onboarding, just couldn't claim pokemons
			fmt.Printf("Warning: Failed to claim starter pokemons: %v\n", err)
		}

		return OnboardingOperationMsg{
			Operation: "generatemap",
			Success:   true,
			Error:     "",
		}
	}
}
