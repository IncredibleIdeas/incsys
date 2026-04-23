# app.py
import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import hashlib
import re
from PIL import Image
import io
import base64

# Page configuration
st.set_page_config(
    page_title="Incredible Studios Management System",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for branding
def load_css():
    st.markdown(f"""
    <style>
        /* Brand Colors */
        :root {{
            --brand-deep: '#1D2E26';
            --brand-mint: '#8FD65A';
            --brand-sand: '#E9C46A';
            --brand-cream: '#F8F3ED';
            --brand-slate: '#2F2F3C';
        }}
        
        /* Main container styling */
        .stApp {{
            background-color: #F8F3ED;
        }}
        
        /* Sidebar styling */
        .css-1d391kg {{
            background-color: #1D2E26;
        }}
        
        .css-1d391kg .st-emotion-cache-1v0mbdj {{
            color: #F8F3ED;
        }}
        
        /* Headers */
        h1, h2, h3 {{
            color: #1D2E26;
            font-weight: 600;
        }}
        
        /* Buttons */
        .stButton > button {{
            background-color: #8FD65A;
            color: #1D2E26;
            border: none;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            font-weight: 600;
            transition: all 0.3s ease;
        }}
        
        .stButton > button:hover {{
            background-color: #E9C46A;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }}
        
        /* Cards */
        .metric-card {{
            background-color: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-left: 4px solid #8FD65A;
            margin-bottom: 1rem;
        }}
        
        /* Dataframes */
        .dataframe {{
            background-color: white;
            border-radius: 8px;
            padding: 1rem;
        }}
        
        /* Success/Warning/Error messages */
        .stAlert {{
            border-radius: 8px;
            border-left: 4px solid;
        }}
        
        /* Expander styling */
        .streamlit-expanderHeader {{
            background-color: white;
            border-radius: 8px;
            color: #1D2E26;
        }}
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 2rem;
        }}
        
        .stTabs [data-baseweb="tab"] {{
            background-color: white;
            border-radius: 8px 8px 0 0;
            color: #1D2E26;
            padding: 0.5rem 1rem;
        }}
        
        .stTabs [aria-selected="true"] {{
            background-color: #8FD65A;
            color: #1D2E26;
        }}
        
        /* Animations */
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        .fade-in {{
            animation: fadeIn 0.5s ease-out;
        }}
    </style>
    """, unsafe_allow_html=True)

# Database setup
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
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # System settings table
    c.execute('''CREATE TABLE IF NOT EXISTS system_settings (
        key TEXT PRIMARY KEY,
        value TEXT,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Financial transactions table
    c.execute('''CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT NOT NULL,
        category TEXT NOT NULL,
        amount REAL NOT NULL,
        description TEXT,
        date DATE NOT NULL,
        created_by TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Social media accounts table
    c.execute('''CREATE TABLE IF NOT EXISTS social_accounts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        platform TEXT NOT NULL,
        username TEXT NOT NULL,
        link TEXT,
        password TEXT,
        notes TEXT,
        created_by TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Projects table
    c.execute('''CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        client TEXT,
        budget REAL,
        status TEXT,
        deadline DATE,
        description TEXT,
        created_by TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Insert default admin user if not exists
    c.execute("SELECT * FROM users WHERE username = 'admin'")
    if not c.fetchone():
        default_password = hashlib.sha256("admin123".encode()).hexdigest()
        c.execute("INSERT INTO users (username, password, role, full_name, email) VALUES (?, ?, ?, ?, ?)",
                  ('admin', default_password, 'admin', 'System Administrator', 'admin@incrediblestudios.com'))
    
    # Insert default settings if not exists
    default_settings = [
        ('site_name', 'Incredible Studios'),
        ('brand_color', '#1D2E26'),
        ('accent_color', '#8FD65A'),
        ('logo', ''),
        ('currency', 'USD'),
        ('tax_rate', '0')
    ]
    for key, value in default_settings:
        c.execute("INSERT OR IGNORE INTO system_settings (key, value) VALUES (?, ?)", (key, value))
    
    conn.commit()
    conn.close()

# Authentication functions
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    return hash_password(password) == hashed

def login_user(username, password):
    conn = sqlite3.connect('incredible_studios.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    conn.close()
    
    if user and verify_password(password, user[2]):
        return user
    return None

def get_user_role(username):
    conn = sqlite3.connect('incredible_studios.db')
    c = conn.cursor()
    c.execute("SELECT role FROM users WHERE username = ?", (username,))
    role = c.fetchone()
    conn.close()
    return role[0] if role else None

# Role-based access decorator
def check_role(allowed_roles):
    if 'logged_in' not in st.session_state or not st.session_state.logged_in:
        st.warning("Please login first")
        return False
    user_role = get_user_role(st.session_state.username)
    if user_role not in allowed_roles:
        st.error(f"Access denied. {user_role} users cannot access this section.")
        return False
    return True

# Financial management functions
def add_transaction(transaction_type, category, amount, description, date):
    conn = sqlite3.connect('incredible_studios.db')
    c = conn.cursor()
    c.execute("""INSERT INTO transactions (type, category, amount, description, date, created_by)
                 VALUES (?, ?, ?, ?, ?, ?)""",
              (transaction_type, category, amount, description, date, st.session_state.username))
    conn.commit()
    conn.close()

def get_financial_summary():
    conn = sqlite3.connect('incredible_studios.db')
    df = pd.read_sql_query("SELECT * FROM transactions", conn)
    conn.close()
    
    if df.empty:
        return {'total_income': 0, 'total_expense': 0, 'balance': 0, 'categories': {}}
    
    income = df[df['type'] == 'Income']['amount'].sum()
    expense = df[df['type'] == 'Expense']['amount'].sum()
    
    category_expense = df[df['type'] == 'Expense'].groupby('category')['amount'].sum().to_dict()
    
    return {
        'total_income': income,
        'total_expense': expense,
        'balance': income - expense,
        'categories': category_expense
    }

# Social media management functions
def add_social_account(platform, username, link, password, notes):
    conn = sqlite3.connect('incredible_studios.db')
    c = conn.cursor()
    c.execute("""INSERT INTO social_accounts (platform, username, link, password, notes, created_by)
                 VALUES (?, ?, ?, ?, ?, ?)""",
              (platform, username, link, password, notes, st.session_state.username))
    conn.commit()
    conn.close()

def get_social_accounts():
    conn = sqlite3.connect('incredible_studios.db')
    df = pd.read_sql_query("SELECT * FROM social_accounts", conn)
    conn.close()
    return df

# Project management functions
def add_project(name, client, budget, status, deadline, description):
    conn = sqlite3.connect('incredible_studios.db')
    c = conn.cursor()
    c.execute("""INSERT INTO projects (name, client, budget, status, deadline, description, created_by)
                 VALUES (?, ?, ?, ?, ?, ?, ?)""",
              (name, client, budget, status, deadline, description, st.session_state.username))
    conn.commit()
    conn.close()

def get_projects():
    conn = sqlite3.connect('incredible_studios.db')
    df = pd.read_sql_query("SELECT * FROM projects", conn)
    conn.close()
    return df

# User management functions (Admin only)
def add_user(username, password, role, full_name, email):
    conn = sqlite3.connect('incredible_studios.db')
    c = conn.cursor()
    try:
        hashed_pw = hash_password(password)
        c.execute("""INSERT INTO users (username, password, role, full_name, email)
                     VALUES (?, ?, ?, ?, ?)""",
                  (username, hashed_pw, role, full_name, email))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_all_users():
    conn = sqlite3.connect('incredible_studios.db')
    df = pd.read_sql_query("SELECT id, username, role, full_name, email, created_at FROM users", conn)
    conn.close()
    return df

def delete_user(user_id):
    conn = sqlite3.connect('incredible_studios.db')
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE id = ? AND username != 'admin'", (user_id,))
    conn.commit()
    conn.close()

def update_user_role(user_id, new_role):
    conn = sqlite3.connect('incredible_studios.db')
    c = conn.cursor()
    c.execute("UPDATE users SET role = ? WHERE id = ? AND username != 'admin'", (new_role, user_id))
    conn.commit()
    conn.close()

# Settings management
def get_setting(key):
    conn = sqlite3.connect('incredible_studios.db')
    c = conn.cursor()
    c.execute("SELECT value FROM system_settings WHERE key = ?", (key,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

def update_setting(key, value):
    conn = sqlite3.connect('incredible_studios.db')
    c = conn.cursor()
    c.execute("UPDATE system_settings SET value = ?, updated_at = CURRENT_TIMESTAMP WHERE key = ?", (value, key))
    conn.commit()
    conn.close()

# Main UI Components
def sidebar_navigation():
    with st.sidebar:
        st.image("https://via.placeholder.com/200x100?text=Incredible+Studios", use_column_width=True)
        site_name = get_setting('site_name')
        st.markdown(f"## {site_name}")
        st.markdown(f"**Welcome, {st.session_state.username}**")
        st.markdown(f"Role: {get_user_role(st.session_state.username).capitalize()}")
        st.divider()
        
        menu_options = ["Dashboard", "Financial Management", "Project Management", "Social Media Vault"]
        
        user_role = get_user_role(st.session_state.username)
        if user_role == 'admin':
            menu_options.extend(["User Management", "System Settings"])
        
        if st.button("Logout", use_container_width=True):
            for key in ['logged_in', 'username']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
        
        st.divider()
        return st.radio("Navigation", menu_options, label_visibility="collapsed")

def dashboard():
    st.markdown("<h1 class='fade-in'>Dashboard</h1>", unsafe_allow_html=True)
    
    # Financial Overview
    col1, col2, col3 = st.columns(3)
    summary = get_financial_summary()
    
    with col1:
        st.markdown(f"""
        <div class='metric-card'>
            <h3>💰 Total Income</h3>
            <h2>${summary['total_income']:,.2f}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class='metric-card'>
            <h3>💸 Total Expenses</h3>
            <h2>${summary['total_expense']:,.2f}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        color = '#8FD65A' if summary['balance'] >= 0 else '#E9C46A'
        st.markdown(f"""
        <div class='metric-card' style='border-left-color: {color};'>
            <h3>⚖️ Balance</h3>
            <h2 style='color: {color};'>${summary['balance']:,.2f}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    # Recent Projects
    st.subheader("📊 Recent Projects")
    projects = get_projects()
    if not projects.empty:
        recent_projects = projects.tail(5)
        st.dataframe(recent_projects[['name', 'client', 'budget', 'status', 'deadline']], use_container_width=True)
    else:
        st.info("No projects yet. Add your first project in Project Management!")
    
    # Quick Stats
    col4, col5 = st.columns(2)
    with col4:
        st.subheader("📱 Social Media Accounts")
        social = get_social_accounts()
        st.metric("Total Accounts", len(social))
    
    with col5:
        st.subheader("👥 Team Members")
        users = get_all_users()
        st.metric("Active Users", len(users))

def financial_management():
    st.markdown("<h1 class='fade-in'>Financial Management</h1>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["Add Transaction", "Transaction History", "Reports"])
    
    with tab1:
        with st.form("add_transaction_form"):
            col1, col2 = st.columns(2)
            with col1:
                trans_type = st.selectbox("Transaction Type", ["Income", "Expense"])
                category = st.text_input("Category (e.g., Client Payment, Software, Rent)")
                amount = st.number_input("Amount", min_value=0.01, step=0.01)
            with col2:
                description = st.text_area("Description")
                date = st.date_input("Date", datetime.now())
            
            if st.form_submit_button("Add Transaction", use_container_width=True):
                add_transaction(trans_type, category, amount, description, date)
                st.success("Transaction added successfully!")
                st.rerun()
    
    with tab2:
        conn = sqlite3.connect('incredible_studios.db')
        transactions = pd.read_sql_query("SELECT * FROM transactions ORDER BY date DESC", conn)
        conn.close()
        
        if not transactions.empty:
            st.dataframe(transactions[['type', 'category', 'amount', 'description', 'date']], use_container_width=True)
            
            # Delete functionality
            transaction_to_delete = st.selectbox("Select transaction to delete (by ID)", transactions['id'].tolist())
            if st.button("Delete Transaction", type="secondary"):
                conn = sqlite3.connect('incredible_studios.db')
                c = conn.cursor()
                c.execute("DELETE FROM transactions WHERE id = ?", (transaction_to_delete,))
                conn.commit()
                conn.close()
                st.success("Transaction deleted!")
                st.rerun()
        else:
            st.info("No transactions yet")
    
    with tab3:
        summary = get_financial_summary()
        st.subheader("Financial Summary")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Income", f"${summary['total_income']:,.2f}")
            st.metric("Total Expenses", f"${summary['total_expense']:,.2f}")
            st.metric("Net Balance", f"${summary['balance']:,.2f}")
        
        with col2:
            if summary['categories']:
                st.subheader("Expense by Category")
                cat_df = pd.DataFrame(list(summary['categories'].items()), columns=['Category', 'Amount'])
                st.bar_chart(cat_df.set_index('Category'))

def project_management():
    st.markdown("<h1 class='fade-in'>Project Management</h1>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Add New Project", "All Projects"])
    
    with tab1:
        with st.form("add_project_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Project Name*")
                client = st.text_input("Client Name")
                budget = st.number_input("Budget", min_value=0.0, step=100.0)
            with col2:
                status = st.selectbox("Status", ["Planning", "In Progress", "Review", "Completed", "On Hold"])
                deadline = st.date_input("Deadline")
            
            description = st.text_area("Description")
            
            if st.form_submit_button("Create Project", use_container_width=True):
                if name:
                    add_project(name, client, budget, status, deadline, description)
                    st.success(f"Project '{name}' created successfully!")
                    st.rerun()
                else:
                    st.error("Project name is required")
    
    with tab2:
        projects = get_projects()
        if not projects.empty:
            # Editable dataframe
            edited_df = st.data_editor(
                projects[['id', 'name', 'client', 'budget', 'status', 'deadline']],
                use_container_width=True,
                hide_index=True
            )
            
            # Update functionality would go here
        else:
            st.info("No projects yet")

def social_media_vault():
    st.markdown("<h1 class='fade-in'>Social Media Vault 🔐</h1>", unsafe_allow_html=True)
    st.warning("⚠️ Passwords are stored securely. Only authorized personnel should access this section.")
    
    tab1, tab2 = st.tabs(["Add Account", "View Accounts"])
    
    with tab1:
        with st.form("add_social_form"):
            col1, col2 = st.columns(2)
            with col1:
                platform = st.selectbox("Platform", ["Instagram", "Facebook", "Twitter", "LinkedIn", "TikTok", "YouTube", "Other"])
                username = st.text_input("Username/Page Name*")
                link = st.text_input("Profile Link (URL)")
            with col2:
                password = st.text_input("Password", type="password")
                notes = st.text_area("Additional Notes")
            
            if st.form_submit_button("Save Account", use_container_width=True):
                if platform and username:
                    add_social_account(platform, username, link, password, notes)
                    st.success("Social media account saved successfully!")
                    st.rerun()
                else:
                    st.error("Platform and username are required")
    
    with tab2:
        accounts = get_social_accounts()
        if not accounts.empty:
            for _, account in accounts.iterrows():
                with st.expander(f"📱 {account['platform']} - {account['username']}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**Platform:** {account['platform']}")
                        st.markdown(f"**Username:** {account['username']}")
                    with col2:
                        if account['link']:
                            st.markdown(f"**Link:** [{account['link']}]({account['link']})")
                        st.markdown(f"**Password:** `{account['password'] if account['password'] else 'Not set'}`")
                    
                    if account['notes']:
                        st.markdown(f"**Notes:** {account['notes']}")
                    
                    st.caption(f"Added by: {account['created_by']} on {account['created_at']}")
        else:
            st.info("No social media accounts added yet")

def user_management():
    if not check_role(['admin']):
        return
    
    st.markdown("<h1 class='fade-in'>User Management</h1>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Add New User", "Manage Users"])
    
    with tab1:
        with st.form("add_user_form"):
            col1, col2 = st.columns(2)
            with col1:
                username = st.text_input("Username*")
                password = st.text_input("Password*", type="password")
                role = st.selectbox("Role", ["admin", "manager", "staff"])
            with col2:
                full_name = st.text_input("Full Name")
                email = st.text_input("Email")
            
            if st.form_submit_button("Create User", use_container_width=True):
                if username and password:
                    if add_user(username, password, role, full_name, email):
                        st.success(f"User '{username}' created successfully!")
                        st.rerun()
                    else:
                        st.error("Username already exists")
                else:
                    st.error("Username and password are required")
    
    with tab2:
        users = get_all_users()
        if not users.empty:
            st.dataframe(users[['username', 'role', 'full_name', 'email', 'created_at']], use_container_width=True)
            
            col1, col2 = st.columns(2)
            with col1:
                user_to_delete = st.selectbox("Select user to delete", users[users['username'] != 'admin']['username'].tolist())
                if st.button("Delete User", type="secondary"):
                    user_id = users[users['username'] == user_to_delete]['id'].values[0]
                    delete_user(user_id)
                    st.success(f"User '{user_to_delete}' deleted!")
                    st.rerun()
            
            with col2:
                user_to_update = st.selectbox("Select user to update role", users[users['username'] != 'admin']['username'].tolist())
                new_role = st.selectbox("New Role", ["admin", "manager", "staff"])
                if st.button("Update Role"):
                    user_id = users[users['username'] == user_to_update]['id'].values[0]
                    update_user_role(user_id, new_role)
                    st.success(f"Role updated for '{user_to_update}'!")
                    st.rerun()
        else:
            st.info("No users found")

def system_settings():
    if not check_role(['admin']):
        return
    
    st.markdown("<h1 class='fade-in'>System Settings</h1>", unsafe_allow_html=True)
    
    with st.form("settings_form"):
        current_name = get_setting('site_name')
        new_name = st.text_input("Site Name", current_name)
        
        current_currency = get_setting('currency')
        new_currency = st.selectbox("Currency", ["USD", "EUR", "GBP", "CAD", "AUD"], 
                                   index=["USD", "EUR", "GBP", "CAD", "AUD"].index(current_currency))
        
        current_tax = get_setting('tax_rate')
        new_tax = st.number_input("Tax Rate (%)", min_value=0.0, max_value=100.0, value=float(current_tax))
        
        st.subheader("Change Admin Password")
        col1, col2 = st.columns(2)
        with col1:
            old_password = st.text_input("Current Password", type="password")
        with col2:
            new_password = st.text_input("New Password", type="password")
        
        if st.form_submit_button("Save Settings", use_container_width=True):
            update_setting('site_name', new_name)
            update_setting('currency', new_currency)
            update_setting('tax_rate', str(new_tax))
            
            if old_password and new_password:
                conn = sqlite3.connect('incredible_studios.db')
                c = conn.cursor()
                c.execute("SELECT password FROM users WHERE username = ?", (st.session_state.username,))
                current_hash = c.fetchone()[0]
                if verify_password(old_password, current_hash):
                    new_hash = hash_password(new_password)
                    c.execute("UPDATE users SET password = ? WHERE username = ?", (new_hash, st.session_state.username))
                    conn.commit()
                    st.success("Password changed successfully!")
                else:
                    st.error("Current password is incorrect")
                conn.close()
            
            st.success("Settings saved successfully!")
            st.rerun()
    
    # Database backup option
    st.divider()
    st.subheader("Database Management")
    if st.button("Export Database Backup", type="secondary"):
        conn = sqlite3.connect('incredible_studios.db')
        backup = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table'", conn)
        
        # Create backup file
        backup_data = {}
        for table in backup['name']:
            backup_data[table] = pd.read_sql_query(f"SELECT * FROM {table}", conn)
        
        conn.close()
        
        # Save to CSV files
        import zipfile
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmpfile:
            with zipfile.ZipFile(tmpfile.name, 'w') as zipf:
                for table_name, df in backup_data.items():
                    csv_path = f"{table_name}.csv"
                    df.to_csv(csv_path, index=False)
                    zipf.write(csv_path)
                    os.remove(csv_path)
            
            with open(tmpfile.name, 'rb') as f:
                st.download_button(
                    label="Download Backup",
                    data=f,
                    file_name="incredible_studios_backup.zip",
                    mime="application/zip"
                )

# Login UI
def login_page():
    st.markdown("""
    <div style='text-align: center; padding: 2rem;'>
        <h1 style='color: #1D2E26;'>🎨 Incredible Studios</h1>
        <h3>Management System</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            
            if st.form_submit_button("Login", use_container_width=True):
                user = login_user(username, password)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.error("Invalid username or password")
        
        st.caption("Default admin credentials: admin / admin123")

# Main app
def main():
    load_css()
    init_database()
    
    if 'logged_in' not in st.session_state:
        login_page()
    else:
        selected = sidebar_navigation()
        
        if selected == "Dashboard":
            dashboard()
        elif selected == "Financial Management":
            financial_management()
        elif selected == "Project Management":
            project_management()
        elif selected == "Social Media Vault":
            social_media_vault()
        elif selected == "User Management":
            user_management()
        elif selected == "System Settings":
            system_settings()

if __name__ == "__main__":
    main()