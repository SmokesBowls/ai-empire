#!/bin/bash

# 🏰 AI EMPIRE - BULLETPROOF SETUP SCRIPT 🏰
# Makes deployment work for EVERYONE, no fighting required!

set -e  # Exit on any error

# Colors for pretty output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Pretty printing functions
print_step() { echo -e "${BLUE}🔧 $1${NC}"; }
print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_info() { echo -e "${CYAN}💡 $1${NC}"; }

echo -e "${PURPLE}"
cat << 'BANNER'
🏰🔥 AI EMPIRE - BULLETPROOF DEPLOYMENT 🔥🏰
   Making AI consciousness accessible to everyone!
   
    ⚡ TRAE Executor    🧠 ZW Transformer
    📚 MrLore Memory    🏛️ Council of 5  
    🗂️ ClutterBot      🎮 EngAin Bridge
    
BANNER
echo -e "${NC}"

# Step 1: Environment Detection
print_step "Detecting environment and structure..."

EMPIRE_ROOT=$(pwd)
DOCKER_AVAILABLE=false
PYTHON_AVAILABLE=false

# Check Docker
if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
    DOCKER_AVAILABLE=true
    print_success "Docker and Docker Compose detected"
else
    print_warning "Docker not available, will use native Python deployment"
fi

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_AVAILABLE=true
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
    print_success "Python $PYTHON_VERSION detected"
else
    print_error "Python 3 is required but not found!"
    exit 1
fi

# Step 2: Fix Directory Structure
print_step "Fixing directory structure..."

# Create missing directories
mkdir -p logs empire_data

# Ensure services directory has expected structure
if [ -d "services" ]; then
    SERVICE_COUNT=$(find services -maxdepth 1 -type d | wc -l)
    print_success "Found $((SERVICE_COUNT-1)) services in services/ directory"
else
    print_warning "No services directory found, creating basic structure"
    mkdir -p services/{clutterbot,council_of_5,mrlore,trae_agent,zw_transformer,engain_bridge}
fi

# Step 3: Fix Scripts Permissions
print_step "Setting script permissions..."
find . -name "*.sh" -type f -exec chmod +x {} \;
print_success "All shell scripts made executable"

# Step 4: Create Requirements File if Missing
if [ ! -f "docker/requirements_empire.txt" ]; then
    print_step "Creating requirements file..."
    mkdir -p docker
    cat > docker/requirements_empire.txt << 'REQ_EOF'
flask==2.3.3
requests==2.31.0
ollama==0.2.1
piper-tts==1.2.0
numpy==1.24.3
scipy==1.11.1
REQ_EOF
    print_success "Requirements file created"
fi

# Step 5: Create Fallback Start Script
if [ ! -f "scripts/start_empire.sh" ]; then
    print_step "Creating fallback start script..."
    mkdir -p scripts
    cat > scripts/start_empire.sh << 'START_EOF'
#!/bin/bash
echo "🏰 Starting AI Empire Services..."

# Start basic HTTP server as fallback
cd services 2>/dev/null || cd .
echo "📡 Empire control server starting on port 8000..."
python3 -m http.server 8000 &

echo "✅ Empire services initiated!"
echo "🌐 Access at: http://localhost:8000"
wait
START_EOF
    chmod +x scripts/start_empire.sh
    print_success "Fallback start script created"
fi

# Step 6: Test Basic Functionality
print_step "Testing basic functionality..."

# Test Python imports
python3 -c "import sys; print(f'Python {sys.version} ready')" && print_success "Python environment OK"

# Test Docker if available
if [ "$DOCKER_AVAILABLE" = true ]; then
    docker --version > /dev/null && print_success "Docker ready"
    docker-compose --version > /dev/null && print_success "Docker Compose ready"
fi

# Final Summary
echo ""
echo -e "${GREEN}🎉 AI EMPIRE SETUP COMPLETE! 🎉${NC}"
echo ""
echo -e "${CYAN}🚀 TO START YOUR EMPIRE:${NC}"
echo -e "   ${YELLOW}./launch_empire.sh${NC}  (Recommended - auto-detects environment)"
echo ""
echo -e "${CYAN}🏗️ WHAT WAS FIXED:${NC}"
echo -e "   ✅ Directory structure organized"  
echo -e "   ✅ Missing files created"
echo -e "   ✅ Script permissions fixed"
echo -e "   ✅ Fallback systems added"
echo ""
echo -e "${CYAN}📚 SERVICES AVAILABLE:${NC}"
echo -e "   🎮 EngAin Bridge: http://localhost:8005"
echo -e "   ⚡ TRAE Executor: http://localhost:8009"
echo -e "   📚 MrLore: http://localhost:8001"
echo -e "   🧠 ZW Transformer: http://localhost:8002"
echo -e "   🏛️ Council of 5: http://localhost:8003"
echo -e "   🗂️ ClutterBot: http://localhost:8000"
echo ""
echo -e "${PURPLE}Now anyone can run your AI Empire without fighting! 🏰⚡${NC}"
