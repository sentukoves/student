import sqlite3
import sys
import os
from flask import Flask, json, request, render_template
import random


def response_all_persons(sql, flag = 0):
    try:
        path_db = os.path.join(sys.path[0], 'Base.db')
        con = sqlite3.connect(path_db)
        cur = con.cursor()
        cur.execute(sql)
    except sqlite3.DatabaseError as err:
        return err
    else:
        asrt = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
        if flag == 0:
            out_array = {}
            for i, row in enumerate(cur.fetchall()):
                temp = {"ID": "",
                        "First Name": "",
                        "Last Name": "",
                        "Family": "",
                        "TabNum": "",
                        "Balance": ""}
                id = ""
                for i in range(10):
                    id +=asrt[random.randint(1 , len(asrt)-1)]

                temp['ID'] = row[0]
                temp['First Name'] = row[1]
                temp['Last Name'] = row[2]
                temp['Family'] = row[3]
                temp['TabNum'] = row[4]
                temp['Balance'] = row[5]
                out_array[id] = temp

            return {"ALL":out_array}
        else:
            con.commit()


app = Flask(__name__)


@app.route('/all', methods=['GET'])
def all_json():
    resp = (response_all_persons('SELECT * FROM persons'))
    print(resp)
    response = app.response_class(response="{}".format(str(resp).replace("'", '"')), mimetype='application/json')
    return response


@app.route('/update', methods=['GET'])
def update_json():
    tabnum = request.args.get('tabnum')
    balance = request.args.get('balance')
    print(tabnum, balance)
    if tabnum and balance:
        pick = response_all_persons("UPDATE Persons SET Balance={} where TabNum = {} ".format(balance,tabnum), flag=1)
        response = app.response_class(
            response=json.dumps(str('{}'.format(pick))),
            mimetype='application/json'
        )
        return response
    else:
        art = {}
        if not tabnum and not balance:
            art = {'lost atributte':'ALL'}
        elif not balance:
            art = {'lost atributte':'balance'}
        elif not tabnum:
            art = {'lost atributte':'tabnum'}

        response = app.response_class(
            response=json.dumps(art),
            mimetype='application/json'
        )
        return response


@app.route('/tabnum', methods=['GET'])
def tabnum_json():
    tabnum = request.args.get('tabnum')
    if tabnum:
        resp = (response_all_persons('SELECT * FROM persons where tabnum = {}'.format(tabnum)))
        response = app.response_class(
            response=json.dumps(str(resp)),
            mimetype='application/json'
        )
        return response
    else:
        return 'Табельный номер не найден'

@app.route("/")
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True,port=5070 , host='vmshqksipdev01')





