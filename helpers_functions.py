import os
import sys
import glob
import json
import joblib
import yagmail
import datetime
import itertools
import subprocess
import webbrowser
import numpy as np
import pandas as pd
# import saxon_math_helpers
from functools import wraps
from flask_wtf import FlaskForm
from flask_pymongo import PyMongo
from collections import defaultdict
from flask_bootstrap import Bootstrap
from wtforms.validators import InputRequired, Email, Length
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, url_for, request, session, redirect, flash, jsonify
from wtforms import StringField, PasswordField, BooleanField, SelectField, IntegerField, RadioField
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

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
        "mon_job": form.mon_job.data,
        "tue_job": form.tue_job.data,
        "wed_job": form.wed_job.data,
        "thu_job": form.thu_job.data,
        "fri_job": form.fri_job.data,
        "sat_job": form.sat_job.data,
        "mon_question": form.mon_dis.data,
        "tue_question": form.tue_dis.data,
        "wed_question": form.wed_dis.data,
        "thu_question": form.thu_dis.data,
        "fri_question": form.fri_dis.data,
        "sat_question": form.sat_dis.data,
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

def weekly_forms_email(type='weekly_time_sheet'):
    yag = yagmail.SMTP('b.travis.howe@gmail.com', os.environ['GMAIL'])
    if type == 'scripture_list':
        yag.send(
            # ["b.travis.howe@gmail.com"],
            ["b.travis.howe@gmail.com", "kassie.howe@gmail.com"],
            subject="Scripture Table",
            contents="",
            attachments='/Users/travis.howe/Projects/github/howeschool_app/scripture_table.pdf'
        )
    else:
        yag.send(
            # ["b.travis.howe@gmail.com"],
            ["b.travis.howe@gmail.com", "kassie.howe@gmail.com"],
            subject="Forms for the Week",
            contents="",
            attachments=[
                '/Users/travis.howe/Projects/github/howeschool_app/weekly_time_sheet.pdf',
                '/Users/travis.howe/Projects/github/howeschool_app/scripture_table.pdf',
            ]
        )

def weekly_browser_display(type='weekly_time_sheet'):
    chrome = webbrowser.get('chrome')
    if type == 'scripture_list':
        chrome.open_new_tab('file:///Users/travis.howe/Projects/github/howeschool_app/scripture_table.pdf')
    else:
        chrome.open_new_tab('file:///Users/travis.howe/Projects/github/howeschool_app/weekly_time_sheet.pdf')
        chrome.open_new_tab('file:///Users/travis.howe/Projects/github/howeschool_app/scripture_table.pdf')


def weekly_form_latex_create(kids, books, dates, scripture, discussion_questions, jobs):
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

    if scripture[0] == 'Review':
        scrip = 'Review Time!'
    else:
        scrip = '``{0}" ({1})'.format(scripture[1], scripture[0])  # 13

    print('\n\n\n\n\n\n\n')
    print(scrip)
    print(scripture[0])
    print(scripture[1])
    print('\n\n\n\n\n\n\n')

    time_sheets = ''''''
    for name in kids:
        time_sheets += '''
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
            discussion_questions[0], discussion_questions[1], discussion_questions[2], discussion_questions[3], discussion_questions[4], discussion_questions[5],  # 6-11
            name,  # 12
            scrip  # 13
        )

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

    commandLine = subprocess.Popen(['/Library/TeX/Root/bin/x86_64-darwin/pdflatex', 'weekly_time_sheet.tex'])
    # commandLine = subprocess.Popen(['pdflatex', 'weekly_time_sheet.tex'])
    commandLine.communicate()

    os.unlink('weekly_time_sheet.aux')
    os.unlink('weekly_time_sheet.log')
    os.unlink('weekly_time_sheet.tex')


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
        scriptures_table += r'''{date} & {ref} & {scripture} \\ \hline'''.format(date=scripture[2], ref=scripture[1], scripture=scripture[0])

    scriptures_table += r'''
    \end{tabular}
    \end{sidewaystable}
    '''


    # content = header + 'hey' + footer
    content = header + scriptures_table + footer

    with open('scripture_table.tex', 'w') as f:
         f.write(content)

    commandLine = subprocess.Popen(['/Library/TeX/Root/bin/x86_64-darwin/pdflatex', 'scripture_table.tex'])
    # commandLine = subprocess.Popen(['pdflatex', 'weekly_time_sheet.tex'])
    commandLine.communicate()

    os.unlink('scripture_table.aux')
    os.unlink('scripture_table.log')
    os.unlink('scripture_table.tex')


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


def scripture_data_json(form):
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
