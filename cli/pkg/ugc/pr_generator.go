package ugc

import (
	"fmt"
	"time"
)

// PullRequestInfo PR information
type PullRequestInfo struct {
	Title           string
	Description     string
	Branch          string
	MapID           string
	MapTitle        string
	OwnerName       string
	ValidationScore int
	Timestamp       time.Time
}

// PRGenerator generates and submits PR to main repo
type PRGenerator struct {
	mainRepoURL string
	github      GitHubHelper
	validator   *MapValidator
	logger      Logger
}

func NewPRGenerator(mainRepoURL string, github GitHubHelper, validator *MapValidator, logger Logger) *PRGenerator {
	return &PRGenerator{
		mainRepoURL: mainRepoURL,
		github:      github,
		validator:   validator,
		logger:      logger,
	}
}

// GeneratePR generates PR for map
func (pg *PRGenerator) GeneratePR(metadata MapMetadata, validationScore int) (*PullRequestInfo, error) {
	pg.logger.Info("Generating PR for map: %s (owner: %s)", metadata.MapID, metadata.OwnerName)

	// Build PR info
	prInfo := &PullRequestInfo{
		MapID:           metadata.MapID,
		MapTitle:        metadata.Title,
		OwnerName:       metadata.OwnerName,
		ValidationScore: validationScore,
		Timestamp:       time.Now(),
	}

	// Build branch name
	prInfo.Branch = pg.buildBranchName(metadata)

	// Build PR title
	prInfo.Title = pg.buildPRTitle(metadata)

	// Build PR description
	prInfo.Description = pg.buildPRDescription(metadata, validationScore)

	pg.logger.Info("PR Title: %s", prInfo.Title)
	pg.logger.Info("PR Branch: %s", prInfo.Branch)

	return prInfo, nil
}

// SubmitPR submits PR to main repo
func (pg *PRGenerator) SubmitPR(prInfo *PullRequestInfo) (string, error) {
	pg.logger.Info("Submitting PR: %s", prInfo.Title)

	// Submit to GitHub
	prURL, err := pg.github.CreatePullRequest(prInfo.Title, prInfo.Description, prInfo.Branch)
	if err != nil {
		return "", fmt.Errorf("failed to submit PR: %w", err)
	}

	pg.logger.Info("PR created successfully: %s", prURL)
	return prURL, nil
}

// buildBranchName builds branch name for PR
func (pg *PRGenerator) buildBranchName(metadata MapMetadata) string {
	timestamp := time.Now().Format("20060102_150405")
	return fmt.Sprintf("map/submit/%s/%s_%s",
		metadata.OwnerName,
		metadata.MapID,
		timestamp,
	)
}

// buildPRTitle builds PR title
func (pg *PRGenerator) buildPRTitle(metadata MapMetadata) string {
	return fmt.Sprintf("Map Submission: [%s] %s by @%s",
		metadata.Difficulty,
		metadata.Title,
		metadata.OwnerName,
	)
}

// buildPRDescription builds PR description
func (pg *PRGenerator) buildPRDescription(metadata MapMetadata, validationScore int) string {
	description := fmt.Sprintf(`## Map Contribution Submission

### Basic Information
- Map ID: %s
- Map Title: %s
- Author: @%s
- Difficulty: %s
- Quality Score: %d/100

### Description
%s

### Map Features
- Tags: %s
- Created: %s
- Version: %s

### Validation Result
Passed format validation (Score: %d/100)

### License
This Map is licensed under CC-BY-4.0

---

### Submission Guidelines
1. This Map has been automatically validated for format
2. Maintainers will review Map quality and balance
3. Any issues will be noted for revision

Thank you for contributing!
`,
		metadata.MapID,
		metadata.Title,
		metadata.OwnerName,
		metadata.Difficulty,
		validationScore,
		metadata.Description,
		fmt.Sprintf("%v", metadata.Tags),
		metadata.CreatedAt.Format("2006-01-02 15:04:05"),
		metadata.Version,
		validationScore,
	)

	return description
}

// GetSubmissionGuide returns Map submission guide
func (pg *PRGenerator) GetSubmissionGuide() string {
	guide := `Map Submission Guide

Overview
Agent Monster is a community-driven project. You can create your own Maps 
and submit them to the main project for other players to explore.

Submission Process

1. Fork the main repository
   gh repo fork chengjia2016/agent-monster

2. Create your Map
   ./agentmonster map create --title "My Awesome Map" \
                            --description "An interesting map" \
                            --difficulty hard

3. Validate Map
   The system automatically validates your Map:
   - Format validation (ensures correct structure)
   - Balance check (element proportions)
   - Diversity check (Pokemon and item variety)

4. Export Map
   Export Map to your Fork repository:
   ./agentmonster map export <map_id>

5. Submit PR
   Create a Pull Request to the main repository:
   gh pr create --title "Add Map: My Awesome Map" \
               --body "This is a new Map created by..."

Map Metadata Requirements

Your Map must include:
- Title (1-100 characters) - Name of the Map
- Description (10-1000 characters) - Detailed description
- Difficulty (easy/medium/hard) - Difficulty level
- Tags - Keywords (maximum 5)
- Version - Map version (e.g., 1.0.0)
- License - Usually CC-BY-4.0

Map Design Recommendations

Size
- Minimum: 10x10 (100 tiles)
- Maximum: 100x100 (10000 tiles)
- Recommended: 20x40 (balanced map)

Element Balance
- Wild Pokemon: 30-50% of elements
- Food: 20-30% of elements
- Obstacles: 15-25% of elements
- NPCs/Other: 5-10% of elements

Content Diversity
- At least 3 different Pokemon types
- At least 2 different food types
- Diverse terrain (grass, forest, water, mountain)

Scoring System

Submitted Maps receive a score of 0-100:
- 90-100: Excellent - Direct merge
- 70-89: Good - May need minor improvements
- < 70: Needs improvement - Requires adjustment before resubmission

Scoring Criteria
1. Format Completeness (20 points) - All required fields present
2. Balance (30 points) - Element proportions reasonable
3. Diversity (25 points) - Content variety
4. Creativity (15 points) - Unique and interesting design
5. Documentation (10 points) - Clear description

FAQ

Q: What if my Map is rejected?
A: Maintainers will provide specific improvement suggestions. 
   You can resubmit after making changes.

Q: How many Maps can one user submit?
A: No limit! But ensure quality before submitting many Maps.

Q: Will my Map be modified?
A: May undergo minor adjustments for game balance. 
   Major changes will be discussed with you first.

Q: How do I update my submitted Map?
A: Submit a new PR with "Update: Map Name" in the title.

Contributor License Agreement

By submitting a Map, you agree that:
- You have rights to submit this content
- Content follows CC-BY-4.0 license
- Map as project part can be used by anyone

Thank you for contributing to Agent Monster community!
`
	return guide
}
