import os
from dotenv import load_dotenv
import psycopg2
from typing import Optional, Any
from psycopg2.extras import DictCursor

# Load environment variables from .env file
load_dotenv()

def get_conn():
    """
    Create and return a database connection.
    
    Environment variables used:
    - DB_HOST: Database host (default: localhost)
    - DB_PORT: Database port (default: 5432)
    - DB_NAME: Database name (default: health_assistant)
    - DB_USER: Database user (default: postgres)
    - DB_PASSWORD: Database password (default: postgres)
    """
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', '5432'),
        dbname=os.getenv('DB_NAME', 'health_assistant'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'postgres')
    )
    conn.autocommit = True
    return conn

def init_db():
    """Initialize the database with required tables."""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            # Create prompts table if it doesn't exist
            cur.execute("""
                CREATE TABLE IF NOT EXISTS ai_prompts (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) UNIQUE NOT NULL,
                    prompt TEXT NOT NULL,
                    meta JSONB,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create a trigger to update the updated_at timestamp
            cur.execute("""
                CREATE OR REPLACE FUNCTION update_updated_at_column()
                RETURNS TRIGGER AS $$
                BEGIN
                    NEW.updated_at = NOW();
                    RETURN NEW;
                END;
                $$ LANGUAGE plpgsql;
            """)
            
            cur.execute("""
                DROP TRIGGER IF EXISTS update_ai_prompts_updated_at ON ai_prompts;
                CREATE TRIGGER update_ai_prompts_updated_at
                BEFORE UPDATE ON ai_prompts
                FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
            """)
            
        conn.commit()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    init_db()
