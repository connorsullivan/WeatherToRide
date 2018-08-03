
from .. import app, db, forms, models

from flask import abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required, login_user, logout_user

from itsdangerous import URLSafeTimedSerializer

import sys

ts = URLSafeTimedSerializer(app.config["SECRET_KEY"])

MAX_USERS = 5

@app.route('/login', methods=['GET', 'POST'])
def login():

    # Redirect if the user is already logged in
    if current_user.is_authenticated:
        return redirect(url_for('location_dashboard'))

    # Get a LoginForm from forms.py
    form = forms.LoginForm()

    # Validate a submitted form
    if form.validate_on_submit():

        # Extract the user credentials
        email = form.email.data
        password = form.password.data

        # Try to find the user by their e-mail
        user = models.User.query.filter_by(email=email).first()

        # If a user with a matching e-mail was found
        if user:

            # Check if the provided password is correct
            if user.validate_password(password):

                # Log the user in
                login_user(user)

                # Print a message to the console
                print(f'\n{current_user.email} has logged in.\n', file=sys.stderr)

                # Flash a message to the user
                flash(f'Welcome, {current_user.name}.', 'success')

                # Redirect to the dashboard
                return redirect(url_for('location_dashboard'))

            # If the password is incorrect
            else:

                # Flash a message to the user
                flash('Wrong password.', 'danger')

        # If a user with a matching e-mail could not be found
        else:

            # Flash a message to the user
            flash('That e-mail address is not registered with an account.', 'danger')

    # Send the login page to the user
    return render_template('login.html', user=current_user, form=form)

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():

    # Print a message to the console
    print(f'\n{current_user.email} is logging out.\n', file=sys.stderr)

    # Log out the current user
    logout_user()

    # Flash a message to the user
    flash('You are now logged out.', 'success')

    # Redirect to the login page
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():

    # If the user is already logged in
    if current_user.is_authenticated:

        # Flash a message to the user
        flash('Please log out before trying to register a new account.', 'danger')

        # Redirect to the dashboard
        return redirect(url_for('location_dashboard'))

    # Get an instance of the RegistrationForm from forms.py
    form = forms.RegistrationForm()

    # If a valid RegistrationForm was submitted
    if form.validate_on_submit():

        # Make sure the user limit hasn't been reached
        users = models.User.query.all()

        if len(users) < MAX_USERS:

            # Create the new user
            user = models.User( 
                email=form.email.data, 
                password=form.password.data, 
                name=form.name.data, 
                phone=form.phone.data 
            )

            # Add the user to the database
            db.session.add(user)

            # Commit the changes
            db.session.commit()

            # Print a message to the console
            print(f'\n{user.email} has registered an account.\n', file=sys.stderr)

            # Flash a message to the user
            flash('You are now registered and may log in.', 'success')

            # Redirect to the login page
            return redirect(url_for('login'))
        
        # If the max user count has been reached
        else:
            flash('Sorry. We are not acccepting new users at the moment.', 'danger')

    # Send the register page to the user
    return render_template('register.html', user=current_user, form=form)

@app.route('/confirm-email/<token>')
def confirm_email(token):

    # Extract the user's e-mail address from the token
    try:
        email = ts.loads(token, salt="email-confirm-key", max_age=86400)

    # If the token is illegitimate or expired
    except:
        abort(404)

    # Find the user by their e-mail address
    user = User.query.filter_by(email=email).first_or_404()

    # Confirm the user's e-mail address in the database
    user.email_confirmed = True

    # Commit the change to the database
    db.session.add(user)
    db.session.commit()

    # Notify the user of the change
    flash('Your e-mail address has been confirmed!', 'success')

    # Redirect the user to the login screen
    return redirect(url_for('login'))
