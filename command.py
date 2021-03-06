import os
import os.path
import json
import datetime
import subprocess
import pandas as pd
from flask_pymongo import PyMongo
from collections import defaultdict
from flask_bootstrap import Bootstrap
from flask import Flask, render_template, url_for, request, redirect, flash, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

import helpers_classes
import helpers_constants
import helpers_functions

# mongod --dbpath ~/path/to/your/app/data

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
db_aggregate = PyMongo(app, uri="mongodb://localhost:27017/math_aggregate")
db_time = PyMongo(app, uri="mongodb://localhost:27017/math_time_aggregate")


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
    total_problems_dic = {}

    if js['test']:
        problems_dic[js['start_chapter']] = str(list(map(str, range(1, 21))))
        total_problems_dic[js['start_chapter']] = str(list(map(str, range(1, 21))))
    else:
        start_chapter_details = list(db_number.db[book].find({'chapter': js['start_chapter']}))[0]
        end_chapter_details = list(db_number.db[book].find({'chapter': js['end_chapter']}))[0]

        if int(js['end_chapter']) - int(js['start_chapter']) == 0:  # if start and end is the same chapter
            problems_dic[js['start_chapter']] = str(helpers_functions._problem_list_create(js['start_problem'], js['end_problem'], start_chapter_details['num_lesson_probs']))

            if start_chapter_details['num_lesson_probs'] == 'none':
                total_problems_dic[js['start_chapter']] = str(helpers_functions._problem_list_create(1, start_chapter_details['num_mixed_probs'], start_chapter_details['num_lesson_probs']))
            else:
                total_problems_dic[js['start_chapter']] = str(helpers_functions._problem_list_create('a', start_chapter_details['num_mixed_probs'], start_chapter_details['num_lesson_probs']))

        elif int(js['end_chapter']) - int(js['start_chapter']) == 1:  # if start and end is one chapter apart
            problems_dic[js['start_chapter']] = str(helpers_functions._problem_list_create(js['start_problem'], start_chapter_details['num_mixed_probs'], start_chapter_details['num_lesson_probs']))
            problems_dic[js['end_chapter']] = str(helpers_functions._problem_list_create('a', js['end_problem'], end_chapter_details['num_lesson_probs']))

            if start_chapter_details['num_lesson_probs'] == 'none':
                total_problems_dic[js['start_chapter']] = str(helpers_functions._problem_list_create(1, start_chapter_details['num_mixed_probs'], start_chapter_details['num_lesson_probs']))
            else:
                total_problems_dic[js['start_chapter']] = str(helpers_functions._problem_list_create('a', start_chapter_details['num_mixed_probs'], start_chapter_details['num_lesson_probs']))
            if end_chapter_details['num_lesson_probs'] == 'none':
                total_problems_dic[js['end_chapter']] = str(helpers_functions._problem_list_create(1, end_chapter_details['num_mixed_probs'], end_chapter_details['num_lesson_probs']))
            else:
                total_problems_dic[js['end_chapter']] = str(helpers_functions._problem_list_create('a', end_chapter_details['num_mixed_probs'], end_chapter_details['num_lesson_probs']))

        else:  # if start and end is multiple chapters apart
            problems_dic[js['start_chapter']] = str(helpers_functions._problem_list_create(js['start_problem'], start_chapter_details['num_mixed_probs'], start_chapter_details['num_lesson_probs']))
            problems_dic[js['end_chapter']] = str(helpers_functions._problem_list_create('a', js['end_problem'], end_chapter_details['num_lesson_probs']))

            if start_chapter_details['num_lesson_probs'] == 'none':
                total_problems_dic[js['start_chapter']] = str(helpers_functions._problem_list_create(1, start_chapter_details['num_mixed_probs'], start_chapter_details['num_lesson_probs']))
            else:
                total_problems_dic[js['start_chapter']] = str(helpers_functions._problem_list_create('a', start_chapter_details['num_mixed_probs'], start_chapter_details['num_lesson_probs']))
            if end_chapter_details['num_lesson_probs'] == 'none':
                total_problems_dic[js['end_chapter']] = str(helpers_functions._problem_list_create(1, end_chapter_details['num_mixed_probs'], end_chapter_details['num_lesson_probs']))
            else:
                total_problems_dic[js['end_chapter']] = str(helpers_functions._problem_list_create('a', end_chapter_details['num_mixed_probs'], end_chapter_details['num_lesson_probs']))

            for chapter in range(int(js['start_chapter']) + 1, int(js['end_chapter'])):
                mid_chapter_details = list(db_number.db[book].find({'chapter': chapter}))[0]
                problems_dic[chapter] = str(helpers_functions._problem_list_create('a', mid_chapter_details['num_mixed_probs'], mid_chapter_details['num_lesson_probs']))

                if mid_chapter_details['num_lesson_probs'] == 'none':
                    total_problems_dic[chapter] = str(helpers_functions._problem_list_create(1, mid_chapter_details['num_mixed_probs'], mid_chapter_details['num_lesson_probs']))
                else:
                    total_problems_dic[chapter] = str(helpers_functions._problem_list_create('a', mid_chapter_details['num_mixed_probs'], mid_chapter_details['num_lesson_probs']))

    return jsonify({'problems_dic': problems_dic, 'total_problems_dic': total_problems_dic})


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

    if js['test']:
        js['start_chapter'] = 'test {}'.format(js['start_chapter'])
        js['end_chapter'] = 'test {}'.format(js['end_chapter'])
        js['miss_lst'] = helpers_functions.miss_lst_create(js, 'add_miss_list', test=True)
        js['hard_lst'] = helpers_functions.miss_lst_create(js, 'hard_miss_list', test=True)
    else:
        js['miss_lst'] = helpers_functions.miss_lst_create(js, 'add_miss_list')
        js['hard_lst'] = helpers_functions.miss_lst_create(js, 'hard_miss_list')

    # update aggregate performance and time databases
    if js['test']:
        record = helpers_functions._test_atomize(js).to_dict(orient='records')
        db_aggregate.db[js['kid']].insert_many(record)
    else:
        record = helpers_functions._ass_atomize(
                db_origin.db[js['book']],
                db_number.db[js['book']],
                js
            ).to_dict(orient='records')
        db_aggregate.db[js['kid']].insert_many(record)
    db_time.db[js['kid']].insert_one(helpers_functions._elapsed_time(js)[0])

    del js['add_miss_list']
    del js['hard_miss_list']
    del js['rem_miss_list']
    del js['test']

    # update performance database
    ret = db_performance.db[js['book']].insert_one(js)

    print('data inserted: {}'.format(ret))

    return ''


