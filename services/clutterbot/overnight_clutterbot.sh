#!/bin/bash
# 🌙 ClutterBot Overnight Daemon
# "Sleep mode productivity - wake up to organized perfection"

CLUTTERBOT_DIR="$HOME/.clutterbot"
WATCH_DIR="$HOME/Downloads"
LOG_FILE="$CLUTTERBOT_DIR/overnight.log"
CONFIG_FILE="$CLUTTERBOT_DIR/overnight.config"

# Default configuration
DEFAULT_EXTERNAL_TARGETS=(
    "/media/usb0"
    "/mnt/external"
    "/Volumes/BACKUP"
    "/media/$USER"
)

# File type organization rules
declare -A FILE_RULES=(
    ["iso|img|dmg"]="OS_Images"
    ["mp4|mkv|avi|mov"]="Videos" 
    ["zip|tar|gz|7z|rar"]="Archives"
    ["pdf|doc|docx"]="Documents"
    ["jpg|png|raw|tiff"]="Photos"
    ["py|js|sh|rs|go"]="Code"
    ["dataset|csv|json"]="Data"
)

# Initialize
init_overnight_mode() {
    mkdir -p "$CLUTTERBOT_DIR"
    
    # Create default config if none exists
    if [ ! -f "$CONFIG_FILE" ]; then
        cat > "$CONFIG_FILE" << EOF
# ClutterBot Overnight Configuration
WATCH_ENABLED=true
AUTO_BACKUP=true
MIN_FILE_SIZE_MB=50
ORGANIZE_BY_TYPE=true
SLEEP_MODE_HOURS="22:00-08:00"
NOTIFICATION_ENABLED=true
EOF
    fi
    
    source "$CONFIG_FILE"
}

# Logging with timestamps
log_overnight() {
    local level="$1"
    local message="$2"
    local timestamp=$(date "+%Y-%m-%d %H:%M:%S")
    echo "[$timestamp] [$level] $message" >> "$LOG_FILE"
    
    # Also display if not in sleep hours
    if ! is_sleep_time; then
        echo "🌙 ClutterBot: $message"
    fi
}

# Check if we're in designated sleep hours
is_sleep_time() {
    local current_hour=$(date +%H)
    local sleep_start=$(echo "$SLEEP_MODE_HOURS" | cut -d'-' -f1 | cut -d':' -f1)
    local sleep_end=$(echo "$SLEEP_MODE_HOURS" | cut -d'-' -f2 | cut -d':' -f1)
    
    if [ "$current_hour" -ge "$sleep_start" ] || [ "$current_hour" -lt "$sleep_end" ]; then
        return 0
    else
        return 1
    fi
}

