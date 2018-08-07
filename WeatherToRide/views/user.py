
from .. import app, db, forms, models

from ..utils import email

from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from itsdangerous import URLSafeTimedSerializer

import sys

ts = URLSafeTimedSerializer(app.config["SECRET_KEY"])

# Limit how many user accounts can be created at one time
MAX_USERS = 5

@app.route('/register', methods=['GET', 'POST'])
def register():

    # If the user is already logged in
    if current_user.is_authenticated:

        # Flash a message to the user
        flash('Please log out before trying to register a new account.', 'danger')

        # Return the location view
        return redirect(url_for('location_view'))

    # Get an instance of the UserForm from forms.py
    form = forms.UserForm()

    # Validate a submitted form
    if form.validate_on_submit():

        # Make sure the user limit hasn't been reached
        users = models.User.query.all()

        if len(users) < MAX_USERS:

            # Create the new user
            user = models.User( 
                email=form.email.data, 
                password=form.password.data, 
                name=form.name.data 
            )

            # Add the user to the database
            db.session.add(user)

            # Commit the changes
            db.session.commit()

            # The subject for the e-mail to be sent
            subject = 'Confirm E-mail'

            # Secure token that is linked to this user
            token = ts.dumps(user.email, salt='confirm-email')

            # The e-mail confirmation link
            url = url_for('confirm_email', token=token, _external=True)

            # The e-mail message
            html = render_template('email/confirm.html', user=user, url=url)

            # Send the e-mail
            email.send(user.email, subject, html)

            flash('You have successfully registered!', 'success')

            return redirect(url_for('login'))
        
        # If the max user count has been reached
        else:
            flash('Sorry. We are not acccepting new users at the moment.', 'danger')

    # Return the user form
    return render_template('user/user-form.html', user=current_user, form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():

    # Check if the user is already signed in
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    # Get a LoginForm from forms.py
    form = forms.LoginForm()

    # Validate a submitted form
    if form.validate_on_submit():

        # Try to find the user by their e-mail
        user = models.User.query.filter_by(email=form.email.data).first()

        # If a user exists
        if user:

            # Check if the provided password is correct
            if user.validate_password(form.password.data):

                # Sign the user in
                login_user(user)

                flash(f'Welcome, {current_user.name}.', 'success')

                # Redirect to the homepage
                return redirect(url_for('index'))

            # If the password is incorrect
            else:
                flash('Password is incorrect.', 'danger')

        # If the user could not be found
        else:
            flash('That e-mail address is not registered with an account.', 'danger')

    # Return the login page
    return render_template('user/login.html', user=current_user, form=form)

@app.route('/logout')
@login_required
def logout():

    # Sign the current user out
    logout_user()

    flash('You are now logged out.', 'success')

    # Return the login page
    return redirect(url_for('login'))

@app.route('/confirm-email/<token>')
def confirm_email(token):

    # Validate the token
    try:
        email = ts.loads(token, salt='confirm-email', max_age=86400)
    except:
        abort(404)

    # Find the user by their e-mail address
    user = models.User.query.filter_by(email=email).first_or_404()

    # Confirm the user's e-mail address in the database
    user.email_confirmed = True

    # Commit the change to the database
    db.session.commit()

    flash('Your e-mail address has been confirmed!', 'success')

    # Return the login page
    return redirect(url_for('login'))

@app.route('/forgot', methods=['GET', 'POST'])
def forgot_password():

    # Get an EmailForm from forms.py
    form = forms.EmailForm()

    # Validate a submitted form
    if form.validate_on_submit():

        # Try to find the user from the e-mail address
        user = models.User.query.filter_by(email=form.email.data).first()

        # If a user with that e-mail address was found
        if user:

            # The subject for the e-mail to be sent
            subject = 'Reset Password'

            # Secure token that is linked to this user
            token = ts.dumps(user.email, salt='reset-password')

            # The URL for password reset
            url = url_for('reset_password', token=token, _external=True)

            # The e-mail message
            html = render_template('email/reset.html', user=user, url=url)

            # Send the e-mail
            email.send(user.email, subject, html)

            flash('Check your e-mail for instructions on how to reset your password.', 'success')

            return redirect(url_for('index'))

        else:
            flash('There is no user with that e-mail address.', 'danger')

    # Return the forgot password page
    return render_template('user/forgot.html', user=current_user, form=form)

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):

    # Validate the token
    try:
        email = ts.loads(token, salt='reset-password', max_age=86400)
    except:
        abort(404)

    # Get a PasswordForm from forms.py
    form = forms.PasswordForm()

    # Validate a submitted form
    if form.validate_on_submit():

        # Find the user by their e-mail address
        user = models.User.query.filter_by(email=email).first()

        if user:

            # Update the user's password
            user.password = form.password.data

            # Commit the password change to the database
            db.session.commit()

            flash('Your password has been successfully reset!', 'success')

            # Return the login page
            return redirect(url_for('login'))

        else:
            flash('There was a problem updating the password.', 'danger')

    # Return the password reset page
    return render_template('user/reset-password.html', user=current_user, form=form, token=token)

@app.route('/account/delete', methods=['GET', 'POST'])
def delete_user():

    if request.method == 'POST':

        for route in current_user.routes:
            db.session.delete(route)
            db.session.commit()

        for location in current_user.locations:
            db.session.delete(location.forecast)
            db.session.delete(location)
            db.session.commit()

        db.session.delete(current_user)
        db.session.commit()

        logout_user()

        return redirect(url_for('index'))

    return render_template('user/delete-account.html', user=current_user)
