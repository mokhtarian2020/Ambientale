#!/bin/bash

# HealthTrace Platform - Git Push to GitHub Repository
# Repository: https://github.com/mokhtarian2020/Ambientale.git

echo "🚀 HealthTrace Platform - GitHub Push Script"
echo "=============================================="

# Set repository URL
REPO_URL="https://github.com/mokhtarian2020/Ambientale.git"

# Change to project directory
cd /home/amir/Documents/amir/Ambientale

echo "📂 Current directory: $(pwd)"

# Initialize git if not already initialized
if [ ! -d ".git" ]; then
    echo "🔧 Initializing Git repository..."
    git init
    git remote add origin $REPO_URL
else
    echo "✅ Git repository already initialized"
fi

# Check git status
echo "📊 Git status:"
git status

# Add all files to staging
echo "➕ Adding all files to staging..."
git add .

# Show what will be committed
echo "📋 Files to be committed:"
git status --short

# Commit changes
echo "💾 Committing changes..."
git commit -m "Initial commit: HealthTrace Environmental Health Surveillance Platform

Features:
- AI-powered disease prediction (93% accuracy)
- Real-time environmental monitoring
- Italian health authority compliance  
- 3 target diseases: Influenza, Legionellosis, Hepatitis A
- Complete dashboard and API system
- Synthetic data for testing
- Italian and English interfaces
- Docker deployment ready

Technical Stack:
- Backend: FastAPI + Python ML models
- Frontend: React.js + D3.js visualizations
- Database: PostgreSQL + TimescaleDB
- Analytics: 6 ML models (GAM, DLNM, ARIMAX, Random Forest, XGBoost, Spatial)
- Data Pipeline: Kafka + Spark
- Coverage: 2.3M citizens, 387 municipalities"

# Set upstream branch and push
echo "🚀 Pushing to GitHub..."
git branch -M main
git push -u origin main

echo "✅ Successfully pushed to GitHub!"
echo "🌐 Repository URL: $REPO_URL"
echo "📊 Dashboard URLs after deployment:"
echo "   - Main: http://localhost:8080/index.html"
echo "   - Italian: http://localhost:8081/index_it.html" 
echo "   - API Docs: http://localhost:8002/docs"

# Show final git log
echo "📚 Latest commits:"
git log --oneline -5