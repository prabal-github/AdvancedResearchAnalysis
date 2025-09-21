"""
Database Query Adapter for ML Models
Routes ML model queries to PostgreSQL while keeping other queries on SQLite
"""

from ml_database_config import MLSession, get_ml_session
from flask import current_app
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker

class MLModelQueryAdapter:
    """
    Adapter to route ML model related queries to PostgreSQL
    while keeping other queries on SQLite
    """
    
    def __init__(self):
        self.ml_session = None
    
    def get_ml_session(self):
        """Get or create ML database session"""
        if not self.ml_session:
            self.ml_session = get_ml_session()
        return self.ml_session
    
    def execute_ml_query(self, model_class, operation, *args, **kwargs):
        """
        Execute a query on the ML database (PostgreSQL)
        
        Args:
            model_class: The model class (PublishedModel, MLModelResult, etc.)
            operation: The operation string ('filter', 'get', 'all', etc.)
            *args, **kwargs: Arguments for the operation
        """
        try:
            session = self.get_ml_session()
            
            # Create query on ML session
            if operation == 'query':
                return session.query(model_class)
            elif operation == 'get':
                return session.query(model_class).get(args[0])
            elif operation == 'filter':
                return session.query(model_class).filter(*args, **kwargs)
            elif operation == 'filter_by':
                return session.query(model_class).filter_by(**kwargs)
            elif operation == 'all':
                return session.query(model_class).all()
            else:
                # Default to building query and letting caller add operations
                return session.query(model_class)
                
        except Exception as e:
            current_app.logger.error(f"ML Query error: {e}")
            # Fallback to original SQLite query
            return getattr(model_class, 'query', None)
    
    def save_to_ml_db(self, instance):
        """Save an instance to ML database"""
        try:
            session = self.get_ml_session()
            session.add(instance)
            session.commit()
            return True
        except Exception as e:
            current_app.logger.error(f"ML Save error: {e}")
            session.rollback()
            return False
    
    def close_ml_session(self):
        """Close ML database session"""
        if self.ml_session:
            self.ml_session.close()
            self.ml_session = None

# Global adapter instance
ml_adapter = MLModelQueryAdapter()

def route_query_to_ml_db(model_class, operation='query', *args, **kwargs):
    """
    Route a query to ML database if it's an ML model class
    
    Args:
        model_class: The model class
        operation: Query operation
        *args, **kwargs: Query arguments
    
    Returns:
        Query object or result
    """
    # List of model classes that should use PostgreSQL
    ML_MODEL_CLASSES = [
        'PublishedModel',
        'MLModelResult', 
        'ScriptExecution',
        'PublishedModelRunHistory',
        'PublishedModelEvaluation',
        'PublishedModelSubscription',
        'PublishedModelWatchlist',
        'PublishedModelChangeAlert'
    ]
    
    model_name = model_class.__name__ if hasattr(model_class, '__name__') else str(model_class)
    
    if model_name in ML_MODEL_CLASSES:
        return ml_adapter.execute_ml_query(model_class, operation, *args, **kwargs)
    else:
        # Use original SQLite query for non-ML models
        if operation == 'query':
            return getattr(model_class, 'query', None)
        elif operation == 'get':
            return getattr(model_class, 'query', None).get(args[0])
        elif operation == 'filter':
            return getattr(model_class, 'query', None).filter(*args, **kwargs)
        elif operation == 'filter_by':
            return getattr(model_class, 'query', None).filter_by(**kwargs)
        else:
            return getattr(model_class, 'query', None)

# Export functions
__all__ = ['ml_adapter', 'route_query_to_ml_db', 'MLModelQueryAdapter']