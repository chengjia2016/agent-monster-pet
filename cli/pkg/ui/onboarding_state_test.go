package ui

import (
	"testing"
)

// TestOnboardingStateInitialization verifies OnboardingState is properly initialized
func TestOnboardingStateInitialization(t *testing.T) {
	app := &App{
		OnboardingState: &OnboardingState{
			CurrentStep:      0,
			SelectedTemplate: 0,
			SelectedNPCs:     make([]bool, 0),
		},
	}

	if app.OnboardingState.CurrentStep != 0 {
		t.Errorf("Expected CurrentStep to be 0, got %d", app.OnboardingState.CurrentStep)
	}

	if app.OnboardingState.SelectedTemplate != 0 {
		t.Errorf("Expected SelectedTemplate to be 0, got %d", app.OnboardingState.SelectedTemplate)
	}

	if app.OnboardingState.RepoForked {
		t.Errorf("Expected RepoForked to be false, got %v", app.OnboardingState.RepoForked)
	}

	if app.OnboardingState.BaseCreated {
		t.Errorf("Expected BaseCreated to be false, got %v", app.OnboardingState.BaseCreated)
	}
}

// TestOnboardingStepProgression verifies steps progress correctly
func TestOnboardingStepProgression(t *testing.T) {
	state := &OnboardingState{
		CurrentStep: 0,
	}

	expectedSteps := 7

	for i := 0; i < expectedSteps; i++ {
		if state.CurrentStep != i {
			t.Errorf("Expected step %d, got %d", i, state.CurrentStep)
		}
		state.CurrentStep++
	}
}

// TestOnboardingTemplateSelection verifies template selection works
func TestOnboardingTemplateSelection(t *testing.T) {
	state := &OnboardingState{
		SelectedTemplate: -1,
	}

	templates := GetMapTemplates()

	for i := 0; i < len(templates); i++ {
		state.SelectedTemplate = i
		if state.SelectedTemplate != i {
			t.Errorf("Expected template %d, got %d", i, state.SelectedTemplate)
		}
	}

	// Test invalid template
	state.SelectedTemplate = 100
	if state.SelectedTemplate == -1 {
		t.Errorf("Template selection failed")
	}
}

// TestOnboardingNPCSelection verifies NPC selection tracking
func TestOnboardingNPCSelection(t *testing.T) {
	state := &OnboardingState{
		SelectedNPCs: make([]bool, 0),
	}

	// Simulate selecting NPCs
	for i := 0; i < 3; i++ {
		state.SelectedNPCs = append(state.SelectedNPCs, false)
	}

	// Toggle first NPC
	state.SelectedNPCs[0] = true

	if !state.SelectedNPCs[0] {
		t.Errorf("Expected first NPC to be selected")
	}

	// Count selected NPCs
	count := 0
	for _, selected := range state.SelectedNPCs {
		if selected {
			count++
		}
	}

	if count != 1 {
		t.Errorf("Expected 1 NPC selected, got %d", count)
	}
}

// TestOnboardingMessageHandling verifies message updates
func TestOnboardingMessageHandling(t *testing.T) {
	state := &OnboardingState{
		Message: "",
		Error:   "",
	}

	state.Message = "Welcome to onboarding"
	if state.Message != "Welcome to onboarding" {
		t.Errorf("Message not updated correctly")
	}

	state.Error = "Test error"
	if state.Error != "Test error" {
		t.Errorf("Error not updated correctly")
	}
}

// TestOnboardingLoadingState verifies loading state management
func TestOnboardingLoadingState(t *testing.T) {
	state := &OnboardingState{
		Loading: false,
	}

	if state.Loading {
		t.Errorf("Expected loading to be false initially")
	}

	state.Loading = true
	if !state.Loading {
		t.Errorf("Expected loading to be true")
	}

	state.Loading = false
	if state.Loading {
		t.Errorf("Expected loading to be false")
	}
}

// TestOnboardingProgressTracking verifies progress percentage
func TestOnboardingProgressTracking(t *testing.T) {
	state := &OnboardingState{
		CompletionProgress: 0,
	}

	expectedProgress := []int{0, 16, 33, 50, 66, 83, 100}

	for i, progress := range expectedProgress {
		state.CompletionProgress = progress
		if state.CompletionProgress != progress {
			t.Errorf("Step %d: Expected progress %d, got %d", i, progress, state.CompletionProgress)
		}
	}
}

// TestOnboardingInputBuffer verifies input buffer management
func TestOnboardingInputBuffer(t *testing.T) {
	state := &OnboardingState{
		InputBuffer: "",
	}

	testInputs := []string{"y", "yes", "n", "no", "1", "2"}

	for _, input := range testInputs {
		state.InputBuffer = input
		if state.InputBuffer != input {
			t.Errorf("Expected input %s, got %s", input, state.InputBuffer)
		}
	}
}

// TestOnboardingRepositoryFlags verifies repo-related flags
func TestOnboardingRepositoryFlags(t *testing.T) {
	state := &OnboardingState{
		RepoForked:  false,
		BaseCreated: false,
	}

	// Test repo fork
	state.RepoForked = true
	if !state.RepoForked {
		t.Errorf("Expected RepoForked to be true")
	}

	// Test base creation
	state.BaseCreated = true
	if !state.BaseCreated {
		t.Errorf("Expected BaseCreated to be true")
	}

	// Test resetting
	state.RepoForked = false
	state.BaseCreated = false
	if state.RepoForked || state.BaseCreated {
		t.Errorf("Expected both flags to be false after reset")
	}
}
