from flask import render_template
from .app import app

@app.route('/')
def home():
    return render_template('home.html')
    
@app.route('/demo')
def demo():
    return render_template('demo.html')

    
# @app.route('/contact')
# def about():
    # return render_template('contact_us.html')
    
# @app.route('/faq')
# def about():
    # return render_template('faq.html')
    
# @app.route('/about')
# def about():
    # return render_template('about.html')
    
    
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404