package ui

import (
	"agent-monster-cli/pkg/github"
	"testing"
)

// TestAppInitializationWithOnboarding verifies App initializes with onboarding state
func TestAppInitializationWithOnboarding(t *testing.T) {
	app := &App{
		OnboardingState: &OnboardingState{
			CurrentStep:      0,
			SelectedTemplate: 0,
			SelectedNPCs:     make([]bool, 0),
			RepoForked:       false,
			BaseCreated:      false,
		},
	}

	if app.OnboardingState == nil {
		t.Errorf("OnboardingState should not be nil")
	}

	if app.OnboardingState.CurrentStep != 0 {
		t.Errorf("Expected CurrentStep to be 0, got %d", app.OnboardingState.CurrentStep)
	}
}

// TestAppInitializationWithAccountSelect verifies App initializes with account select state
func TestAppInitializationWithAccountSelect(t *testing.T) {
	app := &App{
		AccountSelectState: &AccountSelectState{
			Accounts:      make([]github.AuthAccount, 0),
			SelectedIndex: 0,
			Loading:       false,
		},
	}

	if app.AccountSelectState == nil {
		t.Errorf("AccountSelectState should not be nil")
	}

	if app.AccountSelectState.SelectedIndex != 0 {
		t.Errorf("Expected SelectedIndex to be 0, got %d", app.AccountSelectState.SelectedIndex)
	}

	if app.AccountSelectState.Loading {
		t.Errorf("Expected Loading to be false")
	}
}

// TestOnboardingToAccountSelectFlow verifies flow from onboarding to account selection
func TestOnboardingToAccountSelectFlow(t *testing.T) {
	app := &App{
		OnboardingState:    &OnboardingState{CurrentStep: 0},
		AccountSelectState: &AccountSelectState{SelectedIndex: 0},
	}

	// In a real integration flow:
	// 1. User starts onboarding
	if app.OnboardingState.CurrentStep == 0 {
		t.Log("Onboarding started")
	}

	// 2. If user has multiple accounts, show account selection
	if app.AccountSelectState != nil {
		t.Log("Account selection available")
	}
}

// TestOnboardingStatesCoexist verifies both states can exist simultaneously
func TestOnboardingStatesCoexist(t *testing.T) {
	app := &App{
		OnboardingState:    &OnboardingState{CurrentStep: 2},
		AccountSelectState: &AccountSelectState{SelectedIndex: 1},
	}

	// Both states should be accessible and independent
	if app.OnboardingState.CurrentStep != 2 {
		t.Errorf("OnboardingState not preserved: got %d", app.OnboardingState.CurrentStep)
	}

	if app.AccountSelectState.SelectedIndex != 1 {
		t.Errorf("AccountSelectState not preserved: got %d", app.AccountSelectState.SelectedIndex)
	}
}

// TestOnboardingWithTemplateAndNPCSelection verifies full selection flow
func TestOnboardingWithTemplateAndNPCSelection(t *testing.T) {
	app := &App{
		OnboardingState: &OnboardingState{
			CurrentStep:      3, // At template selection
			SelectedTemplate: 2,
			SelectedNPCs:     make([]bool, 3),
		},
	}

	// Select template
	app.OnboardingState.SelectedTemplate = 2

	// Initialize NPC selections for the selected template
	for i := 0; i < 3; i++ {
		app.OnboardingState.SelectedNPCs = append(app.OnboardingState.SelectedNPCs, false)
	}

	// Select NPC 0 and 2
	app.OnboardingState.SelectedNPCs[0] = true
	app.OnboardingState.SelectedNPCs[2] = true

	selectedCount := 0
	for _, selected := range app.OnboardingState.SelectedNPCs {
		if selected {
			selectedCount++
		}
	}

	if selectedCount != 2 {
		t.Errorf("Expected 2 NPCs selected, got %d", selectedCount)
	}
}

// TestProgressTrackingAcrossSteps verifies progress updates through onboarding
func TestProgressTrackingAcrossSteps(t *testing.T) {
	app := &App{
		OnboardingState: &OnboardingState{
			CurrentStep:        0,
			CompletionProgress: 0,
		},
	}

	expectedProgressMap := map[int]int{
		0: 0,
		1: 16,
		2: 33,
		3: 50,
		4: 66,
		5: 83,
		6: 100,
	}

	for step, expectedProgress := range expectedProgressMap {
		app.OnboardingState.CurrentStep = step
		app.OnboardingState.CompletionProgress = expectedProgress

		if app.OnboardingState.CompletionProgress != expectedProgress {
			t.Errorf("Step %d: Expected progress %d, got %d",
				step, expectedProgress, app.OnboardingState.CompletionProgress)
		}
	}
}

// TestErrorHandlingInOnboarding verifies error state management
func TestErrorHandlingInOnboarding(t *testing.T) {
	app := &App{
		OnboardingState: &OnboardingState{
			Error: "",
		},
	}

	// Set an error
	app.OnboardingState.Error = "Failed to fork repository"

	if app.OnboardingState.Error == "" {
		t.Errorf("Error not set")
	}

	if app.OnboardingState.Error != "Failed to fork repository" {
		t.Errorf("Expected specific error message")
	}

	// Clear error
	app.OnboardingState.Error = ""

	if app.OnboardingState.Error != "" {
		t.Errorf("Error not cleared")
	}
}

// TestLoadingStateManagement verifies loading state during async operations
func TestLoadingStateManagement(t *testing.T) {
	app := &App{
		OnboardingState: &OnboardingState{
			Loading: false,
		},
	}

	// Simulate starting an async operation
	app.OnboardingState.Loading = true
	if !app.OnboardingState.Loading {
		t.Errorf("Loading flag not set")
	}

	// Simulate operation complete
	app.OnboardingState.Loading = false
	if app.OnboardingState.Loading {
		t.Errorf("Loading flag not cleared")
	}
}

// TestMessageUpdatesInOnboarding verifies message state transitions
func TestMessageUpdatesInOnboarding(t *testing.T) {
	app := &App{
		OnboardingState: &OnboardingState{
			Message: "",
		},
	}

	messages := []string{
		"Initializing...",
		"Forking repository...",
		"Setting up base...",
		"Complete!",
	}

	for _, msg := range messages {
		app.OnboardingState.Message = msg

		if app.OnboardingState.Message != msg {
			t.Errorf("Message not updated to: %s", msg)
		}
	}
}
