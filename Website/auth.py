from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
import boto3

from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)

access_key = 'AKIA2BIH4HLCO6DGGAG7'
secret_access_key = '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'


s3 = boto3.resource(
    service_name = 's3',
    region_name = 'ap-south-1',
    aws_access_key_id = 'AKIA2BIH4HLCO6DGGAG7',
    aws_secret_access_key = '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'
)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email=request.form.get('email')
        password=request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in Successfully', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again', category='error')
        else:
            flash('Email does not exist', category='error')

    return render_template("login.html", user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('first_name')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters', category='error')
        elif password1 != password2:
            flash('Passwords dont Match', category='error')
        elif len(password1) < 7:
            flash('Password shoud be at least 7 characters', category='error')
        else:
            new_user = User(email=email, first_name=first_name, password=generate_password_hash(password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            flash('Account Created!', category='error')
            return redirect(url_for('views.home'))

    return render_template("sign_up.html", user=current_user)

@auth.route('/about')
def about():
    return render_template("about.html", user=current_user)

@auth.route('/converter')
def converter():
    return render_template("converter.html", user=current_user)

@auth.route('/contact')
def contact():
    return render_template("contact.html", user=current_user)

@auth.route('/uploads', methods=['GET', 'POST'])
@login_required
def uploads():
    my_bucket = s3.Bucket('varunkalbhore-s3')
    my_list = []
    for object_summary in my_bucket.objects.filter(Prefix='PlagCheck/' + str(current_user.email)).all():
        print(object_summary.key)
        temp = object_summary.key.split('/')
        my_list.append(temp[2])
    for item in my_list:
        print(item)
    msg = my_list    
    return render_template("uploads.html", msg = msg, user=current_user)