@app.route('/add_problem_origin', methods=['POST'])
def add_problem_origin():
    js = json.loads(request.data.decode('utf-8'))

    if js['flag'] == 0:
        ret = db_origin.db[js['book']].update({'book': js['book'], 'chapter': js['chapter']}, {'book': js['book'], 'chapter': js['chapter'], 'origin_list': js['origin_list']}, upsert=True)
        print('data updated: {}'.format(ret))
    else:
        ret = db_origin.db[js['book']].insert_one({'book': js['book'], 'chapter': js['chapter'], 'origin_list': js['origin_list']})
        print('data inserted: {}'.format(ret))
    return ''


@app.route('/query_chapter2', methods=['POST', 'GET'])
def query_chapter2():
    js = json.loads(request.data.decode('utf-8'))

    book = js['book']

    output = list(db_number.db[book].find({'chapter': js['chapter']}))[0]

    origin_problems = list(db_origin.db[book].find({'chapter': js['chapter']}))
    if origin_problems:
        return jsonify({'origin_lst': origin_problems[0]['origin_list'], 'num_lesson_probs': output['num_lesson_probs'], 'num_mixed_probs': output['num_mixed_probs'], 'flag': 0})
    return jsonify({'num_lesson_probs': output['num_lesson_probs'], 'num_mixed_probs': output['num_mixed_probs'], 'flag': 1})

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
                'amount': '{0:.2f}'.format(entry['amount']),
                'description': entry['description'],
                'date': entry['date'],
                'cumulative': '{0:.2f}'.format(sum)
            }
        )
    output = {'itemized': itemized, 'total': '{0:.2f}'.format(sum)}
    return jsonify(output)

