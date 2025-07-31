#!/bin/bash
# 🤖 ClutterBot Digital Butler & Universal Sandbox System
# "Your complete digital ecosystem manager"

CLUTTERBOT_HOME="$HOME/.clutterbot"
SANDBOX_ROOT="$CLUTTERBOT_HOME/sandboxes"
ORIGINAL_VAULT="$CLUTTERBOT_HOME/originals"
MESSAGE_QUEUE="$CLUTTERBOT_HOME/messages"
MOOD_PROFILES="$CLUTTERBOT_HOME/moods"
INDEX_DB="$CLUTTERBOT_HOME/index.db"

# Mood and ambiance settings
declare -A MOOD_SETTINGS=(
    ["focus"]="🎵 Lo-fi beats, 🔅 dim terminal colors"
    ["creative"]="🎨 Ambient synth, 🌈 vibrant theme"
    ["evening"]="🎷 Jazz playlist, 🌙 dark mode"
    ["morning"]="☀️ Upbeat indie, 🌅 bright theme"
    ["deep-work"]="🧘 Nature sounds, ⚫ minimal UI"
)

# Initialize ClutterBot ecosystem
init_clutterbot_butler() {
    mkdir -p "$SANDBOX_ROOT" "$ORIGINAL_VAULT" "$MESSAGE_QUEUE" "$MOOD_PROFILES"
    
    # Create index database
    if [ ! -f "$INDEX_DB" ]; then
        cat > "$INDEX_DB" << EOF
# ClutterBot Index Database
# Format: timestamp|action|file|location|status
$(date +%s)|INIT|system|clutterbot|ready
EOF
    fi
    
    # Set up default mood profiles
    setup_mood_profiles
}

# Welcome back routine
welcome_back() {
    local away_time_start=$(get_last_activity)
    local current_time=$(date +%s)
    local time_away=$((current_time - away_time_start))
    
    echo "🏠 Welcome back!"
    echo ""
    
    # Check messages
    show_message_summary
    
    # Offer mood setting
    suggest_mood_setting
    
    # Show sandbox status
    show_sandbox_status
    
    # Update activity log
    log_activity "RETURN" "user" "welcomed back after ${time_away}s away"
}

# Message management system
show_message_summary() {
    local message_count=$(find "$MESSAGE_QUEUE" -name "*.msg" 2>/dev/null | wc -l)
    
    if [ "$message_count" -gt 0 ]; then
        echo "📬 You had $message_count messages while you were out:"
        
        # Show recent messages
        find "$MESSAGE_QUEUE" -name "*.msg" -mtime -1 | head -5 | while read msg_file; do
            local sender=$(head -1 "$msg_file")
            local content=$(tail -1 "$msg_file")
            echo "   • $sender: \"$content\""
        done
        
        if [ "$message_count" -gt 5 ]; then
            echo "   ... and $((message_count - 5)) more"
        fi
        echo ""
    fi
}

# Mood and ambiance management
suggest_mood_setting() {
    local hour=$(date +%H)
    local suggested_mood
    
    if [ "$hour" -ge 18 ] || [ "$hour" -le 6 ]; then
        suggested_mood="evening"
    elif [ "$hour" -ge 9 ] && [ "$hour" -le 12 ]; then
        suggested_mood="morning"
    else
        suggested_mood="focus"
    fi
    
    echo "🎶 Would you like me to set the mood for $suggested_mood?"
    echo "   ${MOOD_SETTINGS[$suggested_mood]}"
    
    read -p "   Apply this mood? (Y/n): " mood_choice
    if [[ ! "$mood_choice" =~ ^[Nn]$ ]]; then
        apply_mood "$suggested_mood"
    fi
    echo ""
}

# Apply mood settings
apply_mood() {
    local mood="$1"
    
    case "$mood" in
        "focus"|"deep-work")
            start_ambient_audio "focus-beats.mp3"
            set_terminal_theme "minimal"
            ;;
        "creative")
            start_ambient_audio "ambient-synth.mp3" 
            set_terminal_theme "vibrant"
            ;;
        "evening")
            start_ambient_audio "jazz-evening.mp3"
            set_terminal_theme "dark"
            ;;
        "morning")
            start_ambient_audio "indie-morning.mp3"
            set_terminal_theme "bright"
            ;;
    esac
    
    echo "🎵 Applied $mood mood settings"
    log_activity "MOOD" "$mood" "mood applied"
}

