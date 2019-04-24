#!/bin/bash

sudo rm -rf /data/db
sudo mkdir /data/db
sudo supervisorctl restart mongod

for collection in Calvin Samuel Kay
do
   mongoimport -d banking -c $collection --type csv --file /media/pi/HOWESCHOOL/database_files_csv/banking/banking_$collection.csv --headerline
done

for collection in Scriptures Weekly
do
   mongoimport -d forms -c $collection --type csv --file /media/pi/HOWESCHOOL/database_files_csv/forms/forms_$collection.csv --headerline
done

for collection in Algebra_1 Algebra_1_2 Math_5_4 Math_7_6 Math_8_7
do
   mongoimport -d math_book_info -c $collection --type csv --file /media/pi/HOWESCHOOL/database_files_csv/math_book_info/math_book_info_$collection.csv --headerline
done

for collection in Algebra_1 Algebra_1_2 Math_5_4 Math_7_6 Math_8_7
do
   mongoimport -d math_exercise_origins -c $collection --type csv --file /media/pi/HOWESCHOOL/database_files_csv/math_exercise_origins/math_exercise_origins_$collection.csv --headerline
done

for collection in Algebra_1 Algebra_1_2 Math_7_6
do
   mongoimport -d math_performance -c $collection --type csv --file /media/pi/HOWESCHOOL/database_files_csv/math_performance/math_performance_$collection.csv --headerline
done

for collection in Calvin Samuel Kay
do
   mongoimport -d scripture_commentary -c $collection --type csv --file /media/pi/HOWESCHOOL/database_files_csv/scripture_commentary/scripture_commentary_$collection.csv --headerline
done

mongoimport -d users -c users --type csv --file /media/pi/HOWESCHOOL/database_files_csv/users/users_users.csv --headerline

for collection in Main Practice Quiz
do
   mongoimport -d vocab -c $collection --type csv --file /media/pi/HOWESCHOOL/database_files_csv/vocab/vocab_$collection.csv --headerline
done

python3 aggregator_math_performance.py
python3 aggregator_math_time.py
