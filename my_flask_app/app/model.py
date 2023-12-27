# app/model.py
from . import db
from sqlalchemy import DateTime
from datetime import datetime
from sqlalchemy.types import Date, Time
from sqlalchemy.types import Numeric

class DataSQL(db.Model):
    __tablename__ = 'data_sql'
    id = db.Column(db.Integer, primary_key=True)
    tgl = db.Column(db.TEXT)
    rrn = db.Column(db.TEXT)
    response_code = db.Column(db.String(10, collation='utf8_general_ci'))
    proc_code = db.Column(db.String(10, collation='utf8_general_ci'))
    acq_bank_nama = db.Column(db.String(50, collation='utf8_general_ci'))
    iss_bank_nama = db.Column(db.String(50, collation='utf8_general_ci'))
    merchant_name_location = db.Column(db.String(100, collation='utf8_general_ci'))
    trx_amount = db.Column(db.Integer)
    
class DataMember(db.Model):
    __tablename__ = 'data_member'
    id = db.Column(db.Integer, primary_key=True)
    tgl = db.Column(db.String(50))
    id_trx = db.Column(db.String(50))
    transaction_date = db.Column(db.String(50))
    transaction_time = db.Column(db.String(50))
    response_code = db.Column(db.String(50))
    rrn = db.Column(db.String(50))
    proc_code = db.Column(db.String(50))
    acq_bank_code = db.Column(db.String(50))
    nama_acq = db.Column(db.String(50))
    id_principal_acq = db.Column(db.String(50))
    iss_bank_code = db.Column(db.String(50))
    nama_iss = db.Column(db.String(50))
    id_principal_iss = db.Column(db.String(50))
    pan = db.Column(db.String(50))
    acc_identification = db.Column(db.String(50))
    merchant_name_location = db.Column(db.String(50))
    trx_amount = db.Column(db.Integer)
    request = db.Column(db.String(50))

