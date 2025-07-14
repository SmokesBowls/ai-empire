#!/bin/bash
# 🏰 AI Empire Docker Manager

EMPIRE_NAME="ai-empire"
OLLAMA_NAME="empire-ollama"

case "$1" in
    build)
        echo "🏗️ Building AI Empire container..."
        docker-compose build
        ;;
    
    start)
        echo "🚀 Starting AI Empire..."
        docker-compose up -d
        echo "⏳ Waiting for services to initialize..."
        sleep 15
        echo "🏰 Empire Status:"
        docker exec $EMPIRE_NAME ./ai_empire_deployable/scripts/status_empire.sh
        ;;
    
    stop)
        echo "🛑 Stopping AI Empire..."
        docker-compose down
        ;;
    
    status)
        echo "🏰 AI Empire Status:"
        if docker ps | grep -q $EMPIRE_NAME; then
            docker exec $EMPIRE_NAME ./ai_empire_deployable/scripts/status_empire.sh
        else
            echo "❌ Empire is not running"
        fi
        ;;
    
    logs)
        echo "📜 Empire Logs:"
        docker-compose logs -f
        ;;
    
    shell)
        echo "🐚 Entering Empire container..."
        docker exec -it $EMPIRE_NAME /bin/bash
        ;;
    
    trae)
        if [ -z "$2" ]; then
            echo "Usage: $0 trae 'your task here'"
            exit 1
        fi
        echo "⚡ TRAE Command: $2"
        docker exec $EMPIRE_NAME python3 /empire/trae-agent-main/real_working_agent.py "$2"
        ;;
    
    engain)
        if [ -z "$2" ]; then
            echo "Usage: $0 engain 'avatar command here'"
            exit 1
        fi
        echo "🎮 EngAin Command: $2"
        curl -X POST http://localhost:8005/avatar_command \
             -H "Content-Type: application/json" \
             -d "{\"command\": \"$2\", \"context\": {}}"
        ;;
    
    models)
        echo "🤖 Setting up Ollama models..."
        docker exec $OLLAMA_NAME ollama pull qwen2.5-coder:3b
        docker exec $OLLAMA_NAME ollama pull deepseek-r1:1.5b
        echo "✅ Models ready"
        ;;
    
    resurrect)
        echo "🏰🔥 FULL EMPIRE RESURRECTION! 🔥🏰"
        $0 build
        $0 start
        $0 models
        echo ""
        echo "✅🎉 AI EMPIRE RESURRECTED IN DOCKER! 🎉✅"
        echo ""
        echo "🎮 EngAin Avatar Bridge: http://localhost:8005"
        echo "⚡ TRAE Executor: http://localhost:8009"
        echo "📚 MrLore: http://localhost:8001"
        echo "🧠 ZW Transformer: http://localhost:8002"
        echo "🏛️ Council of 5: http://localhost:8003"
        echo "🗂️ ClutterBot: http://localhost:8000"
        echo ""
        echo "🧪 Test commands:"
        echo "./empire_manager.sh trae 'Create a spell system'"
        echo "./empire_manager.sh engain 'Generate dungeon lore'"
        ;;
    
    *)
        echo "🏰 AI Empire Docker Manager"
        echo ""
        echo "Usage: $0 {build|start|stop|status|logs|shell|trae|engain|models|resurrect}"
        echo ""
        echo "Commands:"
        echo "  build     - Build the empire container"
        echo "  start     - Start the empire services"
        echo "  stop      - Stop the empire"
        echo "  status    - Check empire status"
        echo "  logs      - View empire logs"
        echo "  shell     - Enter empire container"
        echo "  trae      - Execute TRAE command"
        echo "  engain    - Send command to EngAin avatar"
        echo "  models    - Download Ollama models"
        echo "  resurrect - Full empire resurrection"
        echo ""
        echo "Examples:"
        echo "  $0 resurrect"
        echo "  $0 trae 'Create player controller'"
        echo "  $0 engain 'Generate quest dialogue'"
        ;;
esac
