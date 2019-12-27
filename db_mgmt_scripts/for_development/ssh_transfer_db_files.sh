source ~/Virtualenvs/howeschool_app/bin/activate

#mongod --dbpath=/Users/thowe/data/db
#scp -r pi@192.168.1.74:/media/pi/HOWESCHOOL/database_files /Users/thowe/data/

mongo users --eval "db.dropDatabase()"
mongo math_book_info --eval "db.dropDatabase()"
mongo math_exercise_origins --eval "db.dropDatabase()"
mongo math_performance --eval "db.dropDatabase()"
mongo vocab --eval "db.dropDatabase()"
mongo scripture_commentary --eval "db.dropDatabase()"
mongo forms --eval "db.dropDatabase()"
mongo banking --eval "db.dropDatabase()"

cd ~/data/database_files
mongorestore --db users --verbose users
mongorestore --db math_book_info --verbose math_book_info
mongorestore --db math_exercise_origins --verbose math_exercise_origins
mongorestore --db math_performance --verbose math_performance
mongorestore --db vocab --verbose vocab
mongorestore --db scripture_commentary --verbose scripture_commentary
mongorestore --db forms --verbose forms
mongorestore --db banking --verbose banking
python3 /Users/thowe/Projects/howeschool_app/aggregator_math_performance.py
python3 /Users/thowe/Projects/howeschool_app/aggregator_math_time.py
