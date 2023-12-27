# app/routes.py
from flask import Blueprint, render_template, redirect, url_for, request, flash
from .model import DataSQL, DataMember
from . import db
import pandas as pd
import io
import chardet
from sqlalchemy import text
import math

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    datasql = DataSQL.query.all()
    datamember = DataMember.query.all()
    return render_template('index.html', datasql=datasql, datamember=datamember)

@main_bp.route('/upload', methods=['POST'])
def upload():
    if 'file_sql' not in request.files and 'file_member' not in request.files:
        flash('Please select either SQL or Member file.')
        return redirect(url_for('main.index'))

    try:
        # Process SQL file
        if 'file_sql' in request.files:
            file_sql = request.files['file_sql']

            # Detect encoding using chardet
            sql_encoding = chardet.detect(file_sql.read())['encoding']

            # If encoding is not detected, use a default encoding (you can change 'utf-8' to another encoding)
            if sql_encoding is None:
                sql_encoding = 'utf-8'

            # Reset file cursor to the beginning
            file_sql.seek(0)

            # Read SQL file using pandas with detected encoding and ';' as separator
            if file_sql.filename.endswith('.csv'):
                df_sql = pd.read_csv(io.StringIO(file_sql.read().decode(sql_encoding)), sep='\t', engine='python', skiprows=range(1, 5))
            elif file_sql.filename.endswith('.xlsx'):
                df_sql = pd.read_excel(io.BytesIO(file_sql.read()), engine='openpyxl')
            else:
                flash('Unsupported file format for SQL file. Please use CSV or XLSX.')
                return redirect(url_for('main.index'))

            # Iterate over each row in the DataFrame for DataSQL
            for idx, row in df_sql.iterrows():
                try:
                    data_sql = DataSQL(
                        tgl=row['TGL'],
                        rrn=row['RRN'],
                        response_code=row['RESPONSE_CODE'],
                        proc_code=row['PROC_CODE'],
                        acq_bank_nama=row['ACQ_BANK_NAMA'],
                        iss_bank_nama=row['ISS_BANK_NAMA'],
                        merchant_name_location=row['MERCHANT_NAME_LOCATION'],
                        trx_amount=row['TRX_AMOUNT']
                    )
                    db.session.add(data_sql)
                except Exception as e:
                    flash(f"Error processing SQL file, row {idx + 2}: {str(e)}")
                    print(f"Error processing SQL file, row {idx + 2}: {str(e)}")  # Debugging print
                    continue

        # Process Member file
        if 'file_member' in request.files:
            file_member = request.files['file_member']

            # Detect encoding using chardet
            member_encoding = chardet.detect(file_member.read())['encoding']

            # If encoding is not detected, use a default encoding (you can change 'utf-8' to another encoding)
            if member_encoding is None:
                member_encoding = 'utf-8'

            # Reset file cursor to the beginning
            file_member.seek(0)

            # Read Member file using pandas with detected encoding and ';' as separator
            if file_member.filename.endswith('.csv'):
                df_member = pd.read_csv(io.StringIO(file_member.read().decode(member_encoding)), sep=';', engine='python', skiprows=range(1, 5))
            elif file_member.filename.endswith('.xlsx'):
                df_member = pd.read_excel(io.BytesIO(file_member.read()), engine='openpyxl')
            else:
                flash('Unsupported file format for Member file. Please use CSV or XLSX.')
                return redirect(url_for('main.index'))

            # Print header and first 5 rows of the DataFrame for debugging
            print("Member File Header:", df_member.columns.tolist())
            print("Member File Data:")
            print(df_member.head())  # Print the first 5 rows


            # Debugging: Print data types of each column in DataFrame for Member
            print("Data Types:")
            print(df_member.dtypes)

            # Iterate over each row in the DataFrame for DataMember
            for idx, row in df_member.iterrows():
                try:
                    data_member = DataMember(
                        tgl=row['TGL'],
                        id=row['ID'],
                        id_trx=row['ID_TRX'],
                        transaction_date=row['TRANSACTION_DATE'],
                        transaction_time=row['TRANSACTION_TIME'],
                        response_code=row['RESPONSE_CODE'],
                        rrn=row['RRN'],
                        proc_code=row['PROC_CODE'],
                        acq_bank_code=row['ACQ_BANK_CODE'],
                        nama_acq=row['NAMA'],
                        id_principal_acq=row['ID_PRINCIPAL'],
                        iss_bank_code=row['ISS_BANK_CODE'],
                        nama_iss=row['NAMA'],
                        id_principal_iss=row['ID_PRINCIPAL'],
                        pan=row['PAN'],
                        acc_identification=row['ACC_IDENTIFICATION'],
                        merchant_name_location=row['MERCHANT_NAME_LOCATION'],
                        trx_amount=int(row['TRUNCATE(TRX_AMOUNT,0)']),
                        request=row['REQUEST']
                    )
                    db.session.add(data_member)
                except Exception as e:
                    flash(f"Error processing Member file, row {idx + 2}: {str(e)}")
                    print(f"Error processing Member file, row {idx + 2}: {str(e)}")  # Debugging print
                    continue

        db.session.commit()
        flash('Files uploaded successfully and data inserted into the database.')
    except Exception as e:
        flash(f'Error processing files: {str(e)}')
        print(f'Error processing files: {str(e)}')  # Debugging print

    return redirect(url_for('main.index'))