@app.route('/query_dbs', methods=['POST', 'GET'])
def query_dbs():
    js = json.loads(request.data.decode('utf-8'))

    dbs = js['dbs']
    if dbs == 'Forms':
        date = 'week_start_date'
        database = db_forms
    elif dbs == 'Math Daily':
        date = 'date'
        database = db_performance
    elif dbs == 'Math Origins':
        database = db_origin
    elif dbs == 'Scripture Commentary':
        database = db_script
        date = 'date'
    elif dbs == 'Users':
        database = db_users
    elif dbs == 'Math Aggregate':
        date = 'date'
        database = db_aggregate


    if js['collection'] == 'All':
        collections = database.db.collection_names()
    else:
        collections = [js['collection']]

    docs = []
    for col in collections:
        if js['date'] != '':
            docs += list(database.db[col].find({date: js['date']}, {'_id': False}))
        else:
            docs += list(database.db[col].find({}, {'_id': False}))

    docs = [{str(k): str(v) for k, v in doc.items()} for doc in docs]

    return jsonify(items=docs)


@app.route('/aggregate_kickoff', methods=['GET'])
def aggregate_kickoff():
    subprocess.Popen(['python3', '/home/pi/PythonProjects/howeschool_app/aggregator_math_performance.py'])
    subprocess.Popen(['python3', '/home/pi/PythonProjects/howeschool_app/aggregator_math_time.py'])
    # subprocess.Popen(['python3', '/Users/thowe/PycharmProjects/resources_repos/howeschool_app/aggregator_math_performance.py'])
    # subprocess.Popen(['python3', '/Users/thowe/PycharmProjects/resources_repos/howeschool_app/aggregator_math_time.py'])
    return ''














@app.route('/login', methods=['POST', 'GET'])
def login():
    form = helpers_classes.LoginForm()
    if current_user.is_authenticated:
        return redirect(url_for('main_menu'))
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
    return redirect(url_for('login'))


# todo: at some point I'll probably want to put these three functions in the helpers file
def performance_over_time(df, varname):
    def js_month(x):
        x_lst = x.split('-')
        x_lst[1] = str(int(x_lst[1]) - 1)
        if len(x_lst[1]) == 1:
            x_lst[1] = '0' + x_lst[1]
        return '-'.join(x_lst)
    df['date'] = df['date'].astype(str).apply(js_month)  # this zero indexes the month for js's benefit.

    return df[varname].\
        groupby(df['date']).mean().\
        reset_index(drop=False). \
        assign(position=range(0, df['date'].unique().shape[0]))


def math_daily_create(name):
    df = pd.DataFrame(list(db_aggregate.db[name].find()))
    df['date'] = pd.to_datetime(df['date'])
    df = df.loc[df['date'] >= datetime.date.today() - datetime.timedelta(days=30)]
    df.sort_values('date', ascending=True, inplace=True)
    return performance_over_time(df, 'correct').to_dict('records')


def math_daily_time(name):
    df = pd.DataFrame(list(db_time.db[name].find()))
    df['date'] = pd.to_datetime(df['date'])
    df = df.loc[df['date'] >= datetime.date.today() - datetime.timedelta(days=30)]
    df.sort_values('date', ascending=True, inplace=True)
    return performance_over_time(df[['date', 'duration']], 'duration').to_dict('records')


def _num_practice_probs(x):
    alpha = 'abcdefghijklmnopqrstuvwxyz'
    if x != 'none':
        return alpha.index(x)
    return 0


def _avg_num_probs_in_book(book):
    df = pd.DataFrame(list(db_number.db[book].find())).dropna()
    df['num_of_probs'] = df.apply(lambda x: int(x['num_mixed_probs']) + _num_practice_probs(x['num_lesson_probs']) + 1, axis=1)
    return df['num_of_probs'].mean()

def _indicator_dic():
    dict_out = {}
    for kid in ['Calvin', 'Samuel', 'Kay']:
        df1 = pd.DataFrame(list(db_aggregate.db[kid].find()))
        df1['date'] = pd.to_datetime(df1['date'])
        df1.sort_values('date', ascending=True, inplace=True)

        last_date = df1.iloc[-1]['date'].date()
        df1.query('date == "{}"'.format(last_date), inplace=True)

        df2 = pd.DataFrame(list(db_time.db[kid].find()))
        df2.query('date == "{}"'.format(last_date), inplace=True)

        book = df1.iloc[-1]['book']

        total_probs = df1.shape[0] / _avg_num_probs_in_book(book)
        duration = int(df2['duration']) / 120
        perc_correct = df1['correct'].mean()
        perc_nothard = 1 - df1['hard'].mean()

        dict_out[kid] = {
            'total_probs': total_probs,
            'duration': duration,
            'perc_correct': perc_correct,
            'perc_nothard': perc_nothard,
            'date': str(last_date)
        }
    return dict_out