# Universal sandbox system
create_sandbox() {
    local project_name="$1"
    local source_path="$2"
    local sandbox_path="$SANDBOX_ROOT/$project_name"
    
    # Create sandbox directory
    mkdir -p "$sandbox_path"
    
    # If source provided, create protected copy
    if [ -n "$source_path" ] && [ -e "$source_path" ]; then
        # Store original in vault (immutable)
        local vault_path="$ORIGINAL_VAULT/$(basename "$source_path").$(date +%s)"
        cp -r "$source_path" "$vault_path"
        
        # Create working copy in sandbox
        cp -r "$source_path" "$sandbox_path/"
        
        echo "🧪 Created sandbox: $project_name"
        echo "   📁 Working copy: $sandbox_path"
        echo "   🔒 Original stored safely in vault"
        
        log_activity "SANDBOX" "$project_name" "created from $source_path"
    else
        echo "🧪 Created empty sandbox: $project_name"
        log_activity "SANDBOX" "$project_name" "created empty"
    fi
}

# Show active sandboxes
show_sandbox_status() {
    echo "📊 Active Sandbox Environments:"
    
    if [ ! -d "$SANDBOX_ROOT" ] || [ -z "$(ls -A "$SANDBOX_ROOT" 2>/dev/null)" ]; then
        echo "   (No active sandboxes)"
        echo ""
        return
    fi
    
    for sandbox in "$SANDBOX_ROOT"/*; do
        if [ -d "$sandbox" ]; then
            local name=$(basename "$sandbox")
            local file_count=$(find "$sandbox" -type f | wc -l)
            local last_modified=$(stat -c %Y "$sandbox" 2>/dev/null || stat -f %m "$sandbox" 2>/dev/null)
            local time_ago=$(($(date +%s) - last_modified))
            
            # Check if tests exist and pass
            local status_indicator="🧪"
            if [ -f "$sandbox/package.json" ] && command -v npm >/dev/null; then
                if (cd "$sandbox" && npm test >/dev/null 2>&1); then
                    status_indicator="✅"
                fi
            elif [ -f "$sandbox"/*.py ] && command -v python3 >/dev/null; then
                if python3 -m py_compile "$sandbox"/*.py 2>/dev/null; then
                    status_indicator="✅"
                fi
            fi
            
            echo "   $status_indicator $name ($file_count files, modified ${time_ago}s ago)"
        fi
    done
    echo ""
}

# Enter sandbox environment
enter_sandbox() {
    local sandbox_name="$1"
    local sandbox_path="$SANDBOX_ROOT/$sandbox_name"
    
    if [ ! -d "$sandbox_path" ]; then
        echo "❌ Sandbox '$sandbox_name' not found"
        list_sandboxes
        return 1
    fi
    
    echo "🧪 Entering sandbox: $sandbox_name"
    echo "💡 Remember: All work here is isolated. Originals are safe."
    echo "🔧 Use 'exit' to leave sandbox, 'clutterbot deploy' to apply changes"
    
    # Change to sandbox and start subshell
    cd "$sandbox_path"
    PS1="🧪 [$sandbox_name] \$ " bash --norc
    
    log_activity "ENTER" "$sandbox_name" "user entered sandbox"
}

# Deploy sandbox changes
deploy_sandbox() {
    local sandbox_name="$1"
    local target_path="$2"
    local sandbox_path="$SANDBOX_ROOT/$sandbox_name"
    
    if [ ! -d "$sandbox_path" ]; then
        echo "❌ Sandbox '$sandbox_name' not found"
        return 1
    fi
    
    echo "🚀 Preparing to deploy sandbox: $sandbox_name"
    
    # Run pre-deployment checks
    echo "🔍 Running pre-deployment validation..."
    if ! validate_sandbox "$sandbox_path"; then
        echo "❌ Validation failed. Deploy anyway? (y/N)"
        read confirm
        if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
            echo "🛑 Deployment cancelled"
            return 1
        fi
    fi
    
    # Create backup of target
    if [ -e "$target_path" ]; then
        local backup_path="$ORIGINAL_VAULT/$(basename "$target_path").backup.$(date +%s)"
        cp -r "$target_path" "$backup_path"
        echo "📦 Created backup: $backup_path"
    fi
    
    # Deploy changes
    echo "🚀 Deploying changes..."
    cp -r "$sandbox_path"/* "$target_path"
    
    echo "✅ Successfully deployed $sandbox_name to $target_path"
    log_activity "DEPLOY" "$sandbox_name" "deployed to $target_path"
}

# Background indexing system
start_background_indexing() {
    echo "🔍 Starting background file indexing..."
    
    # Monitor filesystem changes
    if command -v inotifywait >/dev/null 2>&1; then
        # Linux
        inotifywait -m -r -e create,modify,delete "$HOME" 2>/dev/null | while read path action file; do
            index_file_change "$path" "$action" "$file"
        done &
    elif command -v fswatch >/dev/null 2>&1; then
        # macOS
        fswatch -r "$HOME" | while read file; do
            index_file_change "$(dirname "$file")" "modify" "$(basename "$file")"
        done &
    else
        # Fallback: periodic scan
        while true; do
            scan_and_index
            sleep 300  # 5 minutes
        done &
    fi
    
    echo "✅ Background indexing active"
}

# File indexing
index_file_change() {
    local path="$1"
    local action="$2" 
    local file="$3"
    local timestamp=$(date +%s)
    
    # Skip system files and hidden directories
    if [[ "$file" == .* ]] || [[ "$path" == */.*/* ]]; then
        return
    fi
    
    echo "$timestamp|$action|$file|$path|indexed" >> "$INDEX_DB"
}

# Audio system integration
start_ambient_audio() {
    local audio_file="$1"
    local audio_path="$MOOD_PROFILES/$audio_file"
    
    # Try different audio players
    if command -v mpv >/dev/null 2>&1; then
        mpv --loop --volume=30 "$audio_path" >/dev/null 2>&1 &
    elif command -v mplayer >/dev/null 2>&1; then
        mplayer -loop 0 -volume 30 "$audio_path" >/dev/null 2>&1 &
    elif command -v play >/dev/null 2>&1; then
        play "$audio_path" repeat 999 >/dev/null 2>&1 &
    else
        echo "🔇 Audio player not found - install mpv, mplayer, or sox"
        return
    fi
    
    echo "🎵 Started ambient audio: $audio_file"
}

# Activity logging
log_activity() {
    local action="$1"
    local target="$2" 
    local details="$3"
    local timestamp=$(date +%s)
    
    echo "$timestamp|$action|$target|$details" >> "$INDEX_DB"
}

# Get last activity time
get_last_activity() {
    if [ -f "$INDEX_DB" ]; then
        tail -1 "$INDEX_DB" | cut -d'|' -f1
    else
        date +%s
    fi
}

# Main command handler
case "$1" in
    "welcome"|"back")
        welcome_back
        ;;
    "sandbox")
        case "$2" in
            "create")
                create_sandbox "$3" "$4"
                ;;
            "enter")
                enter_sandbox "$3"
                ;;
            "deploy")
                deploy_sandbox "$3" "$4"
                ;;
            "list")
                show_sandbox_status
                ;;
            *)
                echo "🧪 Sandbox Commands:"
                echo "  clutterbot sandbox create <name> [source]"
                echo "  clutterbot sandbox enter <name>"
                echo "  clutterbot sandbox deploy <name> <target>"
                echo "  clutterbot sandbox list"
                ;;
        esac
        ;;
    "mood")
        if [ -n "$2" ]; then
            apply_mood "$2"
        else
            echo "🎶 Available moods: ${!MOOD_SETTINGS[@]}"
        fi
        ;;
    "index")
        start_background_indexing
        ;;
    "done")
        echo "👋 Thanks for letting me know you're done!"
        echo "🧪 All sandbox work preserved. Originals remain untouched."
        echo "💾 Background indexing will continue while you're away."
        log_activity "DONE" "session" "user finished work session"
        ;;
    *)
        init_clutterbot_butler
        echo "🤖 ClutterBot Digital Butler System"
        echo ""
        echo "Commands:"
        echo "  clutterbot welcome          - Welcome back routine"
        echo "  clutterbot sandbox ...      - Sandbox management"
        echo "  clutterbot mood <setting>   - Set ambient mood"
        echo "  clutterbot index            - Start background indexing"
        echo "  clutterbot done             - End work session"
        echo ""
        echo "🏠 Your complete digital ecosystem manager"
        ;;
esac