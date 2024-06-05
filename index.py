from flask import Flask, request, jsonify
import sqlite3
from flask_cors import CORS
import subprocess
import os

import csv
from io import StringIO

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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
    
    # Write header
    if data:
        writer.writerow(data[0].keys())
    
    # Write data rows
    for row in data:
        writer.writerow(row.values())

    output = si.getvalue()
    si.close()
    
    return output, 200, {
        'Content-Type': 'text/csv',
        'Content-Disposition': 'attachment; filename=filtered_data.csv'
    }
    
@app.route('/upload_csv', methods=['POST'])
def upload_csv():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        
        # Clear the database
        clear_database()
        
        # Run the C++ script with the file path as an argument
        result = subprocess.run(['./csv_reader', file_path], capture_output=True, text=True)
        
        if result.returncode != 0:
            return jsonify({"error": result.stderr}), 500
        
        return jsonify({"success": True, "message": "File uploaded and processed successfully"})


def clear_database():
    con = sqlite3.connect('data.db')
    cur = con.cursor()
    cur.execute('DELETE FROM data')
    con.commit()
    con.close()

if __name__ == '__main__':
    app.run(port=5000, debug=True)
