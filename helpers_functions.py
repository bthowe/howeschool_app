import os
import string
import yagmail
import datetime
import itertools
import subprocess
import numpy as np
import pandas as pd
from functools import wraps
from collections import defaultdict
from flask import url_for, redirect
from flask_login import current_user

import helpers_constants


def requires_access_level(access_level):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.allowed(access_level):
                return redirect(url_for('main_menu', message="You do not have access to that page. Sorry!"))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def weekly_data_json(form):
    data = {
        "week_start_date": str(form.weekof.data),
        "scripture_ref": form.scripture_ref.data,
        "scripture": form.scripture.data,
        "discussion_ref": form.discussion_ref.data,
        "discussion_question": form.discussion_question.data,
        "mon_job": form.mon_job.data,
        "tue_job": form.tue_job.data,
        "wed_job": form.wed_job.data,
        "thu_job": form.thu_job.data,
        "fri_job": form.fri_job.data,
        "sat_job": form.sat_job.data,
        "calvin_goal1": form.cal_goal1.data,
        "calvin_goal2": form.cal_goal2.data,
        "calvin_goal3": form.cal_goal3.data,
        "calvin_goal4": form.cal_goal4.data,
        "samuel_goal1": form.sam_goal1.data,
        "samuel_goal2": form.sam_goal2.data,
        "samuel_goal3": form.sam_goal3.data,
        "samuel_goal4": form.sam_goal4.data,
        "kay_goal1": form.kay_goal1.data,
        "kay_goal2": form.kay_goal2.data,
        "kay_goal3": form.kay_goal3.data,
        "kay_goal4": form.kay_goal4.data,
        "calvin_book": form.cal_book.data,
        "samuel_book": form.sam_book.data,
        "kay_book": form.kay_book.data
    }
    return data

def scripture_data_json(form, comment):
    data = {
        "name": form.choose_kid.data,
        "date": str(form.date.data),
        "start_book": form.start_book.data,
        "start_chapter": form.start_chapter.data,
        "start_verse": form.start_verse.data,
        "end_book": form.end_book.data,
        "end_chapter": form.end_chapter.data,
        "end_verse": form.end_verse.data,
        "comment": comment.replace('\n', '')
    }
    return data

def math_num_data_json(form):
    if form.test.data:
        chapter = 'test ' + str(form.chapter.data)
    else:
        chapter = form.chapter.data
    data = {
        "book": form.choose_book.data,
        "chapter": chapter,
        "num_lesson_probs": form.num_lesson_probs.data,
        "num_mixed_probs": form.num_mixed_probs.data
    }
    return data

def credit_debit_data(form):
    print(form.amount.data)
    data = {
        "kid": form.choose_kid.data,
        "type": form.credit_debit.data,
        "amount": form.amount.data,
        "description": form.description.data,
        "date": str(datetime.date.today())
    }
    return data

def weekly_forms_email():
    yag = yagmail.SMTP('b.travis.howe@gmail.com', os.environ['GMAIL'])
    yag.send(
        ["b.travis.howe@gmail.com", "kassie.howe@gmail.com"],
        subject="Forms for the Week",
        contents="",
        attachments=[
            '/home/pi/PythonProjects/howeschool_app/static/weekly_time_sheet.pdf',
            '/home/pi/PythonProjects/howeschool_app/static/scripture_table.pdf',
        ]
    )

