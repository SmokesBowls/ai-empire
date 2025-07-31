#!/bin/bash

# Project Cleanup Script - Organize the remaining clutter
echo "🧹 Cleaning up project clutter..."

# Create organized directory structure
mkdir -p {src/components,src/utils,backend,docs,config,scripts,tests}

echo "📁 Created project directories"

# Move React/TypeScript components
echo "⚛️ Organizing React components..."
mv *.tsx src/components/ 2>/dev/null
mv ZW*.ts src/utils/ 2>/dev/null
mv *Parser*.ts src/utils/ 2>/dev/null
mv *Highlighter*.tsx src/components/ 2>/dev/null
mv *Visualizer*.tsx src/components/ 2>/dev/null

# Move Python backend files
echo "🐍 Organizing Python backend..."
mv *.py backend/ 2>/dev/null
mv zw_transformer_daemon.py backend/ 2>/dev/null
mv zwvoice.py backend/ 2>/dev/null

# Move configuration files
echo "⚙️ Organizing config files..."
mv *.json config/ 2>/dev/null
mv package*.json ./ 2>/dev/null  # Keep package.json in root
mv tsconfig.json ./ 2>/dev/null   # Keep tsconfig in root
mv vite.config.ts ./ 2>/dev/null  # Keep vite config in root

# Move documentation
echo "📚 Organizing documentation..."
mv *.md docs/ 2>/dev/null
mv README.md ./ 2>/dev/null       # Keep README in root
mv *.txt docs/ 2>/dev/null

# Move HTML files (likely templates)
echo "🌐 Organizing HTML templates..."
mv *.html src/ 2>/dev/null
mv index.html ./ 2>/dev/null      # Keep main index.html in root

# Move test and utility scripts
echo "🔧 Organizing scripts and tests..."
mv *test* tests/ 2>/dev/null
mv *script* scripts/ 2>/dev/null
mv voice_cleanup_script.sh scripts/ 2>/dev/null

# Move any remaining random files to a temp folder for review
mkdir -p temp_review
mv *.* temp_review/ 2>/dev/null

echo "✅ Project organized!"
echo ""
echo "📊 New structure:"
echo "src/components/ - React components"
echo "src/utils/ - TypeScript utilities" 
echo "backend/ - Python services"
echo "config/ - Configuration files"
echo "docs/ - Documentation"
echo "scripts/ - Utility scripts"
echo "tests/ - Test files"
echo "voices/ - Voice samples (already done)"
echo "temp_review/ - Files that need manual review"
echo ""
echo "🎯 Check temp_review/ for any files that need manual placement"
