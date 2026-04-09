package github

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"os"
	"os/exec"
	"strings"
	"time"
)

// GitHubClient handles GitHub API interactions
type GitHubClient struct {
	Token   string
	BaseURL string
	Client  *http.Client
}

// AuthAccount represents a GitHub authentication account
type AuthAccount struct {
	Hostname string
	Username string
	Active   bool
}

// Repository represents a GitHub repository
type Repository struct {
	Name        string `json:"name"`
	FullName    string `json:"full_name"`
	Description string `json:"description"`
	URL         string `json:"html_url"`
	Stars       int    `json:"stargazers_count"`
	Forks       int    `json:"forks_count"`
	Language    string `json:"language"`
	IsPrivate   bool   `json:"private"`
}

// Issue represents a GitHub issue
type Issue struct {
	Number  int       `json:"number"`
	Title   string    `json:"title"`
	Body    string    `json:"body"`
	State   string    `json:"state"`
	URL     string    `json:"html_url"`
	Created time.Time `json:"created_at"`
	Updated time.Time `json:"updated_at"`
}

// PullRequest represents a GitHub pull request
type PullRequest struct {
	Number  int       `json:"number"`
	Title   string    `json:"title"`
	Body    string    `json:"body"`
	State   string    `json:"state"`
	URL     string    `json:"html_url"`
	Created time.Time `json:"created_at"`
	Updated time.Time `json:"updated_at"`
}

// User represents a GitHub user
type User struct {
	ID          int    `json:"id"`
	Login       string `json:"login"`
	Name        string `json:"name"`
	AvatarURL   string `json:"avatar_url"`
	Bio         string `json:"bio"`
	Location    string `json:"location"`
	PublicRepos int    `json:"public_repos"`
}

// NewGitHubClient creates a new GitHub client
func NewGitHubClient() (*GitHubClient, error) {
	token, err := GetGitHubToken()
	if err != nil {
		return nil, err
	}

	return &GitHubClient{
		Token:   token,
		BaseURL: "https://api.github.com",
		Client: &http.Client{
			Timeout: 10 * time.Second,
		},
	}, nil
}

// GetGitHubToken retrieves the GitHub CLI token
func GetGitHubToken() (string, error) {
	// Try to get token from gh CLI
	cmd := exec.Command("gh", "auth", "token")
	output, err := cmd.Output()
	if err != nil {
		return "", fmt.Errorf("failed to get GitHub token: %w", err)
	}

	token := strings.TrimSpace(string(output))
	if token == "" {
		return "", fmt.Errorf("GitHub token is empty")
	}

	return token, nil
}

// IsGitHubLoggedIn checks if user is logged into GitHub CLI
func IsGitHubLoggedIn() bool {
	cmd := exec.Command("gh", "auth", "status")
	err := cmd.Run()
	return err == nil
}

// GetAuthAccounts retrieves all logged-in GitHub accounts
func GetAuthAccounts() ([]AuthAccount, error) {
	cmd := exec.Command("gh", "auth", "status", "--show-token")
	output, err := cmd.CombinedOutput()
	if err != nil {
		return nil, fmt.Errorf("failed to get auth status: %w", err)
	}

	// Parse the output to extract account information
	lines := strings.Split(string(output), "\n")
	var accounts []AuthAccount

	for _, line := range lines {
		line = strings.TrimSpace(line)
		if line == "" {
			continue
		}

		// Parse lines like:
		// "Logged in to github.com as username (keyring)"
		// or just check for presence
		if strings.Contains(line, "Logged in to") {
			// Try to extract hostname and username
			if strings.Contains(line, "as") {
				parts := strings.Split(line, "as")
				if len(parts) >= 2 {
					hostPart := strings.TrimSpace(strings.TrimPrefix(parts[0], "Logged in to"))
					userPart := strings.TrimSpace(parts[1])
					// Remove parentheses and other text
					userPart = strings.Split(userPart, "(")[0]
					userPart = strings.TrimSpace(userPart)

					if hostPart != "" && userPart != "" {
						accounts = append(accounts, AuthAccount{
							Hostname: hostPart,
							Username: userPart,
							Active:   true,
						})
					}
				}
			}
		}
	}

	if len(accounts) == 0 {
		return nil, fmt.Errorf("no GitHub accounts found")
	}

	return accounts, nil
}