@app.route('/main_menu')
@helpers_functions.requires_access_level(helpers_constants.ACCESS['guest'])
@login_required
def main_menu():
    return render_template(
        'main_menu.html',
        name=current_user.username,
        access=current_user.access,
        page_name='Main Menu',
        df_calvin=math_daily_create('Calvin'),
        df_samuel=math_daily_create('Samuel'),
        df_kay=math_daily_create('Kay'),
        df_calvin_time=math_daily_time('Calvin'),
        df_samuel_time=math_daily_time('Samuel'),
        df_kay_time=math_daily_time('Kay'),
        indicator_dic=_indicator_dic()
    )

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


@app.route("/enter_performance", methods=['POST', 'GET'])
@helpers_functions.requires_access_level(helpers_constants.ACCESS['admin'])
@login_required
def enter_performance():
    form = helpers_classes.ScriptureDailyForm()
    if request.method == 'POST':  # and form.validate_on_submit():
        tab = db_script.db[form.choose_kid.data]
        for comment in form.comment.data.split('\r'):
            data = helpers_functions.scripture_data_json(form, comment)
            ret = tab.insert_one(data)
            print('data inserted: {}'.format(ret))
        return redirect(url_for('enter_performance'))
    return render_template('enter_performance.html', form=form, access=current_user.access, page_name='Performance')


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
        data_weekly = helpers_functions.weekly_data_json(form)
        ret_weekly = db_forms.db['Weekly'].insert_one(data_weekly)
        print('Weekly data inserted: {}'.format(ret_weekly))
        helpers_functions.weekly_form_latex_create(
                ['Calvin', 'Samuel', 'Kay', 'Seth'],
                [form.cal_book.data, form.sam_book.data, form.kay_book.data, form.seth_book.data],
                [str(form.weekof.data + datetime.timedelta(days)) for days in range(0, 6)],
                [form.scripture_ref.data, form.scripture.data],
                [form.discussion_ref.data, form.discussion_question.data],
                {
                    'Calvin': [form.cal_goal1.data],
                    'Samuel': [form.sam_goal1.data],
                    'Kay': [form.kay_goal1.data],
                    'Seth': [form.seth_goal1.data]
                },
                [form.mon_job.data, form.tue_job.data, form.wed_job.data, form.thu_job.data, form.fri_job.data, form.sat_job.data]
        )
        data_scriptures = helpers_functions.scripture_list_json(form)
        ret_scriptures = db_forms.db['Scriptures'].insert_one(data_scriptures)
        print('Scriptures data inserted: {}'.format(ret_scriptures))
        helpers_functions.scripture_table_create(pd.DataFrame(list(db_forms.db['Scriptures'].find())))
        helpers_functions.goals_latex_create(
            ['Calvin', 'Samuel', 'Kay', 'Seth'],
            {
                'Calvin': [form.cal_goal1.data],
                'Samuel': [form.sam_goal1.data],
                'Kay': [form.kay_goal1.data],
                'Seth': [form.seth_goal1.data]
            }
        )

        return redirect(url_for('weekly_forms_create'))
    return render_template('weekly_forms_create.html', form=form, date=date, form_data=output, access=current_user.access, page_name='Weekly Forms')

