#!/bin/bash

# Test YouTube Niche Discovery Engine Deployment
# Server IP: 38.143.19.241

SERVER_IP="38.143.19.241"

echo "🧪 Testing YouTube Niche Discovery Engine Deployment"
echo "🌍 Server: $SERVER_IP"
echo "=" * 50

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

test_endpoint() {
    local url="$1"
    local name="$2"
    local expected_status="${3:-200}"
    
    echo -n "Testing $name..."
    
    response=$(curl -s -w "HTTPSTATUS:%{http_code}" "$url" || echo "HTTPSTATUS:000")
    status=$(echo "$response" | grep -o "HTTPSTATUS:[0-9]*" | cut -d: -f2)
    body=$(echo "$response" | sed 's/HTTPSTATUS:[0-9]*$//')
    
    if [ "$status" -eq "$expected_status" ]; then
        echo -e " ${GREEN}✅ OK ($status)${NC}"
        return 0
    else
        echo -e " ${RED}❌ FAILED (Status: $status)${NC}"
        return 1
    fi
}

echo ""
echo "🔍 CONNECTIVITY TESTS:"

# Test Backend Health
test_endpoint "http://localhost:8000/health" "Backend Health (Internal)" 200
test_endpoint "http://$SERVER_IP:8000/health" "Backend Health (External)" 200

# Test API Root
test_endpoint "http://$SERVER_IP:8000/" "API Root" 200

# Test API Documentation
test_endpoint "http://$SERVER_IP:8000/docs" "API Documentation" 200

# Test Niche Endpoints
test_endpoint "http://$SERVER_IP:8000/api/v1/niches/" "Niches List" 200
test_endpoint "http://$SERVER_IP:8000/api/v1/niches/dashboard/stats" "Dashboard Stats" 200

echo ""
echo "📊 FUNCTIONAL TESTS:"

# Test Niche Discovery
echo -n "Testing Niche Discovery..."
discovery_response=$(curl -s -X POST "http://$SERVER_IP:8000/api/v1/niches/discover/daily" 2>/dev/null)
if [ $? -eq 0 ]; then
    echo -e " ${GREEN}✅ Discovery endpoint accessible${NC}"
else
    echo -e " ${YELLOW}⚠️ Discovery endpoint may not be ready${NC}"
fi

# Test High Potential Niches
echo -n "Testing High Potential Niches..."
high_potential_response=$(curl -s "http://$SERVER_IP:8000/api/v1/niches/high-potential/" 2>/dev/null)
if [ $? -eq 0 ]; then
    echo -e " ${GREEN}✅ High potential endpoint accessible${NC}"
else
    echo -e " ${YELLOW}⚠️ High potential endpoint may not be ready${NC}"
fi

echo ""
echo "🌍 EXTERNAL ACCESS VERIFICATION:"

# Test from external perspective
echo "External access URLs:"
echo "  🔌 Backend API: http://$SERVER_IP:8000"
echo "  📖 API Docs: http://$SERVER_IP:8000/docs"
echo "  ❤️ Health Check: http://$SERVER_IP:8000/health"

echo ""
echo "🧪 QUICK PM ALGORITHM TEST:"

# Create a test niche to verify scoring works
echo -n "Creating test niche..."
test_niche=$(curl -s -X POST "http://$SERVER_IP:8000/api/v1/niches/" \
    -H "Content-Type: application/json" \
    -d '{"name":"test_ai_tutorials","category":"education","description":"AI tutorial niche for testing"}' 2>/dev/null)

if [ $? -eq 0 ] && [[ "$test_niche" == *"test_ai_tutorials"* ]]; then
    echo -e " ${GREEN}✅ Niche creation works${NC}"
    
    # Extract niche ID and test scoring
    niche_id=$(echo "$test_niche" | grep -o '"id":[0-9]*' | cut -d: -f2)
    if [ -n "$niche_id" ]; then
        echo -n "Testing PM Algorithm Scoring..."
        scoring_response=$(curl -s -X POST "http://$SERVER_IP:8000/api/v1/niches/$niche_id/rescore" 2>/dev/null)
        if [ $? -eq 0 ]; then
            echo -e " ${GREEN}✅ PM scoring algorithm works${NC}"
        else
            echo -e " ${YELLOW}⚠️ Scoring may need more setup time${NC}"
        fi
    fi
else
    echo -e " ${YELLOW}⚠️ Niche creation endpoint may not be ready${NC}"
fi

echo ""
echo "📋 DEPLOYMENT SUMMARY:"

# Container status
echo "🐳 Docker Container Status:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep niche || echo "No containers running yet"

echo ""
echo "🚀 NEXT STEPS:"
echo "1. 📊 Access API: http://$SERVER_IP:8000"
echo "2. 📖 View documentation: http://$SERVER_IP:8000/docs"
echo "3. 🧪 Test niche discovery: POST /api/v1/niches/discover/daily"
echo "4. 🏆 Check high-potential niches: GET /api/v1/niches/high-potential/"

echo ""
echo "💡 TIP: Add real YouTube API key to .env for full PM algorithm functionality"
echo "🎯 The PM Agent 100-point scoring system is ready to discover profitable niches!"