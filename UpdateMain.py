import sqlite3
import sys
import os
from flask import Flask, json, request, render_template
import random


def json_response(string):
    return app.response_class(
        response="{}".format(str(string).replace("'", '"')),
        mimetype='application/json'
    )


def response_all_persons(sql, flag=0):
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
                    id += asrt[random.randint(1, len(asrt) - 1)]

                temp['ID'] = row[0]
                temp['First Name'] = row[1]
                temp['Last Name'] = row[2]
                temp['Family'] = row[3]
                temp['TabNum'] = row[4]
                temp['Balance'] = row[5]
                out_array[id] = temp

            return {"ALL": out_array}
        elif flag == 3:
            return cur.fetchall()
        else:
            con.commit()


app = Flask(__name__)


@app.route('/all', methods=['GET'])
def all_json():
    resp = (response_all_persons('SELECT * FROM persons'))
    return json_response(resp)


@app.route('/update', methods=['GET'])
def update_json():
    tabnum = request.args.get('tabnum')
    fromtabnum = request.args.get('fromtabnum')
    balance = request.args.get('balance')
    admins = request.args.get("admins")


    if admins == 'True' and balance and tabnum:
        response_all_persons('UPDATE Persons '
                             'Set balance = balance + {} '
                             'where TabNum = {}'.format(balance, tabnum),
                             flag=1)
        return json_response({{'Update': 'True'}})


    if tabnum and balance and fromtabnum:
        response_all_persons('UPDATE Persons '
                             'Set balance = balance - {} '
                             'where TabNum = {}'.format(balance, fromtabnum),
                             flag=1)
        response_all_persons("UPDATE Persons "
                             "SET Balance= Balance + {} "
                             "where TabNum = {} ".format(balance, tabnum),
                             flag=1)
        response_all_persons(
            "INSERT INTO history "
            "(ToTabnumPersons , FromTabnumPersons , BalanceTranc)"
            " VALUES "
            "({} , {} , {})".format(
                int(tabnum), int(fromtabnum), int(balance)), flag=1)

        return json_response({'Update': 'True'})
    else:
        art = {}
        if not tabnum and not balance:
            art = {'lost atributte': 'ALL'}
        elif not balance:
            art = {'lost atributte': 'balance'}
        elif not tabnum:
            art = {'lost atributte': 'tabnum'}
        return json_response(art)


@app.route('/tabnum', methods=['GET'])
def tabnum_json():
    tabnum = request.args.get('tabnum')
    if tabnum:
        resp = (response_all_persons('SELECT * FROM persons where tabnum = {}'.format(tabnum)))
        return json_response(resp)
    else:
        return json_response({'Табельный номер не найден'})


@app.route('/auth')
def auth():
    login = request.args.get('login')
    password = request.args.get('password')

    if login and password:
        out_response = response_all_persons(
            "select status from auth where login ="
            " '{}' and password = '{}'"
            " ".format(login, password), flag=3)[0][0]

        if out_response.__len__() >= 0:
            resp = {'Status': {'Category':
                                   '{}'.format(out_response),
                               'Boolean': "True"}}

            return app.response_class(
                response=json.dumps(resp),
                mimetype='application/json')

        return json_response({'Status': {'Category': '{}'.format(out_response), 'Boolean': "False"}}),
    return json_response({'Не все атрибуты заполнены'})

def fetch_history(serts = ''):
    resp = response_all_persons("""
        SELECT 
    kto."First Name"   AS Фамилия,
    kto."Last Name"  as Имя,
    kto.Family  as отчество,
    kto.Balance as Баланс,
    komy."First Name", 
    komy."Last Name", 
    komy.Family, 
    komy.Balance,
    skolko.BalanceTranc as Отправил 
    FROM  
    history as  skolko ,
    persons as kto ,
    persons as  komy
    WHERE skolko.FromTabnumPersons = kto.TabNum and  skolko.ToTabnumPersons =  komy.TabNum {}
        """.format(serts), flag=3)
    arra = {}
    try:
        for row in resp:
            print(row)
            tem = {
                'Family_from': row[0],
                'Name_from': row[1],
                'LastName_from': row[2],
                'Balanc_from': row[3],
                'Family_to': row[4],
                'Name_to': row[5],
                'LastName_to': row[6],
                'Balanc_to': row[7],
                'Summaru': row[8]
            }
            asrt = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
            id = ''
            for i in range(10):
                id += asrt[random.randint(1, len(asrt) - 1)]
            arra[id] = tem
    except TypeError:
        return json_response({"Tabnum": 'None'})
    else:
        return json_response({'response': arra})
@app.route('/history')
def history():
    his = request.args.get('tabnum')
    if his:
        return fetch_history(' and kto.TabNum = {}'.format(his))
    return fetch_history()
@app.route("/")
def index():
    return render_template('index.html')
if __name__ == '__main__':
    app.run(debug=True, port=5070, host='192.168.1.64')
