import os
import pandas as pd
from pymongo import MongoClient
from sshtunnel import SSHTunnelForwarder
import ast
import sys
import json
import datetime
import numpy as np
import pandas as pd
from pymongo import MongoClient

pd.set_option('max_columns', 1000)
pd.set_option('max_info_columns', 1000)
pd.set_option('expand_frame_repr', False)
pd.set_option('display.max_rows', 30000)
pd.set_option('max_colwidth', 4000)
pd.set_option('display.float_format', lambda x: '%.3f' % x)

client = MongoClient()
# db_number = client['math_book_info']
# db_origin = client['math_exercise_origins']
# db_performance = client['math_performance']



def the_big_one(book, df_number, df_origin, df_performance):
    # todo: maybe just remove the offending documents from the database
    if 'chapter' in df_performance.columns.tolist():
        df_performance.drop('chapter', 1, inplace=True)
    if 'miss_list' in df_performance.columns.tolist():
        df_performance.drop('miss_list', 1, inplace=True)

    df_performance = df_performance. \
        query('date == date'). \
        assign(date=pd.to_datetime(df_performance['date'])). \
        sort_values(['date', 'start_chapter', 'start_problem'])

    df_performance['end_chapter'] = df_performance['end_chapter'].astype(str)
    df_performance_test = df_performance.loc[df_performance['end_chapter'].str.contains('test', na=False)]
    df_performance_ass = df_performance.loc[~df_performance['end_chapter'].str.contains('test', na=False)]

    # these columns have different types across the various collections, which makes for a bit of a headache
    df_performance_ass['start_chapter'] = df_performance_ass['start_chapter'].astype(float).astype(int)
    df_performance_ass['end_chapter'] = df_performance_ass['end_chapter'].astype(float).astype(int)

    # assignments
    start_chapter_ass = df_performance_ass['start_chapter'].iloc[0]
    start_problem_ass = df_performance_ass['start_problem'].iloc[0]
    if isinstance(start_problem_ass, int):
        start_problem_ass = str(start_problem_ass)

    end_chapter_ass = df_performance_ass['end_chapter'].iloc[-1]
    end_problem_ass = df_performance_ass['end_problem'].iloc[-1]
    if isinstance(end_problem_ass, int):
        end_problem_ass = str(end_problem_ass)

    alphabet = 'abcdefghijklmnopqrstuvwxyz'
    df_grande_ass = pd.DataFrame()
    for chapter in range(int(float(start_chapter_ass)), int(float(end_chapter_ass)) + 1):
        df_temp = pd.DataFrame()
        lesson_probs = df_number.query('chapter == {}'.format(chapter)).iloc[0]['num_lesson_probs']
        mixed_probs = int(df_number.query('chapter == {}'.format(chapter)).iloc[0]['num_mixed_probs'])
        origin_probs = df_origin.query('chapter == {}'.format(chapter)).iloc[0]['origin_list']
        if isinstance(origin_probs, str):
            origin_probs = ast.literal_eval(origin_probs)
        missed_probs = []
        for dic in df_performance_ass.query('start_chapter == {}'.format(chapter))['miss_lst'].values.tolist() + df_performance_ass.query('end_chapter == {}'.format(chapter))['miss_lst'].values.tolist():
            try:
                missed_probs += dic[str(chapter)]
            except:
                pass
        missed_probs = list(set(missed_probs))

        if start_chapter_ass == end_chapter_ass:
            if start_problem_ass.isdigit():
                problem_lst = range(int(start_problem_ass), int(end_problem_ass) + 1)
                origin_lst = origin_probs[int(start_problem_ass): int(end_problem_ass) + 1]

            else:
                # I'm assuming the end_problem would not also be a letter
                start_ind = alphabet.find(start_problem_ass)
                end_ind = alphabet.find(lesson_probs)
                problem_lst = list(alphabet[start_ind: end_ind + 1]) + list(range(1, int(end_problem_ass) + 1))
                origin_lst = (end_ind - start_ind + 1) * [np.nan] + origin_probs[: int(end_problem_ass)]

        else:
            if chapter == start_chapter_ass:
                if start_problem_ass.isdigit():
                    problem_lst = list(range(int(start_problem_ass), mixed_probs + 1))
                    origin_lst = origin_probs[int(start_problem_ass) - 1:]

                else:
                    start_ind = alphabet.find(start_problem_ass)
                    end_ind = alphabet.find(lesson_probs)
                    problem_lst = list(alphabet[start_ind: end_ind + 1]) + list(range(1, mixed_probs + 1))
                    origin_lst = (end_ind - start_ind + 1) * [np.nan] + origin_probs

            elif chapter == end_chapter_ass:
                if end_problem_ass.isdigit():
                    start_ind = 0
                    end_ind = alphabet.find(lesson_probs)
                    problem_lst = list(alphabet[start_ind: end_ind + 1]) + list(range(1, int(end_problem_ass) + 1))
                    origin_lst = (end_ind - start_ind + 1) * [np.nan] + origin_probs[: int(end_problem_ass)]

                else:
                    start_ind = 0
                    end_ind = alphabet.find(end_problem_ass)
                    problem_lst = list(alphabet[start_ind: end_ind + 1])
                    origin_lst = (end_ind - start_ind + 1) * [np.nan]

            else:
                start_ind = 0
                end_ind = alphabet.find(lesson_probs)
                problem_lst = list(alphabet[start_ind: end_ind + 1]) + list(range(1, mixed_probs + 1))
                origin_lst = (end_ind - start_ind + 1) * [np.nan] + origin_probs

        df_temp['problem'] = problem_lst
        df_temp['origin'] = origin_lst
        df_temp['book'] = book
        df_temp['chapter'] = chapter
        df_temp['correct'] = df_temp.apply(lambda x: 0 if str(x['problem']) in missed_probs else 1, axis=1)

        df_grande_ass = df_grande_ass.append(df_temp)

    df_grande_ass.reset_index(drop=True, inplace=True)

    df_grande_ass['date'] = ''
    df_p_g = df_performance_ass.sort_values('date').iterrows()

    row_p = next(df_p_g)[1]


    # todo: here
    # print(df_performance_ass)



    for ind, row in df_grande_ass.iterrows():
        df_grande_ass.set_value(ind, 'date', row_p['date'])  # FutureWarning: set_value is deprecated and will be removed in a future release. Please use .at[] or .iat[] accessors instead

        if (row['chapter'] == int(float(row_p['end_chapter']))) and (str(row['problem']) == str(row_p['end_problem'])):
        # if (int(float(row['chapter'])) == int(float(row_p['end_chapter']))) and (str(row['problem']) == str(row_p['end_problem'])):
            try:
                row_p = next(df_p_g)[1]
            except:
                print('boom!')


    # tests
    df_grande_test = pd.DataFrame()
    for ind, row in df_performance_test.iterrows():
        df_temp = pd.DataFrame()
        df_temp['problem'] = range(1, 21)
        df_temp['book'] = book
        df_temp['chapter'] = row['end_chapter']
        df_temp['date'] = row['date']

        if isinstance(row['miss_lst'], str):
            miss_lst = ast.literal_eval(row['miss_lst'])
        else:
            miss_lst = row['miss_lst']
        # if row['miss_lst']:
        if miss_lst:
            # missed_probs = row['miss_lst'][row['end_chapter']]
            missed_probs = miss_lst[row['end_chapter']]
        else:
            missed_probs = []

        df_temp['correct'] = df_temp.apply(lambda x: 0 if str(x['problem']) in missed_probs else 1, axis=1)

        df_grande_test = df_grande_test.append(df_temp)

    return df_grande_ass, df_grande_test


