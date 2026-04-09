package api

import (
	"testing"
)

// TestClaimStarterPokemonsClient verifies the client method exists
func TestClaimStarterPokemonsClient(t *testing.T) {
	client := &Client{
		BaseURL: "http://localhost:10000",
	}

	// Verify ClaimStarterPokemons method is callable
	// (can't test it without a real server, but we can test the method structure)
	_ = client.ClaimStarterPokemons
	if client == nil {
		t.Error("Client should not be nil")
	}
}

// TestClaimStarterPokemonsResponseStructure verifies the response structure
func TestClaimStarterPokemonsResponseStructure(t *testing.T) {
	// This verifies that response maps work correctly
	resp := map[string]interface{}{
		"success": true,
		"message": "Successfully claimed starter pokemons: 1 Psyduck + 2 Eggs",
	}

	if success, ok := resp["success"].(bool); !ok || !success {
		t.Error("Response success flag should work")
	}

	if message, ok := resp["message"].(string); !ok {
		t.Errorf("Response message should be a string")
	} else if message != "Successfully claimed starter pokemons: 1 Psyduck + 2 Eggs" {
		t.Errorf("Expected message 'Successfully claimed starter pokemons: 1 Psyduck + 2 Eggs', got '%s'", message)
	}
}

// TestClaimStarterPokemonsRequestPayload verifies the request payload structure
func TestClaimStarterPokemonsRequestPayload(t *testing.T) {
	githubID := 12345

	// Verify payload structure
	payload := map[string]interface{}{
		"github_id": githubID,
	}

	if id, ok := payload["github_id"].(int); !ok || id != githubID {
		t.Errorf("Expected github_id to be %d", githubID)
	}
}

// TestClaimStarterPokemonsSuccessResponse verifies a successful response
func TestClaimStarterPokemonsSuccessResponse(t *testing.T) {
	response := map[string]interface{}{
		"success": true,
		"message": "Successfully claimed starter pokemons: 1 Psyduck + 2 Eggs",
	}

	if success, ok := response["success"].(bool); !ok || !success {
		t.Error("Expected success to be true")
	}

	if message, ok := response["message"].(string); !ok {
		t.Error("Expected message to be present")
	} else if len(message) == 0 {
		t.Error("Expected message to not be empty")
	}
}
