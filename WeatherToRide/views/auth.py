
from .. import app, utils

from ..forms import *
from ..models import *

from flask import abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required, login_user, logout_user

import sys

@app.route('/login', methods=['GET', 'POST'])
def login():

    # If the user is already logged in
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    form = LoginForm()

    # If the user is submitting a valid form
    if form.validate_on_submit():

        # Get the form fields
        email = form.email.data
        password = form.password.data

        # Lookup the user in the database
        user = User.query.filter_by(email=email).first()

        # Check if the user exists
        if user:

            # Check if the password is correct
            if user.validate_password(password):
                login_user(user)
                print(f'\n{current_user.email} has logged in.\n', file=sys.stderr)
                flash(f'Welcome, {current_user.first_name}.', 'success')
                return redirect(url_for('dashboard'))

            else:
                flash('Wrong password.', 'danger')

        else:
            flash('That e-mail address is not registered with an account.', 'danger')

    # If the submitted form has error(s)
    if form.errors:
        print('\nError(s) detected in submitted form:\n', file=sys.stderr)
        for fieldName, errorMessages in form.errors.items():
            for err in errorMessages:
                print(f'* {err}\n', file=sys.stderr)

    return render_template('auth/login.html', user=current_user, form=form)

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    print(f'\n{current_user.email} is logging out.\n', file=sys.stderr)
    logout_user()
    flash('You are now logged out.', 'success')
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():

    # If the user is already logged in
    if current_user.is_authenticated:
        flash('Please log out before trying to register a new account.', 'danger')
        return redirect(url_for('dashboard'))

    form = RegistrationForm()

    # If the user is submitting a valid form
    if form.validate_on_submit():

        # Create the new user
        user = User(
            email=form.email.data, 
            password=form.password.data, 
            first_name=form.first_name.data, 
            last_name=form.last_name.data, 
            phone=form.phone.data
        )

        # Add the user to the database
        db.session.add(user)
        db.session.commit()

        print(f'\n{user.email} has registered an account.\n', file=sys.stderr)

        # # The subject of the activation e-mail
        # subject = 'Confirm your e-mail address'

        # # The secure token that is linked to this user
        # token = security.ts.dumps(user.email, salt='email-confirm-key')

        # # The complete e-mail confirmation URL for this user
        # confirm_url = url_for(

        #     # The function to call
        #     'confirm_email',

        #     # The token to pass to the function
        #     token=token,

        #     # Return an absolute URL instead of a relative one
        #     _external=True

        # )

        # # The HTML for the activation e-mail
        # html = render_template(

        #     # The template to send
        #     'email/confirm.html', 

        #     # The user that is creating this account
        #     user=user, 

        #     # The parameters to pass to the template
        #     confirm_url=confirm_url

        # )

        # email.send(user.email, subject, html)

        # sms.send(user.phone, 'Thanks for trying my app!')

        flash('You are now registered and may log in.', 'success')
        return redirect(url_for('login'))

    # If the submitted form has error(s)
    if form.errors:
        print('\nError(s) detected in submitted form:\n', file=sys.stderr)
        for fieldName, errorMessages in form.errors.items():
            for err in errorMessages:
                print(f'* {err}\n', file=sys.stderr)

    return render_template('auth/register.html', user=current_user, form=form)

@app.route('/confirm/<token>')
def confirm_email(token):

    # Extract the user's e-mail address from the confirmation token
    try:
        email = utils.ts.loads(token, salt="email-confirm-key", max_age=86400)
    except:
        abort(404)

    # Lookup the user by their e-mail address
    user = User.query.filter_by(email=email).first_or_404()

    # Confirm their e-mail address in the database
    user.email_confirmed = True

    # Commit the changes
    db.session.add(user)
    db.session.commit()

    flash('Your e-mail address has been confirmed!', 'success')

    return redirect(url_for('login'))
