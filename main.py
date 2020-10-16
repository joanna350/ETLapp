from collections import OrderedDict
from flask import request
from flask import redirect
from flask import url_for
from flask import render_template
from flask import send_from_directory
from flask import session
from werkzeug.utils import secure_filename
import pandas as pd
import requests
import os
from app import app
from db import Database


DB_URL = 'sqlite:///test.db' # could be postgresql, mysql combinations

app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

ALLOWED_EXTENSIONS = {'csv'} # for now the only extension of interest

def allowed_file(filename):
    '''
    :param filename: the given filename including the extension
    :return: the extension
    '''
    # check that there is . in the filename first
    # split the filename based on the . separator right before the eol
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def baseline(url = "https://breakingbadapi.com/api/characters"):
    '''
    :param url: endpoint that carries the data to compare the input file with
    :return: comparable data in set
    '''
    response = requests.request("GET", url)
    # list of dictionaries per each character
    characters = response.json()
    # one overlap, one unknown
    actors = set()

    for c in characters:
        actors.add(c['portrayed'])

    if 'Unknown' in actors:
        actors.remove('Unknown')

    return actors

def extract(path):
    df = pd.read_csv(path)
    return df

def transform(basechars, raw):

    # return 1 if matches the rubric (at least one actor in common)
    fa = lambda x: 1 if set(i.strip() for i in x.split(',')).intersection(set(basechars)) else 0
    raw['Match'] = raw['Actors'].apply(fa)

    # convert the revenue by multiplying 1.3 USD/GBP
    fr = lambda x: x * 1.3
    raw['Revenue (Millions GBP)'] = raw['Revenue (Millions)'].apply(fr)

    return raw

def load_csv(data, filename):
    # output the identified set of films to a new csv for user
    df = pd.DataFrame(data[data['Match'] == 1])
    df.to_csv(app.config['DOWNLOAD_FOLDER'] + filename, index = False)

def load_table(data):
    # select the columns for table creation
    df = pd.DataFrame(data[data['Match'] == 1],
                      columns=['Title', 'Year', 'Revenue (Millions GBP)'])
    # for an endpoint that paginates this information during a session
    session['table'] = df.to_dict(into=OrderedDict)  # json serializable

    # instantiate database to load to
    db = Database(DB_URL)
    db.upload_df_to_sql(df, 'test')
    db.get_df_from_sql('test')

def process_file(path, filename):
    '''
    :param path: to upload from
    :param filename: so that the user may download
    :return:
    '''

    ## Extract
    raw = extract(path) # read in the uploaded file
    basechars = baseline() # retrieve the list of baseline characters to compare with

    ## Transform
    data = transform(basechars, raw)

    ## Load
    load_csv(data, filename)
    load_table(data)

@app.route('/dataset/', methods=['POST', 'GET'])
def html_table():
    unpack = session['table'] if 'table' in session else ''
    df = pd.DataFrame(unpack)
    return render_template("dataset.html",
                           tables = [df.to_html(classes='data')], # index kept for reference
                           titles = df.columns.values)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['DOWNLOAD_FOLDER'], filename, as_attachment=True )

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            print('File not selected. Try again')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            print('File not selected. Try again')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # 2nd parameter is for the output
            process_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), filename[:-4] +'-retrieved.csv')
            return redirect(url_for('uploaded_file', filename=filename[:-4] + '-retrieved.csv'))
    return render_template('index.html')


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 2000))
    app.run(host='0.0.0.0', debug = True)
