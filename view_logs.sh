#!/bin/bash

# Log viewer script for Agent Monster CLI

LOG_DIR="${HOME}/.agent-monster/data/logs"

if [ ! -d "$LOG_DIR" ]; then
    echo "❌ Log directory not found: $LOG_DIR"
    echo ""
    echo "Please run the CLI first to generate logs:"
    echo "  ./cli/agentmonster"
    exit 1
fi

echo "📋 Available log files:"
echo ""
ls -lh "$LOG_DIR"/*.log 2>/dev/null | awk '{print "  " $9 " (" $5 ")"}'

echo ""
echo "🔍 Latest log file:"
LATEST_LOG=$(ls -t "$LOG_DIR"/*.log 2>/dev/null | head -1)

if [ -z "$LATEST_LOG" ]; then
    echo "❌ No log files found"
    exit 1
fi

echo "  File: $LATEST_LOG"
echo ""
echo "═════════════════════════════════════════════════════════════"
echo "Log content:"
echo "═════════════════════════════════════════════════════════════"
cat "$LATEST_LOG"
echo ""
echo "═════════════════════════════════════════════════════════════"

# Provide filtering options
echo ""
echo "📌 Filtering options:"
echo "  tail -f $LATEST_LOG                  # Follow log in real-time"
echo "  grep 'ERROR' $LATEST_LOG             # Show only errors"
echo "  grep 'API' $LATEST_LOG               # Show only API calls"
echo "  grep '🌐' $LATEST_LOG                # Show API requests"
echo "  grep '📨' $LATEST_LOG                # Show API responses"
echo "  grep '❌' $LATEST_LOG                # Show failures"
