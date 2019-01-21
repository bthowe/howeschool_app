import os
import sys
import json
import datetime
import pandas as pd
from flask_pymongo import PyMongo
from collections import defaultdict
from flask_bootstrap import Bootstrap
from flask import Flask, render_template, url_for, request, session, redirect, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

import helpers_classes
import helpers_constants
import helpers_functions

app = Flask(__name__)
app.secret_key = 'mysecret'
bootstrap = Bootstrap(app)


pd.set_option('max_columns', 1000)
pd.set_option('max_info_columns', 1000)
pd.set_option('expand_frame_repr', False)
pd.set_option('display.max_rows', 30000)
pd.set_option('max_colwidth', 4000)
pd.set_option('display.float_format', lambda x: '%.3f' % x)


app = Flask(__name__)
app.secret_key = 'mysecret'
bootstrap = Bootstrap(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

db_users = PyMongo(app, uri="mongodb://localhost:27017/users")
db_number = PyMongo(app, uri="mongodb://localhost:27017/math_book_info")
db_origin = PyMongo(app, uri="mongodb://localhost:27017/math_exercise_origins")
db_performance = PyMongo(app, uri="mongodb://localhost:27017/math_performance")
db_vocab = PyMongo(app, uri="mongodb://localhost:27017/vocab")
db_script = PyMongo(app, uri="mongodb://localhost:27017/scripture_commentary")
db_forms = PyMongo(app, uri="mongodb://localhost:27017/forms")
db_bank = PyMongo(app, uri="mongodb://localhost:27017/banking")


@login_manager.user_loader
def load_user(username):
    u = db_users.db.users.find_one({'name': username})
    if not u:
        return None
    return helpers_classes.User(u['name'], u['access'])


@app.route('/query_chapter', methods=['POST', 'GET'])
def query_chapter():
    js = json.loads(request.data.decode('utf-8'))
    book = js['book']

    problems_dic = {}

    if js['test']:
        problems_dic[js['start_chapter']] = str(list(map(str, range(1, 21))))
    else:
        start_chapter_details = list(db_number.db[book].find({'chapter': js['start_chapter']}))[0]
        end_chapter_details = list(db_number.db[book].find({'chapter': js['end_chapter']}))[0]

        if int(js['end_chapter']) - int(js['start_chapter']) == 0:  # if start and end is the same chapter
            problems_dic[js['start_chapter']] = str(helpers_functions._problem_list_create(js['start_problem'], js['end_problem'], start_chapter_details['num_lesson_probs']))

        elif int(js['end_chapter']) - int(js['start_chapter']) == 1:  # if start and end is one chapter apart
            problems_dic[js['start_chapter']] = str(helpers_functions._problem_list_create(js['start_problem'], start_chapter_details['num_mixed_probs'], start_chapter_details['num_lesson_probs']))
            problems_dic[js['end_chapter']] = str(helpers_functions._problem_list_create('a', js['end_problem'], end_chapter_details['num_lesson_probs']))

        else:  # if start and end is multiple chapters apart
            problems_dic[js['start_chapter']] = str(helpers_functions._problem_list_create(js['start_problem'], start_chapter_details['num_mixed_probs'], start_chapter_details['num_lesson_probs']))
            problems_dic[js['end_chapter']] = str(helpers_functions._problem_list_create('a', js['end_problem'], end_chapter_details['num_lesson_probs']))
            for chapter in range(int(js['start_chapter']) + 1, int(js['end_chapter'])):
                mid_chapter_details = list(db_number.db[book].find({'chapter': chapter}))[0]
                problems_dic[chapter] = str(helpers_functions._problem_list_create('a', mid_chapter_details['num_mixed_probs'], mid_chapter_details['num_lesson_probs']))

    print(problems_dic)

    return jsonify(problems_dic)


@app.route('/query_book', methods=['POST'])
def query_book():
    js = json.loads(request.data.decode('utf-8'))

    if js['name'] == 'Choose...':
        return jsonify({})
    for book in reversed(helpers_constants.book_lst):
        l = list(db_performance.db[book].find({'kid': js['name']}))
        if l:
            return jsonify(l[0]['book'])
    return ''


@app.route('/add_missed_problems', methods=['POST'])
def add_missed_problems():
    js = json.loads(request.data.decode('utf-8'))

    miss_lst = defaultdict(list)

    for prob in js['add_miss_list']:
        if js['test']:
            miss_lst['test {}'.format(prob['chapter'])].append(prob['problem'])
        else:
            miss_lst[prob['chapter']].append(prob['problem'])
    for prob in js['rem_miss_list']:
        if js['test']:
            miss_lst['test {}'.format(prob['chapter'])].remove(prob['problem'])
        else:
            miss_lst[prob['chapter']].remove(prob['problem'])
    k_to_del = [k for k, v in miss_lst.items() if not miss_lst[k]]
    for k in k_to_del:
        del miss_lst[k]
    js['miss_lst'] = dict(miss_lst)

    if js['test']:
        js['start_chapter'] = 'test {}'.format(js['start_chapter'])
        js['end_chapter'] = 'test {}'.format(js['end_chapter'])

    del js['add_miss_list']
    del js['rem_miss_list']
    del js['test']

    db_performance.db[js['book']].insert_one(js)

    print('data inserted: {}'.format(js))
    return ''


@app.route('/add_problem_origin', methods=['POST'])
def add_problem_origin():
    js = json.loads(request.data.decode('utf-8'))
    print(js)

    collection = db_origin.db[js['book']]
    y = collection.insert_one(js)
    print(y)

    print('data inserted: {}'.format(js))
    return ''


@app.route('/query_chapter2', methods=['POST', 'GET'])
def query_chapter2():
    js = json.loads(request.data.decode('utf-8'))
    print(js)

    book = js['book']

    output = list(db_number.db[book].find({'chapter': js['chapter']}))[0]
    print(output)
    problems_dic = {'num_lesson_probs': output['num_lesson_probs'], 'num_mixed_probs': output['num_mixed_probs']}
    return jsonify(problems_dic)

@app.route('/query_bank', methods=['POST', 'GET'])
def query_bank():
    js = json.loads(request.data.decode('utf-8'))

    sum = 0
    itemized = []
    for entry in list(db_bank.db[js['name']].find()):
        if entry['type'] == 'deposit':
            sum += entry['amount']
        else:
            sum += -entry['amount']

        itemized.append(
            {
                'type': entry['type'],
                'amount': entry['amount'],
                'description': entry['description'],
                'date': entry['date']
            }
        )
    output = {'itemized': itemized, 'total': sum}
    return jsonify(output)















@app.route('/login', methods=['POST', 'GET'])
def login():
    form = helpers_classes.LoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        user = db_users.db.users.find_one({'name': form.username.data})
        if user:
            if form.password.data == user['password']:
            # if check_password_hash(form.password.data, login_user['password']):

                user_obj = helpers_classes.User(user['name'], user['access'])
                login_user(user_obj)
                return redirect(url_for('main_menu'))

        return '<h1>Invalid username or password</h1>'
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('quit'))
    # return redirect(url_for('login'))


