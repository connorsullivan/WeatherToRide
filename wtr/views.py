from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from .models import User
from .forms import LoginForm, RegistrationForm
from .utilities import email, sms, security

from . import app, db, lm

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

        flash('Welcome, {}! You can now log in.'.format(user.first_name), 'success')

        return redirect(url_for('login'))

    return render_template('register.html', form=form, user=current_user)

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

@app.route('/login', methods=['GET', 'POST'])
def login():

    # If the user is already logged in
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    form = LoginForm()

    # If the user is submitting a login form
    if form.validate_on_submit():

        # Get the form fields
        email = form.email.data
        password = form.password.data

        # Lookup the user in the database
        user = User.query.filter_by(email=email).first()

        # If the username doesn't exist
        if not user:
            error = 'That e-mail is not registered with an account.'
            return render_template('login.html', error=error, form=form, user=current_user)

        # Check the provided password
        if user.validate_password(password):
            login_user(user)
            flash('Welcome, {}.'.format(user.first_name), 'success')
            return redirect(url_for('dashboard'))

        # If the password is incorrect
        else:
            error = 'Wrong password.'
            return render_template('login.html', error=error, form=form, user=current_user)

    # If the user is making a GET request
    return render_template('login.html', form=form, user=current_user)

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)

@app.route('/users')
@login_required
def show_all_users():
    users = User.query.order_by(User.id).all()
    return render_template('users.html', user=current_user, users=users)

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash('You are now logged out.', 'success')
    return redirect(url_for('login'))

@app.route('/test', methods=['GET', 'POST'])
def test_route():
    if request.method == 'POST':
        return 'POST request: ' + request.form['test']
    else:
        return 'This route is for testing purposes. \
                    POST form variable "test" to see it displayed here.'
