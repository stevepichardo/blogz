from flask import Flask, request, redirect, render_template, flash, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:patriots@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(500))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner 

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    password = db.Column(db.String(100))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username 
        self.password = password 

@app.before_request
def require_login():
    allowed_routes = ['login','index','signup','list_blogs','static']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/')
def index():
    user_list = User.query.all()
    return render_template('index.html', user_list=user_list)

@app.route('/blog')
def list_blogs():
    blog_id = request.args.get('id')
    owner_id = request.args.get('userId')
    if owner_id:
        bloglist = Blog.query.filter_by(owner_id=owner_id).all()
        return render_template('mainpage.html', title="Blogz", bloglist=bloglist)
    if blog_id:
        blog_id = int(blog_id)
        blog = Blog.query.get(blog_id)
        return render_template('singlepost.html', blog=blog)
    bloglist = Blog.query.all()
    return render_template('mainpage.html', title="Build-a-Blog", bloglist=bloglist)

@app.route('/newpost', methods=['POST','GET'])
def newpost():
    body = ''
    title = ''
    owner = User.query.filter_by(username=session['username']).first()
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        has_error = False
        if not title:
            flash("Please fill in the title",'error')
            has_error = True
        if not body:
            flash("Please fill in the body",'error')
            has_error = True
        if not has_error:
            blog = Blog(title, body, owner)
            db.session.add(blog)
            db.session.commit()
            return redirect('/blog?id={0}'.format(blog.id))
    return render_template('newpost.html', body=body, title=title)

@app.route('/login', methods=['POST','GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash('Logged in')
            return redirect('/newpost')
        elif user and user.password != password:
            flash('Password is incorrect')
            return redirect('/login')
        elif not user:
            flash('Username does not exist')
            return redirect('/login')
    return render_template('login.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

@app.route('/signup', methods=['POST','GET'])
def signup():
    has_error = False
    username = ''
    email = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verifypassword = request.form['verify']

        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            flash('Username already exists')
        if not existing_user:
            if (len(username) < 3 or len(username) > 20) or " " in username:
                has_error = True
                flash('Not a Valid Username')

            if len(password) < 3 or len(password) > 20 or " " in password:
                has_error = True
                flash('Not a valid password')

            if password != verifypassword:
                has_error = True
                flash('Passwords do not match')

            if not has_error:
                new_user = User(username,password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                return redirect('/newpost')
            return redirect('/signup')
    return render_template('signup.html')

if __name__ == '__main__':
    app.run()