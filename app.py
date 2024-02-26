from flask import Flask, render_template, request, redirect, url_for, flash, session, g
from werkzeug.security import generate_password_hash
from helpers import connect_to_database
from users import select_all_users, get_user_data, login_check_existing_user, register_check_existing_user
from selections import check_selection_toggle, select_selections
from mclinks import select_links
import sqlite3
import re

app = Flask(__name__, static_url_path='/static', static_folder='static')
app.secret_key = '*()123poiQWE'

# Before all requests, create the following variables
@app.before_request
def authentication():
    if 'id' in session:
        user_data = get_user_data()
        selection_toggle = check_selection_toggle()
        # Get variables for User - Level, Selection Toggle, and Display Name
        g.is_admin = user_data['is_admin']
        g.sel_lock = user_data['sel_lock']
        g.display_name = user_data['display_name']
        g.selection_toggle = selection_toggle['selections_toggle']
        # Get variable for Global - Selection Toggle.

# User Registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        display_name = request.form['display_name']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Check for empty fields
        if not username or not display_name or not password or not confirm_password:
            flash('All fields are required.', 'error')
        # Check for matching password input
        elif password != confirm_password:
            flash('Passwords do not match.', 'error')
        # Password complexity validation
        elif not (
                len(password) >= 8 and
                re.search(r'[A-Z]', password) and  # At least one uppercase letter
                re.search(r'[a-z]', password) and  # At least one lowercase letter
                re.search(r'\d', password) and  # At least one digit
                re.search(r'[!@#$%^&*()_+=\-[\]{};:\'",.<>?]', password)  # At least one symbol
        ):
            flash(
                'Password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, one digit, and one symbol.',
                'error')
        else:
            # Check if the username already exists
            if register_check_existing_user(username):
                flash('Username already exists. Please choose a different one.', 'error')
            else:
                # Register the user
                conn, cursor = connect_to_database('uonew.db')
                hashed_password = generate_password_hash(password)
                cursor.execute('INSERT INTO users (username, password, display_name) VALUES (?, ?, ?)', (username, hashed_password, display_name))
                conn.commit()
                conn.close()
                flash('Registration successful! Please log in.', 'success')
                return redirect(url_for('login'))

        return redirect(url_for('register'))

    return render_template('register.html')

# Login Page Functionality
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_data = login_check_existing_user(username, password)
        # Redirect to MA if user matches above check_existing_user function
        if user_data:
            session['id'] = user_data['id']
            flash('Login successful!', 'success')
            return redirect('ma')
        if not username and not password:
            flash('Please fill in both fields', 'error')
            return render_template('login.html')
        elif not username:
            flash('Please enter a username.', 'error')
            return render_template('login.html')
        elif not password:
            flash('Please enter a password.', 'error')
            return render_template('login.html')
        if not user:
            flash('Incorrect username or password.', 'error')
            return render_template('login.html')
    return render_template('login.html')

# Logout Functionality
@app.route('/logout')
def logout():
    session.pop('id', None)
    flash('You have been logged out.', 'success')
    return redirect('login')

# Toggles enabling and disabling round of Mastery Link Selections
@app.route('/global_selection_toggle', methods=['POST'])
def global_selection_toggle():
    selection_toggle = check_selection_toggle()
    conn, cursor = connect_to_database('uonew.db')
    if selection_toggle[0] == 0:
        cursor.execute("UPDATE global SET selections_toggle = 1 WHERE id = 1")
    else:
        cursor.execute("UPDATE global SET selections_toggle = 0 WHERE id = 1")
    conn.commit()
    conn.close()
    return redirect(url_for('a_selections'))

# Reset link selections for ALL users
@app.route('/reset_all_selections', methods=['POST'])
def reset_all_selections():
    if request.method == 'POST':
        conn, cursor = connect_to_database('uonew.db')
        cursor.execute("DELETE FROM selections")
        conn.commit()
        conn.close()
        flash('All User selections have been reset')
        return redirect(url_for('a_selections'))

###
# User - Selections Management
###

