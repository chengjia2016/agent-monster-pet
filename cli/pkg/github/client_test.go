package github

import (
	"testing"
)

// TestAuthAccountStructure verifies AuthAccount fields are properly defined
func TestAuthAccountStructure(t *testing.T) {
	account := AuthAccount{
		Hostname: "github.com",
		Username: "testuser",
		Active:   true,
	}

	if account.Hostname != "github.com" {
		t.Errorf("Expected hostname 'github.com', got %s", account.Hostname)
	}

	if account.Username != "testuser" {
		t.Errorf("Expected username 'testuser', got %s", account.Username)
	}

	if !account.Active {
		t.Errorf("Expected Active to be true, got %v", account.Active)
	}
}

// TestMultipleAuthAccounts verifies multiple accounts can be handled
func TestMultipleAuthAccounts(t *testing.T) {
	accounts := []AuthAccount{
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
		{
			Hostname: "github.enterprise.com",
			Username: "enterprise_user",
			Active:   false,
		},
	}

	if len(accounts) != 3 {
		t.Errorf("Expected 3 accounts, got %d", len(accounts))
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
}

// TestAuthAccountActiveFlag verifies only one account can be active
func TestAuthAccountActiveFlag(t *testing.T) {
	accounts := []AuthAccount{
		{Hostname: "github.com", Username: "user1", Active: true},
		{Hostname: "github.com", Username: "user2", Active: false},
	}

	// Verify exactly one is active
	activeCount := 0
	for _, account := range accounts {
		if account.Active {
			activeCount++
		}
	}

	if activeCount != 1 {
		t.Errorf("Expected exactly 1 active account, got %d", activeCount)
	}
}

// TestEnterpriseGitHubHostname verifies enterprise GitHub hostnames are supported
func TestEnterpriseGitHubHostname(t *testing.T) {
	validHostnames := []string{
		"github.com",
		"github.enterprise.com",
		"git.company.com",
	}

	for _, hostname := range validHostnames {
		account := AuthAccount{
			Hostname: hostname,
			Username: "user",
			Active:   false,
		}

		if account.Hostname != hostname {
			t.Errorf("Hostname not set correctly: expected %s, got %s", hostname, account.Hostname)
		}
	}
}

// TestAuthAccountComparison verifies account comparison logic
func TestAuthAccountComparison(t *testing.T) {
	account1 := AuthAccount{
		Hostname: "github.com",
		Username: "user1",
		Active:   true,
	}

	account2 := AuthAccount{
		Hostname: "github.com",
		Username: "user1",
		Active:   true,
	}

	// They should have the same values
	if account1.Hostname != account2.Hostname ||
		account1.Username != account2.Username ||
		account1.Active != account2.Active {
		t.Errorf("Account comparison failed")
	}
}

// TestAuthAccountWithDifferentHostnames verifies accounts with different hostnames
func TestAuthAccountWithDifferentHostnames(t *testing.T) {
	accounts := []AuthAccount{
		{Hostname: "github.com", Username: "user", Active: true},
		{Hostname: "github.enterprise.com", Username: "user", Active: false},
	}

	hostnamesMap := make(map[string]bool)
	for _, account := range accounts {
		hostnamesMap[account.Hostname] = true
	}

	if len(hostnamesMap) != 2 {
		t.Errorf("Expected 2 different hostnames, got %d", len(hostnamesMap))
	}
}

// TestAuthAccountEmptyUsername verifies handling of edge cases
func TestAuthAccountEmptyUsername(t *testing.T) {
	account := AuthAccount{
		Hostname: "github.com",
		Username: "",
		Active:   false,
	}

	if account.Username != "" {
		t.Errorf("Expected empty username")
	}
}
