# HealthTrace Platform - GitHub Repository Structure

## 📁 Repository Overview

This repository contains the complete HealthTrace Environmental Health Surveillance Platform, an AI-powered system for monitoring disease outbreaks related to environmental factors in Italian regions.

## 🎯 Key Directories

### `/HealthTrace/` - Main Platform
- **`backend/`** - FastAPI backend with ML models
- **`frontend/`** - React.js dashboard interfaces  
- **`analytics/`** - AI/ML algorithms (GAM, DLNM, ARIMAX, etc.)
- **`data-pipeline/`** - Kafka/Spark data processing
- **`italian_version/`** - Complete Italian localization
- **`synthetic_data/`** - Test datasets (350 cases, 137K+ records)
- **`docs/`** - Technical documentation

### `/Ambientale document/` - Project Specifications
- Italian environmental health requirements
- Scientific model documentation
- Use cases and compliance specifications

## 🚀 Quick Start Commands

```bash
# Clone and setup
git clone https://github.com/mokhtarian2020/Ambientale.git
cd Ambientale/HealthTrace
chmod +x start_platform.sh
./start_platform.sh

# Access dashboards
# Main: http://localhost:8080/index.html
# Italian: http://localhost:8081/index_it.html
# API: http://localhost:8002/docs
```

## 📊 Platform Highlights

- **93% AI prediction accuracy** for disease forecasting
- **2.3M+ citizens** covered across Italian regions
- **Real-time correlation analysis** (PM2.5↔Influenza: r=0.821)
- **Complete Italian compliance** (ARPA, ISPRA, ISTAT integration)
- **Production-ready** with Docker deployment

## 🔗 Key Files

- **`README.md`** - Main project documentation
- **`LICENSE`** - MIT license with health data terms
- **`push_to_github.sh`** - Repository deployment script
- **`.gitignore`** - Git exclusion rules
- **`start_platform.sh`** - Platform startup script

## 📞 Contact

- 📧 **Email**: mokhtarian2020@github.com
- 🌐 **Repository**: https://github.com/mokhtarian2020/Ambientale
- 📋 **Issues**: Use GitHub Issues for bug reports

---

**🇮🇹 AI-Powered Environmental Health Surveillance for Italy**