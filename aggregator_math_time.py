import sys
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
db_math_time_aggregate = client['math_time_aggregate']


def db_writer(user, df):
    db_math_time_aggregate[user].drop()
    ret = db_math_time_aggregate[user].insert_many(df)
    print(ret.inserted_ids)

def main():
    for name in ['Calvin', 'Samuel']:
        df = pd.DataFrame()
        for book in ['Math_5_4', 'Math_6_5', 'Math_7_6', 'Math_8_7', 'Algebra_1_2', 'Algebra_1', 'Algebra_2']:
            df = df.append(pd.DataFrame(list(db_performance[book].find({'kid': name}))))

        df = df.iloc[2:].drop(['chapter', 'miss_list'], 1)
        df['date'] = pd.to_datetime(df['date'])
        df.sort_values('date', inplace=True)
        df['date'] = df['date'].astype(str)

        df['start_time'] = df.apply(
            lambda x: datetime.datetime.strptime('{0} {1}'.format(x['date'], x['start_time']), '%Y-%m-%d %H:%M'),
            axis=1)
        df['start_time'] = df['start_time'].apply(lambda x: x + datetime.timedelta(hours=12) if x.hour < 7 else x)

        df['end_time'] = df.apply(
            lambda x: datetime.datetime.strptime('{0} {1}'.format(x['date'], x['end_time']), '%Y-%m-%d %H:%M'), axis=1)
        df['end_time'] = df['end_time'].apply(lambda x: x + datetime.timedelta(hours=12) if x.hour < 7 else x)

        df['duration'] = (df['end_time'] - df['start_time']).astype('timedelta64[m]')

        db_writer(name, df[['date', 'kid', 'duration']].to_dict(orient='records'))

if __name__ == '__main__':
    main()
