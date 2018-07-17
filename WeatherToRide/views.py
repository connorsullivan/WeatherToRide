from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from .models import User, Location
from .forms import CommuteForm, LocationForm, LoginForm, RegistrationForm
from .utilities import email, sms, security

from . import app, db, lm

import sys

# Reform '/route/' requests to '/route'
@app.before_request
def clear_trailing():
    rp = request.path
    if rp != '/' and rp.endswith('/'):
        return redirect(rp[:-1])

# Tell Flask-Login how to load users from the database
@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

# 404 Error Handling, status code explicitly set
@app.errorhandler(404)
def page_not_found(e):
    return "Uh-oh! That page cannot be found!", 404

@app.route('/')
def index():
    return render_template('index.html', user=current_user)

@app.route('/about')
def about():
    return render_template('about.html', user=current_user)

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

        # If the username doesn't exist
        if not user:
            error = 'That e-mail is not registered with an account.'
            return render_template('login.html', user=current_user, error=error, form=form)

        # Check the provided password
        if user.validate_password(password):
            login_user(user)
            print('\n{} has logged in.\n'.format(user.email), file=sys.stderr)
            flash('Welcome, {}.'.format(user.first_name), 'success')
            return redirect(url_for('dashboard'))

        # If the password is incorrect
        else:
            error = 'Wrong password.'
            return render_template('login.html', user=current_user, error=error, form=form)

    # If there are errors in the submitted form
    if form.errors:
        print('\nError(s) in submitted Login form:\n', file=sys.stderr)
        for fieldName, errorMessages in form.errors.items():
            for err in errorMessages:
                print(err + '\n', file=sys.stderr)

    # If the user is making a GET request
    return render_template('login.html', user=current_user, form=form)

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    print('\n{} has logged out.\n'.format(current_user.email), file=sys.stderr)
    logout_user()
    flash('You are now logged out.', 'success')
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():

    form = RegistrationForm()

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

        # Log in the new user
        login_user(user)
        print('\n{} has created an account.\n'.format(user.email), file=sys.stderr)
        flash('Welcome, {}.'.format(user.first_name), 'success')
        return redirect(url_for('dashboard'))

    # If there are errors in the submitted form
    if form.errors:
        print('\nError(s) in submitted Registration form:\n', file=sys.stderr)
        for fieldName, errorMessages in form.errors.items():
            for err in errorMessages:
                print(err + '\n', file=sys.stderr)

    return render_template('register.html', user=current_user, form=form)

@app.route('/confirm/<token>')
def confirm_email(token):

    # Extract the user's e-mail address from the confirmation token
    try:
        email = security.ts.loads(token, salt="email-confirm-key", max_age=86400)
    except:
        abort(404)

    # Lookup the user by their e-mail address
    user = User.query.filter_by(email=email).first_or_404()

    # Confirm their e-mail address in the database
    user.email_confirmed = True

    # Commit the changes
    db.session.add(user)
    db.session.commit()

    flash('Thanks for confirming your e-mail address!', 'success')

    return redirect(url_for('login'))

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():

    form = LocationForm()

    # If the user is submitting a valid form
    if form.validate_on_submit():

        # If the user has less than the maximum 3 locations
        if len(current_user.locations) < 3:

            # Create the new location for this user
            location = Location(
                title=form.title.data,
                lat=form.lat.data,
                lng=form.lng.data,
                user_id=current_user.id
            )

            # Add the location to the database
            db.session.add(location)
            db.session.commit()

            print('\n{} has added a location.\n'.format(current_user.email), file=sys.stderr)
            flash('Location added!', 'success')
            return redirect(url_for('dashboard'))

        else:
            flash('Please remove an existing location before trying to add another.', 'danger')

    # If there are errors in the submitted form
    if form.errors:
        print('\nError(s) in submitted Location form:\n', file=sys.stderr)
        for fieldName, errorMessages in form.errors.items():
            for err in errorMessages:
                print(err + '\n', file=sys.stderr)

    return render_template('dashboard.html', user=current_user, form=form)

@app.route('/users')
@login_required
def show_all_users():
    users = User.query.order_by(User.id).all()
    return render_template('users.html', user=current_user, users=users)

@app.route('/commute/new')
@login_required
def add_commute():
    form = CommuteForm()
    return render_template('new_commute.html', user=current_user, form=form)
