#!/bin/bash
# Add these aliases to your ~/.bashrc or ~/.zshrc

echo "🔧 Adding AI Empire aliases..."

cat >> ~/.bashrc << 'ALIASES'

# 🏰 AI Empire Docker Aliases
alias empire-resurrect="./empire_manager.sh resurrect"
alias empire-start="./empire_manager.sh start"
alias empire-stop="./empire_manager.sh stop"
alias empire-status="./empire_manager.sh status"
alias empire-logs="./empire_manager.sh logs"
alias empire-shell="./empire_manager.sh shell"
alias trae-run="./empire_manager.sh trae"
alias engain-cmd="./empire_manager.sh engain"

ALIASES

echo "✅ Aliases added! Restart terminal or run: source ~/.bashrc"
echo ""
echo "🎯 Quick commands:"
echo "  empire-resurrect    # Full empire startup"
echo "  trae-run 'task'     # Execute TRAE task"
echo "  engain-cmd 'cmd'    # Send EngAin command"
echo "  empire-status       # Check all services"
