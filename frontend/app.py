from flask import (
    Flask, render_template, redirect,
    request, session, url_for, flash
)
from functools import wraps
import os
from sql import (
    add_item,
    scan_table_allpages
)

app = Flask(__name__)
app.secret_key = "MySuperSecretKey123123123"
table_name = "my-flask-app-dev"
app.IMAGE_UPLOADS = "image_uploads"


def short(str):
    for i in range(0, len(str), 64):
        return str[i:i+64]


# login required decorator
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap

# route for handling the login page logic
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid Credentials. Please try again.'
        else:
            session['logged_in'] = True
            flash('You were logged in.')
            return redirect(url_for('home'))
    return render_template('login.html', error=error)


@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    flash('You were logged out.')
    return redirect(url_for('home'))


@app.route('/')
def home():
    return render_template('faq.html')


@app.route('/ads')
def ads():
    return render_template('ad.html')


@app.route('/faq')
def faq():
    return render_template('faq.html')


@app.route('/post', methods=['POST', 'GET'])
def result():
    image = request.files["image"]
    filename = image.filename.replace(' ', '_')
    image.save(os.path.join(app.IMAGE_UPLOADS, filename))
    full_path_to_file = app.IMAGE_UPLOADS + '/' + filename
    if request.method == 'POST':
        result = request.form
        print(result)
        province = result['province']
        username = result['email']
        password = result['password']
        ad_title = result['title']
        ad_desc = result['desc']
        city = result['city']

        category_url = result['category']
        print(category_url)
        col_dict = {
            "uuid": username,
            "password": password,
            "ad_title":  ad_title,
            "ad_desc": ad_desc,
            "city": city,
            "province": province,
            "photo_path": full_path_to_file,
            "category": category_url
        }
        add_item(table_name, col_dict)
        return render_template('ad_submitted.html', errors="lol")


@app.route('/query')
def query():
    return render_template('query.html')


@app.route('/check_ads', methods=['POST', 'GET'])
def check_ads():
    if request.method == 'POST':
        result = request.form

        try:
            items = scan_table_allpages(
                table_name,
                filter_key="uuid",
                filter_value=result['email']
            )
            email = items[0]['uuid']
            title = items[0]['ad_title']
            desc = items[0]['ad_desc']
            prov = items[0]['province']
            city = items[0]['city']

            return render_template(
                "query_output.html",
                email=email,
                title=title,
                desc=short(desc) + " ...",
                city=city,
                prov=prov
            )
        except Exception:
            return render_template("query_output_empty.html")


@login_required
@app.route('/logs')
def logs():

    with open('../backend/backend.log', 'r') as f:
        data = f.read()
    # Get the length of logs needed
    num_of_logs = int(request.args.get('length', 100))

    # prints the last x number of logs
    logs = data.split('\n')[-num_of_logs:]

    return render_template("logs.html", logs=logs)

@app.route('/debug')
def dump():
    os.system('cp ../backend/dump.html templates/dump.html')
    
    return render_template('dump.html') 