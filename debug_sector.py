import sys
import os
sys.path.append('.')

from app import app, db, MLModelResult
import json

with app.app_context():
    # Get sector analyzer result
    sector_result = MLModelResult.query.filter(
        MLModelResult.model_name == 'sector_analyzer'
    ).order_by(MLModelResult.created_at.desc()).first()
    
    if sector_result and sector_result.results:
        results_data = json.loads(sector_result.results)
        print('Sector Analysis Keys:', list(results_data.keys()))
        
        # Check if there's sector analysis data
        if 'sector_analysis' in results_data:
            sector_analysis = results_data['sector_analysis']
            print(f'Sector analysis type: {type(sector_analysis)}')
            if isinstance(sector_analysis, dict):
                print('Sector names:', list(sector_analysis.keys()))
                
                # Show first sector structure
                first_sector = list(sector_analysis.values())[0]
                print('First sector keys:', list(first_sector.keys()) if isinstance(first_sector, dict) else 'Not a dict')
                
                # Check if there's recommendation info
                if isinstance(first_sector, dict) and 'sector_recommendation' in first_sector:
                    print('Sector recommendation:', first_sector['sector_recommendation'])
