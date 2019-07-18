import sqlite3
import sys
import os
from flask import Flask, json, request, render_template
from time import gmtime, strftime
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
                        "Balance": "",
                        "FIO": ""}
                id = ""
                for i in range(10):
                    id += asrt[random.randint(1, len(asrt) - 1)]

                temp['ID'] = row[0]
                temp['First Name'] = row[1]
                temp['Last Name'] = row[2]
                temp['Family'] = row[3]
                temp['TabNum'] = row[4]
                temp['Balance'] = row[5]
                temp['FIO'] = row[7]
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
            dt = strftime("%d.%m.%Y %H:%M:%S", gmtime()) # текущее время в нужном формате
            response_all_persons(
                "INSERT INTO history "
                "(ToTabnumPersons , FromTabnumPersons , BalanceTranc)"#вставить время  сюда как четвертый аргумент TransactDate
                " VALUES "
                "({} , {} , {})".format(int(tabnum), 0, int(balance)),
                                            flag=1)
            return json_response({'Status': 'True'})

    if tabnum and balance and fromtabnum:
        resp = (response_all_persons("SELECT * FROM persons where TabNum = {}"
                                     .format(fromtabnum)))
        resp1 = (str(resp)).split()
        resp2 = resp1[len(resp1) - 1]
        oldbalance = int(resp2[:-3])
        if oldbalance >= int(balance):
            response_all_persons('UPDATE Persons '
                                     'Set balance = balance - {} '
                                     'where TabNum = {}'.format(balance, fromtabnum),
                                     flag=1)
            response_all_persons("UPDATE Persons "
                                     "SET Balance= Balance + {} "
                                     "where TabNum = {} ".format(balance, tabnum),
                                     flag=1)
            dt = strftime("%d.%m.%Y %H:%M:%S", gmtime()) # текущее время в нужном формате

            response_all_persons(
                    "INSERT INTO history "
                    "(ToTabnumPersons , FromTabnumPersons , BalanceTranc)"
                    " VALUES "
                    "({} , {} , {})".format(
                        int(tabnum), int(fromtabnum), int(balance)), flag=1)  #вставить время  сюда как четвертый аргумент TransactDate

            return json_response({'Status': 'True'})
        return json_response({'Status': 'Недостаточное количество WorkCoin'})
    else:
        art = {}
        if not tabnum and not balance:
            art = {'Status': 'Отсутствуют табельный номер и сумма'}
        elif not balance:
            art = {'Status': 'Отсутствует сумма'}
        elif not tabnum:
            art = {'Status': 'Отсутствует табельный номер'}
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
            "select status from auth where login = '{}'"
            " ".format(login), flag=3)
        if out_response.__len__() > 0:
            out_response1 = response_all_persons(
                "select status from auth where login = '{}' and password = '{}'"
                " ".format(login, password), flag=3)
            if out_response1.__len__() > 0:
                if (login == 'admin'):
                    resp = {'Status': {'Category': '{}'.format(out_response1[0][0]), 'Boolean': "True"}}
                else:
                    out_response2 = response_all_persons(
                        "select user.TabNum FROM auth as logins, persons as user WHERE logins.id = user.id and logins.login = '{}'"
                        " ".format(login), flag=3)
                    resp = {'Status': {'Category': '{}'.format(out_response1[0][0]), 'Boolean': "True", 'TabNum': '{}'.format(out_response2[0][0])}}

                return app.response_class(
                    response=json.dumps(resp),
                    mimetype='application/json')

            return json_response({'Status': {'Category': '{}'.format(out_response[0][0]), 'Boolean': "False"}})
        return json_response({'Status' : {'Category':"Неверный логин"}})
    return json_response({'Status':{'Category' : "Не все атрибуты заполнены"}})


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
    komy.TabNum,
    skolko.TransactDate,
    skolko.id,
    kto.FIO,
    komy.FIO
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
                'Name_from': row[0],
                'LastName_from': row[1],
                'Family_from': row[2],
                'Balanc_from': row[3],
                'Name_to': row[4],
                'LastName_to': row[5],
                'Family_to': row[6],
                'Balanc_to': row[7],
                'Summaru': row[8],
                'FromTabNum': row[9],
                'ToTabNum': row[10],
                'TransactDate': row[11],
                'ID': row[12],
                'FromFIO': row[13],
                'ToFIO': row[14]

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

def fetch_buys(serts=''):
    resp = response_all_persons("""
        SELECT 
    kto."First Name"   AS Фамилия,
    kto."Last Name"  as Имя,
    kto.Family  as отчество,
    skolko.Summary, 
    skolko.Count, 
    kto.TabNum,
    skolko.BuyDate,
    prize.id,
    kto.FIO
    FROM  
    buy_history as  skolko ,
    persons as kto ,
   Priz as  prize
    WHERE skolko.FromTabnumPersons = kto.TabNum and  skolko.PrizeID =  prize.id {}
        """.format(serts), flag=3)
    arra = {}
    try:
        for row in resp:
            print(row)
            tem = {
                'Name_to': row[0],
                'LastName_to': row[1],
                'Family_to': row[2],
                'Summary': row[3],
                'Count': row[4],
                'TabNum': row[5],
                'Datetime': row[6],
                'BuyId': row[7],
                'FIO': row[8]
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

@app.route('/buyhistory')
def history():
    his = request.args.get('tabnum')
    if his:
        return fetch_buys(' and kto.TabNum = {}'.format(his))
    return fetch_buys()


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
            "SELECT ncount , NBalance from priz where id = '{}'".format(id), flag=3)
        count_balance =  response_all_persons('SELECT balance FROM Persons where tabnum = {}'.format(tabnum) , flag=3 )
        person_balance = count_balance[0][0]
        price = count_check[0][1]
        count_ed = count_check[0][0]

        if len(count_check) > 0:
            if count_ed >= count:
                summary = int(price) * int(count)
                if int(person_balance) >= summary:
                   response_all_persons('UPDATE Persons '
                                        'Set balance = balance - {} '
                                        'where TabNum = {}'.format(price, tabnum),
                                        flag=1)
                   response_all_persons(
                       "UPDATE Priz SET ncount = ncount - {} "
                       "where id = {}".format(count,id) , flag=1)
                   dt = strftime("%d.%m.%Y %H:%M:%S", gmtime()) # текущее время в нужном формате
                   response_all_persons(
                    "INSERT INTO history "
                    "(PrizeId , FromTabnumPersons , Count, Summary)"
                    " VALUES "
                    "({} , {} , {}, {})".format(
                        int(id), int(tabnum), int(count), int(summary)), flag=1)  #вставить время сюда как пятый аргумент BuyDate

                   return json_response({'STATUS': 'True'})
                return json_response({'STATUS': 'Недостаточное количество WorkCoin'})
            return json_response({'STATUS': 'Недостаточное количество товаров'})
        return json_response({"STATUS": 'Не найден товар'})
    return json_response({"STATUS":"Параметры не отпределены"})


@app.route("/")
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True, port=5070, host='127.0.0.1')
