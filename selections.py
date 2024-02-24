import sqlite3
from helpers import connect_to_database
from users import select_all_users, get_user_data, login_check_existing_user, register_check_existing_user

###
# Matery Chain Link Selection Functions
###

# Function to get link info
def select_links():
    conn, cursor = connect_to_database('uonew.db')
    cursor.execute("SELECT * FROM mclinks")
    links_data = cursor.fetchall()
    conn.close()
    return links_data

def select_selections():
    conn, cursor = connect_to_database('uonew.db')
    user_data = get_user_data()

    user_id = user_data['id']

    cursor.execute("SELECT * FROM selections INNER JOIN mclinks ON selections.mclink_id = mclinks.id WHERE selections.user_id = ?", (user_id,))
    selections_data = cursor.fetchall()

    conn.close()
    return selections_data

def admin_select_selections():
    conn, cursor = connect_to_database('uonew.db')
    cursor.execute("SELECT * FROM selections INNER JOIN mclinks ON selections.mclink_id = mclinks.id")
    selections_data = cursor.fetchall()

    conn.close()
    return selections_data

def check_selection_toggle():
    conn, cursor = connect_to_database('uonew.db')
    cursor.execute("SELECT selections_toggle FROM global")
    selection_toggle = cursor.fetchone()
    conn.close()
    return selection_toggle

