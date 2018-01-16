from flask import Flask, request, redirect, render_template, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:patriots@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(500))

    def __init__(self, title, body):
        self.title = title
        self.body = body


@app.route('/blog')
def index():
    blog_id = request.args.get('id')
    if blog_id:
        blog_id = int(blog_id)
        blog = Blog.query.get(blog_id)
        return render_template('singlepost.html', blog=blog)
    
    bloglist = Blog.query.all()
    return render_template('mainpage.html',title="Get It Done!",bloglist=bloglist)

@app.route('/newpost', methods=['POST','GET'])
def newpost():
    body = ''
    title = ''
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
            blog = Blog(title, body)
            db.session.add(blog)
            db.session.commit()
            return redirect('/blog?id={0}'.format(blog.id))
    return render_template('newpost.html', body=body, title=title)

if __name__ == '__main__':
    app.run()