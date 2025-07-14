#!/bin/bash
# 🧪 ClutterBot Sandbox Editor™
# "Edit safely. Deploy tactically."
# Compatible with Termux, Linux, macOS, WSL

VERSION="1.0.0"
CLUTTERBOT_ASCII="
 ╔══════════════════════════════════════╗
 ║    🧪 ClutterBot Sandbox Editor™    ║
 ║      Edit safely. Deploy tactically.  ║
 ╚══════════════════════════════════════╝
"

# Configuration
WARROOM_DIR="${HOME}/warroom"
SANDBOX_DIR="${WARROOM_DIR}/.sandbox"
BACKUP_DIR="${WARROOM_DIR}/.backups"
LOG_FILE="${WARROOM_DIR}/.clutterbot.log"

# Colors and emojis
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Initialize directories
init_clutterbot() {
    mkdir -p "$SANDBOX_DIR" "$BACKUP_DIR"
    touch "$LOG_FILE"
}

# Logging function
log_event() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# Display help
show_help() {
    echo -e "$CLUTTERBOT_ASCII"
    echo -e "${CYAN}Usage:${NC}"
    echo -e "  clutterbot <file>              Edit file in sandbox mode"
    echo -e "  clutterbot --validate <file>   Validate script syntax only"
    echo -e "  clutterbot --history           Show edit history"
    echo -e "  clutterbot --cleanup           Clean old sandbox files"
    echo -e "  clutterbot --version           Show version info"
    echo ""
    echo -e "${CYAN}Features:${NC}"
    echo -e "  🔒 Safe editing in isolated sandbox"
    echo -e "  📦 Automatic backups before deployment"
    echo -e "  🧠 Script validation pre-deployment"
    echo -e "  📜 Git integration (optional)"
    echo -e "  🛡️ Permission detection and fallbacks"
    echo ""
}

# Detect best available editor
detect_editor() {
    if command -v micro >/dev/null 2>&1; then
        echo "micro"
    elif command -v nano >/dev/null 2>&1; then
        echo "nano"
    elif command -v vim >/dev/null 2>&1; then
        echo "vim"
    elif command -v vi >/dev/null 2>&1; then
        echo "vi"
    else
        echo "cat" # Fallback for view-only
    fi
}

# Check if file is writable
check_permissions() {
    local target="$1"
    local target_dir=$(dirname "$target")
    
    if [ ! -w "$target_dir" ] || [ ! -w "$target" ]; then
        echo -e "${YELLOW}⚠️  Detected: read-only mount or restricted path${NC}"
        echo -e "${BLUE}💡 Suggestion: File will be backed up to warroom for safe deployment${NC}"
        return 1
    fi
    return 0
}

# Validate script syntax
validate_script() {
    local file="$1"
    local filename=$(basename "$file")
    
    case "${filename##*.}" in
        sh|bash)
            if bash -n "$file" 2>/dev/null; then
                echo -e "${GREEN}✅ Bash syntax valid${NC}"
                return 0
            else
                echo -e "${RED}❌ Bash syntax errors detected:${NC}"
                bash -n "$file"
                return 1
            fi
            ;;
        py|python)
            if command -v python3 >/dev/null 2>&1; then
                if python3 -m py_compile "$file" 2>/dev/null; then
                    echo -e "${GREEN}✅ Python syntax valid${NC}"
                    return 0
                else
                    echo -e "${RED}❌ Python syntax errors detected${NC}"
                    return 1
                fi
            fi
            ;;
        *)
            echo -e "${BLUE}ℹ️  No syntax validation available for this file type${NC}"
            return 0
            ;;
    esac
}

# Create timestamped backup
create_backup() {
    local target="$1"
    local backup_name="$(basename "$target").$(date +%Y%m%d_%H%M%S).bak"
    local backup_path="$BACKUP_DIR/$backup_name"
    
    cp "$target" "$backup_path"
    echo -e "${GREEN}📦 Backup created: $backup_path${NC}"
    log_event "BACKUP: $target -> $backup_path"
}

# Git integration
git_prompt() {
    local target="$1"
    local target_dir=$(dirname "$target")
    
    if [ -d "$target_dir/.git" ]; then
        echo -e "${PURPLE}🔍 Git repository detected${NC}"
        read -p "Would you like to commit this update? (y/N): " git_confirm
        if [[ "$git_confirm" =~ ^[Yy]$ ]]; then
            cd "$target_dir"
            read -p "Enter commit message: " commit_msg
            git add "$(basename "$target")"
            git commit -m "${commit_msg:-ClutterBot sandbox edit: $(basename "$target")}"
            echo -e "${GREEN}📜 Changes committed to git${NC}"
            log_event "GIT: Committed changes to $(basename "$target")"
        fi
    fi
}

