"""
Database Query Router Utility
Routes ML model database operations to PostgreSQL while keeping others on SQLite
"""

from ml_model_router import MLModelSession
import logging

def get_ml_model_query(model_class):
    """
    Get query object for ML models, routing to PostgreSQL if available
    
    Args:
        model_class: The model class (PublishedModel, MLModelResult, etc.)
    
    Returns:
        Query object (PostgreSQL if available, SQLite as fallback)
    """
    ml_model_classes = {
        'PublishedModel', 'MLModelResult', 'ScriptExecution', 
        'PublishedModelRunHistory', 'PublishedModelEvaluation',
        'PublishedModelSubscription', 'PublishedModelWatchlist',
        'PublishedModelChangeAlert', 'MLModelAnalytics', 'AIModelAlert'
    }
    
    model_name = model_class.__name__ if hasattr(model_class, '__name__') else str(model_class)
    
    # Route ML models to PostgreSQL if available
    if model_name in ml_model_classes:
        try:
            from app import ML_DATABASE_AVAILABLE
            if ML_DATABASE_AVAILABLE:
                session = MLModelSession()
                return session.query(model_class)
        except Exception as e:
            logging.warning(f"ML database query failed for {model_name}, using SQLite: {e}")
    
    # Fallback to original SQLite query
    return getattr(model_class, 'query', None)

def save_ml_model_instance(instance):
    """
    Save ML model instance to PostgreSQL if available, SQLite as fallback
    
    Args:
        instance: Model instance to save
    
    Returns:
        bool: Success status
    """
    ml_model_classes = {
        'PublishedModel', 'MLModelResult', 'ScriptExecution', 
        'PublishedModelRunHistory', 'PublishedModelEvaluation',
        'PublishedModelSubscription', 'PublishedModelWatchlist',
        'PublishedModelChangeAlert', 'MLModelAnalytics', 'AIModelAlert'
    }
    
    model_name = instance.__class__.__name__
    
    # Route ML models to PostgreSQL if available
    if model_name in ml_model_classes:
        try:
            from app import ML_DATABASE_AVAILABLE
            if ML_DATABASE_AVAILABLE:
                session = MLModelSession()
                session.add(instance)
                session.commit()
                session.close()
                return True
        except Exception as e:
            logging.warning(f"ML database save failed for {model_name}, using SQLite: {e}")
            if 'session' in locals():
                session.rollback()
                session.close()
    
    # Fallback to original SQLite save
    try:
        from app import db
        db.session.add(instance)
        db.session.commit()
        return True
    except Exception as e:
        logging.error(f"SQLite save failed for {model_name}: {e}")
        db.session.rollback()
        return False

# Monkey patch the query method for ML model classes
def apply_ml_database_routing():
    """Apply ML database routing to model classes"""
    try:
        from app import (PublishedModel, MLModelResult, ScriptExecution, 
                        PublishedModelRunHistory, PublishedModelEvaluation,
                        PublishedModelSubscription, PublishedModelWatchlist,
                        PublishedModelChangeAlert)
        
        ml_classes = [
            PublishedModel, MLModelResult, ScriptExecution,
            PublishedModelRunHistory, PublishedModelEvaluation, 
            PublishedModelSubscription, PublishedModelWatchlist,
            PublishedModelChangeAlert
        ]
        
        for cls in ml_classes:
            # Store original query
            original_query = cls.query
            
            # Create routed query property
            def make_ml_query(model_class):
                def ml_query_property():
                    return get_ml_model_query(model_class)
                return property(ml_query_property)
            
            # Replace query property
            cls.query = make_ml_query(cls)
            
        print("✅ ML database routing applied to model classes")
        
    except Exception as e:
        print(f"⚠️ Failed to apply ML database routing: {e}")

# Export functions
__all__ = ['get_ml_model_query', 'save_ml_model_instance', 'apply_ml_database_routing']