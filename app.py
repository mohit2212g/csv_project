from flask import Flask, request, jsonify
import sqlite3
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

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
    draw = request.args.get('draw', type=int)
    start = request.args.get('start', type=int)
    length = request.args.get('length', type=int)
    
    total_count = query_db('SELECT COUNT(*) as count FROM data', one=True)['count']
    
    rows = query_db('SELECT * FROM data LIMIT ? OFFSET ?', [length, start])
    data = [dict(row) for row in rows]

    return jsonify({
        "draw": draw,
        "recordsTotal": total_count,
        "recordsFiltered": total_count,
        "data": data
    })

if __name__ == '__main__':
    app.run(port=5001, debug=True)
