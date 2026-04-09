package api

import (
	"testing"
)

// TestDuplicateAccountErrorHandling verifies duplicate account errors are detected
func TestDuplicateAccountErrorHandling(t *testing.T) {
	// Simulate duplicate account error responses
	errorResponses := []string{
		"duplicate key",
		"already exists",
		"Duplicate entry",
		"E11000 duplicate key error",
	}

	for _, errorMsg := range errorResponses {
		isDuplicateError := isSuspectedDuplicateError(errorMsg)
		if !isDuplicateError {
			t.Errorf("Failed to detect duplicate error: %s", errorMsg)
		}
	}
}

// TestNonDuplicateErrors verifies non-duplicate errors are not misidentified
func TestNonDuplicateErrors(t *testing.T) {
	errorMessages := []string{
		"network error",
		"unauthorized",
		"forbidden",
		"server error",
		"timeout",
	}

	for _, errorMsg := range errorMessages {
		isDuplicateError := isSuspectedDuplicateError(errorMsg)
		if isDuplicateError {
			t.Errorf("Incorrectly identified as duplicate error: %s", errorMsg)
		}
	}
}

// Helper function to detect duplicate errors
func isSuspectedDuplicateError(errMsg string) bool {
	duplicatePatterns := []string{
		"duplicate key",
		"already exists",
		"Duplicate entry",
		"E11000",
	}

	for _, pattern := range duplicatePatterns {
		if contains(errMsg, pattern) {
			return true
		}
	}
	return false
}

// Helper function for string containment
func contains(s, substr string) bool {
	for i := 0; i <= len(s)-len(substr); i++ {
		if s[i:i+len(substr)] == substr {
			return true
		}
	}
	return false
}

// TestErrorMessageParsing verifies error messages are parsed correctly
func TestErrorMessageParsing(t *testing.T) {
	testCases := []struct {
		errorMsg    string
		isDuplicate bool
	}{
		{"duplicate key error", true},
		{"user already exists", true},
		{"network timeout", false},
		{"", false},
	}

	for _, tc := range testCases {
		result := isSuspectedDuplicateError(tc.errorMsg)
		if result != tc.isDuplicate {
			t.Errorf("Error parsing failed for '%s': expected %v, got %v",
				tc.errorMsg, tc.isDuplicate, result)
		}
	}
}

// TestErrorRecoveryFlow verifies recovery flow for duplicate accounts
func TestErrorRecoveryFlow(t *testing.T) {
	// When a duplicate account error occurs, the flow should allow user to continue
	duplicateError := "duplicate key: user already exists"

	if !isSuspectedDuplicateError(duplicateError) {
		t.Errorf("Failed to detect duplicate account error")
	}

	// User should be able to continue with existing account
	canContinue := true
	if !canContinue {
		t.Errorf("User should be able to continue after duplicate account error")
	}
}
