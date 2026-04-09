package ui

import (
	"testing"
)

// TestGetMapTemplates verifies all 5 map templates are available
func TestGetMapTemplates(t *testing.T) {
	templates := GetMapTemplates()

	if len(templates) != 5 {
		t.Fatalf("Expected 5 map templates, got %d", len(templates))
	}
}

// TestMapTemplateStructure verifies each template has required fields
func TestMapTemplateStructure(t *testing.T) {
	templates := GetMapTemplates()

	for i, template := range templates {
		if template.ID == "" {
			t.Errorf("Template %d has empty ID", i)
		}
		if template.Name == "" {
			t.Errorf("Template %d has empty Name", i)
		}
		if template.Description == "" {
			t.Errorf("Template %d has empty Description", i)
		}
		if template.Emoji == "" {
			t.Errorf("Template %d has empty Emoji", i)
		}
		if template.Difficulty == "" {
			t.Errorf("Template %d has empty Difficulty", i)
		}
	}
}

// TestMapTemplateNPCs verifies each template has 3 NPCs
func TestMapTemplateNPCs(t *testing.T) {
	templates := GetMapTemplates()

	for i, template := range templates {
		if len(template.NPCs) != 3 {
			t.Errorf("Template %d (%s) has %d NPCs, expected 3", i, template.Name, len(template.NPCs))
		}

		for j, npc := range template.NPCs {
			if npc.ID == "" {
				t.Errorf("Template %d NPC %d has empty ID", i, j)
			}
			if npc.Name == "" {
				t.Errorf("Template %d NPC %d has empty Name", i, j)
			}
			if npc.Type == "" {
				t.Errorf("Template %d NPC %d has empty Type", i, j)
			}
			if npc.Emoji == "" {
				t.Errorf("Template %d NPC %d has empty Emoji", i, j)
			}
			if npc.Position == "" {
				t.Errorf("Template %d NPC %d has empty Position", i, j)
			}
		}
	}
}

// TestMapTemplateTerrainDistribution verifies terrain percentages are valid
func TestMapTemplateTerrainDistribution(t *testing.T) {
	templates := GetMapTemplates()

	for i, template := range templates {
		total := 0
		for _, percentage := range template.TerrainType {
			total += percentage
		}
		if total != 100 {
			t.Errorf("Template %d (%s) terrain percentages sum to %d, expected 100", i, template.Name, total)
		}
	}
}

// TestMapTemplateUniqueness verifies all templates have unique IDs
func TestMapTemplateUniqueness(t *testing.T) {
	templates := GetMapTemplates()
	seen := make(map[string]bool)

	for _, template := range templates {
		if seen[template.ID] {
			t.Errorf("Duplicate template ID: %s", template.ID)
		}
		seen[template.ID] = true
	}
}

// TestMapTemplateFeatures verifies each template has features defined
func TestMapTemplateFeatures(t *testing.T) {
	templates := GetMapTemplates()

	for i, template := range templates {
		if len(template.Features) == 0 {
			t.Errorf("Template %d (%s) has no features defined", i, template.Name)
		}
	}
}

// TestNPCTypes verifies NPCs have valid types
func TestNPCTypes(t *testing.T) {
	templates := GetMapTemplates()
	validTypes := map[string]bool{
		"trainer":    true,
		"shopkeeper": true,
		"healer":     true,
		"elder":      true,
	}

	for _, template := range templates {
		for _, npc := range template.NPCs {
			if !validTypes[npc.Type] {
				t.Errorf("NPC %s has invalid type: %s", npc.Name, npc.Type)
			}
		}
	}
}

// TestNPCPositions verifies NPCs have valid positions
func TestNPCPositions(t *testing.T) {
	templates := GetMapTemplates()
	validPositions := map[string]bool{
		"center": true,
		"north":  true,
		"south":  true,
		"east":   true,
		"west":   true,
	}

	for _, template := range templates {
		for _, npc := range template.NPCs {
			if !validPositions[npc.Position] {
				t.Errorf("NPC %s has invalid position: %s", npc.Name, npc.Position)
			}
		}
	}
}
