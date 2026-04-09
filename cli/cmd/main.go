package main

import (
	"agent-monster-cli/pkg/api"
	"agent-monster-cli/pkg/logger"
	"agent-monster-cli/pkg/ui"
	"flag"
	"fmt"
	"os"
	"path/filepath"

	tea "github.com/charmbracelet/bubbletea"
)

var (
	serverURL string
	debug     bool
)

func init() {
	flag.StringVar(&serverURL, "server", "http://127.0.0.1:10000", "Judge server URL")
	flag.BoolVar(&debug, "debug", false, "Enable debug mode")
	flag.Parse()
}

func main() {
	// 获取用户数据目录
	userDir, err := getUserDataDir()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error: Failed to get user data directory: %v\n", err)
		os.Exit(1)
	}

	// 初始化日志系统
	logDir := filepath.Join(userDir, "logs")
	logLevel := logger.INFO
	if debug {
		logLevel = logger.DEBUG
	}

	if err := logger.Init(logDir, logLevel); err != nil {
		fmt.Fprintf(os.Stderr, "Warning: Failed to initialize logger: %v\n", err)
	}
	defer logger.Get().Close()

	log := logger.Get()
	log.Info("Starting Agent Monster CLI")
	log.Info("Server URL: %s", serverURL)
	log.Info("Debug mode: %v", debug)
	log.Info("User data directory: %s", userDir)
	log.Info("Log directory: %s", logDir)

	// 创建API客户端
	client := api.NewClient(serverURL)
	log.Info("API client initialized")

	// 创建应用
	app := ui.NewApp(client, userDir)
	log.Info("UI application initialized")

	// 启动TUI
	log.Info("Starting TUI program")
	p := tea.NewProgram(app, tea.WithAltScreen())
	if _, err := p.Run(); err != nil {
		log.Error("TUI error: %v", err)
		fmt.Fprintf(os.Stderr, "Error: %v\n", err)
		os.Exit(1)
	}
	log.Info("TUI program ended normally")
}

// getUserDataDir returns the user data directory
func getUserDataDir() (string, error) {
	homeDir, err := os.UserHomeDir()
	if err != nil {
		return "", err
	}

	dataDir := filepath.Join(homeDir, ".agent-monster", "data")
	if err := os.MkdirAll(dataDir, 0755); err != nil {
		return "", err
	}

	return dataDir, nil
}
