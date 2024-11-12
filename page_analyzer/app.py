from flask import Flask, render_template
import os


#load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('a242752b0e9a71335718af7cbebfdd6d')

@app.route('/')
def hello_world():
    return 'Welcome to Flask!'


'''@app.get('/')
def page_analyzer():
    return render_template('html/index.html')'''