@app.route("/download_forms", methods=['POST', 'GET'])
@helpers_functions.requires_access_level(helpers_constants.ACCESS['admin'])
@login_required
def download_forms():
    form = helpers_classes.DownloadFormsForm()

    path_week_base = '/home/pi/PythonProjects/howeschool_app/weekly_time_sheet.pdf'
    path_scrip_base = '/home/pi/PythonProjects/howeschool_app/scripture_table.pdf'
    path_goals_base = '/home/pi/PythonProjects/howeschool_app/goals_table.pdf'
    path_week_static = '/home/pi/PythonProjects/howeschool_app/static/weekly_time_sheet.pdf'
    path_scrip_static = '/home/pi/PythonProjects/howeschool_app/static/scripture_table.pdf'
    path_goals_static = '/home/pi/PythonProjects/howeschool_app/static/goals_table.pdf'

    if os.path.exists(path_week_base):
        os.rename(path_week_base, path_week_static)
    if os.path.exists(path_scrip_base):
        os.rename(path_scrip_base, path_scrip_static)
    if os.path.exists(path_goals_base):
        os.rename(path_goals_base, path_goals_static)

    if request.method == 'POST':  # and form.validate_on_submit():
        helpers_functions.weekly_forms_email()
        return redirect(url_for('download_forms'))
    # todo: flash message that the email has been sent.
    return render_template(
        'download_forms.html',
        form=form,
        access=current_user.access,
        page_name='Download Forms',
        weekly_forms_pdf=str(datetime.datetime.fromtimestamp(os.path.getmtime(path_week_static))),
        scripture_list_pdf=str(datetime.datetime.fromtimestamp(os.path.getmtime(path_scrip_static))),
        goals_list_pdf=str(datetime.datetime.fromtimestamp(os.path.getmtime(path_goals_static)))
    )




@app.route("/enter_problem_number", methods=['POST', 'GET'])
@helpers_functions.requires_access_level(helpers_constants.ACCESS['admin'])
@login_required
def enter_problem_number():
    form = helpers_classes.NumberofExercisesForm()
    chapter = 1
    if request.method == 'POST':  # and form.validate_on_submit():
        data = helpers_functions.math_num_data_json(form)
        ret = db_number.db[form.choose_book.data].insert_one(data)
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

    ret = db_vocab.db[js['page']].insert_one(js)
    print('data inserted: {}'.format(ret))
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
    lesson_num = str(request.args['lesson_num'])
    prompt_type = str(request.args['prompt_type'])
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
        return redirect(url_for('banking_manage'))
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



@app.route("/sotw", methods=['POST', 'GET'])
@helpers_functions.requires_access_level(helpers_constants.ACCESS['guest'])
@login_required
def sotw():
    df_scripture = pd.DataFrame(list(db_forms.db['Scriptures'].find())).sort_values('week_start_date').values[-1, :]
    if df_scripture[1] == 'Review Time!':
        script = pd.DataFrame(list(db_forms.db['Scriptures'].find({}, {'_id': False}))).sort_values('week_start_date').iloc[-4:-1].to_dict('records')
        return render_template('sotw.html', scripture=script, page_name='Scripture of the Week', access=current_user.access)

    script = pd.DataFrame(list(db_forms.db['Scriptures'].find({}, {'_id': False}))).sort_values('week_start_date').iloc[-1:].to_dict('records')
    return render_template('sotw.html', scripture=script, page_name='Scripture of the Week', access=current_user.access)


@app.route("/qotw", methods=['POST', 'GET'])
@helpers_functions.requires_access_level(helpers_constants.ACCESS['guest'])
@login_required
def qotw():
    questions = pd.DataFrame(list(db_forms.db['Weekly'].find())).sort_values('week_start_date')[['mon_question', 'tue_question', 'wed_question', 'thu_question', 'fri_question', 'sat_question']].iloc[[-1]].to_dict('records')
    return render_template('qotw.html', questions=questions, page_name='Questions of the Week', access=current_user.access)


@app.route("/math_todo")
@helpers_functions.requires_access_level(helpers_constants.ACCESS['admin'])
@login_required
def math_todo():
    begin_date = str(datetime.date.today() - datetime.timedelta(17))

    df = {
        'Calvin': helpers_functions._math_todo_create('Calvin', db_aggregate, begin_date),
        'Samuel': helpers_functions._math_todo_create('Samuel', db_aggregate, begin_date),
        'Kay': helpers_functions._math_todo_create('Kay', db_aggregate, begin_date)
    }
    return render_template('math_todo.html', math_todo=df, access=current_user.access, page_name='Math To Do')


@app.route("/database_viewer", methods=['POST', 'GET'])
@helpers_functions.requires_access_level(helpers_constants.ACCESS['admin'])
@login_required
def database_viewer():
    return render_template('data_viewer.html', page_name='Table Viewer', access=current_user.access)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001, debug=True)
