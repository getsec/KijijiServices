from flask import Flask, render_template, redirect, url_for, request, session, flash
from functools import wraps
from uuid import uuid4
import os
from sql import *

app = Flask(__name__)
app.secret_key = "MySuperSecretKey123123123"
table_name = "my-flask-app-dev"
app.IMAGE_UPLOADS = "image_uploads"


# use decorators to link the function to a url
@app.route('/')
def home():
    return render_template('index.html') 


@app.route('/ads')
def ads():
    return render_template('ad.html')

@app.route('/post', methods = ['POST', 'GET'])
def result():
    
    image = request.files["image"]
    filename = image.filename.replace(' ', '_')
    image.save(os.path.join(app.IMAGE_UPLOADS, filename))
    full_path_to_file = app.IMAGE_UPLOADS + '/' + filename
    if request.method == 'POST':
        result = request.form
        username = result['email']
        password = result['password']
        ad_title = result['title']
        ad_desc = result['desc']
        category_url = result['category']
        print(category_url)
        col_dict = {
            "uuid": username,
            "password": password,
            "ad_title":  ad_title,
            "ad_desc": ad_desc,
            "photo_path": full_path_to_file,
            "category": category_url
        }

        add_item(table_name, col_dict)
        return render_template('ad_submitted.html', errors="lol")

@app.route('/query')
def query():
    return render_template('query.html')

@app.route('/check_ads', methods = ['POST', 'GET'])
def check_ads():
    if request.method == 'POST':
        result = request.form

        items = scan_table_allpages(
            table_name, 
            filter_key="uuid", 
            filter_value=result['email']
        )
        email = items[0]['uuid']
        title = items[0]['ad_title']
        desc  = items[0]['ad_desc']

        
    return render_template("query_output.html", email=email, title=title, desc=desc)
    
    


