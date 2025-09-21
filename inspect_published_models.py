import os
from sqlalchemy import text, create_engine
from config import current_config

DB_URL = getattr(current_config, 'SQLALCHEMY_DATABASE_URI', 'sqlite:///investment_research.db')

def main():
    print('Using DB:', DB_URL)
    engine = create_engine(DB_URL)
    with engine.connect() as conn:
        try:
            res = conn.execute(text('PRAGMA table_info(published_models)'))
            cols = [r[1] for r in res]
            print('published_models columns:', cols)
        except Exception as e:
            print('Error introspecting published_models:', e)
            return
        if 'category' in cols:
            print('category column present ✅')
        else:
            print('category column MISSING ❌')
            print('Run app once or execute add_category_column.py after tables exist.')

if __name__ == '__main__':
    main()
