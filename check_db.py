import sys
import os
sys.path.append('.')

from app import app, db, MLModelResult
import json

with app.app_context():
    count = MLModelResult.query.count()
    print(f'Total MLModelResult records: {count}')
    
    if count > 0:
        latest = MLModelResult.query.order_by(MLModelResult.created_at.desc()).limit(5).all()
        for r in latest:
            results_len = len(r.results) if r.results else 0
            print(f'Model: {r.model_name}, Created: {r.created_at}, Results length: {results_len}')
    else:
        print('No MLModelResult records found in database')
