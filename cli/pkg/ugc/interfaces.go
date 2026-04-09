package ugc

import "log"

// Logger 日志接口
type Logger interface {
	Info(format string, args ...interface{})
	Error(format string, args ...interface{})
	Warn(format string, args ...interface{})
	Debug(format string, args ...interface{})
}

// SimpleLogger 简单的日志实现
type SimpleLogger struct {
	verbose bool
}

func NewSimpleLogger(verbose bool) *SimpleLogger {
	return &SimpleLogger{verbose: verbose}
}

func (l *SimpleLogger) Info(format string, args ...interface{}) {
	log.Printf("[INFO] "+format, args...)
}

func (l *SimpleLogger) Error(format string, args ...interface{}) {
	log.Printf("[ERROR] "+format, args...)
}

func (l *SimpleLogger) Warn(format string, args ...interface{}) {
	log.Printf("[WARN] "+format, args...)
}

func (l *SimpleLogger) Debug(format string, args ...interface{}) {
	if l.verbose {
		log.Printf("[DEBUG] "+format, args...)
	}
}

// GitHubHelper GitHub操作接口
type GitHubHelper interface {
	// PushFilesToRepo 推送文件到repo
	PushFilesToRepo(files map[string]string) error

	// CreatePullRequest 创建PR
	CreatePullRequest(title, body string, fromBranch string) (string, error)

	// GetRepoInfo 获取repo信息
	GetRepoInfo() (map[string]interface{}, error)

	// GetUserRepoURL 获取用户repo URL
	GetUserRepoURL(username string) string

	// CloneUserRepo 克隆用户repo
	CloneUserRepo(username string, destPath string) error

	// CheckRepoExists 检查repo是否存在
	CheckRepoExists(username string, repoName string) bool
}

// SimpleGitHubHelper GitHub操作的简单实现
type SimpleGitHubHelper struct {
	token    string
	username string
	repoName string
	logger   Logger
}

func NewSimpleGitHubHelper(token, username, repoName string, logger Logger) *SimpleGitHubHelper {
	return &SimpleGitHubHelper{
		token:    token,
		username: username,
		repoName: repoName,
		logger:   logger,
	}
}

func (gh *SimpleGitHubHelper) PushFilesToRepo(files map[string]string) error {
	gh.logger.Info("推送 %d 个文件到repo", len(files))
	// TODO: 实现GitHub API调用
	return nil
}

func (gh *SimpleGitHubHelper) CreatePullRequest(title, body string, fromBranch string) (string, error) {
	gh.logger.Info("创建PR: %s", title)
	// TODO: 实现GitHub API调用
	return "", nil
}

func (gh *SimpleGitHubHelper) GetRepoInfo() (map[string]interface{}, error) {
	return map[string]interface{}{
		"username": gh.username,
		"repo":     gh.repoName,
	}, nil
}

func (gh *SimpleGitHubHelper) GetUserRepoURL(username string) string {
	return "https://github.com/" + username + "/" + gh.repoName
}

func (gh *SimpleGitHubHelper) CloneUserRepo(username string, destPath string) error {
	gh.logger.Info("克隆用户repo: %s -> %s", username, destPath)
	// TODO: 实现git clone
	return nil
}

func (gh *SimpleGitHubHelper) CheckRepoExists(username string, repoName string) bool {
	// TODO: 实现repo存在检查
	return true
}
