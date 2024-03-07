from flask import Flask, request, render_template, redirect, url_for, jsonify, json, session,make_response
from flask_bcrypt import Bcrypt
from flask_wtf import CSRFProtect
from flask_wtf.csrf import CSRFError
import datetime
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
import secrets
from datetime import timedelta
from models import Test, Users, Roles

import requests
from flask_restful import Resource, Api



app = Flask(__name__)
api = Api(app)
app.secret_key = secrets.token_hex(16)
app.permanent_session_lifetime = timedelta(minutes=10)
csrf = CSRFProtect(app)
bcrypt = Bcrypt()

db_engine1 = sa.create_engine('sqlite:///./database/main.db', poolclass=NullPool)
db_engine2 = sa.create_engine('sqlite:///./database/user.db', poolclass=NullPool)

#=============================================Route below
@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    return "Time Out"

@app.before_request
def make_session_permanent():
    session.permanent = True
    session.modified = True
#=============================================首頁
@app.route("/", methods=['POST', 'GET'])
def hello():
    current_url = request.url
    url = current_url+'/api'
    response = requests.get(url)
    all_posts = response.json()
    message = session.get('message', "")
    session.pop('message', message)
    user_identify = session.get('user_identify', False)
    user_permission = session.get('user_permission', '0')
    user_name = session.get('user_name', '訪客')
    user_role = session.get('user_role')
    #session.pop('user_identify', None)
    #db_engine = sa.create_engine('sqlite:///main.db')
    #Session = sessionmaker(bind=db_engine1)
    #db_session = Session()
    #all_posts = all_posts#db_session.query(Test).all()
    #db_session.close()
    return render_template("index.html",
                            all_posts=all_posts,
                            user_identify=user_identify,
                            user_permission=user_permission,
                            user_name=user_name,
                            user_role=user_role,
                            message=message)

#=============================================首頁-送出貼文後存成json
@app.route("/getpost", methods=['POST'])
def getpost():
    if request.method == "POST":
        user_permission = session.get('user_permission')
        user_role = session.get('user_role')
        if user_permission == 'root' or '1' in user_permission:
            tonow = datetime.datetime.now()
            posttime = "{}/{}/{}".format(tonow.year, tonow.month, tonow.day)
            data = {
                'appInfo': {
                    "poster_name" : session['user_name'],
                    "poster_email" : session['user_email'],
                    "post_content" : request.form['coment'],
                    "post_time" : posttime
                }
            }
            try:
                with open('input_num.txt', 'r') as file:
                    number = int(file.read())
                number += 1
                with open('input_num.txt', 'w') as file:
                    file.write(str(number))
            except:
                with open('input_num.txt', 'w') as file:
                    number = '1'
                    file.write(number)
            session['input_num'] = number
            json_file = 'static/data/input{}.json'.format(number)
            with open(json_file, 'w') as f:
                json.dump(data, f)
            f.close

# 使用方式：increment_number_in_file('yourfile.txt')

            #with open("static/data/input.json", "r") as file:
            #    data = json.load(file)

    return redirect(url_for("add_poster_data"), code=302)

#=============================================首頁-從json中讀取資料存入資料庫
@app.route('/add_poster_data')
def add_poster_data():
    Session = sessionmaker(bind=db_engine1)
    db_session = Session()

    last_post = db_session.query(Test).filter_by(poster_name=session['user_name']).order_by(Test.id.desc()).first()
    if last_post != None:
        last_post = vars(last_post)['post_content']
    else:
        last_post = 'This is the first post from this users'
    json_file = 'static/data/input{}.json'.format(session.get('input_num'))
    with open(json_file) as json_file:
        data = json.load(json_file)
    if last_post != data['appInfo']['post_content']:
        new_user = Test(poster_name=data['appInfo']['poster_name'],
                        poster_email=data['appInfo']['poster_email'],
                        post_content=data['appInfo']['post_content'],
                        post_time=data['appInfo']['post_time'])
        db_session.add(new_user)
        commit_db_session(db_session)
        #db_session.commit()
        #db_session.close()
        return redirect(url_for("hello"))
    else:
        session['message'] = '你已送出過了!'
        return redirect(url_for("hello"))

