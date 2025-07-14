#!/bin/bash
# 🎩 ClutterBot Virtual Workspace Sandbox
# "Work in perfect organization without moving a single file"

CLUTTERBOT_WORKSPACE="$HOME/.clutterbot_workspace"
VIRTUAL_DESKTOP="$CLUTTERBOT_WORKSPACE/Desktop"
SYMLINK_REGISTRY="$CLUTTERBOT_WORKSPACE/.symlink_registry"
SESSION_LOG="$CLUTTERBOT_WORKSPACE/.current_session"

# Virtual folder structure (symlinks to real files)
VIRTUAL_FOLDERS=(
    "Documents/Active_Projects"
    "Documents/PDFs_ToRead" 
    "Documents/Spreadsheets"
    "Media/Recent_Photos"
    "Media/Videos_ToWatch"
    "Code/Current_Work"
    "Downloads/Fresh_Files"
    "Quick_Access"
    "Today_Focus"
)

# Initialize ClutterBot workspace
init_workspace() {
    echo "🎩 Initializing ClutterBot Virtual Workspace..."
    
    # Create workspace structure
    mkdir -p "$VIRTUAL_DESKTOP"
    for folder in "${VIRTUAL_FOLDERS[@]}"; do
        mkdir -p "$VIRTUAL_DESKTOP/$folder"
    done
    
    # Create registry and session files
    touch "$SYMLINK_REGISTRY" "$SESSION_LOG"
    
    # Create workspace info
    cat > "$VIRTUAL_DESKTOP/README_ClutterBot.md" << 'EOF'
# 🎩 ClutterBot Virtual Workspace

## What You See Here:
- **Organized folders** - Clean, logical structure
- **Symbolic links** - Files appear here but live elsewhere
- **Work environment** - Edit, view, organize as normal
- **Non-destructive** - Original files never move

## Commands:
- `clutterbot enter` - Enter this workspace
- `clutterbot add <file>` - Add file to workspace
- `clutterbot focus <folder>` - Focus on specific folder
- `clutterbot done` - Finish session & organize
- `clutterbot exit` - Leave without organizing

## The Magic:
Your files stay exactly where they are. This workspace 
just gives you a perfectly organized view to work in!
EOF
    
    echo "✅ Virtual workspace ready: $VIRTUAL_DESKTOP"
}

# Enter the ClutterBot workspace (like opening a desktop)
enter_workspace() {
    echo "🎩 Opening ClutterBot Virtual Desktop..."
    
    if [ ! -d "$VIRTUAL_DESKTOP" ]; then
        init_workspace
    fi
    
    # Start session log
    echo "Session started: $(date)" > "$SESSION_LOG"
    
    # Auto-populate with recent files
    populate_recent_files
    
    # Open workspace in file manager
    if command -v xdg-open >/dev/null 2>&1; then
        xdg-open "$VIRTUAL_DESKTOP" &
    elif command -v open >/dev/null 2>&1; then
        open "$VIRTUAL_DESKTOP" &
    fi
    
    echo "🖥️  Virtual Desktop opened!"
    echo "📁 Location: $VIRTUAL_DESKTOP"
    echo ""
    echo "🎯 Working inside ClutterBot workspace:"
    echo "   • Files appear organized but stay in original locations"
    echo "   • Edit/view normally - changes apply to real files"
    echo "   • Run 'clutterbot done' when finished working"
    echo ""
    
    # Show workspace status
    show_workspace_status
}

# Add file to workspace (creates symlink in appropriate folder)
add_to_workspace() {
    local source_file="$1"
    
    if [ ! -f "$source_file" ]; then
        echo "❌ File not found: $source_file"
        return 1
    fi
    
    # Get absolute path
    source_file=$(realpath "$source_file")
    local filename=$(basename "$source_file")
    
    # Determine best virtual folder
    local virtual_folder=$(determine_virtual_folder "$filename")
    local target_dir="$VIRTUAL_DESKTOP/$virtual_folder"
    local symlink_path="$target_dir/$filename"
    
    # Handle name conflicts
    local counter=1
    while [ -e "$symlink_path" ]; do
        local name_part="${filename%.*}"
        local ext_part="${filename##*.}"
        if [ "$name_part" = "$ext_part" ]; then
            symlink_path="$target_dir/${filename}_$counter"
        else
            symlink_path="$target_dir/${name_part}_$counter.$ext_part"
        fi
        ((counter++))
    done
    
    # Create symlink
    ln -s "$source_file" "$symlink_path"
    
    # Register symlink
    echo "$symlink_path|$source_file|$(date +%s)" >> "$SYMLINK_REGISTRY"
    
    echo "🔗 Added to workspace: $virtual_folder/$(basename "$symlink_path")"
    echo "   → Links to: $source_file"
}

