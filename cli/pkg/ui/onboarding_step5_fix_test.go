package ui

import (
	"agent-monster-cli/pkg/logger"
	"testing"

	tea "github.com/charmbracelet/bubbletea"
)

// TestStep5LoadingStateBlocksInput verifies that user input is blocked when Loading is true
func TestStep5LoadingStateBlocksInput(t *testing.T) {
	// Initialize logger
	logger.Init("/tmp", logger.INFO)

	// Create app in step 5 with loading state
	app := &App{
		OnboardingState: &OnboardingState{
			CurrentStep: int(OnboardingMapPreviewScreen),
			Loading:     true,
		},
	}

	// Simulate user pressing Enter while loading
	msg := tea.KeyMsg{Type: tea.KeyEnter}
	result, cmd := app.HandleOnboardingInput(msg, OnboardingMapPreviewScreen)

	// Verify input is ignored (no command)
	if cmd != nil {
		t.Errorf("FAIL: Expected no command while loading, got %v", cmd)
	}

	// Verify loading state persists
	if !result.OnboardingState.Loading {
		t.Errorf("FAIL: Loading state should remain true")
	}

	t.Log("PASS: Input correctly blocked during loading")
}

// TestStep5CancelDuringLoading verifies Ctrl+C cancels loading state
func TestStep5CancelDuringLoading(t *testing.T) {
	// Initialize logger
	logger.Init("/tmp", logger.INFO)

	app := &App{
		OnboardingState: &OnboardingState{
			CurrentStep: int(OnboardingMapPreviewScreen),
			Loading:     true,
		},
	}

	// Simulate Ctrl+C
	msg := tea.KeyMsg{Type: tea.KeyCtrlC}
	result, _ := app.HandleOnboardingInput(msg, OnboardingMapPreviewScreen)

	// Verify loading is cancelled
	if result.OnboardingState.Loading {
		t.Errorf("FAIL: Loading should be false after Ctrl+C")
	}

	if result.OnboardingState.Error == "" {
		t.Errorf("FAIL: Error message should be set")
	}

	t.Log("PASS: Ctrl+C correctly cancels loading")
}
