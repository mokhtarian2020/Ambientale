#!/bin/bash
# HealthTrace Platform Startup Script

echo "🏥 Starting HealthTrace Platform..."
echo "=================================="

# Change to HealthTrace directory
cd /home/amir/Documents/amir/Ambientale/HealthTrace

# Kill any existing processes
echo "🔄 Stopping existing servers..."
pkill -f "enhanced_simple_api.py"
pkill -f "http.server 8080"

# Start enhanced API server
echo "🚀 Starting Enhanced API Server (port 8002)..."
nohup python enhanced_simple_api.py > api.log 2>&1 &
API_PID=$!

# Start frontend server  
echo "🌐 Starting Frontend Server (port 8080)..."
cd /home/amir/Documents/amir/Ambientale
nohup python -m http.server 8080 > frontend.log 2>&1 &
FRONTEND_PID=$!

# Wait for servers to start
echo "⏳ Waiting for servers to start..."
sleep 5

# Test API
echo "🧪 Testing API connectivity..."
if curl -s http://localhost:8002/health | grep -q "healthy"; then
    echo "✅ Enhanced API is running (PID: $API_PID)"
else
    echo "❌ Enhanced API failed to start"
fi

# Test frontend
if curl -s http://localhost:8080/ | grep -q "HTTP"; then
    echo "✅ Frontend server is running (PID: $FRONTEND_PID)"
else
    echo "❌ Frontend server failed to start"
fi

echo ""
echo "🎯 HealthTrace Platform Ready!"
echo "================================"
echo "📱 Access URLs:"
echo "   • Main Dashboard: http://localhost:8080/index.html"
echo "   • Environmental Correlations: http://localhost:8080/environmental_correlations.html"
echo "   • API Documentation: http://localhost:8002/docs"
echo ""
echo "📊 Platform Statistics:"
echo "   • 350 disease cases across 3 diseases"
echo "   • 137,880 environmental measurements"
echo "   • 27 epidemiological investigations"
echo "   • 15 Italian ISTAT locations"
echo ""
echo "🎉 Ready for supervisor demonstration!"
echo ""
echo "To stop servers:"
echo "   kill $API_PID $FRONTEND_PID"