# Function for the user to update an individual link selection
@app.route('/update_user_selection', methods=['POST'])
def update_user_selection():
    if request.method == 'POST':
        sel_id = request.form['selection_id']
        quality = request.form['quality']
        quantity = request.form['quantity']
        mclink_id = request.form['mclink_id']
        sel_name = request.form['link_name']
        if quantity == '0':
            flash('Just Delete it!!', 'error')
            return redirect(url_for('selections'))
        if not (quality and quantity):
            flash('All fields are required', 'error')
            return redirect(url_for('selections'))

        conn, cursor = connect_to_database('uonew.db')

        # Check if quality has been changed
        cursor.execute("SELECT quality FROM mclinks WHERE id = ?", (mclink_id,))
        old_quality = cursor.fetchone()[0]

        if old_quality != quality:
            # Quality has been changed, update mclink_id and quanity
            cursor.execute("SELECT id, quantity FROM mclinks WHERE name = ? AND quality = ?", (sel_name, quality,))
            mclinks = cursor.fetchone()
            if int(quantity) > int(mclinks['quantity']):
                flash('Not enough of that link available', 'error')
                return redirect(url_for('selections'))
            cursor.execute("UPDATE selections SET s_quantity = ?, mclink_id = ? WHERE id = ?", (quantity, mclinks['id'], sel_id,))
            conn.commit()
            conn.close()
            flash('Your selection has been updated')
            return redirect(url_for('selections'))
        else:
            # Quality has not been changed, only update s_quantity
            cursor.execute("SELECT id, quantity FROM mclinks WHERE name = ? AND quality = ?", (sel_name, quality,))
            mclinks = cursor.fetchone()
            if int(quantity) > int(mclinks['quantity']):
                flash('Not enough of that link available', 'error')
                return redirect(url_for('selections'))
            cursor.execute("UPDATE selections SET s_quantity = ? WHERE id = ?", (quantity, sel_id,))
            conn.commit()
            conn.close()
            flash('Your selection has been updated')
            return redirect(url_for('selections'))

@app.route('/admin_update_user_selection', methods=['POST'])
def admin_update_user_selection():
    if request.method == 'POST':
        sel_id = request.form['selection_id']
        quality = request.form['quality']
        quantity = request.form['quantity']
        mclink_id = request.form['mclink_id']
        sel_name = request.form['link_name']
        if quantity == '0':
            flash('Just Delete it!!', 'error')
            return redirect(url_for('a_selections'))
        if not (quality and quantity):
            flash('All fields are required', 'error')
            return redirect(url_for('a_selections'))

        conn, cursor = connect_to_database('uonew.db')

        # Get quality of selection before being updated
        cursor.execute("SELECT quality FROM mclinks WHERE id = ?", (mclink_id,))
        old_quality = cursor.fetchone()[0]

        if old_quality != quality:
            # Quality has been changed, update mclink_id
            cursor.execute("SELECT id, quantity FROM mclinks WHERE name = ? AND quality = ?", (sel_name, quality,))
            mclinks = cursor.fetchone()
            if int(quantity) > int(mclinks['quantity']):
                flash('Not enough of that link available', 'error')
                return redirect(url_for('a_selections'))
            cursor.execute("UPDATE selections SET s_quantity = ?, mclink_id = ? WHERE id = ?", (quantity, mclinks['id'], sel_id,))
            conn.commit()
            conn.close()
            flash('Your selection has been updated')
            return redirect(url_for('a_selections'))
        else:
            # Quality has not been changed, only update s_quantity
            cursor.execute("SELECT id, quantity FROM mclinks WHERE name = ? AND quality = ?", (sel_name, quality,))
            mclinks = cursor.fetchone()
            if int(quantity) > int(mclinks['quantity']):
                flash('Not enough of that link available', 'error')
                return redirect(url_for('a_selections'))
            cursor.execute("UPDATE selections SET s_quantity = ? WHERE id = ?", (quantity, sel_id,))
            conn.commit()
            conn.close()
            flash('Your selection has been updated')
            return redirect(url_for('a_selections'))


# Function for the user to delete an individual link selection
@app.route('/delete_user_selection', methods=['POST'])
def delete_user_selection():
    if request.method == 'POST':
        conn, cursor = connect_to_database('uonew.db')
        user_data = get_user_data()
        user_id = user_data['id']
        selection_id = request.form['selection_id']
        cursor.execute("DELETE FROM selections WHERE user_id =? AND id =?", (user_id, selection_id))
        conn.commit()
        conn.close()
        flash('Your selection has been removed', 'success')
        return redirect(url_for('selections'))

# Function for the admin to delete a users individual link selection
@app.route('/admin_delete_user_selection', methods=['POST'])
def admin_delete_user_selection():
    if request.method == 'POST':
        selection_id = request.form['selection_id']
        conn, cursor = connect_to_database('uonew.db')
        cursor.execute("DELETE FROM selections WHERE id =?", (selection_id,))
        conn.commit()
        conn.close()
        flash('Their selection has been removed', 'success')
        return redirect(url_for('a_selections'))