# Determine best virtual folder for file
determine_virtual_folder() {
    local filename="$1"
    local extension="${filename##*.}"
    extension=$(echo "$extension" | tr '[:upper:]' '[:lower:]')
    
    # Check file age for recent categorization
    local file_age_days=$(find "$(dirname "$1")" -name "$filename" -mtime -7 2>/dev/null | wc -l)
    
    case "$extension" in
        pdf)
            if [ "$file_age_days" -gt 0 ]; then
                echo "Documents/PDFs_ToRead"
            else
                echo "Documents/Active_Projects"
            fi
            ;;
        doc|docx|odt)
            echo "Documents/Active_Projects"
            ;;
        xls|xlsx|csv)
            echo "Documents/Spreadsheets"
            ;;
        jpg|png|jpeg|gif)
            echo "Media/Recent_Photos"
            ;;
        mp4|mkv|avi|mov)
            echo "Media/Videos_ToWatch"
            ;;
        py|js|sh|html|css)
            echo "Code/Current_Work"
            ;;
        zip|tar|gz|deb|rpm)
            echo "Downloads/Fresh_Files"
            ;;
        *)
            echo "Quick_Access"
            ;;
    esac
}

# Auto-populate workspace with recent files
populate_recent_files() {
    echo "🔄 Auto-populating workspace with recent files..."
    
    # Find recent files from common locations
    local search_dirs=("$HOME/Downloads" "$HOME/Documents" "$HOME/Desktop")
    
    for search_dir in "${search_dirs[@]}"; do
        if [ -d "$search_dir" ]; then
            # Find files modified in last 3 days
            find "$search_dir" -type f -mtime -3 2>/dev/null | head -20 | while read file; do
                # Skip already linked files
                if ! grep -q "$file" "$SYMLINK_REGISTRY" 2>/dev/null; then
                    add_to_workspace "$file" >/dev/null
                fi
            done
        fi
    done
    
    echo "✅ Workspace populated with recent files"
}

# Show workspace status
show_workspace_status() {
    echo "📊 ClutterBot Workspace Status:"
    echo ""
    
    for folder in "${VIRTUAL_FOLDERS[@]}"; do
        local folder_path="$VIRTUAL_DESKTOP/$folder"
        if [ -d "$folder_path" ]; then
            local file_count=$(find "$folder_path" -type l 2>/dev/null | wc -l)
            if [ "$file_count" -gt 0 ]; then
                echo "   📂 $folder: $file_count files"
            fi
        fi
    done
    
    echo ""
    local total_links=$(wc -l < "$SYMLINK_REGISTRY" 2>/dev/null || echo "0")
    echo "🔗 Total files in workspace: $total_links"
}

# Focus on specific folder (open just that folder)
focus_folder() {
    local folder_name="$1"
    local folder_path="$VIRTUAL_DESKTOP/$folder_name"
    
    if [ ! -d "$folder_path" ]; then
        echo "❌ Folder not found: $folder_name"
        echo "Available folders:"
        for folder in "${VIRTUAL_FOLDERS[@]}"; do
            echo "   📂 $folder"
        done
        return 1
    fi
    
    echo "🎯 Focusing on: $folder_name"
    
    if command -v xdg-open >/dev/null 2>&1; then
        xdg-open "$folder_path"
    elif command -v open >/dev/null 2>&1; then
        open "$folder_path"
    else
        echo "📁 Folder: $folder_path"
    fi
}

# Finish session and offer to organize real files
finish_session() {
    echo "🎩 Finishing ClutterBot workspace session..."
    echo ""
    
    # Show session summary
    if [ -f "$SESSION_LOG" ]; then
        echo "📊 Session Summary:"
        echo "   Started: $(head -1 "$SESSION_LOG")"
        echo "   Duration: $(date)"
        echo ""
    fi
    
    # Count files worked with
    local files_in_workspace=$(wc -l < "$SYMLINK_REGISTRY" 2>/dev/null || echo "0")
    echo "🔗 Files in workspace: $files_in_workspace"
    echo ""
    
    # Offer to organize real files
    echo "🎯 Would you like ClutterBot to organize the real files now?"
    echo "   1) Yes - Move real files to organized locations"
    echo "   2) No - Leave files where they are" 
    echo "   3) Show me what would be organized first"
    
    read -p "Choose (1/2/3): " choice
    
    case "$choice" in
        1)
            organize_real_files
            ;;
        2)
            echo "✅ Files left in original locations"
            echo "🎩 Workspace preserved for next session"
            ;;
        3)
            show_organization_preview
            echo ""
            read -p "Proceed with organization? (y/N): " confirm
            if [[ "$confirm" =~ ^[Yy]$ ]]; then
                organize_real_files
            else
                echo "✅ Files left in original locations"
            fi
            ;;
    esac
}

