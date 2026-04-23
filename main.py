# app.py
import streamlit as st
import pandas as pd
import sqlite3
import hashlib
import json
from datetime import datetime, date, timedelta
import plotly.express as px
import plotly.graph_objects as go
from streamlit_option_menu import option_menu
import re
import random
import string
import base64
import io
import csv
import os

# Try to import reportlab, but provide fallback if not available
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

# Page configuration
st.set_page_config(
    page_title="Incredible Studios Management System",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for branding
def apply_custom_css(primary_color="#1D2E26", accent_color="#8FD65A", secondary_accent="#E9C46A", bg_color="#F8F3ED", text_color="#2F2F3C"):
    st.markdown(f"""
    <style>
        /* Main container styling */
        .stApp {{
            background-color: {bg_color};
        }}
        
        /* Sidebar styling */
        .css-1d391kg, .css-12oz5g0 {{
            background-color: {primary_color};
        }}
        
        /* Headers */
        h1, h2, h3, h4, h5, h6 {{
            color: {primary_color} !important;
            font-weight: 600 !important;
        }}
        
        /* Buttons */
        .stButton > button {{
            background-color: {accent_color};
            color: {primary_color};
            border: none;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            font-weight: 600;
            transition: all 0.3s ease;
        }}
        
        .stButton > button:hover {{
            background-color: {secondary_accent};
            color: {primary_color};
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}
        
        /* Metric cards */
        .metric-card {{
            background-color: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            border-left: 4px solid {accent_color};
            margin-bottom: 1rem;
        }}
        
        /* Custom scrollbar */
        ::-webkit-scrollbar {{
            width: 8px;
            height: 8px;
        }}
        
        ::-webkit-scrollbar-track {{
            background: {bg_color};
        }}
        
        ::-webkit-scrollbar-thumb {{
            background: {accent_color};
            border-radius: 4px;
        }}
        
        /* Task card styling */
        .task-card {{
            background: white;
            border-radius: 10px;
            padding: 1rem;
            margin-bottom: 0.5rem;
            border-left: 3px solid {accent_color};
            transition: all 0.3s ease;
        }}
        
        .task-card:hover {{
            transform: translateX(5px);
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        
        /* Status badges */
        .status-badge {{
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
        }}
        
        .status-high {{
            background-color: #FFE5E5;
            color: #FF4444;
        }}
        
        .status-medium {{
            background-color: #FFF3E0;
            color: #FF9800;
        }}
        
        .status-low {{
            background-color: #E8F5E9;
            color: #4CAF50;
        }}
        
        /* Dataframe styling */
        .dataframe {{
            background-color: white;
            border-radius: 8px;
            overflow: hidden;
        }}
        
        /* Input fields */
        .stTextInput > div > div > input, 
        .stTextArea > div > div > textarea,
        .stSelectbox > div > div,
        .stDateInput > div > div > input {{
            border-radius: 8px;
            border: 1px solid #ddd;
        }}
    </style>
    """, unsafe_allow_html=True)

# Database migration helper
def migrate_database(conn):
    """Add missing columns to existing tables"""
    cursor = conn.cursor()
    
    # Check and add missing columns to users table
    cursor.execute("PRAGMA table_info(users)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'phone' not in columns:
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN phone TEXT")
        except:
            pass
    
    if 'department' not in columns:
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN department TEXT")
        except:
            pass
    
    if 'is_active' not in columns:
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT 1")
        except:
            pass
    
    if 'last_login' not in columns:
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN last_login TIMESTAMP")
        except:
            pass
    
    # Check and add missing columns to projects table
    cursor.execute("PRAGMA table_info(projects)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'client_email' not in columns:
        try:
            cursor.execute("ALTER TABLE projects ADD COLUMN client_email TEXT")
        except:
            pass
    
    if 'client_phone' not in columns:
        try:
            cursor.execute("ALTER TABLE projects ADD COLUMN client_phone TEXT")
        except:
            pass
    
    if 'priority' not in columns:
        try:
            cursor.execute("ALTER TABLE projects ADD COLUMN priority TEXT DEFAULT 'Medium'")
        except:
            pass
    
    if 'actual_completion_date' not in columns:
        try:
            cursor.execute("ALTER TABLE projects ADD COLUMN actual_completion_date DATE")
        except:
            pass
    
    if 'deliverables' not in columns:
        try:
            cursor.execute("ALTER TABLE projects ADD COLUMN deliverables TEXT")
        except:
            pass
    
    if 'project_manager' not in columns:
        try:
            cursor.execute("ALTER TABLE projects ADD COLUMN project_manager TEXT")
        except:
            pass
    
    if 'team_members' not in columns:
        try:
            cursor.execute("ALTER TABLE projects ADD COLUMN team_members TEXT")
        except:
            pass
    
    # Check and add missing columns to transactions table
    cursor.execute("PRAGMA table_info(transactions)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'subcategory' not in columns:
        try:
            cursor.execute("ALTER TABLE transactions ADD COLUMN subcategory TEXT")
        except:
            pass
    
    if 'payment_method' not in columns:
        try:
            cursor.execute("ALTER TABLE transactions ADD COLUMN payment_method TEXT")
        except:
            pass
    
    if 'invoice_number' not in columns:
        try:
            cursor.execute("ALTER TABLE transactions ADD COLUMN invoice_number TEXT")
        except:
            pass
    
    if 'tax_amount' not in columns:
        try:
            cursor.execute("ALTER TABLE transactions ADD COLUMN tax_amount REAL DEFAULT 0")
        except:
            pass
    
    if 'receipt_url' not in columns:
        try:
            cursor.execute("ALTER TABLE transactions ADD COLUMN receipt_url TEXT")
        except:
            pass
    
    # Check and add missing columns to social_accounts table
    cursor.execute("PRAGMA table_info(social_accounts)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'category' not in columns:
        try:
            cursor.execute("ALTER TABLE social_accounts ADD COLUMN category TEXT")
        except:
            pass
    
    if 'followers_count' not in columns:
        try:
            cursor.execute("ALTER TABLE social_accounts ADD COLUMN followers_count INTEGER")
        except:
            pass
    
    if 'last_updated' not in columns:
        try:
            cursor.execute("ALTER TABLE social_accounts ADD COLUMN last_updated TIMESTAMP")
        except:
            pass
    
    conn.commit()

# Database setup with enhanced tables
def init_database():
    # Check if database exists and needs migration
    db_exists = os.path.exists('incredible_studios.db')
    
    conn = sqlite3.connect('incredible_studios.db')
    c = conn.cursor()
    
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL,
        full_name TEXT,
        email TEXT,
        phone TEXT,
        department TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_login TIMESTAMP,
        is_active BOOLEAN DEFAULT 1
    )''')
    
    # System settings table
    c.execute('''CREATE TABLE IF NOT EXISTS system_settings (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Financial transactions table
    c.execute('''CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date DATE NOT NULL,
        type TEXT NOT NULL,
        category TEXT NOT NULL,
        subcategory TEXT,
        description TEXT,
        amount REAL NOT NULL,
        client_name TEXT,
        project_name TEXT,
        payment_method TEXT,
        invoice_number TEXT,
        tax_amount REAL DEFAULT 0,
        receipt_url TEXT,
        created_by TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Social media accounts table
    c.execute('''CREATE TABLE IF NOT EXISTS social_accounts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        platform TEXT NOT NULL,
        username TEXT NOT NULL,
        email TEXT,
        password TEXT NOT NULL,
        profile_url TEXT,
        notes TEXT,
        category TEXT,
        followers_count INTEGER,
        created_by TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_updated TIMESTAMP
    )''')
    
    # Projects table with enhanced fields
    c.execute('''CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        client TEXT NOT NULL,
        client_email TEXT,
        client_phone TEXT,
        status TEXT NOT NULL,
        priority TEXT DEFAULT 'Medium',
        budget REAL,
        spent REAL DEFAULT 0,
        start_date DATE,
        deadline DATE,
        actual_completion_date DATE,
        description TEXT,
        deliverables TEXT,
        project_manager TEXT,
        team_members TEXT,
        created_by TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Tasks table
    c.execute('''CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER,
        title TEXT NOT NULL,
        description TEXT,
        assigned_to TEXT,
        priority TEXT DEFAULT 'Medium',
        status TEXT DEFAULT 'Pending',
        due_date DATE,
        completed_date DATE,
        estimated_hours REAL,
        actual_hours REAL,
        created_by TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (project_id) REFERENCES projects (id)
    )''')
    
    # Documents table
    c.execute('''CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        file_name TEXT,
        file_data BLOB,
        file_type TEXT,
        project_id INTEGER,
        category TEXT,
        uploaded_by TEXT,
        uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (project_id) REFERENCES projects (id)
    )''')
    
    # Client communications table
    c.execute('''CREATE TABLE IF NOT EXISTS communications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_name TEXT NOT NULL,
        project_id INTEGER,
        communication_type TEXT,
        subject TEXT,
        message TEXT,
        direction TEXT,
        date_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        follow_up_date DATE,
        status TEXT DEFAULT 'Open',
        recorded_by TEXT,
        FOREIGN KEY (project_id) REFERENCES projects (id)
    )''')
    
    # Expense claims table
    c.execute('''CREATE TABLE IF NOT EXISTS expense_claims (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_name TEXT NOT NULL,
        date DATE NOT NULL,
        category TEXT NOT NULL,
        description TEXT,
        amount REAL NOT NULL,
        receipt_url TEXT,
        status TEXT DEFAULT 'Pending',
        approved_by TEXT,
        approval_date DATE,
        rejection_reason TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Notifications table
    c.execute('''CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        title TEXT NOT NULL,
        message TEXT NOT NULL,
        type TEXT,
        is_read BOOLEAN DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )''')
    
    # Time tracking table
    c.execute('''CREATE TABLE IF NOT EXISTS time_entries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        project_id INTEGER,
        task_id INTEGER,
        date DATE NOT NULL,
        hours REAL NOT NULL,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (project_id) REFERENCES projects (id)
    )''')
    
    # Run migration for existing database
    if db_exists:
        try:
            migrate_database(conn)
        except Exception as e:
            st.warning(f"Database migration warning: {e}")
    
    # Insert default admin user if not exists (checking existing columns)
    default_password = hashlib.sha256("admin123".encode()).hexdigest()
    
    # Check if admin already exists
    c.execute("SELECT * FROM users WHERE username = 'admin'")
    admin_exists = c.fetchone()
    
    if not admin_exists:
        try:
            # Try with department column
            c.execute("INSERT INTO users (username, password, role, full_name, email, department) VALUES (?, ?, ?, ?, ?, ?)",
                      ("admin", default_password, "admin", "System Administrator", "admin@incrediblestudios.com", "Management"))
        except sqlite3.OperationalError:
            # Fallback without department column
            c.execute("INSERT INTO users (username, password, role, full_name, email) VALUES (?, ?, ?, ?, ?)",
                      ("admin", default_password, "admin", "System Administrator", "admin@incrediblestudios.com"))
    
    # Insert default settings
    default_settings = {
        "studio_name": "Incredible Studios",
        "brand_primary": "#1D2E26",
        "brand_accent": "#8FD65A",
        "brand_secondary": "#E9C46A",
        "brand_background": "#F8F3ED",
        "brand_text": "#2F2F3C",
        "login_attempts": "0",
        "last_login": "",
        "tax_rate": "10",
        "currency_symbol": "$",
        "enable_notifications": "true",
        "smtp_server": "",
        "smtp_port": "587",
        "smtp_email": "",
        "smtp_password": "",
        "backup_frequency": "weekly"
    }
    
    for key, value in default_settings.items():
        c.execute("INSERT OR IGNORE INTO system_settings (key, value) VALUES (?, ?)", (key, value))
    
    conn.commit()
    return conn

# Authentication functions
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(stored_password, provided_password):
    return stored_password == hash_password(provided_password)

def login_user(username, password):
    conn = sqlite3.connect('incredible_studios.db')
    c = conn.cursor()
    try:
        c.execute("SELECT * FROM users WHERE username = ? AND is_active = 1", (username,))
        user = c.fetchone()
        if user and verify_password(user[2], password):
            # Update last login
            try:
                c.execute("UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?", (user[0],))
            except:
                pass  # Skip if column doesn't exist
            conn.commit()
            conn.close()
            return {"id": user[0], "username": user[1], "role": user[3], "full_name": user[4], "email": user[5] if len(user) > 5 else ""}
    except Exception as e:
        st.error(f"Login error: {e}")
    conn.close()
    return None

def get_all_users():
    conn = sqlite3.connect('incredible_studios.db')
    c = conn.cursor()
    try:
        c.execute("SELECT id, username, role, full_name, email, phone, department, created_at, last_login, is_active FROM users")
        users = c.fetchall()
    except sqlite3.OperationalError:
        # Fallback for older database schema
        c.execute("SELECT id, username, role, full_name, email, '', '', created_at, '', 1 FROM users")
        users = c.fetchall()
    conn.close()
    return users

def add_user(username, password, role, full_name, email, phone, department):
    conn = sqlite3.connect('incredible_studios.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password, role, full_name, email, phone, department) VALUES (?, ?, ?, ?, ?, ?, ?)",
                  (username, hash_password(password), role, full_name, email, phone, department))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    except sqlite3.OperationalError:
        # Fallback for older schema
        try:
            c.execute("INSERT INTO users (username, password, role, full_name, email) VALUES (?, ?, ?, ?, ?)",
                      (username, hash_password(password), role, full_name, email))
            conn.commit()
            return True
        except:
            return False
    finally:
        conn.close()

def delete_user(user_id):
    conn = sqlite3.connect('incredible_studios.db')
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE id = ? AND username != 'admin'", (user_id,))
    conn.commit()
    conn.close()

def update_user_role(user_id, new_role):
    conn = sqlite3.connect('incredible_studios.db')
    c = conn.cursor()
    c.execute("UPDATE users SET role = ? WHERE id = ?", (new_role, user_id))
    conn.commit()
    conn.close()

def toggle_user_status(user_id, is_active):
    conn = sqlite3.connect('incredible_studios.db')
    c = conn.cursor()
    try:
        c.execute("UPDATE users SET is_active = ? WHERE id = ?", (is_active, user_id))
        conn.commit()
    except:
        pass  # Skip if column doesn't exist
    conn.close()

def change_password(username, old_password, new_password):
    conn = sqlite3.connect('incredible_studios.db')
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE username = ?", (username,))
    result = c.fetchone()
    
    if result and verify_password(result[0], old_password):
        c.execute("UPDATE users SET password = ? WHERE username = ?", (hash_password(new_password), username))
        conn.commit()
        conn.close()
        return True
    conn.close()
    return False

def reset_user_password(username):
    new_password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    conn = sqlite3.connect('incredible_studios.db')
    c = conn.cursor()
    c.execute("UPDATE users SET password = ? WHERE username = ?", (hash_password(new_password), username))
    conn.commit()
    conn.close()
    return new_password

# Settings functions
def get_system_settings():
    conn = sqlite3.connect('incredible_studios.db')
    c = conn.cursor()
    c.execute("SELECT key, value FROM system_settings")
    settings = dict(c.fetchall())
    conn.close()
    return settings

def update_system_setting(key, value):
    conn = sqlite3.connect('incredible_studios.db')
    c = conn.cursor()
    c.execute("UPDATE system_settings SET value = ?, updated_at = CURRENT_TIMESTAMP WHERE key = ?", (value, key))
    conn.commit()
    conn.close()

# Financial functions with enhancements
def add_transaction(date, type, category, subcategory, description, amount, client_name, project_name, 
                   payment_method, invoice_number, tax_amount, receipt_url, created_by):
    conn = sqlite3.connect('incredible_studios.db')
    c = conn.cursor()
    c.execute("""INSERT INTO transactions 
                 (date, type, category, subcategory, description, amount, client_name, project_name, 
                  payment_method, invoice_number, tax_amount, receipt_url, created_by) 
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
              (date, type, category, subcategory, description, amount, client_name, project_name,
               payment_method, invoice_number, tax_amount, receipt_url, created_by))
    conn.commit()
    conn.close()

def get_transactions(filters=None):
    conn = sqlite3.connect('incredible_studios.db')
    query = "SELECT * FROM transactions ORDER BY date DESC"
    if filters and 'start_date' in filters and 'end_date' in filters:
        query = f"SELECT * FROM transactions WHERE date BETWEEN '{filters['start_date']}' AND '{filters['end_date']}' ORDER BY date DESC"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def get_financial_summary():
    df = get_transactions()
    if df.empty:
        return {"total_income": 0, "total_expense": 0, "net_profit": 0, "total_tax": 0}
    
    income = df[df['type'] == 'Income']['amount'].sum()
    expense = df[df['type'] == 'Expense']['amount'].sum()
    tax = df['tax_amount'].sum() if 'tax_amount' in df.columns else 0
    return {"total_income": income, "total_expense": expense, "net_profit": income - expense, "total_tax": tax}

def generate_invoice_number():
    return f"INV-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"

# Social media functions with encryption
def add_social_account(platform, username, email, password, profile_url, notes, category, followers_count, created_by):
    conn = sqlite3.connect('incredible_studios.db')
    c = conn.cursor()
    # Simple encryption (for demo - use proper encryption in production)
    encrypted_password = base64.b64encode(password.encode()).decode()
    try:
        c.execute("""INSERT INTO social_accounts 
                     (platform, username, email, password, profile_url, notes, category, followers_count, created_by, last_updated) 
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                  (platform, username, email, encrypted_password, profile_url, notes, category, followers_count, created_by, datetime.now()))
    except sqlite3.OperationalError:
        # Fallback for older schema
        c.execute("""INSERT INTO social_accounts 
                     (platform, username, email, password, profile_url, notes, created_by) 
                     VALUES (?, ?, ?, ?, ?, ?, ?)""",
                  (platform, username, email, encrypted_password, profile_url, notes, created_by))
    conn.commit()
    conn.close()

def get_social_accounts():
    conn = sqlite3.connect('incredible_studios.db')
    try:
        df = pd.read_sql_query("SELECT * FROM social_accounts ORDER BY platform", conn)
        # Decrypt passwords for display
        if 'password' in df.columns:
            df['password'] = df['password'].apply(lambda x: base64.b64decode(x.encode()).decode() if x else '')
    except:
        df = pd.DataFrame()
    conn.close()
    return df

def delete_social_account(account_id):
    conn = sqlite3.connect('incredible_studios.db')
    c = conn.cursor()
    c.execute("DELETE FROM social_accounts WHERE id = ?", (account_id,))
    conn.commit()
    conn.close()

def update_social_account_followers(account_id, followers_count):
    conn = sqlite3.connect('incredible_studios.db')
    c = conn.cursor()
    try:
        c.execute("UPDATE social_accounts SET followers_count = ?, last_updated = ? WHERE id = ?", 
                  (followers_count, datetime.now(), account_id))
        conn.commit()
    except:
        pass
    conn.close()

# Project functions with enhancements
def add_project(name, client, client_email, client_phone, status, priority, budget, start_date, deadline, 
                description, deliverables, project_manager, team_members, created_by):
    conn = sqlite3.connect('incredible_studios.db')
    c = conn.cursor()
    try:
        c.execute("""INSERT INTO projects 
                     (name, client, client_email, client_phone, status, priority, budget, spent, start_date, deadline, 
                      description, deliverables, project_manager, team_members, created_by) 
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                  (name, client, client_email, client_phone, status, priority, budget, 0, start_date, deadline,
                   description, deliverables, project_manager, team_members, created_by))
    except sqlite3.OperationalError:
        # Fallback for older schema
        c.execute("""INSERT INTO projects 
                     (name, client, status, budget, spent, start_date, deadline, description, created_by) 
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                  (name, client, status, budget, 0, start_date, deadline, description, created_by))
    conn.commit()
    conn.close()

def get_projects(status_filter=None):
    conn = sqlite3.connect('incredible_studios.db')
    try:
        query = "SELECT * FROM projects ORDER BY deadline"
        if status_filter and status_filter != 'All':
            query = f"SELECT * FROM projects WHERE status = '{status_filter}' ORDER BY deadline"
        df = pd.read_sql_query(query, conn)
    except:
        df = pd.DataFrame()
    conn.close()
    return df

def update_project_spent(project_id, spent_amount):
    conn = sqlite3.connect('incredible_studios.db')
    c = conn.cursor()
    c.execute("UPDATE projects SET spent = spent + ? WHERE id = ?", (spent_amount, project_id))
    conn.commit()
    conn.close()

def update_project_status(project_id, new_status):
    conn = sqlite3.connect('incredible_studios.db')
    c = conn.cursor()
    try:
        if new_status == 'Completed':
            c.execute("UPDATE projects SET status = ?, actual_completion_date = ? WHERE id = ?", 
                      (new_status, date.today(), project_id))
        else:
            c.execute("UPDATE projects SET status = ? WHERE id = ?", (new_status, project_id))
    except:
        c.execute("UPDATE projects SET status = ? WHERE id = ?", (new_status, project_id))
    conn.commit()
    conn.close()

def get_project_kpi():
    df = get_projects()
    if df.empty:
        return {"total_projects": 0, "completed_projects": 0, "on_track": 0, "at_risk": 0, "completion_rate": 0}
    
    total = len(df)
    completed = len(df[df['status'] == 'Completed'])
    
    # Calculate at-risk projects (deadline passed and not completed)
    today = date.today()
    try:
        at_risk = len(df[(pd.to_datetime(df['deadline']) < pd.Timestamp(today)) & (df['status'] != 'Completed')])
    except:
        at_risk = 0
    
    return {
        "total_projects": total,
        "completed_projects": completed,
        "completion_rate": (completed / total * 100) if total > 0 else 0,
        "at_risk": at_risk
    }

# Task management functions
def add_task(project_id, title, description, assigned_to, priority, due_date, estimated_hours, created_by):
    conn = sqlite3.connect('incredible_studios.db')
    c = conn.cursor()
    c.execute("""INSERT INTO tasks 
                 (project_id, title, description, assigned_to, priority, status, due_date, estimated_hours, created_by) 
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
              (project_id, title, description, assigned_to, priority, 'Pending', due_date, estimated_hours, created_by))
    conn.commit()
    conn.close()

def get_tasks(project_id=None, assigned_to=None):
    conn = sqlite3.connect('incredible_studios.db')
    query = "SELECT * FROM tasks"
    conditions = []
    if project_id:
        conditions.append(f"project_id = {project_id}")
    if assigned_to:
        conditions.append(f"assigned_to = '{assigned_to}'")
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += " ORDER BY due_date"
    try:
        df = pd.read_sql_query(query, conn)
    except:
        df = pd.DataFrame()
    conn.close()
    return df

def update_task_status(task_id, new_status, actual_hours=None):
    conn = sqlite3.connect('incredible_studios.db')
    c = conn.cursor()
    if new_status == 'Completed':
        if actual_hours:
            c.execute("UPDATE tasks SET status = ?, completed_date = ?, actual_hours = ? WHERE id = ?", 
                      (new_status, date.today(), actual_hours, task_id))
        else:
            c.execute("UPDATE tasks SET status = ?, completed_date = ? WHERE id = ?", 
                      (new_status, date.today(), task_id))
    else:
        c.execute("UPDATE tasks SET status = ? WHERE id = ?", (new_status, task_id))
    conn.commit()
    conn.close()

# Time tracking functions
def add_time_entry(user_id, project_id, task_id, date, hours, description):
    conn = sqlite3.connect('incredible_studios.db')
    c = conn.cursor()
    c.execute("""INSERT INTO time_entries (user_id, project_id, task_id, date, hours, description) 
                 VALUES (?, ?, ?, ?, ?, ?)""",
              (user_id, project_id, task_id, date, hours, description))
    conn.commit()
    conn.close()

def get_time_entries(user_id=None, project_id=None, start_date=None, end_date=None):
    conn = sqlite3.connect('incredible_studios.db')
    query = "SELECT * FROM time_entries"
    conditions = []
    if user_id:
        conditions.append(f"user_id = {user_id}")
    if project_id:
        conditions.append(f"project_id = {project_id}")
    if start_date and end_date:
        conditions.append(f"date BETWEEN '{start_date}' AND '{end_date}'")
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += " ORDER BY date DESC"
    try:
        df = pd.read_sql_query(query, conn)
    except:
        df = pd.DataFrame()
    conn.close()
    return df

# Expense claim functions
def add_expense_claim(employee_name, date, category, description, amount, receipt_url):
    conn = sqlite3.connect('incredible_studios.db')
    c = conn.cursor()
    c.execute("""INSERT INTO expense_claims 
                 (employee_name, date, category, description, amount, receipt_url, status) 
                 VALUES (?, ?, ?, ?, ?, ?, ?)""",
              (employee_name, date, category, description, amount, receipt_url, 'Pending'))
    conn.commit()
    conn.close()

def get_expense_claims(status_filter=None):
    conn = sqlite3.connect('incredible_studios.db')
    query = "SELECT * FROM expense_claims"
    if status_filter and status_filter != 'All':
        query += f" WHERE status = '{status_filter}'"
    query += " ORDER BY date DESC"
    try:
        df = pd.read_sql_query(query, conn)
    except:
        df = pd.DataFrame()
    conn.close()
    return df

def approve_expense_claim(claim_id, approver, approval_date):
    conn = sqlite3.connect('incredible_studios.db')
    c = conn.cursor()
    c.execute("UPDATE expense_claims SET status = 'Approved', approved_by = ?, approval_date = ? WHERE id = ?",
              (approver, approval_date, claim_id))
    conn.commit()
    conn.close()

def reject_expense_claim(claim_id, rejection_reason):
    conn = sqlite3.connect('incredible_studios.db')
    c = conn.cursor()
    c.execute("UPDATE expense_claims SET status = 'Rejected', rejection_reason = ? WHERE id = ?",
              (rejection_reason, claim_id))
    conn.commit()
    conn.close()

# Notification functions
def add_notification(user_id, title, message, notification_type):
    conn = sqlite3.connect('incredible_studios.db')
    c = conn.cursor()
    c.execute("""INSERT INTO notifications (user_id, title, message, type) 
                 VALUES (?, ?, ?, ?)""",
              (user_id, title, message, notification_type))
    conn.commit()
    conn.close()

def get_notifications(user_id, unread_only=False):
    conn = sqlite3.connect('incredible_studios.db')
    query = f"SELECT * FROM notifications WHERE user_id = {user_id}"
    if unread_only:
        query += " AND is_read = 0"
    query += " ORDER BY created_at DESC"
    try:
        df = pd.read_sql_query(query, conn)
    except:
        df = pd.DataFrame()
    conn.close()
    return df

def mark_notification_read(notification_id):
    conn = sqlite3.connect('incredible_studios.db')
    c = conn.cursor()
    c.execute("UPDATE notifications SET is_read = 1 WHERE id = ?", (notification_id,))
    conn.commit()
    conn.close()

# Client communication functions
def add_communication(client_name, project_id, comm_type, subject, message, direction, follow_up_date, recorded_by):
    conn = sqlite3.connect('incredible_studios.db')
    c = conn.cursor()
    c.execute("""INSERT INTO communications 
                 (client_name, project_id, communication_type, subject, message, direction, follow_up_date, recorded_by) 
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
              (client_name, project_id, comm_type, subject, message, direction, follow_up_date, recorded_by))
    conn.commit()
    conn.close()

def get_communications(client_name=None, project_id=None):
    conn = sqlite3.connect('incredible_studios.db')
    query = "SELECT * FROM communications"
    conditions = []
    if client_name:
        conditions.append(f"client_name = '{client_name}'")
    if project_id:
        conditions.append(f"project_id = {project_id}")
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += " ORDER BY date_time DESC"
    try:
        df = pd.read_sql_query(query, conn)
    except:
        df = pd.DataFrame()
    conn.close()
    return df

# Document management functions
def upload_document(title, description, file, project_id, category, uploaded_by):
    conn = sqlite3.connect('incredible_studios.db')
    c = conn.cursor()
    file_data = file.read()
    c.execute("""INSERT INTO documents (title, description, file_name, file_data, file_type, project_id, category, uploaded_by) 
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
              (title, description, file.name, file_data, file.type, project_id, category, uploaded_by))
    conn.commit()
    conn.close()

def get_documents(project_id=None):
    conn = sqlite3.connect('incredible_studios.db')
    query = "SELECT id, title, description, file_name, file_type, project_id, category, uploaded_by, uploaded_at FROM documents"
    if project_id:
        query += f" WHERE project_id = {project_id}"
    query += " ORDER BY uploaded_at DESC"
    try:
        df = pd.read_sql_query(query, conn)
    except:
        df = pd.DataFrame()
    conn.close()
    return df

def download_document(doc_id):
    conn = sqlite3.connect('incredible_studios.db')
    c = conn.cursor()
    c.execute("SELECT file_data, file_name, file_type FROM documents WHERE id = ?", (doc_id,))
    result = c.fetchone()
    conn.close()
    return result

def delete_document(doc_id):
    conn = sqlite3.connect('incredible_studios.db')
    c = conn.cursor()
    c.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
    conn.commit()
    conn.close()

# Report generation functions
def generate_csv_report(df, filename):
    """Generate CSV report"""
    output = io.StringIO()
    df.to_csv(output, index=False)
    return output.getvalue().encode('utf-8')

def generate_financial_report(start_date, end_date):
    """Generate financial report in CSV format"""
    df = get_transactions(filters={'start_date': start_date, 'end_date': end_date})
    if df.empty:
        return None
    
    return generate_csv_report(df, f"financial_report_{start_date}_{end_date}.csv")

# Dashboard analytics
def get_dashboard_analytics():
    # Get all necessary data
    financial = get_financial_summary()
    projects = get_project_kpi()
    transactions = get_transactions()
    
    # Calculate additional metrics
    analytics = {
        'financial': financial,
        'projects': projects,
        'total_transactions': len(transactions) if not transactions.empty else 0,
        'avg_transaction_value': financial['total_income'] / len(transactions[transactions['type'] == 'Income']) if not transactions.empty and len(transactions[transactions['type'] == 'Income']) > 0 else 0,
        'recent_activity': len(transactions[transactions['date'] >= (date.today() - timedelta(days=30))]) if not transactions.empty else 0
    }
    
    return analytics

# Main application
def main():
    # Initialize database
    conn = init_database()
    
    # Get system settings
    settings = get_system_settings()
    studio_name = settings.get('studio_name', 'Incredible Studios')
    
    # Apply custom CSS
    apply_custom_css(
        settings.get('brand_primary', '#1D2E26'),
        settings.get('brand_accent', '#8FD65A'),
        settings.get('brand_secondary', '#E9C46A'),
        settings.get('brand_background', '#F8F3ED'),
        settings.get('brand_text', '#2F2F3C')
    )
    
    # Session state initialization
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user' not in st.session_state:
        st.session_state.user = None
    
    # Login page
    if not st.session_state.logged_in:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown(f"""
            <div style="text-align: center; padding: 2rem;">
                <h1 style="font-size: 3rem;">🎨 {studio_name}</h1>
                <p style="color: #666;">Creative Studio Management System</p>
            </div>
            """, unsafe_allow_html=True)
            
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Login", use_container_width=True)
                
                if submitted:
                    user = login_user(username, password)
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.user = user
                        st.rerun()
                    else:
                        st.error("Invalid username or password")
        
        return
    
    # Main application after login
    user_role = st.session_state.user['role']
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem;">
            <h2 style="color: {settings.get('brand_background', '#F8F3ED')};">🎨 {studio_name}</h2>
            <p style="color: {settings.get('brand_background', '#F8F3ED')};">Welcome, {st.session_state.user['full_name']}!</p>
            <p style="color: {settings.get('brand_background', '#F8F3ED')}; font-size: 0.8rem;">Role: {user_role.title()}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Show notification badge
        notifications = get_notifications(st.session_state.user['id'], unread_only=True)
        notification_badge = f" 🔔 ({len(notifications)})" if len(notifications) > 0 else " 🔔"
        
        st.markdown("---")
        
        if user_role == 'admin':
            menu_options = ["Dashboard", "Financial Management", "Projects", "Tasks & Time Tracking", 
                           "Social Media Vault", "Expense Claims", "Client Communications", 
                           "Document Management", "User Management", "System Settings", "Reports", 
                           f"Notifications{notification_badge}", "Logout"]
        elif user_role == 'manager':
            menu_options = ["Dashboard", "Financial Management", "Projects", "Tasks & Time Tracking", 
                           "Social Media Vault", "Expense Claims", "Client Communications", 
                           "Document Management", "Reports", f"Notifications{notification_badge}", "Logout"]
        else:  # staff
            menu_options = ["Dashboard", "Projects", "Tasks & Time Tracking", 
                           "Expense Claims", f"Notifications{notification_badge}", "Logout"]
        
        selected = st.sidebar.radio("Navigation", menu_options)
    
    # Dashboard with enhanced analytics
    if selected == "Dashboard":
        st.title("📊 Dashboard")
        
        # Get analytics
        analytics = get_dashboard_analytics()
        
        # Key metrics row
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Revenue", f"{settings.get('currency_symbol', '$')}{analytics['financial']['total_income']:,.2f}")
        with col2:
            st.metric("Net Profit", f"{settings.get('currency_symbol', '$')}{analytics['financial']['net_profit']:,.2f}", 
                     delta=f"{analytics['financial']['net_profit']/analytics['financial']['total_income']*100:.1f}%" if analytics['financial']['total_income'] > 0 else "0%")
        with col3:
            st.metric("Active Projects", analytics['projects']['total_projects'] - analytics['projects']['completed_projects'])
        with col4:
            st.metric("Completion Rate", f"{analytics['projects']['completion_rate']:.1f}%")
        
        # Charts row
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Financial Overview")
            transactions_df = get_transactions()
            if not transactions_df.empty:
                # Monthly trend
                transactions_df['month'] = pd.to_datetime(transactions_df['date']).dt.strftime('%Y-%m')
                monthly = transactions_df.groupby(['month', 'type'])['amount'].sum().reset_index()
                fig = px.line(monthly, x='month', y='amount', color='type', 
                             title="Monthly Income vs Expenses")
                fig.update_layout(showlegend=True)
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Project Status")
            projects_df = get_projects()
            if not projects_df.empty:
                status_counts = projects_df['status'].value_counts()
                fig = px.pie(values=status_counts.values, names=status_counts.index, 
                            title="Projects by Status")
                st.plotly_chart(fig, use_container_width=True)
        
        # Recent activity
        st.subheader("Recent Activity")
        if not transactions_df.empty:
            recent = transactions_df.head(10)
            st.dataframe(recent[['date', 'type', 'category', 'description', 'amount']], use_container_width=True)
        
        # Upcoming deadlines
        st.subheader("Upcoming Project Deadlines")
        if not projects_df.empty:
            today = date.today()
            try:
                upcoming = projects_df[(pd.to_datetime(projects_df['deadline']) >= pd.Timestamp(today)) & 
                                      (pd.to_datetime(projects_df['deadline']) <= pd.Timestamp(today + timedelta(days=30))) &
                                      (projects_df['status'] != 'Completed')]
                if not upcoming.empty:
                    for _, project in upcoming.iterrows():
                        st.info(f"📅 **{project['name']}** - Deadline: {project['deadline']}")
                else:
                    st.info("No upcoming deadlines in the next 30 days")
            except:
                st.info("Unable to load deadlines")
    
    # Financial Management (simplified version for brevity - same as before but with error handling)
    elif selected == "Financial Management":
        st.title("💰 Financial Management")
        st.info("Financial management features are available. Please use the tabs below.")
        
        tab1, tab2, tab3 = st.tabs(["Add Transaction", "View Transactions", "Reports"])
        
        with tab1:
            with st.form("add_transaction"):
                col1, col2 = st.columns(2)
                with col1:
                    trans_date = st.date_input("Date", date.today())
                    trans_type = st.selectbox("Transaction Type", ["Income", "Expense"])
                    category = st.selectbox("Category", 
                        ["Client Payment", "Salary", "Software", "Marketing", "Equipment", "Rent", "Utilities", "Other"])
                with col2:
                    amount = st.number_input(f"Amount ({settings.get('currency_symbol', '$')})", min_value=0.01, step=0.01)
                    client_name = st.text_input("Client Name (optional)")
                    project_name = st.text_input("Project Name (optional)")
                
                description = st.text_area("Description")
                
                submitted = st.form_submit_button("Add Transaction")
                if submitted:
                    add_transaction(trans_date, trans_type, category, "", description, amount, 
                                  client_name, project_name, "Cash", "", 0, None, st.session_state.user['username'])
                    st.success("Transaction added successfully!")
                    st.rerun()
        
        with tab2:
            start_date = st.date_input("Start Date", date.today() - timedelta(days=30))
            end_date = st.date_input("End Date", date.today())
            transactions_df = get_transactions(filters={'start_date': start_date, 'end_date': end_date})
            if not transactions_df.empty:
                st.dataframe(transactions_df[['date', 'type', 'category', 'description', 'amount']], use_container_width=True)
            else:
                st.info("No transactions found")
        
        with tab3:
            if st.button("Generate Report"):
                report = generate_financial_report(start_date, end_date)
                if report:
                    st.download_button(
                        label="Download CSV Report",
                        data=report,
                        file_name=f"financial_report_{start_date}_{end_date}.csv",
                        mime="text/csv"
                    )
    
    # Projects
    elif selected == "Projects":
        st.title("📁 Project Management")
        
        tab1, tab2 = st.tabs(["Project List", "Add New Project"])
        
        with tab1:
            projects_df = get_projects()
            if not projects_df.empty:
                status_filter = st.selectbox("Filter by Status", ["All", "Planning", "In Progress", "Review", "Completed"])
                
                if status_filter != "All":
                    projects_df = projects_df[projects_df['status'] == status_filter]
                
                for idx, project in projects_df.iterrows():
                    with st.expander(f"📌 {project['name']} - {project['client']}"):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.write(f"**Status:** {project['status']}")
                            st.write(f"**Budget:** {settings.get('currency_symbol', '$')}{project['budget']:,.2f}")
                        with col2:
                            st.write(f"**Spent:** {settings.get('currency_symbol', '$')}{project['spent']:,.2f}")
                            progress = (project['spent'] / project['budget'] * 100) if project['budget'] > 0 else 0
                            st.progress(progress / 100)
                        with col3:
                            st.write(f"**Start Date:** {project['start_date']}")
                            st.write(f"**Deadline:** {project['deadline']}")
                        
                        st.write(f"**Description:** {project['description']}")
                        
                        if user_role in ['admin', 'manager']:
                            col1, col2 = st.columns(2)
                            with col1:
                                new_status = st.selectbox("Update Status", ["Planning", "In Progress", "Review", "Completed"], 
                                                         key=f"status_{project['id']}")
                                if st.button(f"Update Status", key=f"update_status_{project['id']}"):
                                    update_project_status(project['id'], new_status)
                                    st.success("Project status updated!")
                                    st.rerun()
                            with col2:
                                additional_spent = st.number_input("Add expense", min_value=0.0, step=100.0, key=f"spent_{project['id']}")
                                if st.button(f"Update Spent", key=f"update_spent_{project['id']}"):
                                    update_project_spent(project['id'], additional_spent)
                                    st.success("Project expenses updated!")
                                    st.rerun()
            else:
                st.info("No projects found. Create your first project!")
        
        with tab2:
            with st.form("add_project"):
                col1, col2 = st.columns(2)
                with col1:
                    project_name = st.text_input("Project Name")
                    client_name = st.text_input("Client Name")
                    status = st.selectbox("Status", ["Planning", "In Progress", "Review", "Completed"])
                with col2:
                    budget = st.number_input(f"Budget ({settings.get('currency_symbol', '$')})", min_value=0.0, step=1000.0)
                    start_date = st.date_input("Start Date", date.today())
                    deadline = st.date_input("Deadline", date.today() + timedelta(days=30))
                
                description = st.text_area("Description")
                
                submitted = st.form_submit_button("Create Project")
                if submitted and project_name and client_name:
                    add_project(project_name, client_name, "", "", status, "Medium", budget, start_date, deadline, 
                              description, "", "", "", st.session_state.user['username'])
                    st.success("Project created successfully!")
                    st.rerun()
    
    # Tasks & Time Tracking
    elif selected == "Tasks & Time Tracking":
        st.title("⏰ Tasks & Time Tracking")
        st.info("Task management and time tracking features are available.")
        
        tab1, tab2 = st.tabs(["My Tasks", "Time Tracking"])
        
        with tab1:
            tasks_df = get_tasks(assigned_to=st.session_state.user['username'] if user_role == 'staff' else None)
            if not tasks_df.empty:
                for idx, task in tasks_df.iterrows():
                    with st.expander(f"✅ {task['title']} - Due: {task['due_date']}"):
                        st.write(f"**Description:** {task['description']}")
                        st.write(f"**Priority:** {task['priority']}")
                        st.write(f"**Status:** {task['status']}")
                        
                        if task['status'] != 'Completed':
                            new_status = st.selectbox("Update Status", ["Pending", "In Progress", "Completed"], key=f"task_{task['id']}")
                            if st.button(f"Update", key=f"update_{task['id']}"):
                                update_task_status(task['id'], new_status)
                                st.success("Task updated!")
                                st.rerun()
            else:
                st.info("No tasks found")
        
        with tab2:
            with st.form("time_entry"):
                entry_date = st.date_input("Date", date.today())
                hours = st.number_input("Hours Worked", min_value=0.25, step=0.25)
                description = st.text_area("Work Description")
                
                submitted = st.form_submit_button("Log Time")
                if submitted:
                    add_time_entry(st.session_state.user['id'], None, None, entry_date, hours, description)
                    st.success("Time entry logged!")
                    st.rerun()
    
    # Social Media Vault
    elif selected == "Social Media Vault" and user_role in ['admin', 'manager']:
        st.title("🔐 Social Media Vault")
        
        tab1, tab2 = st.tabs(["Stored Accounts", "Add New Account"])
        
        with tab1:
            social_df = get_social_accounts()
            if not social_df.empty:
                for idx, account in social_df.iterrows():
                    with st.expander(f"📱 {account['platform']} - @{account['username']}"):
                        st.write(f"**Username:** {account['username']}")
                        st.write(f"**Email:** {account['email']}")
                        if 'password' in account:
                            st.write(f"**Password:** `{account['password']}`")
                        
                        if user_role in ['admin', 'manager']:
                            if st.button(f"Delete Account", key=f"del_{account['id']}"):
                                delete_social_account(account['id'])
                                st.success("Account deleted!")
                                st.rerun()
            else:
                st.info("No social media accounts stored yet.")
        
        with tab2:
            with st.form("add_social"):
                col1, col2 = st.columns(2)
                with col1:
                    platform = st.selectbox("Platform", ["Instagram", "Facebook", "Twitter", "LinkedIn", "TikTok", "YouTube", "Other"])
                    username = st.text_input("Username/Handle")
                    email = st.text_input("Email Address")
                with col2:
                    password = st.text_input("Password", type="password")
                    profile_url = st.text_input("Profile URL (optional)")
                
                notes = st.text_area("Additional Notes")
                
                submitted = st.form_submit_button("Save Account")
                if submitted and platform and username and password:
                    add_social_account(platform, username, email, password, profile_url, notes, "", 0, st.session_state.user['username'])
                    st.success("Social media account saved successfully!")
                    st.rerun()
    
    # Expense Claims
    elif selected == "Expense Claims":
        st.title("📝 Expense Claims")
        
        tab1, tab2 = st.tabs(["My Claims", "Submit Claim"])
        
        with tab1:
            claims_df = get_expense_claims()
            if not claims_df.empty:
                if user_role != 'admin':
                    claims_df = claims_df[claims_df['employee_name'] == st.session_state.user['full_name']]
                
                for idx, claim in claims_df.iterrows():
                    with st.expander(f"📄 Claim #{claim['id']} - {claim['date']} - {claim['status']}"):
                        st.write(f"**Amount:** {settings.get('currency_symbol', '$')}{claim['amount']:,.2f}")
                        st.write(f"**Description:** {claim['description']}")
                        
                        if user_role == 'admin' and claim['status'] == 'Pending':
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.button(f"Approve", key=f"approve_{claim['id']}"):
                                    approve_expense_claim(claim['id'], st.session_state.user['username'], date.today())
                                    st.success("Claim approved!")
                                    st.rerun()
                            with col2:
                                if st.button(f"Reject", key=f"reject_{claim['id']}"):
                                    reject_expense_claim(claim['id'], "Rejected by admin")
                                    st.success("Claim rejected!")
                                    st.rerun()
            else:
                st.info("No expense claims found.")
        
        with tab2:
            with st.form("submit_claim"):
                claim_date = st.date_input("Date of Expense", date.today())
                category = st.selectbox("Category", ["Travel", "Meals", "Supplies", "Software", "Equipment", "Other"])
                amount = st.number_input(f"Amount ({settings.get('currency_symbol', '$')})", min_value=0.01, step=0.01)
                description = st.text_area("Description")
                
                submitted = st.form_submit_button("Submit Claim")
                if submitted:
                    add_expense_claim(st.session_state.user['full_name'], claim_date, category, description, amount, None)
                    st.success("Expense claim submitted successfully!")
                    st.rerun()
    
    # Notifications
    elif selected.startswith("Notifications"):
        st.title("🔔 Notifications")
        
        notifications_df = get_notifications(st.session_state.user['id'])
        
        if not notifications_df.empty:
            for idx, notif in notifications_df.iterrows():
                with st.container():
                    if not notif['is_read']:
                        st.info(f"**{notif['title']}** - {notif['message']}\n\n*{notif['created_at']}*")
                        if st.button("Mark as Read", key=f"mark_{notif['id']}"):
                            mark_notification_read(notif['id'])
                            st.rerun()
                    else:
                        st.write(f"**{notif['title']}** - {notif['message']} *(Read)*")
                    st.markdown("---")
        else:
            st.info("No notifications.")
    
    # User Management (Admin only)
    elif selected == "User Management" and user_role == 'admin':
        st.title("👥 User Management")
        
        tab1, tab2 = st.tabs(["Existing Users", "Add New User"])
        
        with tab1:
            users = get_all_users()
            if users:
                user_df = pd.DataFrame(users, columns=['ID', 'Username', 'Role', 'Full Name', 'Email', 'Phone', 'Department', 'Created At', 'Last Login', 'Active'])
                st.dataframe(user_df, use_container_width=True)
                
                st.subheader("User Actions")
                user_options = [f"{u[3]} ({u[1]})" for u in users if u[1] != 'admin']
                if user_options:
                    user_to_modify = st.selectbox("Select User", user_options)
                    user_id = users[[u[1] for u in users].index(user_to_modify.split('(')[1].rstrip(')'))][0]
                    new_role = st.selectbox("New Role", ["admin", "manager", "staff"])
                    if st.button("Update Role"):
                        update_user_role(user_id, new_role)
                        st.success("Role updated!")
                        st.rerun()
            else:
                st.info("No users found.")
        
        with tab2:
            with st.form("add_user"):
                col1, col2 = st.columns(2)
                with col1:
                    new_username = st.text_input("Username")
                    new_password = st.text_input("Password", type="password")
                    new_fullname = st.text_input("Full Name")
                with col2:
                    new_email = st.text_input("Email")
                    new_phone = st.text_input("Phone")
                    new_department = st.text_input("Department")
                    new_role = st.selectbox("Role", ["staff", "manager", "admin"])
                
                submitted = st.form_submit_button("Add User")
                if submitted and new_username and new_password:
                    if add_user(new_username, new_password, new_role, new_fullname, new_email, new_phone, new_department):
                        st.success(f"User {new_username} added successfully!")
                        st.rerun()
                    else:
                        st.error("Username already exists!")
    
    # System Settings (Admin only)
    elif selected == "System Settings" and user_role == 'admin':
        st.title("⚙️ System Settings")
        
        tab1, tab2 = st.tabs(["Change Password", "Studio Settings"])
        
        with tab1:
            st.subheader("Change Your Password")
            with st.form("change_password"):
                old_pass = st.text_input("Current Password", type="password")
                new_pass = st.text_input("New Password", type="password")
                confirm_pass = st.text_input("Confirm New Password", type="password")
                
                if st.form_submit_button("Update Password"):
                    if new_pass != confirm_pass:
                        st.error("New passwords don't match!")
                    elif len(new_pass) < 6:
                        st.error("Password must be at least 6 characters!")
                    else:
                        if change_password(st.session_state.user['username'], old_pass, new_pass):
                            st.success("Password changed successfully! Please login again.")
                            st.session_state.logged_in = False
                            st.rerun()
                        else:
                            st.error("Current password is incorrect!")
        
        with tab2:
            st.subheader("Studio Settings")
            current_settings = get_system_settings()
            
            tax_rate = st.number_input("Tax Rate (%)", min_value=0.0, max_value=100.0, 
                                      value=float(current_settings.get('tax_rate', '10')))
            currency_symbol = st.text_input("Currency Symbol", current_settings.get('currency_symbol', '$'))
            
            if st.button("Save Settings"):
                update_system_setting('tax_rate', str(tax_rate))
                update_system_setting('currency_symbol', currency_symbol)
                st.success("Settings saved!")
                st.rerun()
            
            st.subheader("Role Permissions")
            st.info("""
            **Role Permissions Overview:**
            
            - **Admin**: Full access to all features including user management and system settings
            - **Manager**: Can access financial management, projects, tasks, social media, expense claims, and reports
            - **Staff**: Can view dashboard, projects, tasks, submit expense claims, and view notifications
            
            To modify user roles, go to User Management tab.
            """)
    
    # Reports
    elif selected == "Reports" and user_role in ['admin', 'manager']:
        st.title("📊 Reports")
        
        report_type = st.selectbox("Select Report Type", ["Financial Summary", "Project Status Report"])
        
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", date.today() - timedelta(days=30))
        with col2:
            end_date = st.date_input("End Date", date.today())
        
        if st.button("Generate Report"):
            if report_type == "Financial Summary":
                df = get_transactions(filters={'start_date': start_date, 'end_date': end_date})
                if not df.empty:
                    st.subheader("Financial Summary")
                    
                    income = df[df['type'] == 'Income']['amount'].sum()
                    expense = df[df['type'] == 'Expense']['amount'].sum()
                    profit = income - expense
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Income", f"{settings.get('currency_symbol', '$')}{income:,.2f}")
                    with col2:
                        st.metric("Total Expenses", f"{settings.get('currency_symbol', '$')}{expense:,.2f}")
                    with col3:
                        st.metric("Net Profit", f"{settings.get('currency_symbol', '$')}{profit:,.2f}")
                    
                    st.dataframe(df[['date', 'type', 'category', 'description', 'amount']], use_container_width=True)
                    
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name=f"financial_report_{start_date}_{end_date}.csv",
                        mime="text/csv"
                    )
                else:
                    st.warning("No data available")
            
            elif report_type == "Project Status Report":
                df = get_projects()
                if not df.empty:
                    st.subheader("Project Status Report")
                    st.dataframe(df[['name', 'client', 'status', 'budget', 'spent', 'deadline']], use_container_width=True)
                else:
                    st.warning("No projects found")
    
    # Logout
    elif selected == "Logout":
        st.session_state.logged_in = False
        st.session_state.user = None
        st.rerun()

if __name__ == "__main__":
    main()