# Function for the user to delete an individual link selection
@app.route('/reset_user_selections', methods=['POST'])
def reset_user_selections():
    if request.method == 'POST':

        user_data = get_user_data()
        user_id = user_data['id']

        conn, cursor = connect_to_database('uonew.db')
        cursor.execute("DELETE FROM selections WHERE user_id =?", (user_id,))

        conn.commit()
        conn.close()

        flash('All your selections have been reset')
        status = user_data['sel_lock']

        print(status)
        return redirect(url_for('selections'))

# Function for the user to lock in or to keep adding/editing link selections
@app.route('/user_selection_toggle', methods=['POST'])
def user_selection_toggle():
    print("TEST")
    user_data = get_user_data()
    user_id = user_data['id']
    print("User Data:", user_data)
    conn, cursor = connect_to_database('uonew.db')
    selection_status = user_data['sel_lock']  # Corrected to use user_data instead of user_id
    print('User ID:', user_id)
    print("Selection Status:", selection_status)

    if selection_status == 0:
        cursor.execute("UPDATE users SET sel_lock = 1 WHERE id = ?", (user_id,))
        g.sel_lock = 1
        flash('Your selections are set!', 'success')
    else:
        cursor.execute("UPDATE users SET sel_lock = 0 WHERE id = ?", (user_id,))
        g.sel_lock = 0
        flash('Your selections are open!', 'success')

    conn.commit()
    conn.close()

    # Redirect or render_template as required
    return redirect(url_for('selections'))  # Example redirect back to selections page



# Function for admin to update any user column from user table in db
@app.route('/admin_update_user', methods=['POST'])
def admin_update_user():
    if request.method == 'POST':
        # Extract data from the form submission
        user_id = request.form['id']
        username = request.form['username']
        display_name = request.form['display_name']
        password = request.form['password']
        user_level = request.form['user_level']

        conn, cursor = connect_to_database('uonew.db')

        if password:  # Check if password is not empty
            hashed_password = generate_password_hash(password)
        else:
            # Fetch the existing hashed password from the database
            cursor.execute("SELECT password FROM users WHERE id = ?", (user_id,))
            hashed_password = cursor.fetchone()[0]  # Get the first column of the first row

        cursor.execute("""
                    UPDATE users
                    SET username = ?,
                        display_name = ?,
                        password = ?,
                        is_admin = ?
                    WHERE id = ?
                """, (username, display_name, hashed_password, user_level, user_id))

        # Commit the transaction
        conn.commit()

        # Close the connection
        conn.close()

        flash('User updated successfully', 'success')
        return redirect(url_for('a_users'))

# Function for admin to a new user to the user table in db
@app.route('/admin_add_user', methods=['POST'])
def admin_add_user():
    if request.method == 'POST':
        # Extract data from the form submission
        username = request.form['name']
        password = request.form['password']
        user_level = request.form['user_level']

        if not (username and password and user_level):
            flash('All fields are required', 'error')
            return redirect(url_for('a_users'))

        conn, cursor = connect_to_database('uonew.db')

        hashed_password = generate_password_hash(password)

        cursor.execute("INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?);", (username, hashed_password, user_level))

        # Commit the transaction
        conn.commit()

        # Close the connection
        conn.close()

        flash('User added successfully', 'success')
        return redirect(url_for('a_users'))

# Function for admin remove a user from the user table in db
@app.route('/delete_a_user', methods=['POST'])
def delete_a_user():
    if request.method == 'POST':
        # Extract data from the form submission
        user_id = request.form['id']

        conn, cursor = connect_to_database('uonew.db')

        cursor.execute("DELETE FROM users WHERE id = ?;", (user_id))

        # Commit the transaction
        conn.commit()

        # Close the connection
        conn.close()

        flash('User deleted successfully', 'success')
        return redirect(url_for('a_users'))

# Route for updating Links
@app.route('/update_a_mclinks', methods=['POST'])
def update_a_mclinks():
    if request.method == 'POST':
        # Extract data from the form submission
        mclink_id = request.form['id']
        name = request.form['name']
        quality = request.form['quality']
        quantity = request.form['quantity']
        market_price = request.form['market_price']
        guild_price = request.form['guild_price']

        if not (name and quality and quantity and market_price and guild_price):
            flash('All fields are required', 'error')
            return redirect(url_for('a_mclinks'))

        conn, cursor = connect_to_database('uonew.db')
        # Perform the update operation
        cursor.execute("""
            UPDATE mclinks
            SET name = ?,
                quality = ?,
                quantity = ?,
                market_price = ?,
                guild_price = ?
            WHERE id = ?
        """, (name, quality, quantity, market_price, guild_price, mclink_id))

        # Commit the transaction
        conn.commit()

        # Close the connection
        conn.close()

        flash('Database updated successfully', 'success')
        return redirect(url_for('a_mclinks'))