#=============================================首頁-刪除貼文
@app.route('/delete_post', methods=["POST"])
def delete_post():
    user_permission = session.get('user_permission', None)
    user_role = session.get('user_role')
    if user_permission == 'root' or ('2' in user_permission and (user_role=='編輯者' or '擁有者')):
        post_id = request.form.get('delete_post_id')
        #db_engine = sa.create_engine('sqlite:///main.db')
        Session = sessionmaker(bind=db_engine1)
        db_session = Session()
        #post = session.query(Test).get(id=post_id)
        post = db_session.query(Test).filter_by(id=post_id).first()
        db_session.delete(post)
        commit_db_session(db_session)
        #db_session.commit()
        #db_session.close()
    else:
        session['message'] = '你沒有該權限！'
        return redirect(url_for("hello"))
    return redirect(url_for("hello"))

#=============================================首頁-註冊
@app.route('/signup', methods=["POST"])
def signup():
    show_user_signup = request.form.get('show_user_signup')
    if request.method == 'POST' and show_user_signup == 'False':
        name = request.form.get('signup_name')
        email = request.form.get('signup_email')
        password = request.form.get('signup_password')
        ###permission = '01'
        #db_engine = sa.create_engine('sqlite:///user.db')
        Session = sessionmaker(bind=db_engine2)
        db_session = Session()
        if db_session.query(Users).filter_by(user_name=name).first() != None:
            message = "用戶名已被使用"
            db_session.close()
            return render_template("signup.html", message=message, show_user_signup=show_user_signup)
        elif db_session.query(Users).filter_by(user_email=email).first() != None:
            message = "電子郵件已被使用"
            db_session.close()
            return render_template("signup.html", message=message, show_user_signup=show_user_signup)
        password = password + "geometry"  #密鑰
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = Users(user_name=name, user_email=email, _user_password_=hashed_password)#, user_permission=permission)
        db_session.add(new_user)
        commit_db_session(db_session)
        #db_session.commit()
        #db_session.close()
        return redirect(url_for("hello"))
    else:
        return render_template("signup.html", show_user_signup=show_user_signup)

#=============================================首頁-登入
@app.route('/login', methods=["POST"])
def login():
    session['message'] = ''
    if request.method=='POST':
        login_email = request.form.get('login_email')
        login_password = request.form.get('login_password')
        login_password = login_password + 'geometry'
        Session = sessionmaker(bind=db_engine2)
        db_session = Session()
        user_identify = db_session.query(Users).filter_by(user_email=login_email).first()
        if user_identify != None:
            if bcrypt.check_password_hash(vars(user_identify)['_user_password_'], login_password):
                session['user_identify'] = True
                session['user_name'] = vars(user_identify)['user_name']
                session['user_email'] = vars(user_identify)['user_email']
                ###session['user_permission'] = vars(user_identify)['user_permission']
                session['user_role'] = vars(user_identify)['_user_role_']
                user_permission = db_session.query(Roles).filter_by(role_name=session.get('user_role')).first()
                session['user_permission'] = vars(user_permission)['permission_num']
                db_session.close()
                return redirect(url_for("hello"))
            else:
                db_session.close()
                session['message'] = '密碼錯誤'
                return redirect(url_for("hello"))
        else:
            db_session.close()
            session['message'] = '帳號不存在'
            return redirect(url_for("hello"))
    db_session.close()
    return render_template("index.html")

#=============================================首頁-登出
@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    session['user_identify'] = False
    return redirect(url_for("hello"))

#=============================================幹部註冊頁        !!!待評估!!!
@app.route('/signup_admin', methods=["POST", "GET"])
def signup_admin():
    show_user_signup = request.form.get('show_user_signup')
    if request.method == 'POST' and show_user_signup == 'False':
        name = request.form.get('signup_name')
        email = request.form.get('signup_email')
        password = request.form.get('signup_password')
        permission = request.form.get('signup_permission')
        if permission == '02':
            role = "編輯者"
        elif permission == '012':
            role = "擁有者"
        elif permission == '013':
            role = '權限管理者'
        #db_engine = sa.create_engine('sqlite:///user.db')
        Session = sessionmaker(bind=db_engine2)
        db_session = Session()
        if db_session.query(Users).filter_by(user_name=name).first() != None:
            message = "用戶名已被使用"
            db_session.close()
            return render_template("signup_admin.html", message=message, show_user_signup=show_user_signup)
        elif db_session.query(Users).filter_by(user_email=email).first() != None:
            message = "電子郵件已被使用"
            db_session.close()
            return render_template("signup_admin.html", message=message, show_user_signup=show_user_signup)
        
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = Users(user_name=name, user_email=email, _user_password_=hashed_password, _user_role_= role, user_permission=permission)
        db_session.add(new_user)
        commit_db_session(db_session)
        #db_session.commit()
        #db_session.close()
        return redirect(url_for("hello"))
    else:
        return render_template("signup_admin.html", show_user_signup=show_user_signup)

