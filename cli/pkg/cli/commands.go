package cli

import (
	"agent-monster-cli/pkg/logger"
	"agent-monster-cli/pkg/ugc"
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"time"
)

// LoggerAdapter adapts logger.Logger to ugc.Logger interface
type LoggerAdapter struct {
	log *logger.Logger
}

func (la *LoggerAdapter) Info(format string, args ...interface{}) {
	la.log.Info(format, args...)
}

func (la *LoggerAdapter) Error(format string, args ...interface{}) {
	la.log.Error(format, args...)
}

func (la *LoggerAdapter) Warn(format string, args ...interface{}) {
	la.log.Warn(format, args...)
}

func (la *LoggerAdapter) Debug(format string, args ...interface{}) {
	la.log.Debug(format, args...)
}

// MapCommand handles map-related CLI commands
type MapCommand struct {
	log         *logger.Logger
	ulog        ugc.Logger
	userDataDir string
	validator   *ugc.MapValidator
	exporter    *ugc.MapExporter
	marketplace *ugc.MapMarketplace
}

// NewMapCommand creates a new map command handler
func NewMapCommand(userDataDir string) *MapCommand {
	log := logger.Get()
	ulog := &LoggerAdapter{log: log}

	// Initialize UGC components
	validator := ugc.NewMapValidator(ulog)
	exporter := ugc.NewMapExporter(
		filepath.Join(userDataDir, "maps"),
		ugc.NewSimpleGitHubHelper("", "", "", ulog),
		ulog,
	)
	marketplace := ugc.NewMapMarketplace(ulog)

	return &MapCommand{
		log:         log,
		ulog:        ulog,
		userDataDir: userDataDir,
		validator:   validator,
		exporter:    exporter,
		marketplace: marketplace,
	}
}

// Execute handles the map command execution
func (mc *MapCommand) Execute(args []string) error {
	if len(args) < 1 {
		return mc.printUsage()
	}

	subcommand := args[0]
	switch subcommand {
	case "create":
		return mc.handleCreate(args[1:])
	case "validate":
		return mc.handleValidate(args[1:])
	case "export":
		return mc.handleExport(args[1:])
	case "list":
		return mc.handleList(args[1:])
	case "info":
		return mc.handleInfo(args[1:])
	case "help":
		return mc.printUsage()
	default:
		return fmt.Errorf("Unknown map command: %s", subcommand)
	}
}

// handleCreate creates a new map interactively
func (mc *MapCommand) handleCreate(args []string) error {
	fs := flag.NewFlagSet("map create", flag.ContinueOnError)
	title := fs.String("title", "", "Map title")
	template := fs.String("template", "starter", "Map template (starter, advanced, custom)")
	difficulty := fs.String("difficulty", "medium", "Difficulty level (easy, medium, hard)")

	if err := fs.Parse(args); err != nil {
		return err
	}

	mc.log.Info("Creating new map...")
	fmt.Println("\n╔════════════════════════════════════════════════════════╗")
	fmt.Println("║              Create New Map                           ║")
	fmt.Println("╚════════════════════════════════════════════════════════╝")

	// Get map title if not provided
	if *title == "" {
		fmt.Print("\nEnter map title: ")
		fmt.Scanln(title)
	}

	// Validate inputs
	if *title == "" {
		return fmt.Errorf("Map title is required")
	}

	validTemplates := map[string]bool{"starter": true, "advanced": true, "custom": true}
	if !validTemplates[*template] {
		return fmt.Errorf("Invalid template: %s (must be starter, advanced, or custom)", *template)
	}

	validDifficulties := map[string]bool{"easy": true, "medium": true, "hard": true}
	if !validDifficulties[*difficulty] {
		return fmt.Errorf("Invalid difficulty: %s (must be easy, medium, or hard)", *difficulty)
	}

	// Create map data from template
	mapData := mc.generateMapFromTemplate(*template)

	// Create metadata
	metadata := ugc.MapMetadata{
		MapID:       generateMapID(),
		Title:       *title,
		Difficulty:  *difficulty,
		OwnerName:   "local-user",
		Description: fmt.Sprintf("Map created with %s template", *template),
		Version:     "1.0.0",
		Tags:        []string{*template, *difficulty},
		CreatedAt:   time.Now(),
		UpdatedAt:   time.Now(),
	}

	// Save map locally
	mapsDir := filepath.Join(mc.userDataDir, "maps")
	if err := os.MkdirAll(mapsDir, 0755); err != nil {
		return fmt.Errorf("Failed to create maps directory: %w", err)
	}

	mapFile := filepath.Join(mapsDir, fmt.Sprintf("%s.json", metadata.MapID))
	data, err := json.MarshalIndent(mapData, "", "  ")
	if err != nil {
		return fmt.Errorf("Failed to marshal map data: %w", err)
	}

	if err := os.WriteFile(mapFile, data, 0644); err != nil {
		return fmt.Errorf("Failed to save map file: %w", err)
	}

	mc.log.Info("Map created successfully: %s", metadata.MapID)
	fmt.Printf("\n✓ Map created successfully!\n")
	fmt.Printf("  Map ID: %s\n", metadata.MapID)
	fmt.Printf("  Title: %s\n", metadata.Title)
	fmt.Printf("  Location: %s\n", mapFile)
	fmt.Printf("\nNext steps:\n")
	fmt.Printf("  1. Run 'map validate %s' to validate the map\n", metadata.MapID)
	fmt.Printf("  2. Run 'map export %s' to export to GitHub\n", metadata.MapID)

	return nil
}