def _time_sheets(dates, goals, name, scrip):
    return '''
    \\begin{{sidewaystable}}
    \\centering
    \\begin{{tabular}}{{|l|p{{1.5cm}}|p{{1.5cm}}|p{{1.5cm}}|p{{1.5cm}}|p{{1.5cm}}|p{{1.5cm}}|p{{1.5cm}}|p{{1.5cm}}|p{{1.5cm}}|p{{1.5cm}}|p{{1.5cm}}|p{{1.5cm}}|}}
    \\multicolumn{{7}}{{l}}{{Name: {12}}} \\\\
    \\multicolumn{{13}}{{p{{25cm}}}}{{Scripture: {13}}} \\\\
    \\multicolumn{{7}}{{l}}{{}} \\\\
    \\multicolumn{{7}}{{l}}{{}} \\\\
    \\cline{{2-13}}
    \\multicolumn{{1}}{{l}}{{}} & \\multicolumn{{2}}{{|c|}}{{Monday}} & \\multicolumn{{2}}{{c|}}{{Tuesday}} & \\multicolumn{{2}}{{c|}}{{Wednesday}} & \\multicolumn{{2}}{{c|}}{{Thursday}} & \\multicolumn{{2}}{{c|}}{{Friday}} & \\multicolumn{{2}}{{c|}}{{Saturday}} \\\\
    \\multicolumn{{1}}{{l}}{{}} & \\multicolumn{{2}}{{|c|}}{{{0}}} & \\multicolumn{{2}}{{c|}}{{{1}}} & \\multicolumn{{2}}{{c|}}{{{2}}} & \\multicolumn{{2}}{{c|}}{{{3}}} & \\multicolumn{{2}}{{c|}}{{{4}}} & \\multicolumn{{2}}{{c|}}{{{5}}} \\\\
    \\cline{{2-13}}
    \\cline{{2-13}}
    \\multicolumn{{1}}{{l|}}{{}} & Start & Stop & Start & Stop & Start & Stop & Start & Stop & Start & Stop & Start & Stop \\\\
    \\hline
    \\hline
    Math & & & & & & & & & & & &\\\\[70pt]
    \\hline
    Reading & & & & & & & & & & & &\\\\[70pt]
    \\hline
    Writing & & & & & & & & & & & &\\\\[70pt]
    \\hline
    Vocabulary & & & & & & & & & & & &\\\\[70pt]
    \\hline
    Discussion &
    \\multicolumn{{2}}{{|p{{3cm}}|}}{{{6}}} &
    \\multicolumn{{2}}{{p{{3cm}}|}}{{{7}}} &
    \\multicolumn{{2}}{{p{{3cm}}|}}{{{8}}} &
    \\multicolumn{{2}}{{p{{3cm}}|}}{{{9}}} &
    \\multicolumn{{2}}{{p{{3cm}}|}}{{{10}}} &
    \\multicolumn{{2}}{{p{{3cm}}|}}{{{11}}}
    \\\\[70pt]
    \\hline
    \\end{{tabular}}
    \\end{{sidewaystable}}
    '''.format(
        dates[0], dates[1], dates[2], dates[3], dates[4], dates[5],  # 0-5
        goals[0], goals[1], goals[2], goals[3], goals[4], goals[5],  # 6-11
        name,  # 12
        scrip  # 13
    )

