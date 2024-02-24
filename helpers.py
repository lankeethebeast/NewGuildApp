# helpers.py
import sqlite3

# Function to connect to database
def connect_to_database(database_name):
    conn = sqlite3.connect(database_name)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    return conn, cursor

##### def authenticate_master():
#####     if 'username' not in session:
#####         flash('Please log in first.', 'error')
#####         return redirect(url_for('login'))
#####     elif session.get('user_level', 0) < 3:
#####         flash('You do not have permission to access this page.', 'error')
#####         return redirect(url_for('index'))
#####     return None
#####
##### def authenticate_admin2():
#####     if 'username' not in session:
#####         flash('Please log in first.', 'error')
#####         return redirect(url_for('login'))
#####     elif session.get('user_level', 0) < 2:
#####         flash('You do not have permission to access this page.', 'error')
#####         return redirect(url_for('index'))
#####     return None
#####
##### def authenticate_admin1():
#####     if 'username' not in session:
#####         flash('Please log in first.', 'error')
#####         return redirect(url_for('login'))
#####     elif session.get('user_level', 0) < 1:
#####         flash('You do not have permission to access this page.', 'error')
#####         return redirect(url_for('index'))
#####     return None
#####
##### def authenticate_user():
#####     if 'username' not in session:
#####         flash('Please log in first.', 'error')
#####         return redirect(url_for('login'))
#####     return None
#####