// handleValidate validates a map and shows score
func (mc *MapCommand) handleValidate(args []string) error {
	if len(args) < 1 {
		return fmt.Errorf("Usage: map validate <map_id>")
	}

	mapID := args[0]
	mc.log.Info("Validating map: %s", mapID)

	fmt.Printf("\n╔════════════════════════════════════════════════════════╗\n")
	fmt.Printf("║            Validating Map: %s\n", padRight(mapID, 33))
	fmt.Printf("╚════════════════════════════════════════════════════════╝\n")

	// Load map data
	mapFile := filepath.Join(mc.userDataDir, "maps", fmt.Sprintf("%s.json", mapID))
	data, err := os.ReadFile(mapFile)
	if err != nil {
		return fmt.Errorf("Failed to read map file: %w", err)
	}

	var mapData interface{}
	if err := json.Unmarshal(data, &mapData); err != nil {
		return fmt.Errorf("Invalid JSON in map file: %w", err)
	}

	// Create minimal metadata for validation
	metadata := ugc.MapMetadata{
		MapID:     mapID,
		Title:     "Validation Test",
		OwnerName: "validator",
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}

	// Validate
	result := mc.validator.ValidateMap(mapData, metadata)

	// Display results
	fmt.Printf("\n📊 Validation Results:\n\n")
	fmt.Printf("  Overall Score: %d/100\n", int(result.Score))
	fmt.Printf("  Valid: %v\n\n", result.IsValid)

	if len(result.Errors) > 0 {
		fmt.Printf("\n⚠️  Issues Found:\n")
		for _, err := range result.Errors {
			fmt.Printf("  - %s\n", err)
		}
	}

	if len(result.Warnings) > 0 {
		fmt.Printf("\n💡 Suggestions:\n")
		for _, warn := range result.Warnings {
			fmt.Printf("  - %s\n", warn)
		}
	}

	if len(result.Errors) == 0 {
		fmt.Printf("\n✓ Map is valid and ready for export!\n")
	} else {
		fmt.Printf("\n✗ Map has issues that should be fixed before export.\n")
	}

	return nil
}

