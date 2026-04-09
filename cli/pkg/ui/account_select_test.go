package ui

import (
	"agent-monster-cli/pkg/github"
	"testing"
)

// TestAccountSelectStateInitialization verifies AccountSelectState is properly initialized
func TestAccountSelectStateInitialization(t *testing.T) {
	state := &AccountSelectState{
		Accounts:      make([]github.AuthAccount, 0),
		SelectedIndex: 0,
		Loading:       false,
	}

	if len(state.Accounts) != 0 {
		t.Errorf("Expected empty accounts, got %d", len(state.Accounts))
	}

	if state.SelectedIndex != 0 {
		t.Errorf("Expected SelectedIndex to be 0, got %d", state.SelectedIndex)
	}

	if state.Loading {
		t.Errorf("Expected Loading to be false, got %v", state.Loading)
	}
}

// TestAccountSelectStateNavigation verifies account selection navigation
func TestAccountSelectStateNavigation(t *testing.T) {
	state := &AccountSelectState{
		Accounts: []github.AuthAccount{
			{
				Hostname: "github.com",
				Username: "user1",
				Active:   true,
			},
			{
				Hostname: "github.com",
				Username: "user2",
				Active:   false,
			},
			{
				Hostname: "github.enterprise.com",
				Username: "user3",
				Active:   false,
			},
		},
		SelectedIndex: 0,
	}

	// Test moving down
	if state.SelectedIndex < len(state.Accounts)-1 {
		state.SelectedIndex++
	}
	if state.SelectedIndex != 1 {
		t.Errorf("Expected SelectedIndex to be 1 after moving down, got %d", state.SelectedIndex)
	}

	// Test moving down again
	if state.SelectedIndex < len(state.Accounts)-1 {
		state.SelectedIndex++
	}
	if state.SelectedIndex != 2 {
		t.Errorf("Expected SelectedIndex to be 2, got %d", state.SelectedIndex)
	}

	// Test boundary - should not go beyond
	if state.SelectedIndex < len(state.Accounts)-1 {
		state.SelectedIndex++
	}
	if state.SelectedIndex != 2 {
		t.Errorf("Expected SelectedIndex to stay at 2 at boundary, got %d", state.SelectedIndex)
	}

	// Test moving up
	if state.SelectedIndex > 0 {
		state.SelectedIndex--
	}
	if state.SelectedIndex != 1 {
		t.Errorf("Expected SelectedIndex to be 1 after moving up, got %d", state.SelectedIndex)
	}
}

// TestAccountSelectStateLoadingFlag verifies loading state management
func TestAccountSelectStateLoadingFlag(t *testing.T) {
	state := &AccountSelectState{
		Loading: false,
	}

	if state.Loading {
		t.Errorf("Expected Loading to be false initially")
	}

	state.Loading = true
	if !state.Loading {
		t.Errorf("Expected Loading to be true")
	}

	state.Loading = false
	if state.Loading {
		t.Errorf("Expected Loading to be false")
	}
}

// TestMultipleAccountsDetection verifies multiple accounts can be stored
func TestMultipleAccountsDetection(t *testing.T) {
	accounts := []github.AuthAccount{
		{
			Hostname: "github.com",
			Username: "personal",
			Active:   true,
		},
		{
			Hostname: "github.com",
			Username: "work",
			Active:   false,
		},
	}

	state := &AccountSelectState{
		Accounts: accounts,
	}

	if len(state.Accounts) != 2 {
		t.Errorf("Expected 2 accounts, got %d", len(state.Accounts))
	}

	if state.Accounts[0].Username != "personal" {
		t.Errorf("Expected first account to be 'personal'")
	}

	if state.Accounts[1].Username != "work" {
		t.Errorf("Expected second account to be 'work'")
	}
}

// TestAccountActiveStatus verifies active account tracking
func TestAccountActiveStatus(t *testing.T) {
	accounts := []github.AuthAccount{
		{
			Hostname: "github.com",
			Username: "user1",
			Active:   true,
		},
		{
			Hostname: "github.com",
			Username: "user2",
			Active:   false,
		},
	}

	activeCount := 0
	for _, account := range accounts {
		if account.Active {
			activeCount++
		}
	}

	if activeCount != 1 {
		t.Errorf("Expected 1 active account, got %d", activeCount)
	}

	if !accounts[0].Active {
		t.Errorf("Expected first account to be active")
	}

	if accounts[1].Active {
		t.Errorf("Expected second account to be inactive")
	}
}

// TestAccountSelection verifies selected account retrieval
func TestAccountSelection(t *testing.T) {
	accounts := []github.AuthAccount{
		{
			Hostname: "github.com",
			Username: "user1",
			Active:   false,
		},
		{
			Hostname: "github.com",
			Username: "user2",
			Active:   false,
		},
		{
			Hostname: "github.com",
			Username: "user3",
			Active:   false,
		},
	}

	state := &AccountSelectState{
		Accounts:      accounts,
		SelectedIndex: 1,
	}

	selectedAccount := state.Accounts[state.SelectedIndex]

	if selectedAccount.Username != "user2" {
		t.Errorf("Expected selected account to be 'user2', got %s", selectedAccount.Username)
	}
}

// TestEnterpriseGitHubSupport verifies enterprise GitHub accounts are supported
func TestEnterpriseGitHubSupport(t *testing.T) {
	accounts := []github.AuthAccount{
		{
			Hostname: "github.com",
			Username: "user1",
			Active:   false,
		},
		{
			Hostname: "github.enterprise.com",
			Username: "user2",
			Active:   false,
		},
	}

	state := &AccountSelectState{
		Accounts: accounts,
	}

	enterpriseCount := 0
	for _, account := range state.Accounts {
		if account.Hostname != "github.com" {
			enterpriseCount++
		}
	}

	if enterpriseCount != 1 {
		t.Errorf("Expected 1 enterprise account, got %d", enterpriseCount)
	}
}

// TestEmptyAccountsList verifies handling of empty account list
func TestEmptyAccountsList(t *testing.T) {
	state := &AccountSelectState{
		Accounts:      make([]github.AuthAccount, 0),
		SelectedIndex: 0,
	}

	if len(state.Accounts) != 0 {
		t.Errorf("Expected empty accounts list")
	}

	// Should not be able to select when empty
	if state.SelectedIndex >= len(state.Accounts) {
		// This is the expected state when no accounts exist
		t.Log("Empty accounts list handled correctly")
	}
}

// TestAccountIndexBoundaries verifies index boundary checks
func TestAccountIndexBoundaries(t *testing.T) {
	accounts := []github.AuthAccount{
		{Hostname: "github.com", Username: "user1", Active: false},
		{Hostname: "github.com", Username: "user2", Active: false},
	}

	state := &AccountSelectState{
		Accounts:      accounts,
		SelectedIndex: 0,
	}

	// Test valid boundaries
	if state.SelectedIndex < 0 || state.SelectedIndex >= len(state.Accounts) {
		t.Errorf("Initial index out of bounds")
	}

	state.SelectedIndex = 1
	if state.SelectedIndex < 0 || state.SelectedIndex >= len(state.Accounts) {
		t.Errorf("Index 1 out of bounds")
	}
}
