import psycopg2
from datetime import datetime
import os

class Database:
    def __init__(self):
        self.conn = psycopg2.connect(os.environ['DATABASE_URL'])
        self.create_tables()

    def create_tables(self):
        with self.conn.cursor() as cur:
            # Users jadvali
            cur.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT PRIMARY KEY,
                    username VARCHAR(255),
                    balance DECIMAL(10,2) DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tasks jadvali
            cur.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    id SERIAL PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    description TEXT,
                    reward DECIMAL(10,2) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE
                )
            ''')
            
            # User tasks jadvali
            cur.execute('''
                CREATE TABLE IF NOT EXISTS user_tasks (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT REFERENCES users(user_id),
                    task_id INTEGER REFERENCES tasks(id),
                    status VARCHAR(50) DEFAULT 'pending',
                    proof_text TEXT,
                    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    reviewed_at TIMESTAMP,
                    admin_comment TEXT
                )
            ''')
            
            # Payouts jadvali
            cur.execute('''
                CREATE TABLE IF NOT EXISTS payouts (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT REFERENCES users(user_id),
                    amount DECIMAL(10,2) NOT NULL,
                    usdt_address VARCHAR(255) NOT NULL,
                    status VARCHAR(50) DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    processed_at TIMESTAMP,
                    tx_hash VARCHAR(255)
                )
            ''')
            
            self.conn.commit()

    def get_user(self, user_id):
        with self.conn.cursor() as cur:
            cur.execute('SELECT * FROM users WHERE user_id = %s', (user_id,))
            return cur.fetchone()

    def create_user(self, user_id, username):
        with self.conn.cursor() as cur:
            cur.execute('''
                INSERT INTO users (user_id, username) 
                VALUES (%s, %s) 
                ON CONFLICT (user_id) DO UPDATE SET username = EXCLUDED.username
            ''', (user_id, username))
            self.conn.commit()

    def get_tasks(self):
        with self.conn.cursor() as cur:
            cur.execute('SELECT * FROM tasks WHERE is_active = TRUE')
            return cur.fetchall()

    # ... boshqa database metodlari