// handleExport exports a map to GitHub
func (mc *MapCommand) handleExport(args []string) error {
	fs := flag.NewFlagSet("map export", flag.ContinueOnError)
	githubToken := fs.String("token", "", "GitHub token (optional, can be set via GITHUB_TOKEN env)")
	githubUser := fs.String("user", "", "GitHub username (optional)")

	if err := fs.Parse(args); err != nil {
		return err
	}

	if len(fs.Args()) < 1 {
		return fmt.Errorf("Usage: map export [options] <map_id>")
	}

	mapID := fs.Args()[0]
	mc.log.Info("Exporting map: %s", mapID)

	fmt.Printf("\n╔════════════════════════════════════════════════════════╗\n")
	fmt.Printf("║            Export Map to GitHub: %s\n", padRight(mapID, 20))
	fmt.Printf("╚════════════════════════════════════════════════════════╝\n")

	// Load map
	mapFile := filepath.Join(mc.userDataDir, "maps", fmt.Sprintf("%s.json", mapID))
	data, err := os.ReadFile(mapFile)
	if err != nil {
		return fmt.Errorf("Failed to read map file: %w", err)
	}

	var mapData interface{}
	if err := json.Unmarshal(data, &mapData); err != nil {
		return fmt.Errorf("Invalid JSON in map file: %w", err)
	}

	metadata := ugc.MapMetadata{
		MapID:       mapID,
		Title:       "Exported Map",
		OwnerName:   *githubUser,
		Description: "Map exported via CLI",
		Version:     "1.0.0",
		Tags:        []string{"exported"},
		CreatedAt:   time.Now(),
		UpdatedAt:   time.Now(),
	}

	if *githubToken == "" {
		*githubToken = os.Getenv("GITHUB_TOKEN")
	}

	if *githubToken == "" {
		return fmt.Errorf("GitHub token required (provide via --token flag or GITHUB_TOKEN environment variable)")
	}

	// Export using the exporter
	localPath, repoPath, err := mc.exporter.ExportMap(mapData, metadata)
	if err != nil {
		return fmt.Errorf("Export failed: %w", err)
	}

	fmt.Printf("\n✓ Map exported successfully!\n")
	fmt.Printf("  Local path: %s\n", localPath)
	fmt.Printf("  Repo path: %s\n", repoPath)
	fmt.Printf("\nNext steps:\n")
	fmt.Printf("  1. Visit the repository to view your map\n")
	fmt.Printf("  2. Submit a pull request to contribute to the community\n")

	return nil
}

// handleList lists available maps
func (mc *MapCommand) handleList(args []string) error {
	fs := flag.NewFlagSet("map list", flag.ContinueOnError)
	source := fs.String("source", "local", "Source to list from (local, community)")
	difficulty := fs.String("difficulty", "", "Filter by difficulty (easy, medium, hard)")

	if err := fs.Parse(args); err != nil {
		return err
	}

	fmt.Printf("\n╔════════════════════════════════════════════════════════╗\n")
	fmt.Printf("║            Available %s Maps\n", strings.Title(*source))
	fmt.Printf("╚════════════════════════════════════════════════════════╝\n\n")

	if *source == "local" {
		return mc.listLocalMaps(*difficulty)
	} else if *source == "community" {
		fmt.Println("Community marketplace coming soon!")
		return nil
	}

	return fmt.Errorf("Unknown source: %s", *source)
}

// handleInfo shows detailed information about a map
func (mc *MapCommand) handleInfo(args []string) error {
	if len(args) < 1 {
		return fmt.Errorf("Usage: map info <map_id>")
	}

	mapID := args[0]
	mc.log.Info("Getting info for map: %s", mapID)

	mapFile := filepath.Join(mc.userDataDir, "maps", fmt.Sprintf("%s.json", mapID))
	data, err := os.ReadFile(mapFile)
	if err != nil {
		return fmt.Errorf("Map not found: %s", mapID)
	}

	var mapData map[string]interface{}
	if err := json.Unmarshal(data, &mapData); err != nil {
		return fmt.Errorf("Invalid map file: %w", err)
	}

	fmt.Printf("\n╔════════════════════════════════════════════════════════╗\n")
	fmt.Printf("║            Map Information: %s\n", padRight(mapID, 20))
	fmt.Printf("╚════════════════════════════════════════════════════════╝\n")
	fmt.Printf("\nMap Data Preview:\n")
	fmt.Printf("%s\n", formatJSON(mapData))

	return nil
}

