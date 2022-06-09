# 本スクリプトは、ログインなどユーザーに関する処理をまとめている
from flask import Flask, session, redirect, request
from functools import wraps
from student_sqlite import exec, select


# ユーザー情報を得る
def get_user(username, password):
    a = select('SELECT * FROM user WHERE username=?', username)
    if len(a) == 0:
        return 'unavailable'
    elif a[0]['password'] != password:
        return 'wrong'
    return True


# ログインしているかの確認
def is_login():
    return 'login' in session


# ログインを試行する
def try_login(form):
    user = form.get('user', '')
    password = form.get('pw', '')
    # パスワードチェック
    if get_user(user, password) == 'unavailable':
        return 'unavailable'
    if get_user(user, password) == 'wrong':
        return 'wrong'
    session['login'] = user
    return True


# ユーザー名を得る
def get_id():
    return session['login'] if is_login() else '未ログイン'


# ログアウトする
def try_logout():
    session.pop('login', None)


# ログイン必須を処理するデコレーターを定義
def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not is_login():
            return redirect('/login')
        return func(*args, **kwargs)
    return wrapper


# 権限判定
def power_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if get_user_power() != 1:
            return redirect('/')
        return func(*args, **kwargs)

    return wrapper


# 新規ユーザーを追加
def user_new():
    user_id = request.form.get('user_id')
    username = request.form.get('username')
    name = request.form.get('name')
    password = request.form.get('pw')
    power = request.form.get('power')
    int_user_id = int(user_id)
    if int_user_id < 10000 or int_user_id > 99999:
        return 0
    p = get_user_id(user_id)
    if user_id == p:
        return 1
    q = check_username(username)
    if username == q:
        return 2
    user_id = exec('INSERT INTO user (user_id, name, username, password, type) VALUES (?, ?, ?, ?, ?)', user_id,
                   name, username, password, power)
    return user_id


# ユーザー情報を編集
def user_edit():
    user_id = request.form.get('user_id')
    username = request.form.get('username')
    name = request.form.get('name')
    password = request.form.get('pw')
    int_user_id = int(user_id)
    if int_user_id < 10000 or int_user_id > 99999:
        return 1
    all_users = get_all_users()
    a = get_user_id_2()
    if a != int_user_id:
        for i in all_users:
            check_user_id = i['user_id']
            if int_user_id == check_user_id:
                return 2
    b = get_id()
    if b != username:
        for i in all_users:
            check_user_name = i['username']
            if username == check_user_name:
                return 3
    user_name = exec('UPDATE user SET user_id=?, name=?, username=?, password=? WHERE username=?', user_id, name,
                    username, password, b)
    session['login'] = username
    return user_name


# データベースから確認、入力したIDを返す
def get_user_id(user_id):
    a = select('SELECT * FROM user WHERE user_id=?', user_id)
    if len(a) == 0:
        return None
    return user_id


# ログイン中のユーザー名からIDの確認
def get_user_id_2():
    a = get_user_info()
    return a['user_id']


# ユーザーの情報を得る
def get_user_info():
    username = get_id()
    a = select('SELECT * FROM user WHERE username=?', username)
    if len(a) == 0:
        return None
    return a[0]


# ユーザーの権限を判定　（1:講師　2:学生）
def get_user_power():
    username = get_id()
    a = select('SELECT * FROM user WHERE username=?', username)
    if a[0]['type'] == 1:
        return 1
    if a[0]['type'] == 2:
        return 2
    return 3


def get_user_name():
    a = get_user_info()
    return a['name']


def check_username(username):
    a = select('SELECT * FROM user WHERE username=?', username)
    if len(a) == 0:
        return None
    return username


def get_user_username():
    a = get_user_info()
    return a['username']


def get_user_password():
    a = get_user_info()
    return a['password']


def get_all_users():
    a = select('SELECT * FROM user')
    return a