@app.route('/main_menu')
@helpers_functions.requires_access_level(helpers_constants.ACCESS['guest'])
@login_required
def main_menu():
    return render_template('main_menu.html', name=current_user.username, access=current_user.access, page_name='Main Menu')

@app.route('/register', methods=['POST', 'GET'])
@helpers_functions.requires_access_level(helpers_constants.ACCESS['admin'])
@login_required
def register():
    form = helpers_classes.RegisterForm()

    if request.method == 'POST' and form.validate_on_submit():
        users = db_users.db.users
        existing_user = users.find_one({'name': form.username.data})

        if existing_user is None:
            # hashpass = generate_password_hash(form.password.data, method='sha256')  # add this in place of the password below
            users.insert({'name': form.username.data, 'password': form.password.data, 'access': form.access.data})

            flash('Registration was successful!')
            return redirect(url_for('register'))

        flash('That username already exists!')
    return render_template('register.html', form=form, access=current_user.access, page_name='Register Child')

@app.route("/enter_performance")
@helpers_functions.requires_access_level(helpers_constants.ACCESS['admin'])
@login_required
def enter_performance():
    return render_template('enter_performance.html', access=current_user.access, page_name='Math Performance')


@app.route("/scripture_commentary", methods=['POST', 'GET'])
@helpers_functions.requires_access_level(helpers_constants.ACCESS['admin'])
@login_required
def scripture_commentary():
    form = helpers_classes.ScriptureDailyForm()
    if request.method == 'POST':  # and form.validate_on_submit():
        tab = db_script.db[form.choose_kid.data]
        for comment in form.comment.data.split('\r'):
            data = helpers_functions.scripture_data_json(form, comment)
            ret = tab.insert_one(data)
            print('data inserted: {}'.format(ret))
        return redirect(url_for('scripture_commentary'))
    return render_template('scripture_commentary.html', form=form, access=current_user.access, page_name='Scripture Commentary')


