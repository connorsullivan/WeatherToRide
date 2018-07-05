from flask import request, render_template, flash, redirect, url_for, abort
from flask_login import login_required, current_user, login_user, logout_user

from .models import User
from .forms import RegistrationForm
from .utilities import email, sms, security

from . import app, db, lm

# Redirect /route/ requests to /route
@app.before_request
def clear_trailing():
    rp = request.path
    if rp != '/' and rp.endswith('/'):
        return redirect(rp[:-1])

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.errorhandler(404)
def page_not_found(e):
    return "Uh-oh! That page cannot be found!", 404

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/register', methods=['GET', 'POST'])
def register():

    form = RegistrationForm()

    if form.validate_on_submit():

        # Add the user to the database
        user = User( 
            username=form.username.data, 
            password=form.password.data, 
            email=form.email.data, 
            phone=form.phone.data
        )

        db.session.add(user)
        db.session.commit()

        # The subject of the activation e-mail
        subject = 'Activate Your Account'

        # The secure token that is linked to this user
        token = security.ts.dumps(user.email, salt='email-confirm-key')

        # The complete e-mail confirmation URL for this user
        confirm_url = url_for(

            # The function to call
            'confirm_email',

            # The token to pass to the function
            token=token,

            # Return an absolute URL instead of a relative one
            _external=True

        )

        # The HTML for the activation e-mail
        html = render_template(

            # The template to send
            'email/confirm.html',

            # The username for the account to be activated
            username=user.username,

            # The parameters to pass to the template
            confirm_url=confirm_url

        )

        email.send(user.email, subject, html)

        # sms.send(user.phone, 'Thanks for trying my app!')

        flash('Your account was created! Check your e-mail for instructions on activating it.', 'success')

        return redirect(url_for('index'))

    return render_template('register.html', form=form)

@app.route('/confirm/<token>')
def confirm_email(token):

    try:
        email = security.ts.loads(token, salt="email-confirm-key", max_age=86400)
    except:
        abort(404)

    user = User.query.filter_by(email=email).first_or_404()

    user.email_confirmed = True

    db.session.add(user)
    db.session.commit()

    flash('Your account is now activated! You may now log in.', 'success')

    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():

    # If the user is already logged in
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    # If the user is submitting a login form
    if request.method == 'POST':

        # Get the form fields
        username = request.form['username']
        password = request.form['password']

        # Lookup the user in the database
        user = User.query.filter_by(username=username).first()

        # If the username doesn't exist
        if not user:
            error = 'That user does not exist.'
            return render_template('login.html', error=error)

        # Check the provided password
        if user.validate_password(password):

            # Check that the user's e-mail is confirmed
            if user.email_confirmed:
                login_user(user)
                flash('Welcome, {}.'.format(username), 'success')
                return redirect(url_for('index'))

            # If the user's e-mail is not yet confirmed
            else:
                error = 'You must confirm your e-mail before logging in.'
                return render_template('login.html', error=error)

        # If the password is incorrect
        else:
            error = 'Wrong password. Try something else?'
            return render_template('login.html', error=error)

    # If the user is making a GET request
    return render_template('login.html')

@app.route('/users')
@login_required
def show_all_users():
    users = User.query.order_by(User.username).all()
    return render_template('users.html', users=users)

@app.route('/users/<username>')
@login_required
def profile(username):
    user = User.query.filter_by(username=username).first()
    return render_template('profile.html', user=user)

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash('You are now logged out.', 'success')
    return redirect(url_for('login'))
