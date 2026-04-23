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
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import string
import matplotlib.pyplot as plt
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import io
import base64
import shutil
import os

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
        
        /* Animation for notifications */
        @keyframes slideIn {{
            from {{
                transform: translateX(100%);
                opacity: 0;
            }}
            to {{
                transform: translateX(0);
                opacity: 1;
            }}
        }}
        
        .notification {{
            animation: slideIn 0.3s ease-out;
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
    </style>
    """, unsafe_allow_html=True)

# Database setup with enhanced tables
def init_database():
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
    
    # Tasks table (NEW)
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
    
    # Documents table (NEW)
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
    
    # Client communications table (NEW)
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
    
    # Expense claims table (NEW)
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
    
    # Notifications table (NEW)
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
    
    # Time tracking table (NEW)
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
    
    # Insert default admin user if not exists
    default_password = hashlib.sha256("admin123".encode()).hexdigest()
    c.execute("INSERT OR IGNORE INTO users (username, password, role, full_name, email, department) VALUES (?, ?, ?, ?, ?, ?)",
              ("admin", default_password, "admin", "System Administrator", "admin@incrediblestudios.com", "Management"))
    
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
    c.execute("SELECT * FROM users WHERE username = ? AND is_active = 1", (username,))
    user = c.fetchone()
    if user and verify_password(user[2], password):
        # Update last login
        c.execute("UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?", (user[0],))
        conn.commit()
        conn.close()
        return {"id": user[0], "username": user[1], "role": user[3], "full_name": user[4], "email": user[5]}
    conn.close()
    return None

def get_all_users():
    conn = sqlite3.connect('incredible_studios.db')
    c = conn.cursor()
    c.execute("SELECT id, username, role, full_name, email, phone, department, created_at, last_login, is_active FROM users")
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
    c.execute("UPDATE users SET is_active = ? WHERE id = ?", (is_active, user_id))
    conn.commit()
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
def add_transaction(date, trans_type, category, subcategory, description, amount, client_name, project_name, 
                   payment_method, invoice_number, tax_amount, receipt_url, created_by):
    conn = sqlite3.connect('incredible_studios.db')
    c = conn.cursor()
    c.execute("""INSERT INTO transactions 
                 (date, type, category, subcategory, description, amount, client_name, project_name, 
                  payment_method, invoice_number, tax_amount, receipt_url, created_by) 
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
              (date, trans_type, category, subcategory, description, amount, client_name, project_name,
               payment_method, invoice_number, tax_amount, receipt_url, created_by))
    conn.commit()
    conn.close()

def get_transactions(filters=None):
    conn = sqlite3.connect('incredible_studios.db')
    if filters and 'start_date' in filters and 'end_date' in filters:
        query = "SELECT * FROM transactions WHERE date BETWEEN ? AND ? ORDER BY date DESC"
        df = pd.read_sql_query(query, conn, params=[filters['start_date'], filters['end_date']])
    else:
        query = "SELECT * FROM transactions ORDER BY date DESC"
        df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def get_financial_summary():
    df = get_transactions()
    if df.empty:
        return {"total_income": 0, "total_expense": 0, "net_profit": 0, "total_tax": 0}
    
    income = df[df['type'] == 'Income']['amount'].sum() if not df[df['type'] == 'Income'].empty else 0
    expense = df[df['type'] == 'Expense']['amount'].sum() if not df[df['type'] == 'Expense'].empty else 0
    tax = df['tax_amount'].sum() if 'tax_amount' in df.columns and not df['tax_amount'].empty else 0
    return {"total_income": income, "total_expense": expense, "net_profit": income - expense, "total_tax": tax}

def generate_invoice_number():
    return f"INV-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"

# Social media functions with encryption
def add_social_account(platform, username, email, password, profile_url, notes, category, followers_count, created_by):
    conn = sqlite3.connect('incredible_studios.db')
    c = conn.cursor()
    # Simple encryption (for demo - use proper encryption in production)
    encrypted_password = base64.b64encode(password.encode()).decode()
    c.execute("""INSERT INTO social_accounts 
                 (platform, username, email, password, profile_url, notes, category, followers_count, created_by, last_updated) 
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
              (platform, username, email, encrypted_password, profile_url, notes, category, followers_count, created_by, datetime.now()))
    conn.commit()
    conn.close()

def get_social_accounts():
    conn = sqlite3.connect('incredible_studios.db')
    df = pd.read_sql_query("SELECT * FROM social_accounts ORDER BY platform", conn)
    # Decrypt passwords for display
    if not df.empty and 'password' in df.columns:
        df['password'] = df['password'].apply(lambda x: base64.b64decode(x.encode()).decode() if x else '')
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
    c.execute("UPDATE social_accounts SET followers_count = ?, last_updated = ? WHERE id = ?", 
              (followers_count, datetime.now(), account_id))
    conn.commit()
    conn.close()

# Project functions with enhancements
def add_project(name, client, client_email, client_phone, status, priority, budget, start_date, deadline, 
                description, deliverables, project_manager, team_members, created_by):
    conn = sqlite3.connect('incredible_studios.db')
    c = conn.cursor()
    c.execute("""INSERT INTO projects 
                 (name, client, client_email, client_phone, status, priority, budget, spent, start_date, deadline, 
                  description, deliverables, project_manager, team_members, created_by) 
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
              (name, client, client_email, client_phone, status, priority, budget, 0, start_date, deadline,
               description, deliverables, project_manager, team_members, created_by))
    conn.commit()
    conn.close()

def get_projects(status_filter=None):
    conn = sqlite3.connect('incredible_studios.db')
    if status_filter and status_filter != 'All':
        query = "SELECT * FROM projects WHERE status = ? ORDER BY deadline"
        df = pd.read_sql_query(query, conn, params=[status_filter])
    else:
        query = "SELECT * FROM projects ORDER BY deadline"
        df = pd.read_sql_query(query, conn)
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
    if new_status == 'Completed':
        c.execute("UPDATE projects SET status = ?, actual_completion_date = ? WHERE id = ?", 
                  (new_status, date.today(), project_id))
    else:
        c.execute("UPDATE projects SET status = ? WHERE id = ?", (new_status, project_id))
    conn.commit()
    conn.close()

def get_project_kpi():
    df = get_projects()
    if df.empty:
        return {"total_projects": 0, "completed_projects": 0, "completion_rate": 0, "at_risk": 0}
    
    total = len(df)
    completed = len(df[df['status'] == 'Completed'])
    
    # Calculate at-risk projects (deadline passed and not completed)
    today = date.today()
    at_risk = len(df[(pd.to_datetime(df['deadline']) < pd.Timestamp(today)) & (df['status'] != 'Completed')]) if 'deadline' in df.columns else 0
    
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
    params = []
    
    if project_id:
        conditions.append("project_id = ?")
        params.append(project_id)
    if assigned_to:
        conditions.append("assigned_to = ?")
        params.append(assigned_to)
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += " ORDER BY due_date"
    df = pd.read_sql_query(query, conn, params=params if params else None)
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

def delete_task(task_id):
    conn = sqlite3.connect('incredible_studios.db')
    c = conn.cursor()
    c.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()

# Time tracking functions
def add_time_entry(user_id, project_id, task_id, entry_date, hours, description):
    conn = sqlite3.connect('incredible_studios.db')
    c = conn.cursor()
    c.execute("""INSERT INTO time_entries (user_id, project_id, task_id, date, hours, description) 
                 VALUES (?, ?, ?, ?, ?, ?)""",
              (user_id, project_id, task_id, entry_date, hours, description))
    conn.commit()
    conn.close()

def get_time_entries(user_id=None, project_id=None, start_date=None, end_date=None):
    conn = sqlite3.connect('incredible_studios.db')
    query = "SELECT * FROM time_entries"
    conditions = []
    params = []
    
    if user_id:
        conditions.append("user_id = ?")
        params.append(user_id)
    if project_id:
        conditions.append("project_id = ?")
        params.append(project_id)
    if start_date and end_date:
        conditions.append("date BETWEEN ? AND ?")
        params.extend([start_date, end_date])
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += " ORDER BY date DESC"
    df = pd.read_sql_query(query, conn, params=params if params else None)
    conn.close()
    return df

# Expense claim functions
def add_expense_claim(employee_name, claim_date, category, description, amount, receipt_url):
    conn = sqlite3.connect('incredible_studios.db')
    c = conn.cursor()
    c.execute("""INSERT INTO expense_claims 
                 (employee_name, date, category, description, amount, receipt_url, status) 
                 VALUES (?, ?, ?, ?, ?, ?, ?)""",
              (employee_name, claim_date, category, description, amount, receipt_url, 'Pending'))
    conn.commit()
    conn.close()

def get_expense_claims(status_filter=None):
    conn = sqlite3.connect('incredible_studios.db')
    if status_filter and status_filter != 'All':
        query = "SELECT * FROM expense_claims WHERE status = ? ORDER BY date DESC"
        df = pd.read_sql_query(query, conn, params=[status_filter])
    else:
        query = "SELECT * FROM expense_claims ORDER BY date DESC"
        df = pd.read_sql_query(query, conn)
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
    if unread_only:
        query = "SELECT * FROM notifications WHERE user_id = ? AND is_read = 0 ORDER BY created_at DESC"
        df = pd.read_sql_query(query, conn, params=[user_id])
    else:
        query = "SELECT * FROM notifications WHERE user_id = ? ORDER BY created_at DESC"
        df = pd.read_sql_query(query, conn, params=[user_id])
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
    params = []
    
    if client_name:
        conditions.append("client_name = ?")
        params.append(client_name)
    if project_id:
        conditions.append("project_id = ?")
        params.append(project_id)
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += " ORDER BY date_time DESC"
    df = pd.read_sql_query(query, conn, params=params if params else None)
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
    if project_id:
        query = "SELECT id, title, description, file_name, file_type, project_id, category, uploaded_by, uploaded_at FROM documents WHERE project_id = ? ORDER BY uploaded_at DESC"
        df = pd.read_sql_query(query, conn, params=[project_id])
    else:
        query = "SELECT id, title, description, file_name, file_type, project_id, category, uploaded_by, uploaded_at FROM documents ORDER BY uploaded_at DESC"
        df = pd.read_sql_query(query, conn)
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
def generate_financial_report(start_date, end_date):
    df = get_transactions(filters={'start_date': start_date, 'end_date': end_date})
    if df.empty:
        return None
    
    # Create PDF report
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title = Paragraph(f"Financial Report: {start_date} to {end_date}", styles['Title'])
    story.append(title)
    story.append(Spacer(1, 12))
    
    # Summary
    income = df[df['type'] == 'Income']['amount'].sum() if not df[df['type'] == 'Income'].empty else 0
    expense = df[df['type'] == 'Expense']['amount'].sum() if not df[df['type'] == 'Expense'].empty else 0
    profit = income - expense
    
    summary_data = [
        ['Metric', 'Amount'],
        ['Total Income', f'${income:,.2f}'],
        ['Total Expenses', f'${expense:,.2f}'],
        ['Net Profit', f'${profit:,.2f}']
    ]
    
    summary_table = Table(summary_data)
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(summary_table)
    story.append(Spacer(1, 12))
    
    # Detailed transactions
    story.append(Paragraph("Detailed Transactions", styles['Heading2']))
    story.append(Spacer(1, 12))
    
    # Prepare transaction data for table
    trans_data = [['Date', 'Type', 'Category', 'Description', 'Amount']]
    for _, row in df.iterrows():
        trans_data.append([
            str(row['date']),
            row['type'],
            row['category'],
            (row['description'][:50] if row['description'] else ''),
            f"${row['amount']:,.2f}"
        ])
    
    trans_table = Table(trans_data)
    trans_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(trans_table)
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# Dashboard analytics
def get_dashboard_analytics():
    # Get all necessary data
    financial = get_financial_summary()
    projects = get_project_kpi()
    transactions = get_transactions()
    
    # Calculate additional metrics
    income_transactions = transactions[transactions['type'] == 'Income'] if not transactions.empty else pd.DataFrame()
    avg_transaction_value = financial['total_income'] / len(income_transactions) if not income_transactions.empty and len(income_transactions) > 0 else 0
    
    recent_activity = 0
    if not transactions.empty and 'date' in transactions.columns:
        transactions['date'] = pd.to_datetime(transactions['date'])
        recent_activity = len(transactions[transactions['date'] >= (pd.Timestamp(date.today()) - pd.Timedelta(days=30))])
    
    analytics = {
        'financial': financial,
        'projects': projects,
        'total_transactions': len(transactions) if not transactions.empty else 0,
        'avg_transaction_value': avg_transaction_value,
        'recent_activity': recent_activity
    }
    
    return analytics

# Main application
def main():
    # Initialize database
    conn = init_database()
    conn.close()
    
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
            icons = ["house", "currency-dollar", "briefcase", "clock", "link", "receipt", 
                    "chat", "folder", "people", "gear", "graph-up", "bell", "box-arrow-right"]
        elif user_role == 'manager':
            menu_options = ["Dashboard", "Financial Management", "Projects", "Tasks & Time Tracking", 
                           "Social Media Vault", "Expense Claims", "Client Communications", 
                           "Document Management", "Reports", f"Notifications{notification_badge}", "Logout"]
            icons = ["house", "currency-dollar", "briefcase", "clock", "link", "receipt", 
                    "chat", "folder", "graph-up", "bell", "box-arrow-right"]
        else:  # staff
            menu_options = ["Dashboard", "Projects", "Tasks & Time Tracking", 
                           "Expense Claims", f"Notifications{notification_badge}", "Logout"]
            icons = ["house", "briefcase", "clock", "receipt", "bell", "box-arrow-right"]
        
        selected = option_menu(
            menu_title=None,
            options=menu_options,
            icons=icons,
            menu_icon="cast",
            default_index=0,
            styles={
                "container": {"padding": "0!important", "background-color": "transparent"},
                "icon": {"color": settings.get('brand_background', '#F8F3ED'), "font-size": "1.2rem"},
                "nav-link": {"color": settings.get('brand_background', '#F8F3ED'), "font-size": "0.9rem", "text-align": "left", "margin": "0.3rem 0"},
                "nav-link-selected": {"background-color": settings.get('brand_accent', '#8FD65A'), "color": settings.get('brand_primary', '#1D2E26')},
            }
        )
    
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
            net_profit = analytics['financial']['net_profit']
            total_income = analytics['financial']['total_income']
            delta = f"{net_profit/total_income*100:.1f}%" if total_income > 0 else "0%"
            st.metric("Net Profit", f"{settings.get('currency_symbol', '$')}{net_profit:,.2f}", delta=delta)
        with col3:
            st.metric("Active Projects", analytics['projects']['total_projects'] - analytics['projects']['completed_projects'])
        with col4:
            st.metric("Completion Rate", f"{analytics['projects']['completion_rate']:.1f}%")
        
        # Charts row
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Financial Overview")
            transactions_df = get_transactions()
            if not transactions_df.empty and len(transactions_df) > 0:
                # Monthly trend
                transactions_df['date'] = pd.to_datetime(transactions_df['date'])
                transactions_df['month'] = transactions_df['date'].dt.strftime('%Y-%m')
                monthly = transactions_df.groupby(['month', 'type'])['amount'].sum().reset_index()
                if not monthly.empty:
                    fig = px.line(monthly, x='month', y='amount', color='type', 
                                 title="Monthly Income vs Expenses")
                    fig.update_layout(showlegend=True)
                    st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Project Status")
            projects_df = get_projects()
            if not projects_df.empty and 'status' in projects_df.columns:
                status_counts = projects_df['status'].value_counts()
                if not status_counts.empty:
                    fig = px.pie(values=status_counts.values, names=status_counts.index, 
                                title="Projects by Status")
                    st.plotly_chart(fig, use_container_width=True)
        
        # Recent activity
        st.subheader("Recent Activity")
        transactions_df = get_transactions()
        if not transactions_df.empty:
            recent = transactions_df.head(10)
            display_cols = ['date', 'type', 'category', 'description', 'amount']
            available_cols = [col for col in display_cols if col in recent.columns]
            st.dataframe(recent[available_cols], use_container_width=True)
        
        # Upcoming deadlines
        st.subheader("Upcoming Project Deadlines")
        projects_df = get_projects()
        if not projects_df.empty and 'deadline' in projects_df.columns and 'status' in projects_df.columns:
            today_date = date.today()
            upcoming = projects_df[(pd.to_datetime(projects_df['deadline']) >= pd.Timestamp(today_date)) & 
                                  (pd.to_datetime(projects_df['deadline']) <= pd.Timestamp(today_date + timedelta(days=30))) &
                                  (projects_df['status'] != 'Completed')]
            if not upcoming.empty:
                for _, project in upcoming.iterrows():
                    st.info(f"📅 **{project['name']}** - Deadline: {project['deadline']}")
            else:
                st.info("No upcoming deadlines in the next 30 days")
    
    # Financial Management with enhanced features
    elif selected == "Financial Management":
        st.title("💰 Financial Management")
        
        # Initialize date filters for tabs
        start_date = date.today() - timedelta(days=30)
        end_date = date.today()
        
        tab1, tab2, tab3, tab4 = st.tabs(["Add Transaction", "View Transactions", "Reports", "Analytics"])
        
        with tab1:
            with st.form("add_transaction"):
                col1, col2 = st.columns(2)
                with col1:
                    trans_date = st.date_input("Date", date.today())
                    trans_type = st.selectbox("Transaction Type", ["Income", "Expense"])
                    category = st.selectbox("Category", 
                        ["Client Payment", "Salary", "Software", "Marketing", "Equipment", "Rent", "Utilities", "Other"])
                    subcategory = st.text_input("Subcategory (optional)")
                with col2:
                    amount = st.number_input(f"Amount ({settings.get('currency_symbol', '$')})", min_value=0.01, step=0.01)
                    payment_method = st.selectbox("Payment Method", ["Cash", "Bank Transfer", "Credit Card", "Check", "Other"])
                    client_name = st.text_input("Client Name (optional)")
                    project_name = st.text_input("Project Name (optional)")
                
                description = st.text_area("Description")
                invoice_number = st.text_input("Invoice Number (optional)", generate_invoice_number())
                tax_amount = st.number_input(f"Tax Amount ({settings.get('currency_symbol', '$')})", min_value=0.0, step=0.01)
                
                submitted = st.form_submit_button("Add Transaction")
                if submitted:
                    add_transaction(trans_date, trans_type, category, subcategory, description, amount, 
                                  client_name, project_name, payment_method, invoice_number, tax_amount, 
                                  None, st.session_state.user['username'])
                    st.success("Transaction added successfully!")
                    st.rerun()
        
        with tab2:
            # Date filter
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("Start Date", date.today() - timedelta(days=30), key="start_date_tab2")
            with col2:
                end_date = st.date_input("End Date", date.today(), key="end_date_tab2")
            
            transactions_df = get_transactions(filters={'start_date': start_date, 'end_date': end_date})
            if not transactions_df.empty:
                # Search and filter
                search_term = st.text_input("Search transactions")
                if search_term:
                    mask = (transactions_df['description'].str.contains(search_term, case=False, na=False) | 
                           transactions_df['client_name'].str.contains(search_term, case=False, na=False) | 
                           transactions_df['category'].str.contains(search_term, case=False, na=False))
                    transactions_df = transactions_df[mask]
                
                display_cols = ['date', 'type', 'category', 'description', 'amount', 'client_name', 'payment_method']
                available_cols = [col for col in display_cols if col in transactions_df.columns]
                st.dataframe(transactions_df[available_cols], use_container_width=True)
            else:
                st.info("No transactions found for the selected period.")
        
        with tab3:
            st.subheader("Financial Reports")
            if st.button("Generate Financial Report"):
                report = generate_financial_report(start_date, end_date)
                if report:
                    st.download_button(
                        label="Download PDF Report",
                        data=report,
                        file_name=f"financial_report_{start_date}_{end_date}.pdf",
                        mime="application/pdf"
                    )
                else:
                    st.warning("No data available for the selected period.")
        
        with tab4:
            transactions_df = get_transactions(filters={'start_date': start_date, 'end_date': end_date})
            if not transactions_df.empty:
                # Advanced analytics
                col1, col2 = st.columns(2)
                with col1:
                    # Income breakdown by category
                    income_data = transactions_df[transactions_df['type'] == 'Income'].groupby('category')['amount'].sum()
                    if not income_data.empty:
                        fig = px.pie(values=income_data.values, names=income_data.index, title="Income by Category")
                        st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Expense breakdown by category
                    expense_data = transactions_df[transactions_df['type'] == 'Expense'].groupby('category')['amount'].sum()
                    if not expense_data.empty:
                        fig = px.pie(values=expense_data.values, names=expense_data.index, title="Expenses by Category")
                        st.plotly_chart(fig, use_container_width=True)
    
    # Projects with enhanced features
    elif selected == "Projects":
        st.title("📁 Project Management")
        
        tab1, tab2 = st.tabs(["Project List", "Add New Project"])
        
        with tab1:
            projects_df = get_projects()
            if not projects_df.empty:
                # Filters
                col1, col2, col3 = st.columns(3)
                with col1:
                    status_filter = st.selectbox("Filter by Status", ["All", "Planning", "In Progress", "Review", "Completed"])
                with col2:
                    priority_filter = st.selectbox("Filter by Priority", ["All", "High", "Medium", "Low"])
                with col3:
                    search_project = st.text_input("Search Projects")
                
                # Apply filters
                filtered_df = projects_df.copy()
                if status_filter != "All" and 'status' in filtered_df.columns:
                    filtered_df = filtered_df[filtered_df['status'] == status_filter]
                if priority_filter != "All" and 'priority' in filtered_df.columns:
                    filtered_df = filtered_df[filtered_df['priority'] == priority_filter]
                if search_project and 'name' in filtered_df.columns:
                    filtered_df = filtered_df[filtered_df['name'].str.contains(search_project, case=False, na=False) | 
                                             filtered_df['client'].str.contains(search_project, case=False, na=False)]
                
                # Display projects
                for idx, project in filtered_df.iterrows():
                    with st.expander(f"📌 {project['name']} - {project['client']} ({project['status']})"):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.write(f"**Status:** {project['status']}")
                            st.write(f"**Priority:** {project['priority']}")
                            budget_val = project['budget'] if project['budget'] is not None else 0
                            st.write(f"**Budget:** {settings.get('currency_symbol', '$')}{budget_val:,.2f}")
                        with col2:
                            spent_val = project['spent'] if project['spent'] is not None else 0
                            st.write(f"**Spent:** {settings.get('currency_symbol', '$')}{spent_val:,.2f}")
                            progress = (spent_val / budget_val * 100) if budget_val > 0 else 0
                            st.progress(progress / 100)
                            st.write(f"**Progress:** {progress:.1f}%")
                        with col3:
                            st.write(f"**Start Date:** {project['start_date']}")
                            st.write(f"**Deadline:** {project['deadline']}")
                            if project['actual_completion_date']:
                                st.write(f"**Completed:** {project['actual_completion_date']}")
                        
                        if project['description']:
                            st.write(f"**Description:** {project['description']}")
                        if project['deliverables']:
                            st.write(f"**Deliverables:** {project['deliverables']}")
                        if project['project_manager']:
                            st.write(f"**Project Manager:** {project['project_manager']}")
                        
                        # Project actions
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
                    client_email = st.text_input("Client Email")
                    client_phone = st.text_input("Client Phone")
                with col2:
                    status = st.selectbox("Status", ["Planning", "In Progress", "Review", "Completed"])
                    priority = st.selectbox("Priority", ["High", "Medium", "Low"])
                    budget = st.number_input(f"Budget ({settings.get('currency_symbol', '$')})", min_value=0.0, step=1000.0)
                
                col1, col2 = st.columns(2)
                with col1:
                    start_date = st.date_input("Start Date", date.today())
                with col2:
                    deadline = st.date_input("Deadline", date.today() + timedelta(days=30))
                
                description = st.text_area("Description")
                deliverables = st.text_area("Deliverables")
                project_manager = st.text_input("Project Manager")
                team_members = st.text_input("Team Members (comma-separated)")
                
                submitted = st.form_submit_button("Create Project")
                if submitted and project_name and client_name:
                    add_project(project_name, client_name, client_email, client_phone, status, priority, 
                              budget, start_date, deadline, description, deliverables, project_manager, 
                              team_members, st.session_state.user['username'])
                    st.success("Project created successfully!")
                    st.rerun()
    
    # Tasks & Time Tracking
    elif selected == "Tasks & Time Tracking":
        st.title("⏰ Tasks & Time Tracking")
        
        tab1, tab2, tab3 = st.tabs(["My Tasks", "Create Task", "Time Tracking"])
        
        with tab1:
            # Get tasks assigned to current user or all if admin/manager
            if user_role in ['admin', 'manager']:
                tasks_df = get_tasks()
            else:
                tasks_df = get_tasks(assigned_to=st.session_state.user['username'])
            
            if not tasks_df.empty:
                # Task filters
                col1, col2 = st.columns(2)
                with col1:
                    status_filter = st.selectbox("Filter by Status", ["All", "Pending", "In Progress", "Completed"])
                with col2:
                    priority_filter = st.selectbox("Filter by Priority", ["All", "High", "Medium", "Low"])
                
                filtered_tasks = tasks_df.copy()
                if status_filter != "All" and 'status' in filtered_tasks.columns:
                    filtered_tasks = filtered_tasks[filtered_tasks['status'] == status_filter]
                if priority_filter != "All" and 'priority' in filtered_tasks.columns:
                    filtered_tasks = filtered_tasks[filtered_tasks['priority'] == priority_filter]
                
                # Display tasks
                for idx, task in filtered_tasks.iterrows():
                    priority_class = "status-high" if task['priority'] == 'High' else "status-medium" if task['priority'] == 'Medium' else "status-low"
                    with st.container():
                        st.markdown(f"""
                        <div class="task-card">
                            <strong>{task['title']}</strong>
                            <span class="status-badge {priority_class}">{task['priority']}</span>
                            <br>
                            <small>Status: {task['status']} | Due: {task['due_date']}</small>
                            <br>
                            <small>{task['description'][:100] if task['description'] else ''}</small>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if task['status'] != 'Completed':
                            col1, col2, col3 = st.columns([2, 1, 1])
                            with col1:
                                new_status = st.selectbox("Update Status", ["Pending", "In Progress", "Completed"], 
                                                         key=f"task_status_{task['id']}")
                            with col2:
                                actual_hours = None
                                if new_status == 'Completed':
                                    actual_hours = st.number_input("Actual Hours", min_value=0.0, step=0.5, key=f"hours_{task['id']}")
                            with col3:
                                if st.button("Update", key=f"update_task_{task['id']}"):
                                    update_task_status(task['id'], new_status, actual_hours if new_status == 'Completed' else None)
                                    st.success("Task updated!")
                                    st.rerun()
                        
                        st.markdown("---")
            else:
                st.info("No tasks found.")
        
        with tab2:
            with st.form("create_task"):
                projects_df = get_projects()
                if not projects_df.empty:
                    project_options = {f"{row['name']} ({row['client']})": row['id'] for _, row in projects_df.iterrows()}
                    project_selection = st.selectbox("Select Project", list(project_options.keys()))
                    project_id = project_options[project_selection]
                    
                    task_title = st.text_input("Task Title")
                    task_description = st.text_area("Task Description")
                    assigned_to = st.text_input("Assign To (Username)")
                    priority = st.selectbox("Priority", ["High", "Medium", "Low"])
                    due_date = st.date_input("Due Date", date.today() + timedelta(days=7))
                    estimated_hours = st.number_input("Estimated Hours", min_value=0.5, step=0.5)
                    
                    submitted = st.form_submit_button("Create Task")
                    if submitted and task_title:
                        add_task(project_id, task_title, task_description, assigned_to, priority, 
                                due_date, estimated_hours, st.session_state.user['username'])
                        st.success("Task created successfully!")
                        st.rerun()
                else:
                    st.warning("Please create a project first before creating tasks.")
        
        with tab3:
            st.subheader("Time Tracking")
            
            # Time entry form
            with st.form("time_entry"):
                col1, col2 = st.columns(2)
                with col1:
                    entry_date = st.date_input("Date", date.today())
                    projects_df = get_projects()
                    if not projects_df.empty:
                        project_options = {f"{row['name']} ({row['client']})": row['id'] for _, row in projects_df.iterrows()}
                        project_selection = st.selectbox("Project", list(project_options.keys()))
                        project_id = project_options[project_selection]
                    else:
                        project_id = None
                        st.warning("No projects available")
                with col2:
                    if project_id:
                        # Get tasks for selected project
                        tasks_df = get_tasks(project_id=project_id)
                        if not tasks_df.empty:
                            task_options = {row['title']: row['id'] for _, row in tasks_df.iterrows()}
                            task_selection = st.selectbox("Task", list(task_options.keys()))
                            task_id = task_options[task_selection]
                        else:
                            task_id = None
                            st.warning("No tasks available for this project")
                    else:
                        task_id = None
                    hours = st.number_input("Hours Worked", min_value=0.25, step=0.25)
                
                description = st.text_area("Work Description")
                
                submitted = st.form_submit_button("Log Time")
                if submitted and task_id:
                    add_time_entry(st.session_state.user['id'], project_id, task_id, entry_date, hours, description)
                    st.success("Time entry logged!")
                    st.rerun()
                elif submitted and not task_id:
                    st.error("Please select a valid task")
            
            # View time entries
            st.subheader("My Time Entries")
            time_entries = get_time_entries(user_id=st.session_state.user['id'])
            if not time_entries.empty:
                display_cols = ['date', 'hours', 'description']
                available_cols = [col for col in display_cols if col in time_entries.columns]
                st.dataframe(time_entries[available_cols], use_container_width=True)
                
                # Summary
                total_hours = time_entries['hours'].sum()
                st.metric("Total Hours Logged", f"{total_hours:.1f} hours")
            else:
                st.info("No time entries found.")
    
    # Social Media Vault with enhanced features
    elif selected == "Social Media Vault":
        st.title("🔐 Social Media Vault")
        st.warning("⚠️ Passwords are stored with basic encryption. In production, use proper encryption.")
        
        tab1, tab2 = st.tabs(["Stored Accounts", "Add New Account"])
        
        with tab1:
            social_df = get_social_accounts()
            if not social_df.empty:
                # Search and filter
                search_term = st.text_input("Search accounts")
                if search_term and 'platform' in social_df.columns:
                    mask = social_df['platform'].str.contains(search_term, case=False, na=False) | \
                           social_df['username'].str.contains(search_term, case=False, na=False)
                    social_df = social_df[mask]
                
                for idx, account in social_df.iterrows():
                    with st.expander(f"📱 {account['platform']} - @{account['username']}"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Username:** {account['username']}")
                            st.write(f"**Email:** {account['email']}")
                            st.write(f"**Category:** {account['category']}")
                        with col2:
                            st.write(f"**Password:** `{account['password']}`")
                            followers = account['followers_count'] if account['followers_count'] is not None else 0
                            st.write(f"**Followers:** {followers:,}" if followers else "**Followers:** Not tracked")
                            last_updated = account['last_updated'] if account['last_updated'] else 'Never'
                            st.write(f"**Last Updated:** {str(last_updated)[:10] if last_updated != 'Never' else 'Never'}")
                        
                        st.write(f"**Profile URL:** {account['profile_url'] or 'Not provided'}")
                        st.write(f"**Notes:** {account['notes'] or 'No notes'}")
                        
                        if user_role in ['admin', 'manager']:
                            col1, col2 = st.columns(2)
                            with col1:
                                new_followers = st.number_input("Update Followers", min_value=0, step=100, key=f"followers_{account['id']}")
                                if st.button(f"Update Followers", key=f"update_followers_{account['id']}"):
                                    update_social_account_followers(account['id'], new_followers)
                                    st.success("Followers updated!")
                                    st.rerun()
                            with col2:
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
                    category = st.selectbox("Category", ["Business", "Personal", "Client", "Marketing", "Other"])
                with col2:
                    password = st.text_input("Password", type="password")
                    profile_url = st.text_input("Profile URL (optional)")
                    followers_count = st.number_input("Initial Followers Count", min_value=0, step=100)
                
                notes = st.text_area("Additional Notes")
                
                submitted = st.form_submit_button("Save Account")
                if submitted and platform and username and password:
                    add_social_account(platform, username, email, password, profile_url, notes, 
                                     category, followers_count, st.session_state.user['username'])
                    st.success("Social media account saved successfully!")
                    st.rerun()
    
    # Expense Claims
    elif selected == "Expense Claims":
        st.title("📝 Expense Claims")
        
        tab1, tab2 = st.tabs(["My Claims", "Submit Claim"])
        
        with tab1:
            if user_role in ['admin', 'manager']:
                # Show all claims for admin/manager
                claims_df = get_expense_claims()
                status_filter = st.selectbox("Filter by Status", ["All", "Pending", "Approved", "Rejected"])
                if status_filter != "All" and not claims_df.empty:
                    claims_df = claims_df[claims_df['status'] == status_filter]
            else:
                # Show only user's claims
                claims_df = get_expense_claims()
                if not claims_df.empty and 'employee_name' in claims_df.columns:
                    claims_df = claims_df[claims_df['employee_name'] == st.session_state.user['full_name']]
            
            if not claims_df.empty:
                for idx, claim in claims_df.iterrows():
                    with st.expander(f"📄 Claim #{claim['id']} - {claim['date']} - {claim['category']} - {claim['status']}"):
                        st.write(f"**Employee:** {claim['employee_name']}")
                        st.write(f"**Amount:** {settings.get('currency_symbol', '$')}{claim['amount']:,.2f}")
                        st.write(f"**Description:** {claim['description']}")
                        if claim['receipt_url']:
                            st.write(f"**Receipt:** {claim['receipt_url']}")
                        
                        if claim['status'] == 'Rejected' and claim['rejection_reason']:
                            st.error(f"**Rejection Reason:** {claim['rejection_reason']}")
                        
                        if user_role in ['admin', 'manager'] and claim['status'] == 'Pending':
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.button(f"Approve", key=f"approve_{claim['id']}"):
                                    approve_expense_claim(claim['id'], st.session_state.user['username'], date.today())
                                    st.success("Claim approved!")
                                    st.rerun()
                            with col2:
                                rejection_reason = st.text_input("Rejection Reason", key=f"reason_{claim['id']}")
                                if st.button(f"Reject", key=f"reject_{claim['id']}"):
                                    if rejection_reason:
                                        reject_expense_claim(claim['id'], rejection_reason)
                                        st.success("Claim rejected!")
                                        st.rerun()
                                    else:
                                        st.error("Please provide a rejection reason")
            else:
                st.info("No expense claims found.")
        
        with tab2:
            with st.form("submit_claim"):
                col1, col2 = st.columns(2)
                with col1:
                    claim_date = st.date_input("Date of Expense", date.today())
                    category = st.selectbox("Category", ["Travel", "Meals", "Supplies", "Software", "Equipment", "Other"])
                with col2:
                    amount = st.number_input(f"Amount ({settings.get('currency_symbol', '$')})", min_value=0.01, step=0.01)
                    receipt_url = st.text_input("Receipt URL (optional)")
                
                description = st.text_area("Description")
                
                submitted = st.form_submit_button("Submit Claim")
                if submitted:
                    add_expense_claim(st.session_state.user['full_name'], claim_date, category, 
                                    description, amount, receipt_url)
                    st.success("Expense claim submitted successfully!")
                    st.rerun()
    
    # Client Communications
    elif selected == "Client Communications":
        st.title("💬 Client Communications")
        
        tab1, tab2 = st.tabs(["Communication Log", "New Communication"])
        
        with tab1:
            # Filter by client
            projects_df = get_projects()
            client_list = projects_df['client'].unique().tolist() if not projects_df.empty and 'client' in projects_df.columns else []
            selected_client = st.selectbox("Filter by Client", ["All"] + client_list)
            
            communications_df = get_communications(client_name=selected_client if selected_client != "All" else None)
            
            if not communications_df.empty:
                for idx, comm in communications_df.iterrows():
                    with st.expander(f"📧 {comm['subject']} - {str(comm['date_time'])[:10]}"):
                        st.write(f"**Client:** {comm['client_name']}")
                        st.write(f"**Type:** {comm['communication_type']}")
                        st.write(f"**Direction:** {comm['direction']}")
                        st.write(f"**Message:** {comm['message']}")
                        st.write(f"**Follow-up Date:** {comm['follow_up_date']}")
                        st.write(f"**Status:** {comm['status']}")
                        
                        if comm['follow_up_date'] and pd.to_datetime(comm['follow_up_date']) <= pd.Timestamp(date.today()) and comm['status'] == 'Open':
                            st.warning("⚠️ Follow-up required!")
            else:
                st.info("No communications found.")
        
        with tab2:
            with st.form("add_communication"):
                projects_df = get_projects()
                if not projects_df.empty:
                    client_options = {f"{row['client']} - {row['name']}": row['id'] for _, row in projects_df.iterrows()}
                    client_selection = st.selectbox("Select Project", list(client_options.keys()))
                    client_name = client_selection.split(" - ")[0]
                    project_id = client_options[client_selection]
                    
                    comm_type = st.selectbox("Communication Type", ["Email", "Phone Call", "Meeting", "Message", "Other"])
                    subject = st.text_input("Subject")
                    direction = st.selectbox("Direction", ["Incoming", "Outgoing"])
                    message = st.text_area("Message")
                    follow_up_date = st.date_input("Follow-up Date", date.today() + timedelta(days=7))
                    
                    submitted = st.form_submit_button("Log Communication")
                    if submitted:
                        add_communication(client_name, project_id, comm_type, subject, message, 
                                        direction, follow_up_date, st.session_state.user['username'])
                        st.success("Communication logged successfully!")
                        st.rerun()
                else:
                    st.warning("Please create a project first before logging communications.")
    
    # Document Management
    elif selected == "Document Management":
        st.title("📄 Document Management")
        
        tab1, tab2 = st.tabs(["Documents", "Upload Document"])
        
        with tab1:
            projects_df = get_projects()
            if not projects_df.empty:
                project_options = {f"{row['name']} ({row['client']})": row['id'] for _, row in projects_df.iterrows()}
                project_options["All Projects"] = None
                selected_project = st.selectbox("Filter by Project", list(project_options.keys()))
                project_id = project_options[selected_project]
                
                documents_df = get_documents(project_id=project_id)
            else:
                documents_df = get_documents()
                st.info("No projects available. Showing all documents.")
            
            if not documents_df.empty:
                for idx, doc in documents_df.iterrows():
                    with st.expander(f"📁 {doc['title']} - {str(doc['uploaded_at'])[:10]}"):
                        st.write(f"**Description:** {doc['description']}")
                        st.write(f"**Category:** {doc['category']}")
                        st.write(f"**File Type:** {doc['file_type']}")
                        st.write(f"**Uploaded By:** {doc['uploaded_by']}")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button(f"Download", key=f"download_{doc['id']}"):
                                result = download_document(doc['id'])
                                if result:
                                    file_data, file_name, file_type = result
                                    st.download_button(
                                        label="Click to Download",
                                        data=file_data,
                                        file_name=file_name,
                                        mime=file_type,
                                        key=f"download_btn_{doc['id']}"
                                    )
                        with col2:
                            if user_role in ['admin', 'manager']:
                                if st.button(f"Delete", key=f"delete_{doc['id']}"):
                                    delete_document(doc['id'])
                                    st.success("Document deleted!")
                                    st.rerun()
            else:
                st.info("No documents found.")
        
        with tab2:
            with st.form("upload_document"):
                title = st.text_input("Document Title")
                description = st.text_area("Description")
                category = st.selectbox("Category", ["Contract", "Invoice", "Design", "Resource", "Other"])
                
                projects_df = get_projects()
                if not projects_df.empty:
                    project_options = {f"{row['name']} ({row['client']})": row['id'] for _, row in projects_df.iterrows()}
                    project_selection = st.selectbox("Associated Project", list(project_options.keys()))
                    project_id = project_options[project_selection]
                else:
                    project_id = None
                    st.warning("No projects available. Please create a project first.")
                
                uploaded_file = st.file_uploader("Choose file", type=['pdf', 'doc', 'docx', 'jpg', 'png', 'xlsx', 'txt'])
                
                submitted = st.form_submit_button("Upload Document")
                if submitted and title and uploaded_file and project_id:
                    upload_document(title, description, uploaded_file, project_id, category, 
                                  st.session_state.user['username'])
                    st.success("Document uploaded successfully!")
                    st.rerun()
                elif submitted and (not title or not uploaded_file):
                    st.error("Please provide both title and file.")
                elif submitted and not project_id:
                    st.error("Please select a project.")
    
    # Reports
    elif selected == "Reports":
        st.title("📊 Advanced Reports")
        
        report_type = st.selectbox("Select Report Type", 
                                 ["Financial Summary", "Project Status Report", "Time Tracking Report", "Expense Claims Report"])
        
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
                    
                    # Summary metrics
                    income = df[df['type'] == 'Income']['amount'].sum() if not df[df['type'] == 'Income'].empty else 0
                    expense = df[df['type'] == 'Expense']['amount'].sum() if not df[df['type'] == 'Expense'].empty else 0
                    profit = income - expense
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total Income", f"{settings.get('currency_symbol', '$')}{income:,.2f}")
                    with col2:
                        st.metric("Total Expenses", f"{settings.get('currency_symbol', '$')}{expense:,.2f}")
                    with col3:
                        st.metric("Net Profit", f"{settings.get('currency_symbol', '$')}{profit:,.2f}")
                    with col4:
                        st.metric("Profit Margin", f"{(profit/income*100):.1f}%" if income > 0 else "0%")
                    
                    # Detailed table
                    display_cols = ['date', 'type', 'category', 'description', 'amount']
                    available_cols = [col for col in display_cols if col in df.columns]
                    st.dataframe(df[available_cols], use_container_width=True)
                    
                    # Download option
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name=f"financial_report_{start_date}_{end_date}.csv",
                        mime="text/csv"
                    )
                else:
                    st.warning("No data available for the selected period.")
            
            elif report_type == "Project Status Report":
                df = get_projects()
                if not df.empty:
                    st.subheader("Project Status Report")
                    
                    # Project metrics
                    total_budget = df['budget'].sum() if 'budget' in df.columns and not df['budget'].empty else 0
                    total_spent = df['spent'].sum() if 'spent' in df.columns and not df['spent'].empty else 0
                    remaining_budget = total_budget - total_spent
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Projects", len(df))
                    with col2:
                        st.metric("Total Budget", f"{settings.get('currency_symbol', '$')}{total_budget:,.2f}")
                    with col3:
                        st.metric("Budget Utilization", f"{(total_spent/total_budget*100):.1f}%" if total_budget > 0 else "0%")
                    
                    # Status breakdown
                    if 'status' in df.columns:
                        status_counts = df['status'].value_counts()
                        if not status_counts.empty:
                            fig = px.bar(x=status_counts.index, y=status_counts.values, title="Projects by Status")
                            st.plotly_chart(fig, use_container_width=True)
                    
                    # Detailed table
                    display_cols = ['name', 'client', 'status', 'priority', 'budget', 'spent', 'deadline']
                    available_cols = [col for col in display_cols if col in df.columns]
                    st.dataframe(df[available_cols], use_container_width=True)
                else:
                    st.warning("No projects found.")
            
            elif report_type == "Time Tracking Report":
                time_entries = get_time_entries(start_date=start_date, end_date=end_date)
                if not time_entries.empty:
                    st.subheader("Time Tracking Report")
                    
                    # Hours by user
                    if 'user_id' in time_entries.columns:
                        user_hours = time_entries.groupby('user_id')['hours'].sum()
                        if not user_hours.empty:
                            st.bar_chart(user_hours)
                    
                    # Detailed table
                    display_cols = [col for col in ['date', 'hours', 'description'] if col in time_entries.columns]
                    if display_cols:
                        st.dataframe(time_entries[display_cols], use_container_width=True)
                    
                    # Total hours
                    total_hours = time_entries['hours'].sum()
                    st.metric("Total Hours Logged", f"{total_hours:.1f} hours")
                else:
                    st.warning("No time entries found for the selected period.")
            
            elif report_type == "Expense Claims Report":
                claims_df = get_expense_claims()
                if not claims_df.empty and 'date' in claims_df.columns:
                    # Filter by date
                    claims_df['date'] = pd.to_datetime(claims_df['date'])
                    claims_df = claims_df[(claims_df['date'] >= pd.Timestamp(start_date)) & 
                                         (claims_df['date'] <= pd.Timestamp(end_date))]
                    
                    if not claims_df.empty:
                        st.subheader("Expense Claims Report")
                        
                        # Summary by status
                        if 'status' in claims_df.columns:
                            status_summary = claims_df['status'].value_counts()
                            if not status_summary.empty:
                                fig = px.pie(values=status_summary.values, names=status_summary.index, title="Claims by Status")
                                st.plotly_chart(fig, use_container_width=True)
                        
                        # Total amount
                        total_approved = claims_df[claims_df['status'] == 'Approved']['amount'].sum() if not claims_df[claims_df['status'] == 'Approved'].empty else 0
                        total_pending = claims_df[claims_df['status'] == 'Pending']['amount'].sum() if not claims_df[claims_df['status'] == 'Pending'].empty else 0
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Total Approved", f"{settings.get('currency_symbol', '$')}{total_approved:,.2f}")
                        with col2:
                            st.metric("Total Pending", f"{settings.get('currency_symbol', '$')}{total_pending:,.2f}")
                        
                        # Detailed table
                        display_cols = ['employee_name', 'date', 'category', 'description', 'amount', 'status']
                        available_cols = [col for col in display_cols if col in claims_df.columns]
                        st.dataframe(claims_df[available_cols], use_container_width=True)
                    else:
                        st.warning("No claims found for the selected period.")
                else:
                    st.warning("No expense claims found.")
    
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
                
                # User actions
                st.subheader("User Actions")
                col1, col2, col3 = st.columns(3)
                with col1:
                    user_options = [f"{u[3]} ({u[1]})" for u in users if u[1] != 'admin']
                    if user_options:
                        user_to_modify = st.selectbox("Select User", user_options)
                        username = user_to_modify.split('(')[1].rstrip(')')
                        user_id = next((u[0] for u in users if u[1] == username), None)
                        if user_id:
                            new_role = st.selectbox("New Role", ["admin", "manager", "staff"])
                            if st.button("Update Role"):
                                update_user_role(user_id, new_role)
                                st.success("Role updated!")
                                st.rerun()
                
                with col2:
                    if user_options:
                        user_to_reset = st.selectbox("Select User for Password Reset", user_options, key="reset_select")
                        if st.button("Reset Password"):
                            username = user_to_reset.split('(')[1].rstrip(')')
                            new_password = reset_user_password(username)
                            st.success(f"Password reset successfully! New password: {new_password}")
                            st.info("Please share this password with the user securely.")
                
                with col3:
                    if user_options:
                        user_to_toggle = st.selectbox("Select User to Toggle Status", user_options, key="toggle_select")
                        username = user_to_toggle.split('(')[1].rstrip(')')
                        user_data = next((u for u in users if u[1] == username), None)
                        if user_data:
                            current_status = user_data[9]
                            if st.button(f"{'Deactivate' if current_status else 'Activate'} User"):
                                toggle_user_status(user_data[0], not current_status)
                                st.success(f"User {'deactivated' if current_status else 'activated'}!")
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
        
        tab1, tab2, tab3, tab4 = st.tabs(["Branding", "Change Password", "Studio Settings", "Backup"])
        
        with tab1:
            st.subheader("Branding Customization")
            current_settings = get_system_settings()
            
            col1, col2 = st.columns(2)
            with col1:
                new_studio_name = st.text_input("Studio Name", current_settings.get('studio_name', 'Incredible Studios'))
                brand_primary = st.color_picker("Primary Color", current_settings.get('brand_primary', '#1D2E26'))
                brand_accent = st.color_picker("Accent Color", current_settings.get('brand_accent', '#8FD65A'))
            
            with col2:
                brand_secondary = st.color_picker("Secondary Accent", current_settings.get('brand_secondary', '#E9C46A'))
                brand_background = st.color_picker("Background Color", current_settings.get('brand_background', '#F8F3ED'))
                brand_text = st.color_picker("Text Color", current_settings.get('brand_text', '#2F2F3C'))
            
            if st.button("Save Branding Settings"):
                update_system_setting('studio_name', new_studio_name)
                update_system_setting('brand_primary', brand_primary)
                update_system_setting('brand_accent', brand_accent)
                update_system_setting('brand_secondary', brand_secondary)
                update_system_setting('brand_background', brand_background)
                update_system_setting('brand_text', brand_text)
                st.success("Branding updated! Page will refresh.")
                st.rerun()
        
        with tab2:
            st.subheader("Change Your Password")
            with st.form("change_password"):
                old_pass = st.text_input("Current Password", type="password")
                new_pass = st.text_input("New Password", type="password")
                confirm_pass = st.text_input("Confirm New Password", type="password")
                
                submitted = st.form_submit_button("Update Password")
                if submitted:
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
        
        with tab3:
            st.subheader("Studio Settings")
            current_settings = get_system_settings()
            
            tax_rate = st.number_input("Tax Rate (%)", min_value=0.0, max_value=100.0, 
                                      value=float(current_settings.get('tax_rate', '10')))
            currency_symbol = st.text_input("Currency Symbol", current_settings.get('currency_symbol', '$'))
            enable_notifications = st.checkbox("Enable Notifications", 
                                              value=current_settings.get('enable_notifications', 'true') == 'true')
            
            if st.button("Save Settings"):
                update_system_setting('tax_rate', str(tax_rate))
                update_system_setting('currency_symbol', currency_symbol)
                update_system_setting('enable_notifications', str(enable_notifications))
                st.success("Settings saved!")
                st.rerun()
            
            st.subheader("Role Permissions")
            st.info("""
            **Role Permissions Overview:**
            
            - **Admin**: Full access to all features including user management and system settings
            - **Manager**: Can access financial management, projects, tasks, social media, expense claims, communications, documents, and reports
            - **Staff**: Can view dashboard, projects, tasks, submit expense claims, and view notifications
            
            To modify user roles, go to User Management tab.
            """)
        
        with tab4:
            st.subheader("Database Backup")
            if st.button("Create Backup"):
                # Create backup of database
                if os.path.exists('incredible_studios.db'):
                    backup_filename = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
                    shutil.copy('incredible_studios.db', backup_filename)
                    
                    with open(backup_filename, 'rb') as f:
                        st.download_button(
                            label="Download Backup",
                            data=f,
                            file_name=backup_filename,
                            mime="application/octet-stream"
                        )
                    # Clean up backup file
                    os.remove(backup_filename)
                    st.success("Backup created successfully!")
                else:
                    st.error("Database file not found!")
    
    # Logout
    elif selected == "Logout":
        st.session_state.logged_in = False
        st.session_state.user = None
        st.rerun()

if __name__ == "__main__":
    main()