def query_performance(name):
    df_assignment = pd.DataFrame()
    df_test = pd.DataFrame()

    # for book in ['Math_5_4', 'Math_6_5', 'Math_7_6', 'Math_8_7', 'Algebra_1_2', 'Algebra_1', 'Algebra_2']:
    if name == 'Calvin':
        book = 'Algebra_1_2'
    else:
        book = 'Math_8_7'

    if name:

        # perf_temp = pd.DataFrame(list(db_performance[book].find({'kid': name})))
        perf_temp = pi_data_fetch('math_performance', book, {'kid': name})

        if not perf_temp.empty:
            def to_dict(x):
                if isinstance(x, str):
                    return json.loads(x)
                return x
            perf_temp['miss_lst'] = perf_temp['miss_lst'].apply(to_dict)

        # numb_temp = pd.DataFrame(list(db_number[book].find()))
        numb_temp = pi_data_fetch('math_book_info', book, None)

        # orig_temp = pd.DataFrame(list(db_origin[book].find()))
        orig_temp = pi_data_fetch('math_exercise_origins', book, None)

        if perf_temp.shape[0] > 0:
            df_grande_ass, df_grande_test = the_big_one(
                book,
                numb_temp,
                orig_temp,
                perf_temp
            )
            df_assignment = df_assignment.append(df_grande_ass)
            df_test = df_test.append(df_grande_test)
    return df_assignment.append(df_test)


def pi_data_fetch(dbs, collection):
    ssh_host = os.getenv('raspberry_pi_ip')
    ssh_user = os.getenv('raspberry_pi_username')
    ssh_password = os.getenv('raspberry_pi_password')

    with SSHTunnelForwarder(
            ssh_host,
            ssh_username=ssh_user,
            ssh_password=ssh_password,
            remote_bind_address=('127.0.0.1', 27017)
    ) as server:
        with MongoClient(
                host='127.0.0.1',
                port=server.local_bind_port
        ) as client:
            # db = pd.DataFrame(list(client[dbs][collection].find()))


            # for ind, row in enumerate(list(client[dbs][collection].find())):
            #     try:
            #         row['chapter']
            #     except:
            #         print({'_id': row['_id']})
            #         client[dbs][collection].update({'_id': row['_id']}, {'book': collection, 'origin_list': row['origin_list'], 'chapter': ind + 1, })
            #         print('\n')


            import ast
            for row in list(client[dbs][collection].find()):
                if type(row['origin_list']) == str:
                    print({'_id': row['_id']})
                    print({'origin_list': ast.literal_eval(row['origin_list'])})
                    client[dbs][collection].update({'_id': row['_id']}, {'book': collection, 'origin_list': ast.literal_eval(row['origin_list']), 'chapter': row['chapter']})
                    print('\n')


            sys.exit()
    return db

def p_main():
    db = pi_data_fetch('math_exercise_origins', 'Math_5_4')
    # db = pi_data_fetch('math_exercise_origins', 'Algebra_1_2')
    # db = pi_data_fetch('math_exercise_origins', 'Math_7_6')
    # db = pi_data_fetch('math_exercise_origins', 'Algebra_1')
    # db = pi_data_fetch('math_exercise_origins', 'Math_8_7')
    print(db)

def main():
    for user in ['Calvin', 'Samuel']:
        qp = query_performance(user).reset_index(drop=True)
        qp['chapter'] = qp['chapter'].astype(str)
        # print(qp.info())
    # sys.exit()

        qp['name'] = user
        qp['date'] = qp['date'].dt.date.astype(str)
        qp['meta__insert_time'] = str(datetime.datetime.today().strftime('%Y-%m-%d %H:%M'))
        # print(qp.head(100))

if __name__ == '__main__':
    # main()
    p_main()
# todo: this is cool, but need to fetch the data and use it to figure out what is wrong with aggregator_math_performance.py
