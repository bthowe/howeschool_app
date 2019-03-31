#!/bin/bash

sudo rm -rf /data/db
sudo mkdir /data/db
sudo supervisorctl restart mongod

mongorestore --db users --verbose /media/pi/HOWESCHOOL/database_files/users
mongorestore --db math_book_info --verbose /media/pi/HOWESCHOOL/database_files/math_book_info
mongorestore --db math_exercise_origins --verbose /media/pi/HOWESCHOOL/database_files/math_exercise_origins
mongorestore --db math_performance --verbose /media/pi/HOWESCHOOL/database_files/math_performance
mongorestore --db vocab --verbose /media/pi/HOWESCHOOL/database_files/vocab
mongorestore --db scripture_commentary --verbose /media/pi/HOWESCHOOL/database_files/scripture_commentary
mongorestore --db forms --verbose /media/pi/HOWESCHOOL/database_files/forms
mongorestore --db banking --verbose /media/pi/HOWESCHOOL/database_files/banking
python3 aggregator_math_performance.py
python3 aggregator_math_time.py
