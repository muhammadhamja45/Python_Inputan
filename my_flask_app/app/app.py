# app.py
from flask import render_template, request, redirect, url_for
import pandas as pd
from app.model import DataSQL, DataMember
from app import create_app, db

app = create_app()

# Routes
@app.route('/')
def index():
    datasql = DataSQL.query.all()
    datamember = DataMember.query.all()
    return render_template('index.html', datasql=datasql, datamember=datamember)

@app.route('/upload', methods=['POST'])
def upload():
    if 'file_sql' not in request.files or 'file_member' not in request.files:
        return redirect(request.url)

    file_sql = request.files['file_sql']
    file_member = request.files['file_member']

    if file_sql.filename == '' or file_member.filename == '':
        return redirect(request.url)

    if file_sql and file_member:
        # Proses file_sql
        df_sql = pd.read_excel(file_sql)
        for index, row in df_sql.iterrows():
            data_sql = DataSQL(**row)
            db.session.add(data_sql)  

        # Proses file_member
        df_member = pd.read_excel(file_member)
        for index, row in df_member.iterrows():
            data_member = DataMember(**row)
            db.session.add(data_member)

        db.session.commit()

    return redirect(url_for('index'))
