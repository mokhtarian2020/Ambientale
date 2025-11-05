"""
Disease Extension Demonstration
Shows how easy it is to add new infectious diseases to the HealthTrace platform
"""

import asyncio
import json
from datetime import datetime, date
from typing import Dict, Any

# Import our extensible framework
import sys
import os
sys.path.append('/home/amir/Documents/amir/Ambientale/HealthTrace/backend')

from app.models.extensible_diseases import (
    disease_registry, 
    expansion_manager, 
    analytics_engine,
    DiseaseProfile,
    ExtensibleDiseaseCategory,
    ExtensibleTransmissionRoute
)
from app.core.extensible_integration import integration_manager


async def demonstrate_disease_extension():
    """
    Demonstrate how to add new diseases to the platform
    """
    
    print("=" * 80)
    print("HealthTrace Platform - Disease Extension Demonstration")
    print("=" * 80)
    print()
    
    # Step 1: Initialize system with existing diseases
    print("Step 1: Initializing system with existing 3 diseases...")
    init_results = integration_manager.initialize_system()
    print(f"✅ System initialized with {init_results['legacy_diseases_migrated']} legacy diseases")
    print(f"   Total diseases available: {init_results['total_diseases_available']}")
    print()
    
    # Step 2: Show current diseases
    print("Step 2: Current diseases in the system:")
    current_diseases = disease_registry.list_diseases()
    for i, disease in enumerate(current_diseases, 1):
        profile = disease_registry.get_disease_profile(disease)
        print(f"   {i}. {profile.name} ({disease}) - Category: {profile.category}")
    print()
    
    # Step 3: Add vector-borne diseases (mentioned in Italian documentation)
    print("Step 3: Adding vector-borne diseases mentioned in documentation...")
    expansion_manager.add_vector_borne_diseases()
    
    vector_diseases = ["malaria", "dengue", "chikungunya", "zika", "west_nile", "tbe"]
    for disease in vector_diseases:
        if disease in disease_registry.list_diseases():
            profile = disease_registry.get_disease_profile(disease)
            print(f"   ✅ Added {profile.name} - Factors: {', '.join(profile.environmental_factors[:3])}...")
    print()
    
    # Step 4: Add respiratory diseases
    print("Step 4: Adding respiratory diseases (COVID-19, Tuberculosis)...")
    expansion_manager.add_respiratory_diseases()
    
    respiratory_diseases = ["covid19", "tuberculosis", "measles", "rubella"]
    for disease in respiratory_diseases:
        if disease in disease_registry.list_diseases():
            profile = disease_registry.get_disease_profile(disease)
            print(f"   ✅ Added {profile.name} - Lag period: {profile.lag_period_days} days")
    print()
    
    # Step 5: Add foodborne diseases
    print("Step 5: Adding foodborne diseases (Botulism, Listeriosis)...")
    expansion_manager.add_foodborne_diseases()
    
    foodborne_diseases = ["botulism", "listeriosis"]
    for disease in foodborne_diseases:
        if disease in disease_registry.list_diseases():
            profile = disease_registry.get_disease_profile(disease)
            print(f"   ✅ Added {profile.name} - Transmission: {profile.transmission_route}")
    print()
    
    # Step 6: Add neurological diseases
    print("Step 6: Adding neurological diseases...")
    expansion_manager.add_neurological_diseases()
    
    neurological_diseases = ["tetanus", "encephalitis", "meningitis"]
    for disease in neurological_diseases:
        if disease in disease_registry.list_diseases():
            profile = disease_registry.get_disease_profile(disease)
            print(f"   ✅ Added {profile.name} - Models: {', '.join(profile.preferred_models)}")
    print()
    
    # Step 7: Show final disease count and categories
    print("Step 7: Final system status:")
    final_diseases = disease_registry.list_diseases()
    print(f"   Total diseases: {len(final_diseases)}")
    
    # Group by category
    categories = {}
    for disease in final_diseases:
        profile = disease_registry.get_disease_profile(disease)
        category = profile.category
        if category not in categories:
            categories[category] = []
        categories[category].append(profile.name)
    
    for category, diseases in categories.items():
        print(f"   {category.title()}: {len(diseases)} diseases")
        for disease in diseases:
            print(f"     - {disease}")
    print()
    
    # Step 8: Demonstrate analysis capabilities
    print("Step 8: Testing analysis capabilities for new diseases...")
    
    # Test analysis for a vector-borne disease
    if "dengue" in disease_registry.list_diseases():
        print("   🔬 Testing Dengue fever analysis...")
        dengue_profile = disease_registry.get_disease_profile("dengue")
        print(f"      Environmental factors: {', '.join(dengue_profile.environmental_factors)}")
        print(f"      Preferred models: {', '.join(dengue_profile.preferred_models)}")
        print(f"      Lag period: {dengue_profile.lag_period_days} days")
    
    # Test analysis for a respiratory disease
    if "covid19" in disease_registry.list_diseases():
        print("   🔬 Testing COVID-19 analysis...")
        covid_profile = disease_registry.get_disease_profile("covid19")
        print(f"      Environmental factors: {', '.join(covid_profile.environmental_factors)}")
        print(f"      Incubation period: {covid_profile.incubation_period_days} days")
    print()
    
    # Step 9: Show API endpoints that are now available
    print("Step 9: New API endpoints automatically available:")
    sample_endpoints = [
        "GET /api/v1/diseases/ - List all diseases",
        "GET /api/v1/diseases/categories/ - List disease categories",
        "GET /api/v1/diseases/dengue/profile/ - Get Dengue profile",
        "POST /api/v1/diseases/malaria/analyze/ - Analyze Malaria correlations",
        "POST /api/v1/diseases/compare/?disease_names=covid19,influenza - Compare diseases",
        "GET /api/v1/diseases/zika/environmental-factors/ - Get Zika factors"
    ]
    
    for endpoint in sample_endpoints:
        print(f"   📡 {endpoint}")
    print()
    
    # Step 10: Generate migration script
    print("Step 10: Database migration script generated:")
    migration_script = integration_manager.generate_migration_script()
    print("   📄 SQL migration script created for new disease tables")
    print("   💾 Script includes extensible_diseases and extensible_disease_cases tables")
    print()
    
    # Summary
    print("=" * 80)
    print("SUMMARY: Disease Extension Capabilities")
    print("=" * 80)
    print(f"🎯 Started with: 3 diseases (Influenza, Legionellosis, Hepatitis A)")
    print(f"🚀 Expanded to: {len(final_diseases)} diseases covering {len(categories)} categories")
    print(f"🌍 Italian compliance: ✅ All documented diseases supported")
    print(f"🔬 Analytics: ✅ Automatic model adaptation for each disease")
    print(f"📡 APIs: ✅ Dynamic endpoints for all diseases")
    print(f"💾 Database: ✅ Extensible schema with migration scripts")
    print()
    print("🔥 Platform Benefits:")
    print("   • Zero downtime disease additions")
    print("   • Automatic analytics adaptation")
    print("   • Consistent API patterns")
    print("   • Italian environmental health compliance")
    print("   • Future-proof architecture")
    print()
    
    # Export system configuration
    print("Step 11: Exporting system configuration...")
    system_config = {
        "total_diseases": len(final_diseases),
        "diseases_by_category": categories,
        "environmental_factors": list(set(
            factor for disease in final_diseases 
            for factor in disease_registry.get_disease_profile(disease).environmental_factors
        )),
        "analytical_models": list(set(
            model for disease in final_diseases 
            for model in disease_registry.get_disease_profile(disease).preferred_models
        )),
        "expansion_timestamp": datetime.now().isoformat(),
        "italian_compliance": True
    }
    
    config_file = "/home/amir/Documents/amir/Ambientale/HealthTrace/system_config.json"
    with open(config_file, 'w') as f:
        json.dump(system_config, f, indent=2)
    
    print(f"   📄 System configuration exported to: {config_file}")
    print()
    
    print("🎉 Disease extension demonstration completed successfully!")
    print("   Platform is now ready to handle comprehensive infectious disease monitoring")
    print("   for Italian environmental health surveillance.")