// Helper functions

func (mc *MapCommand) printUsage() error {
	fmt.Println(`
╔════════════════════════════════════════════════════════╗
║            Agent Monster Map Commands                 ║
╚════════════════════════════════════════════════════════╝

Usage: map <command> [options]

Commands:
  create [--title <title>] [--template <template>] [--difficulty <level>]
          Create a new map interactively
          Templates: starter, advanced, custom
          Difficulties: easy, medium, hard

  validate <map_id>
           Validate a map and show quality score (0-100)

  export [--token <token>] [--user <username>] <map_id>
          Export map to GitHub for community submission
          Token can be set via GITHUB_TOKEN environment variable

  list [--source <source>] [--difficulty <level>]
        List available maps
        Sources: local (default), community
        Difficulties: easy, medium, hard

  info <map_id>
       Show detailed information about a map

  help
       Show this help message

Examples:
  map create --title "My Adventure" --difficulty hard
  map validate my_map_001
  map export --user myusername my_map_001
  map list --source community --difficulty easy
  map info my_map_001
`)
	return nil
}

func (mc *MapCommand) listLocalMaps(difficulty string) error {
	mapsDir := filepath.Join(mc.userDataDir, "maps")
	entries, err := os.ReadDir(mapsDir)
	if err != nil {
		if os.IsNotExist(err) {
			fmt.Println("No local maps found.")
			return nil
		}
		return fmt.Errorf("Failed to read maps directory: %w", err)
	}

	if len(entries) == 0 {
		fmt.Println("No local maps found.")
		return nil
	}

	fmt.Println("Local Maps:")
	fmt.Println("─────────────────────────────────────────────────────────")
	for _, entry := range entries {
		if !entry.IsDir() && strings.HasSuffix(entry.Name(), ".json") {
			mapID := strings.TrimSuffix(entry.Name(), ".json")
			fmt.Printf("  • %s\n", mapID)
		}
	}

	return nil
}

func (mc *MapCommand) generateMapFromTemplate(template string) map[string]interface{} {
	baseMap := map[string]interface{}{
		"terrain": map[string]interface{}{
			"width":  20,
			"height": 20,
			"type":   "grass",
		},
		"elements": []map[string]interface{}{},
	}

	switch template {
	case "starter":
		// Basic starter map with a few pokemon and items
		baseMap["elements"] = []map[string]interface{}{
			{"type": "wild_pokemon", "x": 5, "y": 5, "data": map[string]interface{}{"species": "Psyduck", "level": 1}},
			{"type": "food", "x": 10, "y": 10, "data": map[string]interface{}{"kind": "apple"}},
		}
	case "advanced":
		// More complex map with various terrain types
		baseMap["elements"] = []map[string]interface{}{
			{"type": "wild_pokemon", "x": 3, "y": 3, "data": map[string]interface{}{"species": "Pikachu", "level": 5}},
			{"type": "wild_pokemon", "x": 15, "y": 15, "data": map[string]interface{}{"species": "Bulbasaur", "level": 3}},
			{"type": "food", "x": 8, "y": 8, "data": map[string]interface{}{"kind": "berry"}},
			{"type": "obstacle", "x": 12, "y": 5, "data": map[string]interface{}{"kind": "rock"}},
		}
	default:
		// Custom empty map
		baseMap["elements"] = []map[string]interface{}{}
	}

	return baseMap
}

func generateMapID() string {
	return fmt.Sprintf("map_%d_%d", time.Now().Unix(), os.Getpid())
}

func padRight(s string, length int) string {
	if len(s) >= length {
		return s[:length]
	}
	return s + strings.Repeat(" ", length-len(s))
}

func formatJSON(data interface{}) string {
	jsonData, err := json.MarshalIndent(data, "  ", "  ")
	if err != nil {
		return fmt.Sprintf("%v", data)
	}
	return string(jsonData)
}
