from flask import Flask, jsonify, request
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS
import create_db

import sqlite3

app = Flask(__name__)
CORS(app)

SWAGGER_URL = '/api/docs'
API_URL = '/static/swagger.json'
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Python Tech Test API"
    }
)
app.register_blueprint(swaggerui_blueprint)

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

# TODO - you will need to implement the other endpoints
# GET /api/person/{id} - get person with given id
# POST /api/people - create 1 person
# PUT /api/person/{id} - Update a person with the given id
# DELETE /api/person/{id} - Delete a person with a given id
@app.route("/api/people", methods=['GET','POST'])
def getall_people():
    conn = sqlite3.connect('test.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()

    if request.method == 'GET':
        all_people = cur.execute('SELECT * FROM Person;').fetchall()

        return jsonify(all_people)

    elif request.method == 'POST':
        person = request.json

        #see if person exists already
        person_exists = cur.execute('''SELECT * FROM Person 
                                    WHERE firstName = ? AND lastName = ?;''',(person['firstName'], person['lastName']))
        
        if not person_exists:
            #get id for new person 
            id = cur.execute('SELECT MAX(id) FROM Person;').fetchone()[0]

            #assume Person table exists. Checking if any records.
            if id:
                id += 1
            else:
                id = 1
            
            values = (id, person["firstName"], person["lastName"], person["authorised"], person["enabled"])
            cur.execute('''INSERT INTO Person (id,firstName,lastName,authorised,enabled)
                        VALUES(?,?,?,?,?);''',values)
            conn.commit()

            return jsonify(person)

        else:
            return('Person already exists, please use update')


@app.route("/api/people/<id>", methods = ['GET','PUT','DELETE'])
def get_person(id):
    conn = sqlite3.connect('test.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()

    if request.method == 'GET':
        person = cur.execute('SELECT * FROM Person WHERE id = ?;',id).fetchone()

        return jsonify(person)

    elif request.method == 'PUT':
        update_dets = request.json

        values = [update_dets['firstName'], update_dets['lastName'], update_dets['authorised'], update_dets['enabled'], id]
        cur.execute('''UPDATE person SET firstName = ?, lastName = ?, authorised = ?, enabled = ?
                    WHERE id = ?;''',values)
        conn.commit()

        return jsonify(update_dets)

    elif request.method == 'DELETE':

        cur.execute('DELETE FROM Person WHERE id = ?',id)

        return('Person with ID = {} deleted'.format(id))

if __name__ == '__main__':
    app.run()