#!/bin/bash

# REVERSE Project Cleanup Script - Put everything back!
echo "🔄 REVERSING cleanup - putting files back..."

# Move React/TypeScript components back to root
echo "⚛️ Moving React components back to root..."
mv src/components/*.tsx ./ 2>/dev/null
mv src/utils/ZW*.ts ./ 2>/dev/null
mv src/utils/*Parser*.ts ./ 2>/dev/null

# Move Python backend files back to root
echo "🐍 Moving Python files back to root..."
mv backend/*.py ./ 2>/dev/null

# Move configuration files back to root
echo "⚙️ Moving config files back to root..."
mv config/*.json ./ 2>/dev/null

# Move documentation back to root
echo "📚 Moving docs back to root..."
mv docs/*.md ./ 2>/dev/null
mv docs/*.txt ./ 2>/dev/null

# Move HTML files back to root
echo "🌐 Moving HTML back to root..."
mv src/*.html ./ 2>/dev/null

# Move test and utility scripts back to root
echo "🔧 Moving scripts back to root..."
mv tests/* ./ 2>/dev/null
mv scripts/* ./ 2>/dev/null

# Move anything from temp_review back to root
echo "🗂️ Moving temp_review files back to root..."
mv temp_review/* ./ 2>/dev/null

# Clean up empty directories
echo "🧹 Removing empty directories..."
rmdir src/components src/utils src backend config docs scripts tests temp_review 2>/dev/null
rmdir src 2>/dev/null

echo "✅ REVERSE COMPLETE!"
echo ""
echo "🎯 All files moved back to root directory"
echo "🔧 Your imports should work again!"
echo ""
echo "📊 Files in root now:"
ls -la *.tsx *.ts *.py *.json *.html 2>/dev/null | wc -l | xargs echo "Working files:"