@app.route('/delete_a_mclink', methods=['POST'])
def delete_a_mclink():
    if request.method == 'POST':
        # Extract data from the form submission
        mclink_id = request.form['id']

        conn, cursor = connect_to_database('uonew.db')

        cursor.execute("DELETE FROM mclinks WHERE id = ?;", (mclink_id,))

        # Commit the transaction
        conn.commit()

        # Close the connection
        conn.close()

        flash('Mastery Chain Link deleted successfully', 'success')
        return redirect(url_for('a_mclinks'))

@app.route('/add_a_mclink', methods=['POST'])
def add_a_mclink():
    if request.method == 'POST':
        # Extract data from the form submission
        name = request.form['name']
        quality = request.form['quality']
        quantity = request.form['quantity']
        market_price = request.form['market_price']
        guild_price = request.form['guild_price']

        if not (name and quality and quantity and market_price and guild_price):
            flash('All fields are required', 'error')
            return redirect(url_for('a_mclinks'))

        conn, cursor = connect_to_database('uonew.db')

        cursor.execute("INSERT INTO mclinks (name, quality, quantity, market_price, guild_price) VALUES (?, ?, ?, ?, ?);", (name, quality, quantity, market_price, guild_price))

        # Commit the transaction
        conn.commit()

        # Close the connection
        conn.close()

        flash('Mastery Chain Link added successfully', 'success')
        return redirect(url_for('a_mclinks'))

# Route for '/' (Login Check)
@app.route('/')
def login_check():
    # Check if user is logged in
    if 'id' in session:
        # If logged in, redirect to '/ma'
        return redirect(url_for('ma'))
    else:
        # If not logged in, redirect to '/login'
        return redirect(url_for('login'))

# Route for Index / Main Template
@app.route('/index')
def index():
    return render_template('index.html')

# Route for Members' Area
@app.route('/ma')
def ma():
    return render_template('ma.html')

# Route for Admin Page
@app.route('/admin')
def admin():
    return render_template('admin.html')

# Route for User - Mastery Chain Link List
@app.route('/mclinks', methods=['GET'])
def mclinks():
    mclinks_data = select_links()
    return render_template('mclinks.html', mclinks_data=mclinks_data)

# Route for Admin - Mastery Chain Link List
@app.route('/a_mclinks', methods=['GET'])
def a_mclinks():
    mclinks_data = select_links()
    return render_template('a_mclinks.html', mclinks_data=mclinks_data)

# Route for User - Mastery Chain Link Selections
@app.route('/selections', methods=['GET', 'POST'])
def selections():
    # Get User ID
    user_data = get_user_data()
    user_id = user_data['id']

    # Initiate DB Connection
    conn, cursor = connect_to_database('uonew.db')

    # Get unique names in database for dropdown menu
    cursor.execute("SELECT DISTINCT name FROM mclinks;")
    unique_names = cursor.fetchall()

    # Get total cost of all links chosen by user
    cursor.execute("SELECT SUM(links_total) FROM selections WHERE user_id=?", (user_id,))
    total_links_total = cursor.fetchone()[0]
    conn.close()

    # Get all selected links of user (including mclinks data)
    selections_data = select_selections(user_id)

    return render_template('selections.html', unique_names=unique_names, selections_data=selections_data, total_links_total=total_links_total)

@app.route('/add_selection', methods=['POST'])
def add_selection():
    if request.method == 'POST':
        name = request.form['name']
        quality = request.form['quality']
        quantity = int(request.form['quantity'])

        if quantity == '0':
            flash('Just Delete it!!', 'error')
            return redirect(url_for('selections'))

        # Get User ID
        user_data = get_user_data()
        user_id = user_data['id']

        # Ensure all fields are used
        if not (name and quality and quantity):
            flash('All fields are required', 'error')
            return redirect(url_for('selections'))

        # Initiate DB Connection
        conn, cursor = connect_to_database('uonew.db')

        cursor.execute("SELECT * FROM mclinks WHERE name=? AND quality=?", (name, quality))
        mclink_data = cursor.fetchone()

        if not mclink_data:
            flash('No matching link found', 'error')
            return redirect(url_for('selections'))

        if quantity > mclink_data['quantity']:
            flash('Not enough quantity available', 'error')
            return redirect(url_for('selections'))

        # Check if selection exists
        cursor.execute("SELECT * FROM selections WHERE mclink_id=? AND user_id=?", (mclink_data['id'], user_id))
        existing_selection = cursor.fetchone()

        if existing_selection:
            # If selection exists, update selection
            new_quantity = existing_selection['s_quantity'] + quantity
            if new_quantity > mclink_data['quantity']:
                flash('Not enough quantity available', 'error')
                return redirect(url_for('selections'))
            else:
                cursor.execute("UPDATE selections SET s_quantity=? WHERE id=?", (new_quantity, existing_selection['id']))
        else:
            # If selection doesn't exist, add new selection
            links_total = quantity * mclink_data['guild_price']
            cursor.execute("INSERT INTO selections (mclink_id, s_quantity, user_id, links_total) VALUES (?, ?, ?, ?)", (mclink_data['id'], quantity, user_id, links_total))

        conn.commit()
        conn.close()

        flash('Selection added successfully', 'success')
        return redirect(url_for('selections'))


