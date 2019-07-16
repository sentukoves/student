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


def fetch_history(serts=''):
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
    skolko.BalanceTranc, 
    kto.TabNum, 
    komy.TabNum
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
                'Summaru': row[8],
                'FromTabNum': row[9],
                'ToTabNum': row[10]
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


@app.route('/priz')
def priz():
    list_point = request.args.get('all')
    tabnum = request.args.get('tabnum')
    count = request.args.get('count')
    id = request.args.get('id')

    if list_point == 'True':
        All_priz = response_all_persons("SELECT *  FROm priz", flag=3)
        out_array_priz = {}
        for elements in All_priz:
            asrt = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
            id = ''
            for i in range(10):
                id += asrt[random.randint(1, len(asrt) - 1)]
            temp = {
                "id":elements[0],
                'Name': elements[1],
                'Price': elements[2],
                'Count': elements[3],
            }
            out_array_priz[id] = temp
        return json_response({'ALL':out_array_priz})

    if tabnum and count and id:
        count_check = response_all_persons(
            "SELECT ncount , NBalance from priz where id = '{}'".format(id) , flag=3)
        count_balance =  response_all_persons('SELECT balance FROM Persons where tabnum = {}'.format(tabnum) , flag=3 )
        person_balance = count_balance[0][0]
        price = count_check[0][1]
        count_ed = count_check[0][0]

        if len(count_check) >= 0:
            if count_ed > count and person_balance > price :
                response_all_persons('UPDATE Persons '
                                     'Set balance = balance - {} '
                                     'where TabNum = {}'.format(price, tabnum),
                                     flag=1)
                response_all_persons(
                    "UPDATE Priz SET ncount = ncount - {} "
                    "where id = {}".format(count,id) , flag=1)
                return json_response({'STATUS': 'Успешно'})
            return json_response({'STATUS': 'Недостаточное количество воркоинов'})
        return json_response({"STATUS": 'Ненайден товар'})
    return json_response({"STATUS:'Параметры не отпределены"})


@app.route("/")
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True, port=5070, host='VMSHQKSIPDEV01')
