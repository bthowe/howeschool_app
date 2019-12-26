import ast
import sys
import json
import string
import datetime
import numpy as np
import pandas as pd
from pymongo import MongoClient
from collections import defaultdict

pd.set_option('max_columns', 1000)
pd.set_option('max_info_columns', 1000)
pd.set_option('expand_frame_repr', False)
pd.set_option('display.max_rows', 30000)
pd.set_option('max_colwidth', 4000)
pd.set_option('display.float_format', lambda x: '%.3f' % x)

client = MongoClient()
db_number = client['math_book_info']
db_origin = client['math_exercise_origins']
db_performance = client['math_performance']
db_users = client['users']
db_math_aggregate = client['math_aggregate']


def user_list():
    users = [dic['name'] for dic in list(db_users['users'].find({'access': 1}))]
    return users


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
    if df_performance_ass.shape[0] != 0:
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

            print(book, chapter)
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
        for ind, row in df_grande_ass.iterrows():
            df_grande_ass.set_value(ind, 'date', row_p['date'])  # FutureWarning: set_value is deprecated and will be removed in a future release. Please use .at[] or .iat[] accessors instead

            if (int(row['chapter']) == int(float(row_p['end_chapter']))) and (str(row['problem']) == str(row_p['end_problem'])):
                try:
                    row_p = next(df_p_g)[1]
                except:
                    print('boom!')

    else:
        df_grande_ass = pd.DataFrame()

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


def miss_lst_create(record):
    dict_out = defaultdict(list)

    add_miss_list = [{'chapter': problem['chapter'], 'problem': problem['problem']} for problem in record['add_miss_list']]
    rem_miss_list = [{'chapter': problem['chapter'], 'problem': problem['problem']} for problem in record['rem_miss_list']]

    for prob in add_miss_list:
        dict_out[prob['chapter']].append(prob['problem'])
    for prob in rem_miss_list:
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
    df_out['chapter'] = 'test {}'.format(record['end_chapter'])
    df_out['date'] = record['date']
    df_out['origin'] = np.nan

    miss_lst = miss_lst_create(record)[str(record['end_chapter'])]
    df_out['correct'] = df_out.apply(lambda x: 0 if str(x['problem']) in miss_lst else 1, axis=1)

    df_out['meta__insert_time'] = str(datetime.datetime.today().strftime('%Y-%m-%d %H:%M'))

    return df_out[['book', 'chapter', 'correct', 'date', 'origin', 'problem', 'name', 'meta__insert_time']]


def _chapter_atomize(chapter, record):
    df_origins = pd.DataFrame(list(db_origin[record['book']].find({'chapter': chapter})))
    df_number = pd.DataFrame(list(db_number[record['book']].find({'chapter': chapter})))

    df_practice = pd.DataFrame()
    practice_problems_index = list(string.ascii_lowercase).index(df_number['num_lesson_probs'].iloc[0]) + 1
    df_practice['problem'] = list(string.ascii_lowercase)[:practice_problems_index]
    df_practice['origin'] = np.nan

    df_review = pd.DataFrame()
    df_review['origin'] = df_origins['origin_list'][0]
    df_review['problem'] = df_review.index + 1

    df = df_practice.append(df_review).reset_index(drop=True)

    miss_lst = miss_lst_create(record).get(str(chapter))  # how to return None instead of throwing an error when key doesn't exist.

    if miss_lst:
        df['correct'] = df.apply(lambda x: 0 if str(x['problem']) in miss_lst else 1, axis=1)
    else:
        df['correct'] = 1
    df['book'] = record['book']
    df['chapter'] = chapter
    df['date'] = record['date']
    df['name'] = record['kid']
    df['meta__insert_time'] = str(datetime.datetime.today().strftime('%Y-%m-%d %H:%M'))

    if chapter == record['start_chapter']:
        index = df[df['problem'].astype(str) == record['start_problem']].index[0]
        return df.iloc[index:]
    if chapter == record['end_chapter']:
        index = df[df['problem'].astype(str) == record['end_problem']].index[0]
        return df.iloc[:index + 1]
    return df


def _ass_atomize(record):
    df = pd.DataFrame()
    for chapter in range(record['start_chapter'], record['end_chapter'] + 1):
        df = df.append(_chapter_atomize(chapter, record))
    return df[['book', 'chapter', 'correct', 'date', 'origin', 'problem', 'name', 'meta__insert_time']]


def db_writer(user, df):
    db_math_aggregate[user].drop()
    ret = db_math_aggregate[user].insert_many(df)
    print(ret)


def main():
    record = {'kid': 'Calvin', 'book': 'Algebra_2', 'start_chapter': 40, 'start_problem': '4', 'end_chapter': 42, 'end_problem': '11', 'date': '2019-12-23', 'start_time': '12:00', 'end_time': '01:00', 'add_miss_list': [{'chapter': '41', 'problem': 'b'}, {'chapter': '41', 'problem': '3'}], 'rem_miss_list': [], 'test': False}
    df = _ass_atomize(record)
    print(df.head())

    record = {'kid': 'Calvin', 'book': 'Algebra_2', 'start_chapter': 4, 'start_problem': '1', 'end_chapter': 4, 'end_problem': '20', 'date': '2019-12-23', 'start_time': '11:00', 'end_time': '12:00', 'add_miss_list': [{'chapter': '4', 'problem': '1'}, {'chapter': '4', 'problem': '13'}], 'rem_miss_list': [], 'test': True}
    df = _test_atomize(record)
    print(df)

    sys.exit()

    db_writer(record['kid'], df.to_dict(orient='records'))


if __name__ == '__main__':
    main()

# todo:
#   (x)1. refactor code
#   2. switch to develop branch
#   3. implement in command.py
#   4. do the same for the time script
#   5. problems that still had problems with capabilities