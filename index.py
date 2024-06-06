from flask import Flask, request, jsonify
import sqlite3
from flask_cors import CORS
import os
import csv
from io import StringIO
import subprocess

app = Flask(__name__)
CORS(app)

# UPLOAD_FOLDER = 'uploads'
# if not os.path.exists(UPLOAD_FOLDER):
#     os.makedirs(UPLOAD_FOLDER)

# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

UPLOAD_FOLDER = '.'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
CSV_FILE_NAME = '123_Output.csv'


def query_db(query, args=(), one=False):
    con = sqlite3.connect('data.db')
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute(query, args)
    rv = cur.fetchall()
    con.close()
    return (rv[0] if rv else None) if one else rv

@app.route('/data')
def get_data():
    page = request.args.get('page', type=int)
    limit = 1000  # Number of rows per page
    offset = (page - 1) * limit
    
    total_count = query_db('SELECT COUNT(*) as count FROM data', one=True)['count']
    rows = query_db('SELECT * FROM data LIMIT ? OFFSET ?', [limit, offset])
    data = [dict(row) for row in rows]

    return jsonify({
        "recordsTotal": total_count,
        "data": data
    })
    
@app.route('/filter_data', methods=['GET'])
def filter_data():
    filters = request.args.to_dict()
    print("filters : ", filters)
    page = int(filters.pop('filterPage', 1))  # Extract the page number, default to 1
    limit = 1000  # Number of rows per page
    offset = (page - 1) * limit

    filter_conditions = []
    filter_values = []

    for column, value in filters.items():
        filter_conditions.append(f"{column} LIKE ?")
        filter_values.append(f"%{value}%")
    
    filter_query = " AND ".join(filter_conditions)
    base_query = 'SELECT * FROM data'
    count_query = 'SELECT COUNT(*) as count FROM data'

    if filter_conditions:
        base_query += ' WHERE ' + filter_query
        count_query += ' WHERE ' + filter_query
    
    count_result = query_db(count_query, filter_values, one=True)
    total_filtered_count = count_result['count']

    base_query += ' LIMIT ? OFFSET ?'
    filter_values.extend([limit, offset])
    rows = query_db(base_query, filter_values)
    data = [dict(row) for row in rows]
    # print("data", data, "rows", rows,"total_filtered_count", total_filtered_count )

    return jsonify({
        "recordsTotal": total_filtered_count,
        "data": data
    })
    
@app.route('/download_filtered_data', methods=['GET'])
def download_filtered_data():
    filters = request.args.to_dict()
    filter_conditions = []
    filter_values = []

    for column, value in filters.items():
        filter_conditions.append(f"{column} LIKE ?")
        filter_values.append(f"%{value}%")
    
    filter_query = " AND ".join(filter_conditions)
    base_query = 'SELECT * FROM data'

    if filter_conditions:
        base_query += ' WHERE ' + filter_query

    rows = query_db(base_query, filter_values)
    data = [dict(row) for row in rows]

    si = StringIO()
    writer = csv.writer(si)
    
    # # Write header
    # if data:
    #     writer.writerow(data[0].keys())
    
    # Write data rows
    for row in data:
        writer.writerow(row.values())

    output = si.getvalue()
    si.close()
    
    return output, 200, {
        'Content-Type': 'text/csv',
        'Content-Disposition': 'attachment; filename=filtered_data.csv'
    }

# by PYTHON

# @app.route('/upload_csv', methods=['POST'])
# def upload_csv():
#     if 'file' not in request.files:
#         return jsonify({"error": "No file part"}), 400
#     file = request.files['file']
#     if file.filename == '':
#         return jsonify({"error": "No selected file"}), 400
#     if file:
#         file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
#         file.save(file_path)
        
#         # Clear the database
#         clear_database()
        
#         # Process the CSV file and insert data into the database by PYTHON
#         process_csv_and_insert_to_db(file_path)

        
#         return jsonify({"success": True, "message": "File uploaded and processed successfully"})

# by C++
@app.route('/upload_csv', methods=['POST'])
def upload_csv():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], CSV_FILE_NAME)
        
        # Delete the old file if it exists
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Save the new file
        file.save(file_path)
        
        # Clear the database
        clear_database()
        
        # # Compile and run the C++ script to process the CSV and insert data into the database
        # compile_result = subprocess.run(['g++', '-o', 'csv_reader', 'csv_reader.cpp', '-lsqlite3'], capture_output=True, text=True)
        # if compile_result.returncode != 0:
        #     return jsonify({"error": "Failed to compile C++ script", "details": compile_result.stderr}), 500

        # Compile the C++ script
        compile_result = subprocess.run(['g++', '-std=c++17', '-o', 'csv_reader', 'csv_reader.cpp', '-lsqlite3'], capture_output=True, text=True)
        if compile_result.returncode != 0:
            return jsonify({"error": "Failed to compile C++ script", "details": compile_result.stderr}), 500

            
        
        run_result = subprocess.run(['./csv_reader'], capture_output=True, text=True)
        if run_result.returncode != 0:
            return jsonify({"error": "Failed to run C++ script", "details": run_result.stderr}), 500

        return jsonify({"success": True, "message": "File uploaded and processed successfully"})



def clear_database():
    con = sqlite3.connect('data.db')
    cur = con.cursor()
    cur.execute('DELETE FROM data')
    con.commit()
    cur.execute('VACUUM')
    con.commit()
    con.close()

# by PYTHON
def process_csv_and_insert_to_db(file_path):
    con = sqlite3.connect('data.db')
    cur = con.cursor()
    
    # Start a transaction
    cur.execute("BEGIN TRANSACTION;")
    
    # Create the table if it doesn't exist
    cur.execute("""
    CREATE TABLE IF NOT EXISTS data (
        col1 TEXT, col2 TEXT, col3 TEXT, col4 TEXT, col5 TEXT, 
        col6 TEXT, col7 TEXT, col8 TEXT, col9 TEXT, col10 TEXT, 
        col11 TEXT, col12 TEXT, col13 TEXT, col14 TEXT, col15 TEXT, 
        col16 TEXT, col17 TEXT, col18 TEXT, col19 TEXT, col20 TEXT, 
        col21 TEXT, col22 TEXT, col23 TEXT, col24 TEXT, col25 TEXT, 
        col26 TEXT, col27 TEXT, col28 TEXT, col29 TEXT, col30 TEXT, 
        col31 TEXT
    );
    """)
    
    with open(file_path, 'r') as csvfile:
        csv_reader = csv.reader(csvfile)
        for row in csv_reader:
            cur.execute("""
            INSERT INTO data (
                col1, col2, col3, col4, col5, col6, col7, col8, col9, col10, 
                col11, col12, col13, col14, col15, col16, col17, col18, col19, col20, 
                col21, col22, col23, col24, col25, col26, col27, col28, col29, col30, col31
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, row)
    
    # Commit the transaction
    con.commit()
    con.close()

if __name__ == '__main__':
    app.run(host='192.168.10.107',  port=5000, debug=True)
    # app.run(port=5000, debug=True)