# Organize real files based on workspace organization
organize_real_files() {
    echo "🎩✨ Organizing real files based on workspace..."
    
    # Create organized directory structure in home
    local org_base="$HOME/Organized_by_ClutterBot"
    mkdir -p "$org_base"
    
    for folder in "${VIRTUAL_FOLDERS[@]}"; do
        mkdir -p "$org_base/$folder"
    done
    
    # Move real files
    local moved_count=0
    while IFS='|' read -r symlink_path source_file timestamp; do
        if [ -f "$source_file" ] && [ -L "$symlink_path" ]; then
            local virtual_folder=$(dirname "$symlink_path" | sed "s|$VIRTUAL_DESKTOP/||")
            local dest_dir="$org_base/$virtual_folder"
            local filename=$(basename "$source_file")
            
            # Move real file
            mv "$source_file" "$dest_dir/"
            echo "📄 $(basename "$source_file") → $virtual_folder"
            
            # Update symlink to point to new location
            rm "$symlink_path"
            ln -s "$dest_dir/$filename" "$symlink_path"
            
            ((moved_count++))
        fi
    done < "$SYMLINK_REGISTRY"
    
    echo ""
    echo "✅ Organized $moved_count real files!"
    echo "📁 New location: $org_base"
    echo "🔗 Workspace symlinks updated"
}

# Show what would be organized
show_organization_preview() {
    echo "🔍 Organization Preview:"
    echo ""
    
    while IFS='|' read -r symlink_path source_file timestamp; do
        if [ -f "$source_file" ]; then
            local virtual_folder=$(dirname "$symlink_path" | sed "s|$VIRTUAL_DESKTOP/||")
            echo "   📄 $(basename "$source_file") → $virtual_folder/"
        fi
    done < "$SYMLINK_REGISTRY"
}

# Exit workspace (leave files where they are)
exit_workspace() {
    echo "🎩 Exiting ClutterBot workspace..."
    echo "📁 Files remain in original locations"
    echo "🔗 Workspace preserved for next session"
    echo ""
    echo "💡 Next time: 'clutterbot enter' to resume"
}

# Clean up broken symlinks
cleanup_workspace() {
    echo "🧹 Cleaning up workspace..."
    
    # Remove broken symlinks
    find "$VIRTUAL_DESKTOP" -type l -exec test ! -e {} \; -delete 2>/dev/null
    
    # Clean registry of broken entries
    if [ -f "$SYMLINK_REGISTRY" ]; then
        while IFS='|' read -r symlink_path source_file timestamp; do
            if [ ! -f "$source_file" ] || [ ! -L "$symlink_path" ]; then
                # Remove from registry
                grep -v "$symlink_path" "$SYMLINK_REGISTRY" > "${SYMLINK_REGISTRY}.tmp"
                mv "${SYMLINK_REGISTRY}.tmp" "$SYMLINK_REGISTRY"
            fi
        done < "$SYMLINK_REGISTRY"
    fi
    
    echo "✅ Workspace cleaned"
}

# Main command handler
case "$1" in
    "init")
        init_workspace
        ;;
    "enter"|"open")
        enter_workspace
        ;;
    "add")
        if [ -n "$2" ]; then
            add_to_workspace "$2"
        else
            echo "Usage: clutterbot add <filename>"
        fi
        ;;
    "focus")
        if [ -n "$2" ]; then
            focus_folder "$2"
        else
            echo "Available folders:"
            for folder in "${VIRTUAL_FOLDERS[@]}"; do
                echo "   📂 $folder"
            done
        fi
        ;;
    "status")
        show_workspace_status
        ;;
    "done"|"finish")
        finish_session
        ;;
    "exit"|"leave")
        exit_workspace
        ;;
    "cleanup")
        cleanup_workspace
        ;;
    *)
        echo "🎩 ClutterBot Virtual Workspace Sandbox"
        echo ""
        echo "Commands:"
        echo "  clutterbot enter         - Open virtual desktop workspace"
        echo "  clutterbot add <file>    - Add file to workspace"
        echo "  clutterbot focus <folder> - Focus on specific folder"
        echo "  clutterbot status        - Show workspace status"
        echo "  clutterbot done          - Finish & offer to organize real files"
        echo "  clutterbot exit          - Leave files where they are"
        echo "  clutterbot cleanup       - Clean broken symlinks"
        echo ""
        echo "💡 Concept:"
        echo "   • Work inside organized virtual desktop"
        echo "   • Files never move until you say so"
        echo "   • Perfect organization without the risk"
        echo "   • Always accessible outside the workspace too"
        ;;
esac