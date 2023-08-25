from flask import Flask, render_template, jsonify, request, flash, url_for, redirect, session
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient  # pymongo를 임포트 하기(패키지 인스톨 먼저 해야겠죠?)
from forms import RegistrationForm, LoginForm
import secrets
from datetime import date,datetime,timedelta
from flask_jwt_extended import *
import jwt
import time,threading
import random

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SECRET_KEY"] = secrets.token_hex(16)




# client = MongoClient('mongodb://test:test@18.212.182.25',27017)
client = MongoClient('localhost', 27017)
db = client.gw
initcount = 0

#### 실행 함수
def set_interval(func,sec):
    def func_wrapper():
        set_interval(func,sec)
        func()
    t = threading.Timer(sec,func_wrapper)
    t.start()
    return t

##### 당첨배정
def get_winner(names, cnts):
    names_list = list(name['name'] for name in names)
    cnt_list = list(cnt['cnt'] for cnt in cnts)
    max_cnt = max(cnt_list)+1
    ln = len(cnt_list)
    for i in range(ln):
        cnt_list[i] = max_cnt - cnt_list[i]
    arr = []
    for i in range(ln):
        for _ in range(cnt_list[i]):
            arr.append(names_list[i])
    return arr[random.randrange(len(arr))]

#### 백그라운드 서버시간
def time_interval():
    global initcount
    curtime = datetime.now().strftime('%Y-%m-%d')
    stand_time = standard_time().strftime('%Y-%m-%d')
    deadline = (standard_time() - timedelta(1)).strftime('%Y-%m-%d')
    if initcount == 300:
        initcount = 0
        time.sleep(1)
    else:
        initcount += 1

     ### 마감시간 출발시간 if문
    if curtime == stand_time:
        db.user_data.update_many({'join':1},{'$set': {'join': 0}})
    elif curtime == deadline:
        name = list(db.user_data.find({'join':0},{'_id':0,'name':1}))
        cnt = list(db.user_data.find({'join':0},{'_id':0,'cnt':1}))
        get_winner(name,cnt)

def standard_time() :
    Startweekday = 6
    crntweek = datetime.today().weekday()
    # 당일 출발시간으로 변경.
    # StandardTime = datetime.now()
    # 당일 마감시간으로 변경
    # StandardTime = datetime.now() + timedelta(1)
    # 매주 일요일 출발~
    StandardTime = datetime.now() + timedelta(Startweekday-crntweek)
    return StandardTime

set_interval(time_interval, 1)

winner = ''
if standard_time().strftime('%Y-%m-%d') == datetime.now().strftime('%Y-%m-%d'):
    winner = ''

# 홈화면!
@app.route('/')
def home():
    form = LoginForm()
    # set_interval(time_interval,1)
    return render_template('SignIn.html', form=form)

# 회원가입 페이지로~
@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        email = request.form['email']
        check = db.user_data.find_one({'email': email})
        if check:
            flash("이미 가입한 회원입니다. 로그인을 해주세요")
            return redirect(url_for('home'))
        else :
            flash(f'{form.username.data} 님 가입 완료!', 'success')
            name_receive = request.form['username']
            email_receive = request.form['email']
            password_receive = request.form['password']
            account_receive = request.form['account']
            bank_receive = request.form['bank']
            user_data = {'name': name_receive,'email': email_receive,'password': password_receive, 'account': account_receive, 'bank': bank_receive, 'cnt': 1, 'join': 0}
            db.user_data.insert_one(user_data)
            return redirect(url_for('home'))
    return render_template('SignUp.html', form=form)

@app.route('/gonggu', methods=["POST"])
def login():
    global winner
    StandardTime = standard_time()
    deadline = StandardTime - timedelta(1)

    id = request.form['id']
    password = request.form['password']

    check = db.user_data.find_one({'email': id})

    if check:
        if check['password'] == password:
            now = str(datetime.now()).split('-')[2][0:2]
            dead = str(deadline).split('-')[2][0:2]
            if now != dead:
                user_login = list(db.user_data.find({'email': id}))[0]
                id_ = user_login['email']
                join_ = user_login['join']
                cnt_ = user_login['cnt']
                user_login_data={'id': id_, 'join': join_, 'cnt': cnt_}

                join_list = list(db.user_data.find({'join':1}))

                token = jwt.encode({'id': id_}, "secret", algorithm="HS256")
                session['token'] = token

                return render_template('gonggu.html', StandardTime=StandardTime.strftime('%Y-%m-%d'), deadline=deadline.strftime('%Y-%m-%d'), user_login_data=user_login_data, join_list=join_list)
            else:
                join_list = list(db.user_data.find({'join':1}))

                names = list(db.user_data.find({'join': 1},{'_id':0, 'name':1}))
                cnts = list(db.user_data.find({'join': 1},{'_id':0, 'cnt':1}))
                

                if names:
                    if winner == '':
                        winner = get_winner(names, cnts)
                        return render_template('winner.html', StandardTime=StandardTime.strftime('%Y-%m-%d'), join_list=join_list, winner=winner)
                    else:
                        return render_template('winner.html', StandardTime=StandardTime.strftime('%Y-%m-%d'), join_list=join_list, winner=winner)

                else:
                    winner = "없음"
                    return render_template('winner.html', StandardTime=StandardTime.strftime('%Y-%m-%d'), join_list=join_list, winner=winner)



        else:
            flash("비밀번호가 틀렸습니다.")
            return redirect(url_for('home'))
    else:
        flash("아이디가 틀렸습니다.")
        return redirect(url_for('home'))
    
@app.route('/gonggu', methods=['GET'])
def gonggu():
    token = session.get('token')
    decode_token = jwt.decode(token, "secret", algorithms="HS256")
    cur_id = decode_token['id']
    cur_join = list(db.user_data.find({'email': cur_id}))[0]['join']
    cur_user_data = {'id': cur_id, 'join': cur_join}

    StandardTime = standard_time()
    deadline = StandardTime - timedelta(1)

    return render_template("gonggu.html", user_login_data=cur_user_data, StandardTime=StandardTime.strftime('%Y-%m-%d'), deadline=deadline.strftime('%Y-%m-%d'))

@app.route('/update', methods=['GET'])
def update():
    token = session.get('token')
    decode_token = jwt.decode(token, "secret", algorithms="HS256")
    cur_id = decode_token['id']
    join_b4 = list(db.user_data.find({'email': cur_id}))[0]['join']
    cnt_b4 = list(db.user_data.find({'email': cur_id}))[0]['cnt']
    if join_b4:
        db.user_data.update_one({'email': cur_id}, {'$set':{'join': 0}})
        db.user_data.update_one({'email': cur_id}, {'$set':{'cnt': cnt_b4-1}})
        return redirect(url_for('gonggu'))
    else:
        db.user_data.update_one({'email': cur_id}, {'$set':{'join': 1}})
        db.user_data.update_one({'email': cur_id}, {'$set':{'cnt': cnt_b4+1}})
        return redirect(url_for('gonggu'))


if __name__ == '__main__':
  app.run('0.0.0.0', port=5000, debug=True)