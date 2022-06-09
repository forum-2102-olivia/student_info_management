from flask import Flask, redirect, request, session
from flask import render_template, Markup
import student_db, sns_user as user   # 自作モジュールを取り込む
import math

app = Flask(__name__)
app.secret_key = 'random...'

limit = 10
a = '<a href="/logout">ログアウト</a>'


# ログイン処理を実現する
@app.route('/login')
def login():
    return render_template('login_form.html', login='未ログイン')


@app.route('/login/try', methods=['POST'])
def login_try():
    ok = user.try_login(request.form)
    if ok == 'unavailable':
        return msg('ログイン失敗。ユーザーが存在していません')
    if ok == 'wrong':
        return msg('ログイン失敗。パスワードが間違っています')
    return redirect('/')


@app.route('/logout')
def logout():
    user.try_logout()
    return msg('ログアウトしました')


# ユーザーの追加機能
@app.route('/user/new')
def user_new():
    return render_template('user_new_form.html', login='未ログイン')


@app.route('/user/new/try', methods=["POST"])
def user_new_try():
    id = user.user_new()
    if id == 0:
        return msg('登録失敗。管理番号は10000~99999の数字を入力してください')
    if id == 1:
        return msg('登録失敗。管理番号が既に存在しています')
    if id == 2:
        return msg('登録失敗。ユーザー名が既に存在しています')
    return msg('新規ユーザー登録完了')


# ユーザー情報の編集機能
@app.route('/user/edit')
@user.login_required
def user_edit():
    username = user.get_id()
    user_id = user.get_user_id_2()
    name = user.get_user_name()
    password = user.get_user_password()
    logout = Markup(a)
    return render_template('user_edit_form.html', username=username, user_id=user_id, name=name, password=password,
                           login='でログイン中　　　', logout=logout)


@app.route('/user/edit/try', methods=["POST"])
@user.login_required
def user_edit_try():
    id = user.user_edit()
    if id == 1:
        return msg('更新失敗。管理番号は10000~99999の数字を入力してください')
    if id == 2:
        return msg('更新失敗。管理番号が既に存在しています')
    if id == 3:
        return msg('更新失敗。ユーザー名が既に存在しています')
    return msg('ユーザー情報を更新しました')


# メイン画面 - 学生情報一覧
@app.route('/')
@user.login_required
def index():
    students = student_db.get_files()
    # ページ番号を振る
    page_s = request.args.get('page', '0')
    page = int(page_s)
    # 表示データの先頭を計算
    index = page * limit
    # ページャーを作る
    s = make_pager(page, len(students), limit)
    s = Markup(s)
    username = user.get_id()
    power = user.get_user_power()
    logout = Markup(a)
    return render_template('index.html', students=students, username=username, login='でログイン中　　　',
                           logout=logout, s=s, limit=limit, index=index, power=power)


def make_button(href, label):
    klass = 'btn btn-primary'
    if href == '#':
        klass += ' disabled'
    return '''
    <a href="{0}" class="{1}">{2}</a>
    '''.format(href, klass, label)


def make_pager(page, total, per_page):
    # ページ数を計算
    page_count = math.ceil(total / per_page)
    s = '<div style="text-align:center;">'
    # 前へボタン
    prev_link = '?page=' + str(page - 1)
    if page <= 0:
        prev_link = '#'
    s += make_button(prev_link, '←前へ')
    # ページ番号
    s += '{0}/{1}'.format(page+1, page_count)
    # 次へボタン
    next_link = '?page=' + str(page + 1)
    if page >= page_count - 1:
        next_link = '#'
    s += make_button(next_link, '次へ→')
    s += '</div>'
    return s


# 学生情報の追加機能
@app.route('/student/new')
@user.login_required
@user.power_required
def student_new():
    logout = Markup(a)
    return render_template('student_new_form.html', username=user.get_id(), login='でログイン中　　　',
                           logout=logout)


@app.route('/student/new/try', methods=["POST"])
@user.login_required
@user.power_required
def student_new_try():
    id = student_db.student_new()
    if id == 'exist':
        return msg('登録失敗。学籍番号が既に存在しています')
    if id == 'short':
        return msg('登録失敗。学籍番号は100~999の数字を入力してください')
    return msg('学生情報を登録しました')


# 学生情報を削除
@app.route('/student/delete/<student_id>/try')
@user.login_required
@user.power_required
def student_delete_try(student_id):
    id = student_db.student_delete(student_id)
    return redirect('/')


# 学生情報の編集機能
@app.route('/student/edit/<student_id>')
@user.login_required
@user.power_required
def student_edit(student_id):
    students = student_db.get_student_files(student_id)
    logout = Markup(a)
    return render_template('student_edit_form.html', username=user.get_id(), login='でログイン中　　　', logout=logout,
                           students=students)


@app.route('/student/edit/try', methods=["POST"])
@user.login_required
@user.power_required
def student_edit_try():
    id = student_db.student_edit()
    return msg('学生情報を更新しました')


def msg(s):
    return render_template('msg.html', msg=s)


# CSSなど静的ファイルの後ろにバージョンを自動追記
@app.context_processor
def add_staticfile():
    return dict(staticfile=staticfile_cp)


def staticfile_cp(fname):
    import os
    path = os.path.join(app.root_path, 'static', fname)
    mtime = str(int(os.stat(path).st_mtime))
    return '/static/' + fname + '?v=' + str(mtime)


if __name__ == '__main__':
    app.debug = True
    app.run(host='localhost', port=9000)
    