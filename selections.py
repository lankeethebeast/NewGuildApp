import sqlite3
from helpers import connect_to_database
from users import select_all_users, get_user_data, login_check_existing_user, register_check_existing_user

###
# Matery Chain Link Selection Functions
###

def select_selections(user_id=None):
    conn, cursor = connect_to_database('uonew.db')
    if user_id:
        cursor.execute("SELECT * FROM selections INNER JOIN mclinks ON selections.mclink_id = mclinks.id WHERE selections.user_id = ?", (user_id,))
    else:
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

def select_delivery(user_id=None):
    conn, cursor = connect_to_database('uonew.db')
    if user_id:
        cursor.execute("SELECT * FROM link_delivery INNER JOIN mclinks ON link_delivery.mclink_id = mclinks.id WHERE link_delivery.user_id = ?", (user_id,))
    else:
        cursor.execute("SELECT * FROM link_delivery INNER JOIN mclinks ON link_delivery.mclink_id = mclinks.id")
    delivery_data = cursor.fetchall()
    conn.close()
    return delivery_data

def select_history(user_id=None):
    conn, cursor = connect_to_database('uonew.db')
    if user_id:
        cursor.execute("SELECT * FROM history INNER JOIN mclinks ON history.mclink_id = mclinks.id WHERE history.user_id = ?", (user_id,))
    else:
        cursor.execute("SELECT * FROM history INNER JOIN mclinks ON history.mclink_id = mclinks.id")
    history_data = cursor.fetchall()
    conn.close()
    return history_data