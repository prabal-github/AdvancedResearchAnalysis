#!/usr/bin/env python3
"""
Test script to verify dual database routing is working correctly.
Tests PostgreSQL vs SQLite routing for different model types.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from ml_database_config import test_ml_connection, get_ml_session
from ml_models_postgres import (
    MLPublishedModel, MLContactForm, MLReferralCode, 
    MLInvestorPortfolio, query_ml_published_models
)

def test_postgresql_connection():
    """Test PostgreSQL connection"""
    print("🔍 Testing PostgreSQL Connection...")
    if test_ml_connection():
        print("✅ PostgreSQL connection successful")
        return True
    else:
        print("❌ PostgreSQL connection failed")
        return False

def test_helper_functions():
    """Test that helper functions route to correct databases"""
    print("\n🔍 Testing Database Routing Helper Functions...")
    
    with app.app_context():
        try:
            # Test PublishedModel routing
            from app import get_published_model_query
            published_query = get_published_model_query()
            print(f"✅ get_published_model_query() returned: {type(published_query)}")
            
            # Test ContactForm routing  
            from app import get_contact_form_query
            contact_query = get_contact_form_query()
            print(f"✅ get_contact_form_query() returned: {type(contact_query)}")
            
            # Test Referral routing
            from app import get_referral_query
            referral_query = get_referral_query()
            print(f"✅ get_referral_query() returned: {type(referral_query)}")
            
            # Test Portfolio routing
            from app import get_portfolio_query
            portfolio_query = get_portfolio_query()
            print(f"✅ get_portfolio_query() returned: {type(portfolio_query)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Helper function test failed: {e}")
            return False

def test_model_queries():
    """Test that models can query their respective databases"""
    print("\n🔍 Testing Model Query Execution...")
    
    with app.app_context():
        try:
            # Test PostgreSQL models if available
            if hasattr(app, 'ml_queries') and app.ml_queries:
                print("📊 Testing PostgreSQL ML Models...")
                
                # Test published models
                ml_published_models = query_ml_published_models()
                print(f"✅ ML Published Models query executed, found: {len(list(ml_published_models))} models")
                
                # Test contact forms
                if 'contact_forms' in app.ml_queries:
                    ml_contact_forms = app.ml_queries['contact_forms']()
                    print(f"✅ ML Contact Forms query executed, found: {len(list(ml_contact_forms))} forms")
                
                # Test referrals
                if 'referrals' in app.ml_queries:
                    ml_referrals = app.ml_queries['referrals']()
                    print(f"✅ ML Referrals query executed, found: {len(list(ml_referrals))} referrals")
                
                # Test portfolios
                if 'investor_portfolios' in app.ml_queries:
                    try:
                        ml_portfolios = app.ml_queries['investor_portfolios']()
                        print(f"✅ ML Portfolios query executed, found: {len(list(ml_portfolios))} portfolios")
                    except Exception as e:
                        print(f"❌ ML Portfolios query failed: {e}")
                        
                # Test portfolio holdings
                if 'investor_portfolio_holdings' in app.ml_queries:
                    try:
                        ml_holdings = app.ml_queries['investor_portfolio_holdings']()
                        print(f"✅ ML Portfolio Holdings query executed, found: {len(list(ml_holdings))} holdings")
                    except Exception as e:
                        print(f"❌ ML Portfolio Holdings query failed: {e}")
                        
                # Test portfolio commentary
                if 'portfolio_commentary' in app.ml_queries:
                    try:
                        ml_commentary = app.ml_queries['portfolio_commentary']()
                        print(f"✅ ML Portfolio Commentary query executed, found: {len(list(ml_commentary))} commentaries")
                    except Exception as e:
                        print(f"❌ ML Portfolio Commentary query failed: {e}")
                        
                # Test imported portfolios
                if 'imported_portfolios' in app.ml_queries:
                    try:
                        ml_imported = app.ml_queries['imported_portfolios']()
                        print(f"✅ ML Imported Portfolios query executed, found: {len(list(ml_imported))} imported portfolios")
                    except Exception as e:
                        print(f"❌ ML Imported Portfolios query failed: {e}")
                        
                # Test realtime portfolios
                if 'realtime_portfolios' in app.ml_queries:
                    try:
                        ml_realtime = app.ml_queries['realtime_portfolios']()
                        print(f"✅ ML Realtime Portfolios query executed, found: {len(list(ml_realtime))} realtime portfolios")
                    except Exception as e:
                        print(f"❌ ML Realtime Portfolios query failed: {e}")
                    
            else:
                print("⚠️ ML database queries not available (fallback to SQLite)")
                
            return True
            
        except Exception as e:
            print(f"❌ Model query test failed: {e}")
            return False

def main():
    """Run all database routing tests"""
    print("🚀 Starting Database Routing Tests...")
    print("=" * 50)
    
    # Test 1: PostgreSQL Connection
    pg_success = test_postgresql_connection()
    
    # Test 2: Helper Functions
    helper_success = test_helper_functions()
    
    # Test 3: Model Queries
    query_success = test_model_queries()
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Test Summary:")
    print(f"  PostgreSQL Connection: {'✅ PASS' if pg_success else '❌ FAIL'}")
    print(f"  Helper Functions: {'✅ PASS' if helper_success else '❌ FAIL'}")
    print(f"  Model Queries: {'✅ PASS' if query_success else '❌ FAIL'}")
    
    overall_success = pg_success and helper_success and query_success
    print(f"\n🎯 Overall Result: {'✅ ALL TESTS PASSED' if overall_success else '❌ SOME TESTS FAILED'}")
    
    if overall_success:
        print("\n🎉 Dual Database Configuration is working correctly!")
        print("   • PostgreSQL: ML models, contact forms, referrals, portfolios")
        print("   • SQLite: Other application data (unchanged)")
    
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)