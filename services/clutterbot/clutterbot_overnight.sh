#!/bin/bash
# 🌙 ClutterBot Overnight - Simplified Version

WATCH_DIR="$HOME/Downloads"
WARROOM_DIR="$HOME/warroom"
LOG_FILE="$WARROOM_DIR/.overnight.log"

case "$1" in
    "start")
        echo "🌙 ClutterBot Overnight started (test mode)"
        echo "📁 Watching: $WATCH_DIR"
        echo "$(date): Overnight daemon started" >> "$LOG_FILE"
        
        # Simple background monitor
        while true; do
            find "$WATCH_DIR" -name "*.txt" -size +1k -mmin -2 2>/dev/null | while read file; do
                echo "$(date): Found large file: $file" >> "$LOG_FILE"
                echo "🔍 Processing: $(basename "$file")"
            done
            sleep 30
        done
        ;;
    "summary")
        echo "🌅 Overnight Summary:"
        if [ -f "$LOG_FILE" ]; then
            tail -5 "$LOG_FILE"
        else
            echo "No activity logged yet"
        fi
        ;;
    "status")
        if pgrep -f "clutterbot.*overnight" >/dev/null; then
            echo "✅ Overnight daemon is running"
        else
            echo "❌ Overnight daemon is not running"
        fi
        ;;
    *)
        echo "🌙 ClutterBot Overnight Commands:"
        echo "  clutterbot overnight start   - Start monitoring"
        echo "  clutterbot overnight summary - Show activity"
        echo "  clutterbot overnight status  - Check if running"
        ;;
esac