def _time_sheet(dates, discussion_question, name, scrip, goals):
    return '''
    \\begin{{sidewaystable}}
    \\centering
    \\begin{{tabular}}{{|l|p{{1.5cm}}|p{{1.5cm}}|p{{1.5cm}}|p{{1.5cm}}|p{{1.5cm}}|p{{1.5cm}}|p{{1.5cm}}|p{{1.5cm}}|p{{1.5cm}}|p{{1.5cm}}|p{{1.5cm}}|p{{1.5cm}}|}}
    \\multicolumn{{7}}{{l}}{{Name: {11}}} \\\\
    \\multicolumn{{13}}{{p{{25cm}}}}{{Scripture: {12}}} \\\\
    \\multicolumn{{7}}{{l}}{{}} \\\\
    \\multicolumn{{7}}{{l}}{{}} \\\\
    \\cline{{2-13}}
    \\multicolumn{{1}}{{l}}{{}} & \\multicolumn{{2}}{{|c|}}{{Monday}} & \\multicolumn{{2}}{{c|}}{{Tuesday}} & \\multicolumn{{2}}{{c|}}{{Wednesday}} & \\multicolumn{{2}}{{c|}}{{Thursday}} & \\multicolumn{{2}}{{c|}}{{Friday}} & \\multicolumn{{2}}{{c|}}{{Saturday}} \\\\
    \\multicolumn{{1}}{{l}}{{}} & \\multicolumn{{2}}{{|c|}}{{{0}}} & \\multicolumn{{2}}{{c|}}{{{1}}} & \\multicolumn{{2}}{{c|}}{{{2}}} & \\multicolumn{{2}}{{c|}}{{{3}}} & \\multicolumn{{2}}{{c|}}{{{4}}} & \\multicolumn{{2}}{{c|}}{{{5}}} \\\\
    \\cline{{2-13}}
    \\cline{{2-13}}
    \\multicolumn{{1}}{{l|}}{{}} & Start & Stop & Start & Stop & Start & Stop & Start & Stop & Start & Stop & Start & Stop \\\\
    \\hline
    \\hline
    Math & & & & & & & & & & & &\\\\[70pt]
    \\hline
    Reading & & & & & & & & & & & &\\\\[70pt]
    \\hline
    Writing & & & & & & & & & & & &\\\\[70pt]
    \\hline
    Vocabulary & & & & & & & & & & & &\\\\[70pt]
    \\hline
    \\hline
    &
    \\multicolumn{{2}}{{||p{{3cm}}|}}{{Spiritual Goal: {6}}} &
    \\multicolumn{{2}}{{p{{3cm}}|}}{{Physical Goal: {7}}} &
    \\multicolumn{{2}}{{p{{3cm}}|}}{{Social Goal: {8}}} &
    \\multicolumn{{2}}{{p{{3cm}}||}}{{Intellectual Goal: {9}}} &
    \\multicolumn{{4}}{{p{{6cm}}|}}{{{10}}}
    \\\\[70pt]
    \\hline
    \\end{{tabular}}
    \\end{{sidewaystable}}
    '''.format(
        dates[0], dates[1], dates[2], dates[3], dates[4], dates[5],  # 0-5
        goals[0], goals[1], goals[2], goals[3],  # 6-9
        '{0} (from {1})'.format(discussion_question[1], discussion_question[0]),  # 10
        name,  # 11
        scrip  # 12
    )