def get_paginated_results(page, page_size, status):
    offset = (page - 1) * page_size

    query = text("""WITH NoHaveSuccess AS (
    SELECT DISTINCT rrn
    FROM data_sql
    UNION
    SELECT DISTINCT rrn
    FROM data_member
    EXCEPT
    SELECT DISTINCT rrn
    FROM data_sql
    INTERSECT
    SELECT DISTINCT rrn
    FROM data_member
),
NoHaveSQL AS (
    SELECT DISTINCT rrn
    FROM data_member
    EXCEPT
    SELECT DISTINCT rrn
    FROM data_sql
),
NoHaveMember AS (
    SELECT DISTINCT rrn
    FROM data_sql
    EXCEPT
    SELECT DISTINCT rrn
    FROM data_member
)
SELECT 
    tgl,
    rrn,
    merchant_name_location_sql,
    response_code_sql,
    acq_bank_code_sql,
    nama_iss_sql,
    trx_amount_sql,
    merchant_name_location_member,
    response_code_member,
    acq_bank_code_member,
    nama_iss_member,
    trx_amount_member,
    rrn_sql,
    rrn_member,
    rrn_source,
    CASE 
        WHEN overall_status = 'Success' THEN 'Success'
        WHEN overall_status = 'Have SQL' THEN 'Have SQL'
        WHEN overall_status = 'Have Member' THEN 'Have Member'
    END AS status,
    COUNT(*) OVER () AS total_sukses_rrn,
    COUNT(*) OVER (PARTITION BY overall_status) AS total_transaksi_success,
    (SELECT COUNT(DISTINCT rrn) FROM NoHaveSuccess) AS no_have_success,
    (SELECT COUNT(DISTINCT rrn) FROM NoHaveSQL) AS no_have_sql,
    (SELECT COUNT(DISTINCT rrn) FROM NoHaveMember) AS no_have_member
FROM (
    SELECT 
        COALESCE(data_sql.tgl::text, data_member.tgl::text) AS tgl,
        COALESCE(data_sql.rrn, data_member.rrn) AS rrn,
        COALESCE(data_sql.merchant_name_location, '') AS merchant_name_location_sql,
        COALESCE(data_sql.response_code, '') AS response_code_sql,
        COALESCE(data_sql.acq_bank_nama, '') AS acq_bank_code_sql,
        COALESCE(data_sql.iss_bank_nama, '') AS nama_iss_sql,
        COALESCE(CAST(data_sql.trx_amount AS INTEGER), 0) AS trx_amount_sql,
        COALESCE(data_member.merchant_name_location, '') AS merchant_name_location_member,
        COALESCE(data_member.response_code, '') AS response_code_member,
        COALESCE(data_member.acq_bank_code, '') AS acq_bank_code_member,
        COALESCE(data_member.nama_iss, '') AS nama_iss_member,
        COALESCE(CAST(data_member.trx_amount AS INTEGER), 0) AS trx_amount_member,
        COALESCE(data_sql.rrn, '') AS rrn_sql,
        COALESCE(data_member.rrn, '') AS rrn_member,
        CASE 
            WHEN data_sql.rrn IS NOT NULL AND data_member.rrn IS NOT NULL THEN 'Success'
            WHEN data_sql.rrn IS NOT NULL THEN 'Have SQL'
            WHEN data_member.rrn IS NOT NULL THEN 'Have Member'
        END AS rrn_source,
        CASE 
            WHEN data_sql.rrn IS NOT NULL AND data_member.rrn IS NOT NULL THEN 'Success'
            WHEN data_sql.rrn IS NOT NULL THEN 'Have SQL'
            WHEN data_member.rrn IS NOT NULL THEN 'Have Member'
        END AS overall_status
    FROM data_sql
    FULL OUTER JOIN data_member ON data_sql.rrn = data_member.rrn
) AS subquery
WHERE overall_status = :status
ORDER BY rrn_source, rrn, overall_status
LIMIT :page_size OFFSET :offset;





    """)


    

    # Menambahkan parameter page dan page_size
    results = db.session.execute(query, {'status': status, 'page_size': page_size, 'offset': offset, 'page': page})
    results_list = results.fetchall()

    return results_list





@main_bp.route('/show_results', methods=['POST'])
def show_results():
    status = request.form.get('status')
    if not status:
        flash('Please select a status.')
        return redirect(url_for('main.index'))

    # Menambahkan validasi status untuk pilihan yang diinginkan
    allowed_statuses = ['Success', 'Have Member', 'Have SQL', 'No Have SQL', 'No Have Member', 'No Have Success']
    if status not in allowed_statuses:
        flash('Invalid status selected.')
        return redirect(url_for('main.index'))

    page = int(request.form.get('page', 1))
    page_size = 20

    try:
        if status in ['No Have SQL', 'No Have Member', 'No Have Success']:
            # Menggunakan fungsi get_no_have_results
            
            total_sukses_rrn, total_transaksi_success = 0, 0  # Untuk No Have SQL, Member, Success, nilai ini diatur ke 0
            result_heading = f"Results {status}"
        else:
            # Menggunakan fungsi get_paginated_results
            results_list = get_paginated_results(page, page_size, status)
            total_sukses_rrn = results_list[0][16] if results_list else 0
            total_transaksi_success = results_list[0][17] if results_list else 0
            total_not_sql = 0  # Untuk hasil bukan No Have SQL, Member, Success, nilai ini diatur ke 0
            result_heading = f"Results {status}"

        total_pages = math.ceil(total_sukses_rrn / page_size)

        # Pengecekan results_list
        print("Results List:", results_list)

        return render_template('index.html', results_list=results_list, total_sukses_rrn=total_sukses_rrn,
                               total_transaksi_success=total_transaksi_success, current_page=page,
                               total_pages=total_pages, total_not_sql=total_not_sql, result_heading=result_heading)
    except Exception as e:
        flash(f'Error executing query: {str(e)}')
        print(f'Error executing query: {str(e)}')
        return redirect(url_for('main.index'))