# Route for Admin - Mastery Chain Link Selections
@app.route('/a_selections', methods=['POST', 'GET'])
def a_selections():
    if g.selection_toggle == 1:
        # If selection feature is enabled
        s_toggle = 'ON'
    else:
        # If selection feature is not enabled
        s_toggle = 'OFF'

    selection_data = select_selections()

    conn, cursor = connect_to_database('uonew.db')

    # Get unique names in database
    cursor.execute(
        "SELECT DISTINCT selections.user_id, users.id, users.display_name, users.sel_lock FROM selections INNER JOIN users ON selections.user_id = users.id;")
    unique_names = cursor.fetchall()



    # Fetch total sum of links for each user
    totals = {}
    for names in unique_names:
        user_id = names['id']
        cursor.execute("SELECT SUM(links_total) FROM selections WHERE user_id=?", (user_id,))
        total_price = cursor.fetchone()[0]
        totals[user_id] = total_price

    # Get unique links in database
    cursor.execute("SELECT DISTINCT name FROM mclinks;")
    unique_links = cursor.fetchall()

    conn.commit()
    conn.close()

    return render_template('a_selections.html', s_toggle=s_toggle, selection_data=selection_data,
                           unique_names=unique_names, totals=totals, unique_links=unique_links)


@app.route('/mclinks_delivery')
def mclinks_delivery():
    return render_template('mclinks_delivery.html')

# Route for Admin - User Management
@app.route('/a_users')
def a_users():
    users_data = select_all_users()
    return render_template('a_users.html', users_data=users_data)

# Route for User - User Management
@app.route('/user', methods=['GET', 'POST'])
def user():
    user_data = get_user_data()
    return render_template('user.html', user_data=user_data)

@app.route('/user_update_user', methods=['POST'])
def user_update_user():
    if request.method == 'POST':
        # Extract data from the form submission
        user_id = request.form['id']
        username = request.form['username']
        display_name = request.form['display_name']

        conn, cursor = connect_to_database('uonew.db')

        cursor.execute("UPDATE users SET username = ?, display_name = ? WHERE id = ?",
                       (username, display_name, user_id))

        # Commit the transaction
        conn.commit()

        # Close the connection
        conn.close()
        g.display_name = display_name
        flash('User details updated successfully', 'success')
        return redirect(url_for('user'))

@app.route('/user_update_pass', methods=['POST'])
def user_update_pass():
    if request.method == 'POST':
        # Extract data from the form submission
        user_id = request.form['id']
        old_password = request.form['old_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        # Check for empty fields
        if not old_password or not new_password or not confirm_password:
            flash('All fields are required.', 'error')
        # Check for matching password input
        elif new_password != confirm_password:
            flash('Passwords do not match.', 'error')
        # Password complexity validation
        elif not (
                len(new_password) >= 8 and
                re.search(r'[A-Z]', new_password) and  # At least one uppercase letter
                re.search(r'[a-z]', new_password) and  # At least one lowercase letter
                re.search(r'\d', new_password) and  # At least one digit
                re.search(r'[!@#$%^&*()_+=\-[\]{};:\'",.<>?]', new_password)  # At least one symbol
        ):
            flash(
                'Password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, one digit, and one symbol.',
                'error')
        else:

            conn, cursor = connect_to_database('uonew.db')
            hashed_password = generate_password_hash(new_password)
            cursor.execute('UPDATE users SET password = ? WHERE id = ?', (hashed_password, user_id))
            conn.commit()
            conn.close()
            flash('Password Updated Successful', 'success')

    return redirect(url_for('user'))

if __name__ == '__main__':
    app.run(debug=True)
