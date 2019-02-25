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
    start_chapter_ass = df_performance_ass['start_chapter'].iloc[0]
    start_problem_ass = df_performance_ass['start_problem'].iloc[0]

    end_chapter_ass = df_performance_ass['end_chapter'].iloc[-1]
    end_problem_ass = df_performance_ass['end_problem'].iloc[-1]

    alphabet = 'abcdefghijklmnopqrstuvwxyz'
    df_grande_ass = pd.DataFrame()
    for chapter in range(int(float(start_chapter_ass)), int(float(end_chapter_ass)) + 1):
        df_temp = pd.DataFrame()
        lesson_probs = df_number.query('chapter == {}'.format(chapter)).iloc[0]['num_lesson_probs']
        mixed_probs = int(df_number.query('chapter == {}'.format(chapter)).iloc[0]['num_mixed_probs'])
        origin_probs = df_origin.query('chapter == {}'.format(chapter)).iloc[0]['origin_list']
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
        if (row['chapter'] == int(float(row_p['end_chapter']))) and (str(row['problem']) == row_p['end_problem']):
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

        if row['miss_lst']:
            missed_probs = row['miss_lst'][row['end_chapter']]
        else:
            missed_probs = []

        df_temp['correct'] = df_temp.apply(lambda x: 0 if str(x['problem']) in missed_probs else 1, axis=1)

        df_grande_test = df_grande_test.append(df_temp)

    return df_grande_ass, df_grande_test


def query_performance(name):
    df_assignment = pd.DataFrame()
    df_test = pd.DataFrame()

    for book in ['Math_5_4', 'Math_6_5', 'Math_7_6', 'Math_8_7', 'Algebra_1_2', 'Algebra_1', 'Algebra_2']:
        perf_temp = pd.DataFrame(list(db_performance[book].find({'kid': name})))
        numb_temp = pd.DataFrame(list(db_number[book].find()))
        orig_temp = pd.DataFrame(list(db_origin[book].find()))
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

def db_writer(user, df):
    db_math_aggregate[user].drop()
    ret = db_math_aggregate[user].insert_many(df)
    # print(ret.inserted_ids)

def main():
    for user in ['Calvin', 'Samuel']:
        qp = query_performance(user).reset_index(drop=True)
        qp['name'] = user
        qp['date'] = qp['date'].dt.date.astype(str)
        qp['meta__insert_time'] = str(datetime.datetime.today().strftime('%Y-%m-%d %H:%M'))

        # [{'name': 'Calvin', 'time': str(datetime.datetime.today())}]
        db_writer(user, qp.to_dict(orient='records'))

if __name__ == '__main__':
    main()