def weekly_form_latex_create(kids, books, dates, scripture, discussion_question, goals, jobs):
    header = r'''
    \documentclass[10pt,twoside,letterpaper,oldfontcommands,openany]{memoir}
    \usepackage{rotating, caption}
    \usepackage[margin=0.25in]{geometry}
    \newcommand{\tabitem}{~~\llap{\textbullet}~~}
    \pagenumbering{gobble}
    \begin{document}
    '''

    footer = r'''\end{document}'''

    math_scripture = ''''''
    for i in itertools.product(zip(kids, books), dates):
        math_scripture += '''
        \\clearpage
        \\newpage
        \\makeatletter
        \\setlength{{\@fptop}}{{35pt}}
        \\makeatother
        \\begin{{table}}
        \\caption*{{Math Assignment}}
        \\begin{{tabular}}{{| l | l | l | l | l | l |}}
        \\hline
        \\multicolumn{{3}}{{|p{{9.5cm}}|}}{{Name: {0}}} & \\multicolumn{{3}}{{|p{{9.5cm}}|}}{{Book: {1}}} \\\\[20pt]
        \\hline
        \\multicolumn{{3}}{{|l|}}{{Start Chapter: }} & \\multicolumn{{3}}{{|l|}}{{First Problem: }} \\\\[20pt]
        \\hline
        \\multicolumn{{3}}{{|l|}}{{End Chapter: }} & \\multicolumn{{3}}{{|l|}}{{Last Problem: }} \\\\[20pt]
        \\hline
        \\multicolumn{{2}}{{|p{{6.33cm}}|}}{{Date: {2}}} & \\multicolumn{{2}}{{|p{{6.33cm}}|}}{{Start Time: }} & \\multicolumn{{2}}{{|p{{6.33cm}}|}}{{End Time: }} \\\\[20pt]
        \\hline
        \\multicolumn{{6}}{{|l|}}{{Problems Missed: }} \\\\[20pt]
        \\hline
        \\end{{tabular}}
        \\end{{table}}

        \\clearpage
        \\newpage
        \\makeatletter
        \\setlength{{\@fptop}}{{35pt}}
        \\makeatother
        \\begin{{table}}
        \\caption*{{Scripture Questions and Principles}}
        \\begin{{tabular}}{{| l | l | l | l | l | l |}}
        \\hline
        \\multicolumn{{3}}{{|p{{9.5cm}}|}}{{Name: {0}}} & \\multicolumn{{3}}{{|p{{9.5cm}}|}}{{Date: {2}}} \\\\[20pt]
        \\hline
        \\multicolumn{{2}}{{|p{{6.33cm}}|}}{{Start Book: }} & \\multicolumn{{2}}{{|p{{6.33cm}}|}}{{Start Chapter: }} & \\multicolumn{{2}}{{|p{{6.33cm}}|}}{{Start Verse: }} \\\\[20pt]
        \\hline
        \\multicolumn{{2}}{{|p{{6.33cm}}|}}{{End Book: }} & \\multicolumn{{2}}{{|p{{6.33cm}}|}}{{End Chapter: }} & \\multicolumn{{2}}{{|p{{6.33cm}}|}}{{End Verse: }} \\\\[20pt]
        \\hline
        \\multicolumn{{6}}{{l}}{{}} \\\\[20pt]
        \\multicolumn{{6}}{{l}}{{Comment:}} \\\\[20pt]
        \\end{{tabular}}
        \\end{{table}}
        '''.format(
            i[0][0], i[0][1], i[1]
        )
        if i[1] == dates[-1]:
            sunday_date = datetime.datetime.strftime(datetime.datetime.strptime(dates[-1], '%Y-%m-%d') + datetime.timedelta(days=1), '%Y-%m-%d')
            math_scripture += '''
            \\clearpage
            \\newpage
            \\makeatletter
            \\setlength{{\@fptop}}{{35pt}}
            \\makeatother
            \\begin{{table}}
            \\caption*{{Scripture Questions and Principles}}
            \\begin{{tabular}}{{| l | l | l | l | l | l |}}
            \\hline
            \\multicolumn{{3}}{{|p{{9.5cm}}|}}{{Name: {0}}} & \\multicolumn{{3}}{{|p{{9.5cm}}|}}{{Date: {1}}} \\\\[20pt]
            \\hline
            \\multicolumn{{2}}{{|p{{6.33cm}}|}}{{Start Book: }} & \\multicolumn{{2}}{{|p{{6.33cm}}|}}{{Start Chapter: }} & \\multicolumn{{2}}{{|p{{6.33cm}}|}}{{Start Verse: }} \\\\[20pt]
            \\hline
            \\multicolumn{{2}}{{|p{{6.33cm}}|}}{{End Book: }} & \\multicolumn{{2}}{{|p{{6.33cm}}|}}{{End Chapter: }} & \\multicolumn{{2}}{{|p{{6.33cm}}|}}{{End Verse: }} \\\\[20pt]
            \\hline
            \\multicolumn{{6}}{{l}}{{}} \\\\[20pt]
            \\multicolumn{{6}}{{l}}{{Comment:}} \\\\[20pt]
            \\end{{tabular}}
            \\end{{table}}
            '''.format(i[0][0], sunday_date)

    if scripture[1] == 'Review Time!':
        scrip = 'Review Time!'
    else:
        scrip = '``{0}" ({1})'.format(scripture[1], scripture[0])  # 13

    time_sheets = ''''''
    for name in kids:
        time_sheets += _time_sheet(dates, discussion_question, name, scrip, goals[name])

    jobs = '''
    \\clearpage
    \\newpage
    \\makeatletter
    \\setlength{{\@fptop}}{{5pt}}
    \\makeatother
    \\begin{{sidewaystable}}
    \\footnotesize
    \\centering
    \\begin{{tabular}}{{| p{{1cm}} | p{{3.5cm}} | p{{3.5cm}} | p{{3.5cm}} | p{{3.5cm}} | p{{3.5cm}} | p{{3.5cm}} |}}
    \\hline\\hline
     & Monday & Tuesday & Wednesday & Thursday & Friday & Saturday \\\\[10pt]
    \\hline\\hline
    Calvin & \\tabitem {0} & \\tabitem {1} & \\tabitem {2} & \\tabitem {3} & \\tabitem {4} & \\tabitem {5} \\\\
    & \\tabitem {6} & \\tabitem {6} & \\tabitem {6} & \\tabitem {6} & \\tabitem {6} & \\tabitem {6} \\\\
    & \\tabitem 4:30 & \\tabitem 4:30 & \\tabitem 4:30 & \\tabitem 4:30 & \\tabitem 4:30 & \\tabitem 4:30 \\\\
    \\hline\\hline
    Samuel & \\tabitem {0} & \\tabitem {1} & \\tabitem {2} & \\tabitem {3} & \\tabitem {4} & \\tabitem {5} \\\\
    & \\tabitem {6} & \\tabitem {6} & \\tabitem {6} & \\tabitem {6} & \\tabitem {6} & \\tabitem {6} \\\\
    & \\tabitem 4:30 & \\tabitem 4:30 & \\tabitem 4:30 & \\tabitem 4:30 & \\tabitem 4:30 & \\tabitem 4:30 \\\\
    \\hline\\hline
    Kay & \\tabitem {0} & \\tabitem {1} & \\tabitem {2} & \\tabitem {3} & \\tabitem {4} & \\tabitem {5} \\\\
    & \\tabitem {6} & \\tabitem {6} & \\tabitem {6} & \\tabitem {6} & \\tabitem {6} & \\tabitem {6} \\\\
    & \\tabitem 4:30 & \\tabitem 4:30 & \\tabitem 4:30 & \\tabitem 4:30 & \\tabitem 4:30 & \\tabitem 4:30 \\\\
    \\hline\\hline
    Seth & \\tabitem School & \\tabitem School & \\tabitem School & \\tabitem School & \\tabitem School & \\tabitem School \\\\
     & \\tabitem {6} & \\tabitem {6} & \\tabitem {6} & \\tabitem {6} & \\tabitem {6} & \\tabitem {6} \\\\
     & \\tabitem Stairwell & \\tabitem Stairwell & \\tabitem Stairwell & \\tabitem Stairwell & \\tabitem Stairwell & \\tabitem Stairwell \\\\
    \\hline\\hline
    \\end{{tabular}}
    \\end{{sidewaystable}}
    '''.format(jobs[0], jobs[1], jobs[2], jobs[3], jobs[4], jobs[5], '5 minute pickup')


    content = header + jobs + time_sheets + math_scripture + footer

    with open('weekly_time_sheet.tex', 'w') as f:
         f.write(content)

    subprocess.Popen(['sudo', '/usr/local/bin/laton', 'weekly_time_sheet.tex'])


