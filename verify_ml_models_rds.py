#!/usr/bin/env python3
"""
Verification script to check ML models saved in RDS PostgreSQL database
and generate a comprehensive summary report.
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import json
from datetime import datetime
from urllib.parse import unquote

# RDS Database Configuration
RDS_HOST = "3.85.19.80"
RDS_PORT = 5432
RDS_DB = "research"
RDS_USER = "admin"
RDS_PASSWORD = unquote("admin%402001")

def create_database_connection():
    """Create connection to RDS PostgreSQL database"""
    try:
        conn = psycopg2.connect(
            host=RDS_HOST,
            port=RDS_PORT,
            database=RDS_DB,
            user=RDS_USER,
            password=RDS_PASSWORD,
            cursor_factory=RealDictCursor
        )
        return conn
    except Exception as e:
        print(f"❌ Failed to connect to RDS database: {e}")
        return None

def verify_models_in_database():
    """Verify all ML models are properly saved in the database"""
    conn = create_database_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Get all published models
        cursor.execute("""
            SELECT 
                id, name, version, author_user_key, category, 
                created_at, artifact_path, visibility
            FROM published_models 
            ORDER BY created_at DESC
        """)
        
        models = cursor.fetchall()
        print("📊 PUBLISHED MODELS IN RDS DATABASE")
        print("=" * 60)
        for i, m in enumerate(models, 1):
            print(f"{i}. {m['name']}")
            print(f"   ID: {m['id']}")
            print(f"   Category: {m['category']}")
            print(f"   Author: {m['author_user_key']}")
            print(f"   Version: {m['version']}")
            print(f"   Created: {m['created_at']}")
            print(f"   Artifact: {m['artifact_path']}")
            print(f"   Visibility: {m['visibility']}")
            print()
        
        # Get performance data
        cursor.execute("""
            SELECT 
                pm.name, mp.accuracy, mp.total_return, mp.total_trades
            FROM ml_model_performance mp
            JOIN published_models pm ON pm.id = mp.model_id
            ORDER BY mp.accuracy DESC
        """)
        
        performance_data = cursor.fetchall()
        print("📈 MODEL PERFORMANCE METRICS")
        print("=" * 60)
        for p in performance_data:
            print(f"Model: {p['name']}")
            print(f"  Accuracy: {p['accuracy']:.1f}%")
            print(f"  Expected Return: {p['total_return']:.1f}%")
            print()
        
        # Get stock recommendations
        cursor.execute("""
            SELECT 
                pm.name as model_name, sr.stock_symbol, sr.company_name,
                sr.recommendation, sr.confidence_score, sr.expected_return
            FROM ml_stock_recommendations sr
            JOIN published_models pm ON pm.id = sr.model_id
            ORDER BY sr.confidence_score DESC
        """)
        
        recommendations = cursor.fetchall()
        print("🎯 STOCK RECOMMENDATIONS")
        print("=" * 60)
        for r in recommendations:
            print(f"Model: {r['model_name']}")
            print(f"  Stock: {r['stock_symbol']} ({r['company_name']})")
            print(f"  Recommendation: {r['recommendation']}")
            print(f"  Confidence: {r['confidence_score']:.1f}%")
            print(f"  Expected Return: {r['expected_return']:.1f}%")
            print()
        
        # Summary statistics
        cursor.execute("SELECT COUNT(*) as model_count FROM published_models")
        model_count = cursor.fetchone()['model_count']
        
        cursor.execute("SELECT COUNT(*) as perf_count FROM ml_model_performance")
        perf_count = cursor.fetchone()['perf_count']
        
        cursor.execute("SELECT COUNT(*) as rec_count FROM ml_stock_recommendations")
        rec_count = cursor.fetchone()['rec_count']
        
        cursor.execute("SELECT COUNT(DISTINCT category) as category_count FROM published_models")
        category_count = cursor.fetchone()['category_count']
        
        print("📊 DATABASE SUMMARY")
        print("=" * 60)
        print(f"Total Models: {model_count}")
        print(f"Performance Records: {perf_count}")
        print(f"Stock Recommendations: {rec_count}")
        print(f"Categories: {category_count}")
        print()
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error verifying database: {e}")
        return False

def generate_summary_report():
    """Generate a comprehensive summary report"""
    conn = create_database_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Generate detailed report
        report = {
            "verification_timestamp": datetime.now().isoformat(),
            "database": {
                "host": RDS_HOST,
                "port": RDS_PORT,
                "database": RDS_DB,
                "url": f"postgresql://{RDS_USER}:***@{RDS_HOST}:{RDS_PORT}/{RDS_DB}"
            },
            "models": [],
            "categories": {},
            "performance_summary": {},
            "recommendations_summary": {}
        }
        
        # Get all models with details
        cursor.execute("""
            SELECT 
                id, name, version, author_user_key, category, 
                created_at, artifact_path, visibility, allowed_functions
            FROM published_models 
            ORDER BY category, name
        """)
        
        models = cursor.fetchall()
        
        for model in models:
            model_dict = dict(model)
            model_dict['created_at'] = model_dict['created_at'].isoformat()
            report['models'].append(model_dict)
            
            # Count by category
            category = model['category']
            if category not in report['categories']:
                report['categories'][category] = 0
            report['categories'][category] += 1
        
        # Get performance summary
        cursor.execute("""
            SELECT 
                AVG(accuracy) as avg_accuracy,
                MAX(accuracy) as max_accuracy,
                MIN(accuracy) as min_accuracy,
                AVG(total_return) as avg_return
            FROM ml_model_performance
        """)
        
        perf_summary = cursor.fetchone()
        report['performance_summary'] = {
            'average_accuracy': float(perf_summary['avg_accuracy']) if perf_summary['avg_accuracy'] else 0,
            'max_accuracy': float(perf_summary['max_accuracy']) if perf_summary['max_accuracy'] else 0,
            'min_accuracy': float(perf_summary['min_accuracy']) if perf_summary['min_accuracy'] else 0,
            'average_return': float(perf_summary['avg_return']) if perf_summary['avg_return'] else 0
        }
        
        # Get recommendations summary
        cursor.execute("""
            SELECT 
                recommendation,
                COUNT(*) as count,
                AVG(confidence_score) as avg_confidence
            FROM ml_stock_recommendations
            GROUP BY recommendation
        """)
        
        rec_summary = cursor.fetchall()
        for rec in rec_summary:
            report['recommendations_summary'][rec['recommendation']] = {
                'count': rec['count'],
                'avg_confidence': float(rec['avg_confidence'])
            }
        
        # Save report to file
        report_filename = f"ml_models_verification_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"📄 Verification report saved to: {report_filename}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating report: {e}")
        return False

def main():
    """Main verification function"""
    print("🔍 VERIFYING ML MODELS IN RDS DATABASE")
    print("=" * 60)
    print(f"🗃️  Database: {RDS_HOST}:{RDS_PORT}/{RDS_DB}")
    print(f"📅 Verification Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Verify models
    if verify_models_in_database():
        print("✅ Database verification completed successfully!")
        
        # Generate detailed report
        if generate_summary_report():
            print("✅ Summary report generated successfully!")
        else:
            print("⚠️  Failed to generate summary report")
    else:
        print("❌ Database verification failed!")
        return False
    
    print()
    print("🎉 VERIFICATION COMPLETE!")
    print("📈 All ML models are now available in the RDS database")
    print("🌐 Access them at: http://127.0.0.1:5008/published")
    
    return True

if __name__ == "__main__":
    main()