@app.route("/weekly_forms_create", methods=['POST', 'GET'])
@helpers_functions.requires_access_level(helpers_constants.ACCESS['admin'])
@login_required
def weekly_forms_create():
    today = datetime.date.today()
    date_shift = 7 - today.weekday()  # Monday is 0
    date = str(today + datetime.timedelta(date_shift))
    output = {k: v for k, v in list(db_forms.db.Weekly.find())[-1].items() if k != '_id'}

    form = helpers_classes.WeeklyForm()
    if request.method == 'POST':  # and form.validate_on_submit():
        data = helpers_functions.weekly_data_json(form)
        tab = db_forms.db['Weekly']
        ret = tab.insert_one(data)
        print('data inserted: {}'.format(ret))

        helpers_functions.latex_create(
                ['Calvin', 'Samuel', 'Kay'],
                [form.cal_book.data, form.sam_book.data, form.kay_book.data],
                [str(form.weekof.data + datetime.timedelta(days)) for days in range(0, 6)],
                [form.scripture_ref.data, form.scripture.data],
                [form.mon_dis.data, form.tue_dis.data, form.wed_dis.data, form.thu_dis.data, form.fri_dis.data, form.sat_dis.data],
                [form.mon_job.data, form.tue_job.data, form.wed_job.data, form.thu_job.data, form.fri_job.data, form.sat_job.data]
        )
        helpers_functions.weekly_forms_email()
        helpers_functions.weekly_browser_display()
        return redirect(url_for('weekly_forms_create'))
    return render_template('weekly_forms_create.html', form=form, date=date, form_data=output, access=current_user.access, page_name='Weekly Forms')


@app.route("/enter_problem_number", methods=['POST', 'GET'])
@helpers_functions.requires_access_level(helpers_constants.ACCESS['admin'])
@login_required
def enter_problem_number():
    form = helpers_classes.NumberofExercisesForm()
    chapter = 1
    if request.method == 'POST':  # and form.validate_on_submit():
        data = helpers_functions.math_num_data_json(form)
        tab = db_forms.db[form.choose_book.data]
        ret = tab.insert_one(data)
        print('data inserted: {}'.format(ret))
        chapter += form.chapter.data
        return render_template('enter_problem_number.html', form=form, access=current_user.access, page_name='Number of Exercises', chapter=chapter)
    return render_template('enter_problem_number.html', form=form, access=current_user.access, page_name='Number of Exercises', chapter=chapter)

@app.route("/enter_problem_origin")
@helpers_functions.requires_access_level(helpers_constants.ACCESS['admin'])
@login_required
def enter_problem_origin():
    return render_template('enter_problem_origins.html', access=current_user.access, page_name='Origin of Exercises')




@app.route('/mongo_call_vocab', methods=['POST'])
def mongo_call_vocab():
    js = json.loads(request.data.decode('utf-8'))
    js['name'] = current_user.username

    tab = db_vocab[js['page']]
    tab.insert_one(js)

    print('data inserted: {}'.format(js))
    return ''