# Main editing function
edit_file() {
    local target="$1"
    local sandbox_file="$SANDBOX_DIR/.tmp_edit_$(basename "$target")"
    local editor=$(detect_editor)
    
    # Validation
    if [ ! -f "$target" ]; then
        echo -e "${RED}❌ File not found: $target${NC}"
        exit 1
    fi
    
    # Check permissions
    local can_write=true
    if ! check_permissions "$target"; then
        can_write=false
    fi
    
    # Copy to sandbox
    cp "$target" "$sandbox_file"
    echo -e "${CYAN}🧪 Editing sandbox: $sandbox_file${NC}"
    echo -e "${BLUE}📝 Using editor: $editor${NC}"
    sleep 1
    
    # Edit the file
    "$editor" "$sandbox_file"
    
    # Pre-deployment validation
    echo -e "\n${PURPLE}🔍 Running pre-deployment checks...${NC}"
    if ! validate_script "$sandbox_file"; then
        read -p "Deploy anyway despite validation errors? (y/N): " force_deploy
        if [[ ! "$force_deploy" =~ ^[Yy]$ ]]; then
            rm "$sandbox_file"
            echo -e "${YELLOW}🧼 Sandbox discarded due to validation errors${NC}"
            log_event "ABORT: Validation failed for $(basename "$target")"
            exit 1
        fi
    fi
    
    # Deployment confirmation
    echo -e "\n${YELLOW}🚀 Ready for deployment${NC}"
    if [ "$can_write" = true ]; then
        read -p "Deploy changes to original file? (y/N): " confirm
    else
        echo -e "${BLUE}💡 Original file is read-only. Deploy to warroom instead? (y/N):${NC}"
        read confirm
    fi
    
    if [[ "$confirm" =~ ^[Yy]$ ]]; then
        if [ "$can_write" = true ]; then
            # Standard deployment
            create_backup "$target"
            mv "$sandbox_file" "$target"
            echo -e "${GREEN}✅ Successfully deployed to $target${NC}"
            log_event "DEPLOY: Changes deployed to $target"
            
            # Git integration
            git_prompt "$target"
            
            # Set executable if original was executable
            if [ -x "$BACKUP_DIR/$(basename "$target")."* ]; then
                chmod +x "$target"
            fi
        else
            # Fallback deployment to warroom
            local warroom_target="$WARROOM_DIR/$(basename "$target")"
            mv "$sandbox_file" "$warroom_target"
            chmod +x "$warroom_target" 2>/dev/null
            echo -e "${GREEN}✅ Deployed to warroom: $warroom_target${NC}"
            echo -e "${BLUE}💡 You can now manually copy this to the target location${NC}"
            log_event "FALLBACK: Deployed to warroom $warroom_target"
        fi
    else
        rm "$sandbox_file"
        echo -e "${YELLOW}🧼 Sandbox discarded. No changes made.${NC}"
        log_event "DISCARD: User discarded changes for $(basename "$target")"
    fi
}

# Show edit history
show_history() {
    echo -e "${CYAN}📚 ClutterBot Edit History:${NC}"
    if [ -f "$LOG_FILE" ]; then
        tail -20 "$LOG_FILE" | while read line; do
            if [[ "$line" == *"DEPLOY"* ]]; then
                echo -e "${GREEN}$line${NC}"
            elif [[ "$line" == *"ABORT"* ]] || [[ "$line" == *"ERROR"* ]]; then
                echo -e "${RED}$line${NC}"
            elif [[ "$line" == *"BACKUP"* ]]; then
                echo -e "${YELLOW}$line${NC}"
            else
                echo -e "${BLUE}$line${NC}"
            fi
        done
    else
        echo -e "${YELLOW}No history found${NC}"
    fi
}

# Cleanup old files
cleanup() {
    echo -e "${CYAN}🧹 Cleaning up old sandbox files...${NC}"
    find "$SANDBOX_DIR" -name ".tmp_edit_*" -mtime +7 -delete 2>/dev/null
    find "$BACKUP_DIR" -name "*.bak" -mtime +30 -delete 2>/dev/null
    echo -e "${GREEN}✅ Cleanup complete${NC}"
    log_event "CLEANUP: Removed old sandbox and backup files"
}

# Main script logic
main() {
    init_clutterbot
    
    case "$1" in
        --help|-h)
            show_help
            ;;
        --version|-v)
            echo -e "${CYAN}ClutterBot Sandbox Editor™ v$VERSION${NC}"
            ;;
        --history)
            show_history
            ;;
        --cleanup)
            cleanup
            ;;
        --validate)
            if [ -z "$2" ]; then
                echo -e "${RED}❌ Please specify a file to validate${NC}"
                exit 1
            fi
            validate_script "$2"
            ;;
        "")
            show_help
            ;;
        *)
            if [ -f "$1" ]; then
                edit_file "$1"
            else
                echo -e "${RED}❌ File not found: $1${NC}"
                echo -e "${BLUE}💡 Use 'clutterbot --help' for usage information${NC}"
                exit 1
            fi
            ;;
    esac
}

# Run the main function with all arguments
main "$@"