def goals_latex_create(kids, goals):
    header = r'''
    \documentclass[10pt,twoside,letterpaper,oldfontcommands,openany]{memoir}
    \usepackage{rotating, caption}
    \usepackage[margin=0.25in]{geometry}
    \newcommand{\tabitem}{~~\llap{\textbullet}~~}
    \pagenumbering{gobble}
    \begin{document}
    '''

    footer = r'''\end{document}'''

    goals_table = r'''
    \begin{table}
    \centering
    \begin{tabular}{| l | l | l  | l  | l |}
    \hline
    & Spiritual Goal & Physical Goal & Social Goal & Intellectual Goal \\
    \hline\hline
    '''
    for kid in kids:
        goals_table += r'''{kid} & {g1} & {g2} & {g3} & {g4} \\ \hline '''.format(kid=kid, g1=goals[kid][0], g2=goals[kid][1], g3=goals[kid][2], g4=goals[kid][3])

    goals_table += r'''
    \end{tabular}
    \end{table}
    '''

    content = header + goals_table + footer
    print(content)

    with open('goals_table.tex', 'w') as f:
        f.write(content)

    subprocess.Popen(['sudo', '/usr/local/bin/laton', 'goals_table.tex'])





def scriptures_latex_create(df):
    df.sort_values('week_start_date', inplace=True)

    header = r'''
    \documentclass[10pt,twoside,letterpaper,oldfontcommands,openany]{memoir}
    \usepackage{rotating, caption}
    \usepackage[margin=0.25in]{geometry}
    \newcommand{\tabitem}{~~\llap{\textbullet}~~}
    \pagenumbering{gobble}
    \begin{document}
    '''

    footer = r'''\end{document}'''

    scriptures_table = r'''
    \begin{sidewaystable}
    \centering
    \begin{tabular}{| l | l | p{20cm} |}
    \hline
     Start Date & Reference & Scriptures \\
    \hline\hline
    '''
    for scripture in df.values:
        if scripture[1] == 'Review Time!':
            scriptures_table += r'''{date} & Review &  \\ \hline'''.format(date=scripture[2])
        else:
            scriptures_table += r'''{date} & {ref} & {scripture} \\ \hline'''.format(date=scripture[2], ref=scripture[1], scripture=scripture[0])

    scriptures_table += r'''
    \end{tabular}
    \end{sidewaystable}
    '''

    # content = header + 'hey' + footer
    content = header + scriptures_table + footer

    with open('scripture_table.tex', 'w') as f:
        f.write(content)

    subprocess.Popen(['sudo', '/usr/local/bin/laton', 'scripture_table.tex'])