// SwitchAccount switches to a different GitHub account
func SwitchAccount(hostname, username string) error {
	// Note: gh CLI doesn't have a direct "switch" command
	// Instead, we would need to manage credentials through the CLI
	// This sets the active account in the gh config
	cmd := exec.Command("gh", "auth", "switch", "-h", hostname)
	return cmd.Run()
}

// LoginToGitHub opens the GitHub login flow
func LoginToGitHub() error {
	cmd := exec.Command("gh", "auth", "login", "--web")
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	cmd.Stdin = os.Stdin
	return cmd.Run()
}

// GetCurrentUser retrieves the authenticated user
func (c *GitHubClient) GetCurrentUser() (*User, error) {
	resp, err := c.makeRequest("GET", "/user", nil)
	if err != nil {
		return nil, err
	}

	if len(resp) == 0 {
		return nil, fmt.Errorf("empty response from GitHub API")
	}

	var user User
	if err := json.Unmarshal(resp, &user); err != nil {
		return nil, fmt.Errorf("failed to unmarshal user: %w (response: %s)", err, string(resp))
	}

	return &user, nil
}

// ListUserRepositories lists repositories for the authenticated user
func (c *GitHubClient) ListUserRepositories() ([]Repository, error) {
	resp, err := c.makeRequest("GET", "/user/repos?sort=updated&per_page=30", nil)
	if err != nil {
		return nil, err
	}

	var repos []Repository
	if err := json.Unmarshal(resp, &repos); err != nil {
		return nil, err
	}

	return repos, nil
}

// GetRepository retrieves a specific repository
func (c *GitHubClient) GetRepository(owner, repo string) (*Repository, error) {
	path := fmt.Sprintf("/repos/%s/%s", url.QueryEscape(owner), url.QueryEscape(repo))
	resp, err := c.makeRequest("GET", path, nil)
	if err != nil {
		return nil, err
	}

	var repository Repository
	if err := json.Unmarshal(resp, &repository); err != nil {
		return nil, err
	}

	return &repository, nil
}

// ListIssues lists issues in a repository
func (c *GitHubClient) ListIssues(owner, repo, state string) ([]Issue, error) {
	path := fmt.Sprintf("/repos/%s/%s/issues?state=%s&per_page=30",
		url.QueryEscape(owner), url.QueryEscape(repo), url.QueryEscape(state))
	resp, err := c.makeRequest("GET", path, nil)
	if err != nil {
		return nil, err
	}

	var issues []Issue
	if err := json.Unmarshal(resp, &issues); err != nil {
		return nil, err
	}

	return issues, nil
}

// ListPullRequests lists pull requests in a repository
func (c *GitHubClient) ListPullRequests(owner, repo, state string) ([]PullRequest, error) {
	path := fmt.Sprintf("/repos/%s/%s/pulls?state=%s&per_page=30",
		url.QueryEscape(owner), url.QueryEscape(repo), url.QueryEscape(state))
	resp, err := c.makeRequest("GET", path, nil)
	if err != nil {
		return nil, err
	}

	var prs []PullRequest
	if err := json.Unmarshal(resp, &prs); err != nil {
		return nil, err
	}

	return prs, nil
}

// makeRequest sends an HTTP request to GitHub API
func (c *GitHubClient) makeRequest(method, path string, body interface{}) ([]byte, error) {
	url := c.BaseURL + path

	req, err := http.NewRequest(method, url, nil)
	if err != nil {
		return nil, err
	}

	req.Header.Set("Authorization", fmt.Sprintf("Bearer %s", c.Token))
	req.Header.Set("Accept", "application/vnd.github.v3+json")
	req.Header.Set("User-Agent", "Agent-Monster-CLI")

	resp, err := c.Client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode < 200 || resp.StatusCode >= 300 {
		return nil, fmt.Errorf("GitHub API error: status %d", resp.StatusCode)
	}

	// Read entire response body properly
	result, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}

	return result, nil
}
