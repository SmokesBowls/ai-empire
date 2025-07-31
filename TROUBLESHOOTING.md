# 🏰 AI Empire Troubleshooting Guide

## Quick Fixes

### Docker Build Fails
```bash
# Clean Docker cache and rebuild
docker system prune -f
docker-compose build --no-cache
```

### Permission Denied on Scripts
```bash
# Fix all script permissions
find . -name "*.sh" -exec chmod +x {} \;
```

### Python Import Errors
```bash
# Install missing dependencies
pip3 install flask requests ollama piper-tts numpy scipy
```

### Port Already in Use
```bash
# Kill processes using empire ports
sudo lsof -ti:8000,8001,8002,8003,8005,8009 | xargs kill -9
```

## Common Issues

1. **"ai_empire_deployable not found"** - Fixed by new Dockerfile
2. **Scripts not executable** - Run: `chmod +x scripts/*.sh`
3. **Docker permissions** - Add user to docker group: `sudo usermod -aG docker $USER`

## Getting Help

The setup script automatically fixes most issues. If problems persist:
1. Run `./launch_empire.sh` - it auto-detects your environment
2. Check logs in `logs/empire.log`
3. Ensure ports 8000-8009 are available