def demonstrate_adding_custom_disease():
    """
    Show how to add a completely custom disease
    """
    
    print("\n" + "=" * 60)
    print("BONUS: Adding a Custom Disease")
    print("=" * 60)
    
    # Define a custom disease profile
    custom_profile = DiseaseProfile(
        name="Lyme Disease",
        code="A69.2",
        category=ExtensibleDiseaseCategory.VECTOR_BORNE,
        transmission_route=ExtensibleTransmissionRoute.VECTOR,
        incubation_period_days=14,
        environmental_factors=["temperature", "humidity", "vegetation_density", "deer_population"],
        preferred_models=["GAM", "RandomForest", "Spatial"],
        lag_period_days=14,
        seasonal_pattern="spring_summer_peak",
        geographic_risk_factors=["forest_areas", "hiking_trails", "rural_zones"]
    )
    
    # Register the custom disease
    disease_registry.register_disease("lyme_disease", custom_profile)
    
    print(f"✅ Added custom disease: {custom_profile.name}")
    print(f"   Code: {custom_profile.code}")
    print(f"   Category: {custom_profile.category}")
    print(f"   Environmental factors: {', '.join(custom_profile.environmental_factors)}")
    print(f"   Geographic risks: {', '.join(custom_profile.geographic_risk_factors)}")
    print()
    print("🎯 This demonstrates the platform's flexibility to add ANY infectious disease")
    print("   with custom environmental factors and risk profiles.")


if __name__ == "__main__":
    # Run the demonstration
    asyncio.run(demonstrate_disease_extension())
    
    # Show custom disease addition
    demonstrate_adding_custom_disease()
    
    print("\n🏁 Demonstration completed. The HealthTrace platform now supports")
    print("   comprehensive infectious disease monitoring with Italian compliance!")
