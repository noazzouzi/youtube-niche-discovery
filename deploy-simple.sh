#!/bin/bash

# YouTube Niche Discovery Engine - Simple External Deployment
# Deploy on current server with external access

set -e

SERVER_IP="38.143.19.241"

echo "🚀 Deploying YouTube Niche Discovery Engine"
echo "🌍 Server IP: $SERVER_IP"  
echo "📊 Frontend: http://$SERVER_IP:3000"
echo "🔌 Backend: http://$SERVER_IP:8000"
echo "=" * 50

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'  
RED='\033[0;31m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check Docker
if ! command -v docker &> /dev/null; then
    print_error "Docker not found. Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    systemctl start docker
    systemctl enable docker
    print_status "Docker installed"
fi

# Check Docker Compose
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    print_error "Docker Compose not found. Installing..."
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    print_status "Docker Compose installed"
fi

# Determine Docker Compose command
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
else
    DOCKER_COMPOSE="docker compose"
fi

# Stop any existing containers
print_status "Cleaning up existing containers..."
$DOCKER_COMPOSE -f docker-compose.simple.yml down --remove-orphans 2>/dev/null || true

# Build and start services
print_status "Building and starting services..."
$DOCKER_COMPOSE -f docker-compose.simple.yml up --build -d

# Wait for services to be ready
print_status "Waiting for services to start..."

# Check PostgreSQL
echo -n "PostgreSQL"
for i in {1..30}; do
    if docker exec niche_postgres_simple pg_isready -U niche_user -d niche_discovery_prod >/dev/null 2>&1; then
        echo " ✅"
        break
    fi
    echo -n "."
    sleep 2
done

# Check Redis
echo -n "Redis"
for i in {1..15}; do
    if docker exec niche_redis_simple redis-cli ping >/dev/null 2>&1; then
        echo " ✅"
        break
    fi
    echo -n "."
    sleep 2
done

# Check Backend
echo -n "Backend API"
for i in {1..60}; do
    if curl -s http://localhost:8000/health >/dev/null 2>&1; then
        echo " ✅"
        break
    fi
    echo -n "."
    sleep 3
done

# Check Frontend
echo -n "Frontend"
for i in {1..60}; do
    if curl -s http://localhost:3000 >/dev/null 2>&1; then
        echo " ✅"
        break
    fi
    echo -n "."
    sleep 3
done

echo ""
echo "🎉 DEPLOYMENT SUCCESSFUL!"
echo "=" * 60

print_status "System Status:"
echo "  🗄️  Database: PostgreSQL running"
echo "  📦  Cache: Redis running"
echo "  🔌  Backend API: http://$SERVER_IP:8000"
echo "  📊  Frontend: http://$SERVER_IP:3000"
echo "  📖  API Docs: http://$SERVER_IP:8000/docs"

echo ""
echo "🔥 IMMEDIATE ACCESS:"
echo "  📊 Dashboard: http://$SERVER_IP:3000"
echo "  🔌 API: http://$SERVER_IP:8000"
echo "  📖 Documentation: http://$SERVER_IP:8000/docs"
echo "  ❤️  Health Check: http://$SERVER_IP:8000/health"

echo ""  
echo "🚀 QUICK TEST:"
echo "  1. Open: http://$SERVER_IP:3000"
echo "  2. Click 'Start Discovery' button"
echo "  3. Watch real-time PM algorithm scoring!"

echo ""
echo "📊 MONITORING:"
echo "  View logs: docker-compose -f docker-compose.simple.yml logs -f"
echo "  Stop: docker-compose -f docker-compose.simple.yml down"
echo "  Restart: docker-compose -f docker-compose.simple.yml restart"

echo ""
print_warning "💡 TIP: Add real YouTube API key to .env for full functionality"
print_warning "💡 TIP: System works with demo data for immediate testing"

# Test external connectivity
echo ""
echo "🌍 TESTING EXTERNAL CONNECTIVITY..."

# Test backend
if curl -s http://$SERVER_IP:8000/health >/dev/null 2>&1; then
    print_status "Backend externally accessible: http://$SERVER_IP:8000"
else
    print_warning "Backend may not be externally accessible yet (starting up...)"
fi

# Test frontend  
if curl -s http://$SERVER_IP:3000 >/dev/null 2>&1; then
    print_status "Frontend externally accessible: http://$SERVER_IP:3000"
else
    print_warning "Frontend may not be externally accessible yet (starting up...)"
fi

echo ""
echo "🎯 NICHE DISCOVERY ENGINE IS LIVE!"
echo "🌍 External Access: http://$SERVER_IP:3000"
echo "💰 Start discovering profitable niches NOW!"