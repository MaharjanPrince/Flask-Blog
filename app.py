from flask import Flask, request, render_template, redirect, session, url_for
import json
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# JSON file to store users
USERS_FILE = 'users.json'

# Helper functions
def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)

# Load users at startup
users = load_users()

@app.route('/')
def index():
    return redirect('/login')

#Login 
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        mail = request.form.get('email')
        pwd = request.form.get('password')
        user = users.get(mail)
        if user and user['password'] == pwd:
            session['mail'] = mail
            session['name'] = user['name']
            return redirect(url_for('blogs'))
        else:
            error = "Invalid Email or password"
            return render_template('login.html', error = error)
    return render_template('login.html', error=None)


#Registering Users
@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    global users
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if email in users:
            error = "User already exists!"
        else:
            users[email] = {
                "name": name,
                "password": password
            }
            save_users(users)
            return redirect(url_for('login'))
    
    return render_template('register.html', error=error)


@app.route('/blogs')
def blogs():
    if 'mail' not in session:
        return redirect(url_for('login'))
    
    user_name = session.get('name')
    all_posts = load_post()
    
    # Filter only posts by this user
    user_posts = [p for p in all_posts if p['author'] == user_name]

    return render_template('blog.html', posts=user_posts, user=user_name)


#route to addd posts
POSTS = 'posts.json' 

def load_post():
    if os.path.exists(POSTS):
        with open(POSTS, 'r') as f:
            return json.load(f)
    return []

def save_post(posts):
    with open(POSTS, 'w') as f:
        json.dump(posts, f, indent=4)

posts = load_post()

@app.route('/add_posts', methods=['GET', 'POST'])
def addBlogs():
    if 'name' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        author = session.get('name')

        # posts = load_post()           # Load all posts
        new_post = {                  # Create new post
            'title': title,
            'content': content,
            'author': author
        }
        posts.append(new_post)        # Add to list
        save_post(posts)              # Save list back to file
        return redirect(url_for('blogs'))

    return render_template('add.html')



@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