#=============================================使用者的角色管理頁
@app.route('/user_role_manager', methods=['POST', 'GET'])
def user_role_manager():
    user_identify = session.get('user_identify', False)
    user_permission = session.get('user_permission', None)
    #user_role = session.get('user_role')
    if '3' in user_permission or 'root' == user_permission:
        #user_permission = session.get('user_permission', '0')
        Session = sessionmaker(bind=db_engine2)
        db_session = Session()
        all_user_permission = db_session.query(Users.id, Users.user_name, Users._user_role_).all()
        all_role_permission = db_session.query(Roles.id, Roles.role_name, Roles.permission_num).all()
        db_session.close()
        return render_template("user_role_manager.html",
                                all_user_permission=all_user_permission,
                                all_role_permission=all_role_permission,
                                user_identify=user_identify,
                                user_permission=user_permission)
    session['message'] = '你沒有權限'
    return render_template("index.html")

#=============================================使用者的角色管理頁-變更角色
@app.route('/change_user_role', methods=['POST'])
def change_user_role():
    Session = sessionmaker(bind=db_engine2)
    db_session = Session()
    new_role = request.form.get('user_role')
    change_user_role_id = request.form.get('change_user_role_id')
    user = db_session.query(Users).filter_by(id=change_user_role_id).first()
    user._user_role_ = new_role
    commit_db_session(db_session)
    #db_session.commit()
    #db_session.close()
    return redirect(url_for("user_role_manager"))

#=============================================角色的管理頁
@app.route('/roles_manager', methods=['POST', 'GET'])
def roles_manager():
    user_identify = session.get('user_identify', False)
    user_permission = session.get('user_permission', None)
    if user_permission == 'root' or '4' in user_permission:
        Session = sessionmaker(bind=db_engine2)
        db_session = Session()
        all_roles = db_session.query(Roles.id, Roles.role_name, Roles.permission_num).all()
        db_session.close()
        return render_template("roles_manager.html",
                                all_roles=all_roles,
                                user_identify=user_identify,
                                user_permission=user_permission,
                                )

#=============================================角色的管理頁-新增角色
@app.route('/add_new_role', methods=['POST'])
def add_new_role():
    user_permission = session.get('user_permission', None)
    new_role_name = request.form.get('new_role_name')
    if '4' in user_permission or 'root' == user_permission:
        Session = sessionmaker(bind=db_engine2)
        db_session = Session()
        new_role = Roles(role_name=new_role_name, permission_num='0')
        db_session.add(new_role)
        commit_db_session(db_session)
    return redirect(url_for("roles_manager"))

#=============================================角色的管理頁-變更角色權限
@app.route('/change_permission', methods=['POST'])
def change_permission():
    changed_permission_role_id = request.form.get('changed_permission_role_id')
    new_permission = request.form.getlist('checkbox')
    Session = sessionmaker(bind=db_engine2)
    db_session = Session()
    role = db_session.query(Roles).filter_by(id=changed_permission_role_id).first()
    new_permission = ''.join(new_permission)
    role.permission_num = new_permission
    commit_db_session(db_session)
    return redirect(url_for('roles_manager'))

@app.route('/api/hello', methods=['POST', 'GET'])
def hello_api():
    message = session.get('message', "")
    session.pop('message', message)
    user_identify = session.get('user_identify', False)
    user_permission = session.get('user_permission', '0')
    user_name = session.get('user_name', '訪客')
    user_role = session.get('user_role')
    db_engine1 = sa.create_engine('sqlite:///main.db')
    Session = sessionmaker(bind=db_engine1)
    db_session = Session()
    all_posts = db_session.query(Test).all()
    db_session.close()
    return jsonify({
        'all_posts': all_posts,  # 假設你的 Test 模型有一個 to_dict 方法來轉換為字典
        'user_identify': user_identify,
        'user_permission': user_permission,
        'user_name': user_name,
        'user_role': user_role,
        'message': message
    })

#=============================================API
class HelloWorld(Resource):
    def get(self):
        #return {'hello': 'world'}
        Session = sessionmaker(bind=db_engine1)
        db_session = Session()
        all_posts = db_session.query(Test).all()
        db_session.close()
        return jsonify([post.to_dict() for post in all_posts])
api.add_resource(HelloWorld, '/api')

#=============================================純函式
def commit_db_session(db_session):
    db_session.commit()
    db_session.close()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5151)