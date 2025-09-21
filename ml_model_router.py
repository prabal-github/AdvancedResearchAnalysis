"""
ML Model Database Router
Automatically routes ML model database operations to PostgreSQL
"""

from functools import wraps
from ml_database_config import MLSession, get_ml_session, ml_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import inspect
import logging

# Create a separate session class for ML models
MLModelSession = sessionmaker(bind=ml_engine)

class MLModelMixin:
    """
    Mixin class that routes database operations to PostgreSQL for ML models
    """
    
    @classmethod
    def get_ml_query(cls):
        """Get query object using ML database session"""
        try:
            session = MLModelSession()
            return session.query(cls)
        except Exception as e:
            logging.error(f"ML Query error for {cls.__name__}: {e}")
            # Fallback to original query
            return cls.query if hasattr(cls, 'query') else None
    
    @classmethod
    def ml_get(cls, primary_key):
        """Get single record by primary key from ML database"""
        try:
            session = MLModelSession()
            return session.query(cls).get(primary_key)
        except Exception as e:
            logging.error(f"ML Get error for {cls.__name__}: {e}")
            return cls.query.get(primary_key) if hasattr(cls, 'query') else None
    
    @classmethod
    def ml_filter(cls, *args, **kwargs):
        """Filter records from ML database"""
        try:
            session = MLModelSession()
            if args:
                return session.query(cls).filter(*args)
            else:
                return session.query(cls).filter_by(**kwargs)
        except Exception as e:
            logging.error(f"ML Filter error for {cls.__name__}: {e}")
            if hasattr(cls, 'query'):
                if args:
                    return cls.query.filter(*args)
                else:
                    return cls.query.filter_by(**kwargs)
            return None
    
    @classmethod
    def ml_filter_by(cls, **kwargs):
        """Filter records by attributes from ML database"""
        return cls.ml_filter(**kwargs)
    
    def save_to_ml_db(self):
        """Save this instance to ML database"""
        try:
            session = MLModelSession()
            session.add(self)
            session.commit()
            session.close()
            return True
        except Exception as e:
            logging.error(f"ML Save error for {self.__class__.__name__}: {e}")
            session.rollback()
            session.close()
            return False

def use_ml_database(model_class):
    """
    Decorator to automatically route model operations to ML database
    """
    
    # Store original query attribute
    original_query = getattr(model_class, 'query', None)
    
    # Replace query with ML database query
    @property
    def ml_query(cls):
        try:
            session = MLModelSession()
            return session.query(model_class)
        except Exception as e:
            logging.error(f"ML Query fallback for {model_class.__name__}: {e}")
            return original_query
    
    # Add ML query as class property
    setattr(model_class, 'query', ml_query)
    
    # Add MLModelMixin methods
    for attr_name in dir(MLModelMixin):
        if not attr_name.startswith('_'):
            attr = getattr(MLModelMixin, attr_name)
            if callable(attr):
                setattr(model_class, attr_name, classmethod(attr.__func__) if hasattr(attr, '__func__') else attr)
    
    return model_class

def create_ml_tables():
    """Create all ML model tables in PostgreSQL database"""
    try:
        # Import model classes
        from app import PublishedModel, MLModelResult, ScriptExecution
        
        # Create tables using ML engine
        from sqlalchemy import MetaData
        metadata = MetaData()
        
        # Bind models to ML engine
        for model_cls in [PublishedModel, MLModelResult, ScriptExecution]:
            if hasattr(model_cls, '__table__'):
                model_cls.__table__.create(bind=ml_engine, checkfirst=True)
        
        print("✅ ML tables created in PostgreSQL")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create ML tables: {e}")
        return False

# Export the decorator and functions
__all__ = ['use_ml_database', 'MLModelMixin', 'create_ml_tables', 'MLModelSession']