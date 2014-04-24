from flask import render_template, flash, redirect, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, lm, oid
from forms import LoginForm, PostCreateForm, EditForm
from models import User, Post, ROLE_USER, ROLE_ADMIN
import datetime

@app.route('/')
@app.route('/index')
def index():
    user = g.user
    posts = [
        { 
            'author': { 'nickname': 'John' }, 
            'body': 'Beautiful day in Portland!' 
        },
        { 
            'author': { 'nickname': 'Susan' }, 
            'body': 'The Avengers movie was so cool!' 
        }
    ]
    posts = Post.all()
    #

    return render_template('index.html',
    posts = posts,
    user = user)



# check out if there are any users
@app.before_request
def before_request():
    g.user = current_user

# login view function
@app.route('/login', methods = ['GET', 'POST'])
@oid.loginhandler
def login():
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        session['remember_me'] = form.remember_me.data
        return oid.try_login(form.openid.data, ask_for = ['nickname', 'email'])
    return render_template('login.html', 
        title = 'Sign In',
        form = form,
        providers = app.config['OPENID_PROVIDERS'])

# load user's info from database
@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

# openID login callback
@oid.after_login
def after_login(resp):
    if resp.email is None or resp.email == "":
        flash('Invalid login. Please try again.')
        return redirect(url_for('login'))
    user = User.query.filter_by(email = resp.email).first()
    if user is None:
        nickname = resp.nickname
        if nickname is None or nickname == "":
            nickname = resp.email.split('@')[0]
        nickname = User.make_unique_nickname(nickname)
        user = User(nickname = nickname, email = resp.email, role = ROLE_USER)
        db.session.add(user)
        db.session.commit()
    remember_me = False
    if 'remember_me' in session:
        remember_me = session['remember_me']
        session.pop('remember_me', None)
    login_user(user, remember = remember_me)
    return redirect(request.args.get('next') or url_for('index'))

# logout
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

# nickname unique
@app.route('/create', methods = ['GET', 'POST'])
@login_required
def create():
    post = Post()
    form = PostCreateForm()
    if request.method == 'POST' and form.validate_on_submit():
        form.populate_obj(post)
        post.created = datetime.datetime.now()
        post.user_id = g.user.id
        db.session.add(post)
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('index'))
    return render_template('edit.html',
        form = form)

@app.route('/edit/<int:id>', methods = ['GET', 'POST'])
@login_required
def edit(id):
    post = Post.query.get(id)
    form = EditForm(post.title, post.body)
    if post == None:
        flash('Post not found.')
        return redirect(url_for('index'))
    if post.user_id != g.user.id:
        flash('You cannot delete this post.')
        return redirect(url_for('index'))
    if form.validate_on_submit():
        db.session.query(Post).filter_by(id = id).update(
            {"title": form.title.data, "body":form.body.data})
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('index'))
    elif request.method != "POST":
        form.title.data = post.title
        form.body.data = post.body
    return render_template('edit.html',
        form = form)


@app.route('/delete/<int:id>')
@login_required
def delete(id):
    post = Post.query.get(id)
    if post == None:
        flash('Post not found.')
        return redirect(url_for('index'))
    if post.user_id != g.user.id:
        flash('You cannot delete this post.')
        return redirect(url_for('index'))
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted.')
    return redirect(url_for('index'))



@app.route('/post/<int:id>')
def show_post(id):
    post = Post.get_by_id(id)
    return render_template('post.html', post = post)

@app.route('/user/<nickname>')
@login_required
def user(nickname):    
    user = User.query.filter_by(nickname = nickname).first()
    if user == None:        
        flash('User '+ nickname +' not found.')
        return redirect(url_for('index'))    
    posts = user.posts.all()
    return render_template('index.html',        
        user = user,        
        posts = posts)
