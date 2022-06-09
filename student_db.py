from student_sqlite import exec, select
from flask import request


# 新規学生を登録
def student_new():
    student_id = request.form.get('student_id')
    call_name = request.form.get('call_name')
    country = request.form.get('country')
    visa_expiry = request.form.get('visa_expiry')
    memo = request.form.get('memo')
    a = get_students(student_id)
    if student_id == a:
        return 'exist'
    int_student_id = int(student_id)
    if int_student_id < 100 or int_student_id > 999:
        return 'short'
    student_id = exec('INSERT INTO student (student_id, call_name, country, visa_expiry, memo) VALUES (?, ?, ?, ?, ?)',
                      student_id, call_name, country, visa_expiry, memo)
    return student_id


# 学生情報を編集
def student_edit():
    student_id = request.form.get('student_id')
    call_name = request.form.get('call_name')
    country = request.form.get('country')
    visa_expiry = request.form.get('visa_expiry')
    memo = request.form.get('memo')
    execute = exec('UPDATE student SET student_id=?, call_name=?, country=?, visa_expiry=?, memo=? WHERE student_id=?',
                   student_id, call_name, country, visa_expiry, memo, student_id)
    return execute


# 学生情報を削除
def student_delete(student_id):
    # student_id = request.form.get('student_id')
    execute = exec('DELETE FROM student WHERE student_id=?', student_id)
    return execute


# 特定の学生情報を得る　（新規学生登録用）
def get_students(student_id):
    a = select('SELECT * FROM student WHERE student_id=?', student_id)
    if len(a) == 0:
        return None
    return student_id


# データベースの学生テーブルの情報を得る
def get_files():
    a = select('SELECT * FROM student')
    return a


# 特定の学生情報を得る　（学生情報を編集、削除用）
def get_student_files(student_id):
    return select('''
        SELECT * FROM student WHERE student_id=?''', student_id)
