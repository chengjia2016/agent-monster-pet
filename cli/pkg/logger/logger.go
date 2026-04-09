package logger

import (
	"fmt"
	"os"
	"path/filepath"
	"sync"
	"time"
)

type LogLevel int

const (
	DEBUG LogLevel = iota
	INFO
	WARN
	ERROR
)

var levelNames = map[LogLevel]string{
	DEBUG: "DEBUG",
	INFO:  "INFO",
	WARN:  "WARN",
	ERROR: "ERROR",
}

type Logger struct {
	file      *os.File
	logDir    string
	mu        sync.Mutex
	level     LogLevel
	sessionID string
}

var globalLogger *Logger
var once sync.Once

// Init initializes the global logger
func Init(logDir string, level LogLevel) error {
	var err error
	once.Do(func() {
		globalLogger, err = NewLogger(logDir, level)
	})
	return err
}

// NewLogger creates a new logger instance
func NewLogger(logDir string, level LogLevel) (*Logger, error) {
	// Create log directory if it doesn't exist
	if err := os.MkdirAll(logDir, 0755); err != nil {
		return nil, err
	}

	// Generate session ID
	sessionID := time.Now().Format("20060102_150405")

	// Create log file
	logFile := filepath.Join(logDir, fmt.Sprintf("agentmonster_%s.log", sessionID))
	file, err := os.Create(logFile)
	if err != nil {
		return nil, err
	}

	logger := &Logger{
		file:      file,
		logDir:    logDir,
		level:     level,
		sessionID: sessionID,
	}

	// Log startup message
	logger.logToFile("═══════════════════════════════════════════════════════════")
	logger.logToFile("Agent Monster CLI - Session Started")
	logger.logToFile(fmt.Sprintf("Session ID: %s", sessionID))
	logger.logToFile(fmt.Sprintf("Timestamp: %s", time.Now().Format("2006-01-02 15:04:05")))
	logger.logToFile("═══════════════════════════════════════════════════════════")

	return logger, nil
}

// GetGlobalLogger returns the global logger instance
func Get() *Logger {
	if globalLogger == nil {
		// Create a default logger if not initialized
		NewLogger(filepath.Join(os.Getenv("HOME"), ".agentmonster", "logs"), DEBUG)
	}
	return globalLogger
}

func (l *Logger) logToFile(message string) {
	if l.file != nil {
		fmt.Fprintf(l.file, "%s\n", message)
	}
}

func (l *Logger) log(level LogLevel, format string, args ...interface{}) {
	if level < l.level {
		return
	}

	l.mu.Lock()
	defer l.mu.Unlock()

	timestamp := time.Now().Format("15:04:05.000")
	levelName := levelNames[level]
	message := fmt.Sprintf(format, args...)
	output := fmt.Sprintf("[%s] [%s] %s", timestamp, levelName, message)

	// Write to file
	l.logToFile(output)

	// Also write to console (stderr) for real-time feedback
	fmt.Fprintf(os.Stderr, "%s\n", output)
}

func (l *Logger) Debug(format string, args ...interface{}) {
	l.log(DEBUG, format, args...)
}

func (l *Logger) Info(format string, args ...interface{}) {
	l.log(INFO, format, args...)
}

func (l *Logger) Warn(format string, args ...interface{}) {
	l.log(WARN, format, args...)
}

func (l *Logger) Error(format string, args ...interface{}) {
	l.log(ERROR, format, args...)
}

// Section marks the start of a new section in logs
func (l *Logger) Section(name string) {
	l.mu.Lock()
	defer l.mu.Unlock()

	l.logToFile("")
	l.logToFile("─────────────────────────────────────────────────────────────")
	l.logToFile(fmt.Sprintf("▶ %s", name))
	l.logToFile("─────────────────────────────────────────────────────────────")
}

// APIRequest logs an API request
func (l *Logger) APIRequest(method, endpoint string, payload interface{}) {
	l.Info("🌐 API Request: %s %s", method, endpoint)
	l.Debug("  Payload: %v", payload)
}

// APIResponse logs an API response
func (l *Logger) APIResponse(statusCode int, data interface{}) {
	l.Info("📨 API Response: Status %d", statusCode)
	l.Debug("  Response: %v", data)
}

// APIError logs an API error
func (l *Logger) APIError(endpoint string, err error) {
	l.Error("❌ API Error at %s: %v", endpoint, err)
}

// Close closes the logger
func (l *Logger) Close() {
	l.mu.Lock()
	defer l.mu.Unlock()

	if l.file != nil {
		l.logToFile("")
		l.logToFile("═══════════════════════════════════════════════════════════")
		l.logToFile("Session Ended")
		l.logToFile(fmt.Sprintf("Timestamp: %s", time.Now().Format("2006-01-02 15:04:05")))
		l.logToFile("═══════════════════════════════════════════════════════════")
		l.file.Close()
	}
}

// GetLogFile returns the path to the current log file
func (l *Logger) GetLogFile() string {
	return filepath.Join(l.logDir, fmt.Sprintf("agentmonster_%s.log", l.sessionID))
}

// GetLogDir returns the log directory
func (l *Logger) GetLogDir() string {
	return l.logDir
}