def _problem_list_create(first, last, less_num):
    alphabet = 'abcdefghijklmnopqrstuvwxyz'
    if str(first).isalpha():
        if str(last).isalpha():
            return [letter for letter in alphabet if (letter >= str(first) and letter <= str(last))]
        else:
            return [letter for letter in alphabet if (letter >= str(first) and letter <= less_num)] + list(map(str, range(1, int(last) + 1)))
    else:
        return list(map(str, range(int(first), int(last) + 1)))


def _alternatives_create(length, num):
    alternatives = []
    for card_i in range(length):
        alternatives_i = []
        for j in range(3):
            random_lesson = np.random.choice(helpers_constants.lesson_lst)
            num_cards_in_random_lesson = len(os.listdir('static/{0}'.format(random_lesson)))
            random_card = np.random.choice(range(0, num_cards_in_random_lesson, 2))
            alternatives_i.append('../static/{0}/rc_vocab_{0}_{1}.png'.format(random_lesson, random_card + num))
        alternatives.append(alternatives_i)
    return alternatives


def scripture_list_json(form):
    data = {
        "week_start_date": str(form.weekof.data),
        "scripture_ref": form.scripture_ref.data,
        "scripture": form.scripture.data,
    }
    return data


def scripture_table_create(data, year='current'):
    data['week_start_date'] = pd.to_datetime(data['week_start_date'])
    if year == 'current':
        year = max(data['week_start_date'].dt.year)
    elif year == 'all':
        year = '2019'
    data. \
        query('week_start_date >= "{year}-01-01"'.format(year=year)).\
        sort_values('week_start_date').\
        assign(week_start_date=data['week_start_date'].astype(str)).\
        groupby('scripture'). \
        first(). \
        reset_index() \
        [['scripture', 'scripture_ref', 'week_start_date']]. \
        pipe(scriptures_latex_create)


def db_writer(db_math_aggregate, user, df):
    db_math_aggregate[user].drop()
    ret = db_math_aggregate[user].insert_many(df)
    print(ret)


def miss_lst_create(record, lst, test=False):
    dict_out = defaultdict(list)

    if test:
        add_list = [{'chapter': 'test {}'.format(problem['chapter']), 'problem': problem['problem']} for problem in record[lst]]
        rem_list = [{'chapter': 'test {}'.format(problem['chapter']), 'problem': problem['problem']} for problem in record['rem_miss_list']]
    else:
        add_list = [{'chapter': problem['chapter'], 'problem': problem['problem']} for problem in record[lst]]
        rem_list = [{'chapter': problem['chapter'], 'problem': problem['problem']} for problem in record['rem_miss_list']]

    # todo: this method for removing from miss list is maybe flawed
    for prob in add_list:
        dict_out[prob['chapter']].append(prob['problem'])
    for prob in rem_list:
        dict_out[prob['chapter']].remove(prob['problem'])
    k_to_del = [k for k, v in dict_out.items() if not dict_out[k]]
    for k in k_to_del:
        del dict_out[k]
    return dict(dict_out)