# Detect available external storage
detect_external_storage() {
    local external_drives=()
    
    for target in "${DEFAULT_EXTERNAL_TARGETS[@]}"; do
        if [ -d "$target" ] && [ -w "$target" ]; then
            local free_space=$(df "$target" | awk 'NR==2 {print $4}')
            if [ "$free_space" -gt 1000000 ]; then  # At least 1GB free
                external_drives+=("$target")
            fi
        fi
    done
    
    # Also check for auto-mounted drives
    if command -v lsblk >/dev/null 2>&1; then
        while read -r mountpoint; do
            if [ -w "$mountpoint" ] && [[ "$mountpoint" == /media/* ]] || [[ "$mountpoint" == /mnt/* ]]; then
                external_drives+=("$mountpoint")
            fi
        done < <(lsblk -no MOUNTPOINT | grep -E "^/media|^/mnt" | head -5)
    fi
    
    printf '%s\n' "${external_drives[@]}" | sort -u
}

# Get file category based on extension
get_file_category() {
    local filename="$1"
    local extension="${filename##*.}"
    extension=$(echo "$extension" | tr '[:upper:]' '[:lower:]')
    
    for pattern in "${!FILE_RULES[@]}"; do
        if [[ "$extension" =~ $pattern ]]; then
            echo "${FILE_RULES[$pattern]}"
            return
        fi
    done
    
    echo "Misc"
}

# Check if file is large enough to process
is_large_file() {
    local filepath="$1"
    local size_mb=$(du -m "$filepath" 2>/dev/null | cut -f1)
    
    [ "$size_mb" -ge "$MIN_FILE_SIZE_MB" ]
}

# Organize file to external storage
organize_to_external() {
    local source_file="$1"
    local external_drives=($(detect_external_storage))
    
    if [ ${#external_drives[@]} -eq 0 ]; then
        log_overnight "WARN" "No external storage detected for $source_file"
        return 1
    fi
    
    # Use first available external drive
    local target_base="${external_drives[0]}"
    local category=$(get_file_category "$(basename "$source_file")")
    local target_dir="$target_base/ClutterBot_Archive/$category"
    
    # Create category directory
    mkdir -p "$target_dir"
    
    # Generate unique filename if conflict
    local target_file="$target_dir/$(basename "$source_file")"
    local counter=1
    while [ -f "$target_file" ]; do
        local name_part="${source_file%.*}"
        local ext_part="${source_file##*.}"
        target_file="$target_dir/$(basename "$name_part")_$counter.$ext_part"
        ((counter++))
    done
    
    # Copy file to external storage
    log_overnight "INFO" "Moving $(basename "$source_file") → $target_file"
    
    if cp "$source_file" "$target_file"; then
        # Verify copy succeeded
        if cmp -s "$source_file" "$target_file"; then
            rm "$source_file"
            log_overnight "SUCCESS" "Archived: $(basename "$source_file") → $category/"
            return 0
        else
            rm "$target_file"
            log_overnight "ERROR" "Copy verification failed for $(basename "$source_file")"
            return 1
        fi
    else
        log_overnight "ERROR" "Failed to copy $(basename "$source_file")"
        return 1
    fi
}

# Process completed downloads
process_download_queue() {
    local processed_count=0
    local total_size=0
    
    # Find recently completed files (modified in last 10 minutes)
    while IFS= read -r -d '' file; do
        if [ -f "$file" ] && is_large_file "$file"; then
            local file_size=$(du -m "$file" | cut -f1)
            
            if organize_to_external "$file"; then
                ((processed_count++))
                ((total_size += file_size))
            fi
        fi
    done < <(find "$WATCH_DIR" -type f -mmin -10 -print0 2>/dev/null)
    
    if [ "$processed_count" -gt 0 ]; then
        log_overnight "SUMMARY" "Processed $processed_count files (${total_size}MB total)"
        
        # Send notification if enabled and not in sleep mode
        if [ "$NOTIFICATION_ENABLED" = "true" ] && ! is_sleep_time; then
            notify_user "ClutterBot processed $processed_count downloads (${total_size}MB)"
        fi
    fi
}

# Send notification (cross-platform)
notify_user() {
    local message="$1"
    
    if command -v notify-send >/dev/null 2>&1; then
        notify-send "🌙 ClutterBot" "$message"
    elif command -v osascript >/dev/null 2>&1; then
        osascript -e "display notification \"$message\" with title \"🌙 ClutterBot\""
    elif command -v termux-notification >/dev/null 2>&1; then
        termux-notification --title "🌙 ClutterBot" --content "$message"
    fi
}

# Main daemon loop
run_overnight_daemon() {
    log_overnight "START" "ClutterBot Overnight Daemon started"
    
    while true; do
        if [ "$WATCH_ENABLED" = "true" ]; then
            process_download_queue
        fi
        
        # Sleep for 5 minutes between checks
        sleep 300
    done
}

# Generate morning summary
generate_morning_summary() {
    local today=$(date +%Y-%m-%d)
    local overnight_logs=$(grep "$today" "$LOG_FILE" | grep -E "SUCCESS|SUMMARY")
    
    if [ -n "$overnight_logs" ]; then
        echo "🌅 Good morning! Here's what ClutterBot did overnight:"
        echo "$overnight_logs" | while read line; do
            echo "  ✅ $(echo "$line" | cut -d']' -f3-)"
        done
        
        # Show storage summary
        local external_drives=($(detect_external_storage))
        if [ ${#external_drives[@]} -gt 0 ]; then
            echo ""
            echo "📊 External Storage Status:"
            for drive in "${external_drives[@]}"; do
                local usage=$(df -h "$drive" | awk 'NR==2 {print $3 "/" $2 " (" $5 " used)"}')
                echo "  💾 $(basename "$drive"): $usage"
            done
        fi
    else
        echo "😴 ClutterBot had a quiet night - no large downloads to process"
    fi
}

# Command handling
case "$1" in
    "start"|"daemon")
        init_overnight_mode
        run_overnight_daemon
        ;;
    "summary"|"morning")
        generate_morning_summary
        ;;
    "status")
        if pgrep -f "clutterbot.*daemon" >/dev/null; then
            echo "✅ ClutterBot daemon is running"
            echo "📁 Watching: $WATCH_DIR"
            detect_external_storage | while read drive; do
                echo "💾 External storage: $drive"
            done
        else
            echo "❌ ClutterBot daemon is not running"
            echo "💡 Start with: clutterbot overnight daemon"
        fi
        ;;
    "stop")
        pkill -f "clutterbot.*daemon"
        log_overnight "STOP" "ClutterBot Overnight Daemon stopped"
        echo "🛑 ClutterBot daemon stopped"
        ;;
    "config")
        ${EDITOR:-nano} "$CONFIG_FILE"
        ;;
    *)
        echo "🌙 ClutterBot Overnight Mode"
        echo ""
        echo "Usage:"
        echo "  clutterbot overnight start    - Start background daemon"
        echo "  clutterbot overnight summary  - Show morning summary"
        echo "  clutterbot overnight status   - Check daemon status"
        echo "  clutterbot overnight stop     - Stop daemon"
        echo "  clutterbot overnight config   - Edit configuration"
        echo ""
        echo "Features:"
        echo "  🛌 Processes downloads while you sleep"
        echo "  💾 Auto-organizes to external storage"
        echo "  📊 Morning summaries of overnight activity"
        echo "  🔧 Configurable file size and time thresholds"
        ;;
esac