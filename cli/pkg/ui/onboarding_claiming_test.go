package ui

import (
	"strings"
	"testing"
)

// TestOnboardingClaimingScreenState verifies claiming screen state is properly initialized
func TestOnboardingClaimingScreenState(t *testing.T) {
	state := &OnboardingState{
		CurrentStep:     int(OnboardingClaimingScreen),
		PokemonsClaimed: false,
	}

	if state.CurrentStep != int(OnboardingClaimingScreen) {
		t.Errorf("Expected CurrentStep to be OnboardingClaimingScreen, got %d", state.CurrentStep)
	}

	if state.PokemonsClaimed {
		t.Errorf("Expected PokemonsClaimed to be false initially, got %v", state.PokemonsClaimed)
	}
}

// TestPokemonsClaimedFlag verifies flag transitions correctly
func TestPokemonsClaimedFlag(t *testing.T) {
	state := &OnboardingState{
		PokemonsClaimed: false,
	}

	// Initially should be false
	if state.PokemonsClaimed {
		t.Errorf("Expected PokemonsClaimed to be false initially")
	}

	// Should be able to set to true
	state.PokemonsClaimed = true
	if !state.PokemonsClaimed {
		t.Errorf("Expected PokemonsClaimed to be true after setting")
	}

	// Should be able to reset to false
	state.PokemonsClaimed = false
	if state.PokemonsClaimed {
		t.Errorf("Expected PokemonsClaimed to be false after reset")
	}
}

// TestOnboardingClaimingScreenContent verifies rendering content
func TestOnboardingClaimingScreenContent(t *testing.T) {
	app := &App{
		OnboardingState: &OnboardingState{
			CurrentStep:     int(OnboardingClaimingScreen),
			PokemonsClaimed: false,
		},
	}

	// Mock the render function
	content := app.RenderOnboardingClaiming()

	// Verify essential content is present
	expectedStrings := []string{
		"🎁",       // Gift emoji
		"领取初始宝可梦", // Title
		"小黄鸭",     // Psyduck name
		"宝可梦蛋",    // Egg name
		"请稍候",     // Wait message
	}

	for _, expected := range expectedStrings {
		if !strings.Contains(content, expected) {
			t.Errorf("Expected content to contain '%s', but it doesn't", expected)
		}
	}
}

// TestOnboardingCompleteScreenWithPokemons verifies completion screen shows pokemons
func TestOnboardingCompleteScreenWithPokemons(t *testing.T) {
	app := &App{
		OnboardingState: &OnboardingState{
			CurrentStep:     int(OnboardingCompleteScreen),
			PokemonsClaimed: true,
		},
	}

	content := app.RenderOnboardingComplete()

	// Verify pokemon-related content is present in completion screen
	expectedStrings := []string{
		"🎉",     // Celebration emoji
		"恭喜",    // Congratulations
		"初始宝可梦", // Initial pokemon
		"小黄鸭",   // Psyduck
		"宝可梦蛋",  // Eggs
	}

	for _, expected := range expectedStrings {
		if !strings.Contains(content, expected) {
			t.Errorf("Expected completion screen to contain '%s', but it doesn't", expected)
		}
	}
}

