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


def timer(record):
    start_time = datetime.datetime.strptime('{0} {1}'.format(record['date'], record['start_time']), '%Y-%m-%d %H:%M')
    if start_time.hour < 6:
        start_time = start_time + datetime.timedelta(hours=12)

    end_time = datetime.datetime.strptime('{0} {1}'.format(record['date'], record['end_time']), '%Y-%m-%d %H:%M')
    if end_time.hour < 6:
        end_time = end_time + datetime.timedelta(hours=12)

    return [{'date': record['date'], 'kid': record['kid'], 'duration': int((end_time - start_time).seconds / 60)}]


def main():
    # record = {'kid': 'Calvin', 'book': 'Algebra_2', 'start_chapter': 40, 'start_problem': '4', 'end_chapter': 42, 'end_problem': '11', 'date': '2019-12-23', 'start_time': '12:00', 'end_time': '01:00', 'add_miss_list': [{'chapter': '41', 'problem': 'b'}, {'chapter': '41', 'problem': '3'}], 'rem_miss_list': [], 'test': False}
    # df = _ass_atomize(record)
    # print(df.head())
    #
    # record = {'kid': 'Calvin', 'book': 'Algebra_2', 'start_chapter': 4, 'start_problem': '1', 'end_chapter': 4, 'end_problem': '20', 'date': '2019-12-23', 'start_time': '11:00', 'end_time': '12:00', 'add_miss_list': [{'chapter': '4', 'problem': '1'}, {'chapter': '4', 'problem': '13'}], 'rem_miss_list': [], 'test': True}
    # df = _test_atomize(record)
    # print(df)

    record = {'kid': 'Calvin', 'book': 'Algebra_2', 'start_chapter': 4, 'start_problem': '1', 'end_chapter': 4, 'end_problem': '20', 'date': '2019-12-23', 'start_time': '11:00', 'end_time': '03:13', 'add_miss_list': [{'chapter': '4', 'problem': '1'}, {'chapter': '4', 'problem': '13'}], 'rem_miss_list': [], 'test': True}
    print(timer(record))


if __name__ == '__main__':
    main()

# todo:
#   1. merge with master