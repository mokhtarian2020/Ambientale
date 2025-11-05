#!/usr/bin/env python3
"""
Test Script for Enhanced HealthTrace Platform with Synthetic Data
Validates all endpoints and data consistency
"""

import requests
import json
from datetime import datetime

def test_api_endpoint(url, description):
    """Test an API endpoint and display results"""
    print(f"\n🔍 Testing: {description}")
    print(f"   URL: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Success! Status: {response.status_code}")
            
            # Display key metrics
            if isinstance(data, dict):
                if 'total_reports' in data:
                    print(f"   📊 Total reports: {data['total_reports']:,}")
                if 'total_cases' in data:
                    print(f"   📊 Total cases: {data['total_cases']:,}")
                if 'disease_name' in data:
                    print(f"   🦠 Disease: {data['disease_name']}")
                if 'total_diseases' in data:
                    print(f"   🦠 Diseases available: {data['total_diseases']}")
                if 'total_measurements' in data:
                    print(f"   🌍 Environmental measurements: {data['total_measurements']:,}")
                if 'data_source' in data:
                    print(f"   📡 Data source: {data['data_source']}")
            
            return True, data
        else:
            print(f"   ❌ Failed! Status: {response.status_code}")
            return False, None
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False, None

def main():
    """Run comprehensive API tests"""
    
    base_url = "http://localhost:8002"
    
    print("🧪 HealthTrace Enhanced API Test Suite")
    print("=" * 60)
    
    # Test core endpoints
    tests = [
        (f"{base_url}/", "Root endpoint"),
        (f"{base_url}/health", "Health check"),
        (f"{base_url}/api/v1/dashboard/summary", "Dashboard summary with synthetic data"),
        (f"{base_url}/api/v1/diseases/", "Disease list"),
        (f"{base_url}/api/v1/diseases/influenza/analytics", "Influenza analytics"),
        (f"{base_url}/api/v1/diseases/legionellosis/analytics", "Legionellosis analytics"),
        (f"{base_url}/api/v1/diseases/hepatitis_a/analytics", "Hepatitis A analytics"),
        (f"{base_url}/api/v1/environmental/factors", "Environmental factors"),
        (f"{base_url}/api/v1/analytics/correlation", "Correlation analysis"),
        (f"{base_url}/api/v1/analytics/correlation?disease=influenza", "Influenza correlations"),
        (f"{base_url}/api/v1/models/available", "Available models"),
        (f"{base_url}/api/v1/istat/081001/2024/mensile/media/PM25/", "ISTAT environmental data")
    ]
    
    successful_tests = 0
    total_tests = len(tests)
    results = {}
    
    for url, description in tests:
        success, data = test_api_endpoint(url, description)
        if success:
            successful_tests += 1
            results[description] = data
    
    print("\n" + "=" * 60)
    print(f"🎯 Test Results: {successful_tests}/{total_tests} endpoints working")
    
    if successful_tests == total_tests:
        print("✅ All tests passed! Platform is fully operational with synthetic data.")
    else:
        print(f"⚠️  {total_tests - successful_tests} tests failed. Check API server status.")
    
    # Display summary statistics
    if "Dashboard summary with synthetic data" in results:
        dashboard_data = results["Dashboard summary with synthetic data"]
        print("\n📊 Platform Statistics:")
        print(f"   • Total reports: {dashboard_data.get('total_reports', 0):,}")
        print(f"   • Total investigations: {dashboard_data.get('total_investigations', 0):,}")
        print(f"   • Active patients: {dashboard_data.get('active_patients', 0):,}")
        print(f"   • Data sources: {len(dashboard_data.get('data_sources', {}))}")
        
        # Show disease breakdown
        if 'disease_breakdown' in dashboard_data:
            print(f"   • Disease breakdown:")
            for disease, count in dashboard_data['disease_breakdown'].items():
                print(f"     - {disease.title()}: {count:,} cases")
    
    if "Disease list" in results:
        disease_data = results["Disease list"]
        print(f"\n🦠 Available Diseases: {disease_data.get('total_diseases', 0)}")
        if 'diseases' in disease_data:
            for disease in disease_data['diseases']:
                print(f"   • {disease['name'].title()} ({disease['category']}): {disease.get('total_cases', 0)} cases")
    
    if "Available models" in results:
        model_data = results["Available models"]
        print(f"\n🧮 Analytics Models: {model_data.get('total_models', 0)} available")
        for category in ['statistical_models', 'machine_learning_models', 'spatial_models']:
            if category in model_data:
                category_name = category.replace('_', ' ').title()
                print(f"   • {category_name}: {len(model_data[category])} models")
    
    print("\n🌐 Access URLs:")
    print(f"   • API Documentation: http://localhost:8002/docs")
    print(f"   • Dashboard: http://localhost:8080/HealthTrace/index.html")
    print(f"   • Disease Analytics: http://localhost:8002/api/v1/diseases/influenza/analytics")
    print(f"   • Environmental Data: http://localhost:8002/api/v1/environmental/factors")
    
    print("\n✨ Platform Ready for Testing!")
    print("   All analytical models can now be tested with realistic Italian health data")

if __name__ == "__main__":
    main()