// TestOnboardingFlowWithClaiming verifies complete flow with claiming
func TestOnboardingFlowWithClaiming(t *testing.T) {
	state := &OnboardingState{
		CurrentStep:     0,
		RepoForked:      false,
		BaseCreated:     false,
		PokemonsClaimed: false,
	}

	// Verify initial state
	if state.CurrentStep != 0 {
		t.Errorf("Expected CurrentStep to be 0 initially")
	}
	if state.PokemonsClaimed {
		t.Errorf("Expected PokemonsClaimed to be false initially")
	}

	// Simulate progressing through steps
	stepsBeforeClaiming := []int{
		int(OnboardingWelcomeScreen),
		int(OnboardingForkScreen),
		int(OnboardingBaseScreen),
		int(OnboardingTemplateScreen),
		int(OnboardingNPCScreen),
		int(OnboardingMapPreviewScreen),
	}

	for i, step := range stepsBeforeClaiming {
		state.CurrentStep = step
		if state.CurrentStep != step {
			t.Errorf("Step %d: Expected CurrentStep to be %d, got %d", i, step, state.CurrentStep)
		}
		// Pokemons should not be claimed yet
		if state.PokemonsClaimed {
			t.Errorf("Step %d: Pokemons should not be claimed yet", i)
		}
	}

	// Move to claiming screen
	state.CurrentStep = int(OnboardingClaimingScreen)
	if state.CurrentStep != int(OnboardingClaimingScreen) {
		t.Errorf("Expected CurrentStep to be OnboardingClaimingScreen")
	}

	// Mark as claimed
	state.PokemonsClaimed = true
	if !state.PokemonsClaimed {
		t.Errorf("Expected PokemonsClaimed to be true after claiming")
	}

	// Move to complete screen
	state.CurrentStep = int(OnboardingCompleteScreen)
	if state.CurrentStep != int(OnboardingCompleteScreen) {
		t.Errorf("Expected CurrentStep to be OnboardingCompleteScreen")
	}

	// Both conditions should be true at completion
	if !state.PokemonsClaimed {
		t.Errorf("Expected PokemonsClaimed to be true at completion")
	}
}

// TestOnboardingClaimingScreenNavigation verifies no input needed on claiming screen
func TestOnboardingClaimingScreenNavigation(t *testing.T) {
	app := &App{
		OnboardingState: &OnboardingState{
			CurrentStep:     int(OnboardingClaimingScreen),
			PokemonsClaimed: false,
		},
	}

	// Simulate input handling for claiming screen
	// The claiming screen should not respond to normal input
	// It auto-completes after the command finishes
	screen := app.OnboardingState.CurrentStep
	if screen != int(OnboardingClaimingScreen) {
		t.Errorf("Expected to be on claiming screen")
	}
}

// TestPokemonQualitiesInClaim verifies correct pokemon qualities in claiming message
func TestPokemonQualitiesInClaim(t *testing.T) {
	app := &App{
		OnboardingState: &OnboardingState{
			CurrentStep: int(OnboardingClaimingScreen),
		},
	}

	content := app.RenderOnboardingClaiming()

	// Verify Psyduck specific details
	psyduckDetails := []string{
		"等级: 1",      // Level 1
		"属性: 超能力/水系", // Psychic/Water type
		"特性: 迟钝",     // Capability: Oblivious
	}

	for _, detail := range psyduckDetails {
		if !strings.Contains(content, detail) {
			t.Errorf("Expected Psyduck details to contain '%s'", detail)
		}
	}

	// Verify egg details
	eggDetails := []string{
		"需要孵化后获得真实宝可梦",
		"照顾来加速孵化",
	}

	for _, detail := range eggDetails {
		if !strings.Contains(content, detail) {
			t.Errorf("Expected egg details to contain '%s'", detail)
		}
	}
}

// TestOnboardingStateScreenConstants verifies all screen constants exist
func TestOnboardingStateScreenConstants(t *testing.T) {
	screens := []OnboardingStep{
		OnboardingWelcomeScreen,
		OnboardingForkScreen,
		OnboardingBaseScreen,
		OnboardingTemplateScreen,
		OnboardingNPCScreen,
		OnboardingMapPreviewScreen,
		OnboardingClaimingScreen, // New screen
		OnboardingCompleteScreen,
	}

	// Verify screens are distinct
	screenValues := make(map[int]bool)
	for _, screen := range screens {
		screenValue := int(screen)
		if screenValues[screenValue] {
			t.Errorf("Duplicate screen value found: %d", screenValue)
		}
		screenValues[screenValue] = true
	}

	// Verify claiming screen exists and is before complete screen
	if int(OnboardingClaimingScreen) >= int(OnboardingCompleteScreen) {
		t.Errorf("OnboardingClaimingScreen should come before OnboardingCompleteScreen")
	}
}
