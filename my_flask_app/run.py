# run.py

from app import create_app, db

app = create_app()

@app.cli.command("init-db")
def init_db():
    with app.app_context():
        # Query untuk membuat tabel data_sql
        db.session.execute('''
            CREATE TABLE IF NOT EXISTS data_sql (
                id SERIAL PRIMARY KEY,
                tgl TIMESTAMP,
                rrn VARCHAR(255),
                response_code VARCHAR(255),
                proc_code VARCHAR(255),
                acq_bank_nama VARCHAR(255),
                iss_bank_nama VARCHAR(255),
                merchant_name_location VARCHAR(255),
                trx_amount INTEGER
            )
        ''')

        # Query untuk membuat tabel data_member
        db.session.execute('''
            CREATE TABLE IF NOT EXISTS data_member (
                tgl DATE,
                id INTEGER PRIMARY KEY,
                id_trx VARCHAR(255),
                transaction_date DATE,
                transaction_time TIME,
                response_code VARCHAR(255),
                rrn VARCHAR(255),
                proc_code VARCHAR(255),
                acq_bank_code VARCHAR(255),
                nama_id_principal VARCHAR(255),
                iss_bank_code VARCHAR(255),
                nama_id_principal_1 VARCHAR(255),
                pan VARCHAR(255),
                acc_identification VARCHAR(255),
                merchant_name_location VARCHAR(255),
                trx_amount INTEGER,
                request VARCHAR(255)
            )
        ''')

        db.create_all()
        print("Database initialized.")

if __name__ == '__main__':
    app.run(debug=True)