@app.route("/vocab", methods=['POST', 'GET'])
@helpers_functions.requires_access_level(helpers_constants.ACCESS['guest'])
@login_required
def vocab():
    form = helpers_classes.VocabForm()
    if request.method == 'POST' and form.validate_on_submit():
        if form.practice_type.data == 'quiz':
            return redirect(url_for('quiz_card', lesson_num=form.lesson_num.data, prompt_type=form.prompt_type.data))
        else:
            return redirect(url_for('practice_card', lesson_num=form.lesson_num.data, prompt_type=form.prompt_type.data))
    return render_template('vocab.html', form=form, page_name='Vocabulary Menu', access=current_user.access)


@app.route("/practice_card")
@helpers_functions.requires_access_level(helpers_constants.ACCESS['guest'])
@login_required
def practice_card():
    lesson_num = 4
    prompt_type = 'word'
    num_cards = len(os.listdir('static/{0}'.format(lesson_num)))

    if prompt_type == 'word':
        cards = [['static/{0}/rc_vocab_{0}_{1}.png'.format(lesson_num, num),
                  'static/{0}/rc_vocab_{0}_{1}.png'.format(lesson_num, num + 1)] for num in range(0, num_cards, 2)]
    else:
        cards = [['static/{0}/rc_vocab_{0}_{1}.png'.format(lesson_num, num + 1),
                  'static/{0}/rc_vocab_{0}_{1}.png'.format(lesson_num, num)] for num in range(0, num_cards, 2)]

    return render_template("practice_card.html", cards=cards, access=current_user.access, page_name='Vocabulary Practice', lesson_num=lesson_num)


@app.route("/quiz_card")
@helpers_functions.requires_access_level(helpers_constants.ACCESS['guest'])
@login_required
def quiz_card():
    lesson_num = str(request.args['lesson_num'])
    prompt_type = str(request.args['prompt_type'])
    num_cards = len(os.listdir('static/{0}'.format(lesson_num)))

    if prompt_type == 'word':
        cards = [['../static/{0}/rc_vocab_{0}_{1}.png'.format(lesson_num, num),
                  '../static/{0}/rc_vocab_{0}_{1}.png'.format(lesson_num, num + 1)] for num in range(0, num_cards, 2)]
        alternatives = helpers_functions._alternatives_create(len(cards), 1)

    else:
        cards = [['../static/{0}/rc_vocab_{0}_{1}.png'.format(lesson_num, num + 1),
                  '../static/{0}/rc_vocab_{0}_{1}.png'.format(lesson_num, num)] for num in range(0, num_cards, 2)]
        alternatives = helpers_functions._alternatives_create(len(cards), 0)

    return render_template('quiz_card.html', cards=cards, alts=alternatives, access=current_user.access, page_name='Vocabulary Quiz', lesson_num=lesson_num)


@app.route("/banking_manage", methods=['POST', 'GET'])
@helpers_functions.requires_access_level(helpers_constants.ACCESS['admin'])
@login_required
def banking_manage():
    form = helpers_classes.CreditDebit()
    if request.method == 'POST':  # and form.validate_on_submit():
        data = helpers_functions.credit_debit_data(form)
        tab = db_bank.db[form.choose_kid.data]
        ret = tab.insert_one(data)
        print('data inserted: {}'.format(ret))
    return render_template('banking_manage.html', form=form, access=current_user.access, page_name='Banking Accounts Manage')

@app.route("/banking_history")
@helpers_functions.requires_access_level(helpers_constants.ACCESS['admin'])
@login_required
def banking_history():
    return render_template('banking_history.html', access=current_user.access, page_name='Banking History')

@app.route("/banking_history_personal")
@helpers_functions.requires_access_level(helpers_constants.ACCESS['user'])
@login_required
def banking_history_personal():
    return render_template('banking_history_personal.html', name=current_user.username, access=current_user.access, page_name='Banking History')


@app.route('/killer', methods=['POST'])
def killer():
    sys.exit(4)
    return ''

@app.route('/quit')
def quit():
    return render_template('quit.html')

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=8001, debug=True)