def _test_atomize(record):
    df_out = pd.DataFrame()

    df_out['problem'] = range(1, 21)
    df_out['name'] = record['kid']
    df_out['book'] = record['book']
    df_out['chapter'] = record['end_chapter']
    df_out['date'] = record['date']
    df_out['origin'] = np.nan

    miss_lst = record['miss_lst'].get(str(record['end_chapter']))
    if not miss_lst:
        miss_lst = []
    df_out['correct'] = df_out.apply(lambda x: 0 if str(x['problem']) in miss_lst else 1, axis=1)

    hard_lst = record['hard_lst'].get(str(record['end_chapter']))
    if not hard_lst:
        hard_lst = []
    df_out['hard'] = df_out.apply(lambda x: 1 if str(x['problem']) in hard_lst else 0, axis=1)

    df_out['meta__insert_time'] = str(datetime.datetime.today().strftime('%Y-%m-%d %H:%M'))

    return df_out[['book', 'chapter', 'correct', 'hard', 'date', 'origin', 'problem', 'name', 'meta__insert_time']]


def _chapter_atomize(db_origin, db_number, chapter, record):
    df_origins = pd.DataFrame(list(db_origin.find({'chapter': chapter})))
    df_number = pd.DataFrame(list(db_number.find({'chapter': chapter})))

    df_practice = pd.DataFrame()
    practice_problems_index = list(string.ascii_lowercase).index(df_number['num_lesson_probs'].iloc[0]) + 1
    df_practice['problem'] = list(string.ascii_lowercase)[:practice_problems_index]
    df_practice['origin'] = np.nan

    df_review = pd.DataFrame()
    df_review['origin'] = df_origins['origin_list'][0]
    df_review['problem'] = df_review.index + 1

    df = df_practice.append(df_review).reset_index(drop=True)

    miss_lst = record['miss_lst'].get(str(chapter))  # how to return None instead of throwing an error when key doesn't exist.
    hard_lst = record['hard_lst'].get(str(chapter))

    if miss_lst:
        df['correct'] = df.apply(lambda x: 0 if str(x['problem']) in miss_lst else 1, axis=1)
    else:
        df['correct'] = 1
    if hard_lst:
        df['hard'] = df.apply(lambda x: 1 if str(x['problem']) in hard_lst else 0, axis=1)
    else:
        df['hard'] = 0

    df['book'] = record['book']
    df['chapter'] = chapter
    df['date'] = record['date']
    df['name'] = record['kid']
    df['meta__insert_time'] = str(datetime.datetime.today().strftime('%Y-%m-%d %H:%M'))

    if chapter == record['start_chapter']:
        index = df[df['problem'].astype(str) == record['start_problem']].index[0]
        df = df.loc[index:]
    if chapter == record['end_chapter']:
        index = df[df['problem'].astype(str) == record['end_problem']].index[0]
        df = df.loc[:index]
    return df.reset_index(drop=True)


def _ass_atomize(db_origin, db_number, record):
    df = pd.DataFrame()
    for chapter in range(record['start_chapter'], record['end_chapter'] + 1):
        df = df.append(_chapter_atomize(db_origin, db_number, chapter, record))
    return df[['book', 'chapter', 'correct', 'hard', 'date', 'origin', 'problem', 'name', 'meta__insert_time']]


def _elapsed_time(record):
    start_time = datetime.datetime.strptime('{0} {1}'.format(record['date'], record['start_time']), '%Y-%m-%d %H:%M')
    if start_time.hour < 6:
        start_time = start_time + datetime.timedelta(hours=12)
    end_time = datetime.datetime.strptime('{0} {1}'.format(record['date'], record['end_time']), '%Y-%m-%d %H:%M')
    if end_time.hour < 6:
        end_time = end_time + datetime.timedelta(hours=12)

    return [{'date': record['date'], 'kid': record['kid'], 'duration': int((end_time - start_time).seconds / 60)}]
