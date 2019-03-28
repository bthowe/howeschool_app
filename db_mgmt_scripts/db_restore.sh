mongorestore --db users --verbose database_files/users
mongorestore --db math_book_info --verbose database_files/math_book_info
mongorestore --db math_exercise_origins --verbose database_files/math_exercise_origins
mongorestore --db math_performance --verbose database_files/math_performance
mongorestore --db vocab --verbose database_files/vocab
mongorestore --db scripture_commentary --verbose database_files/scripture_commentary
mongorestore --db forms --verbose database_files/forms
mongorestore --db banking --verbose database_files/banking
python3 aggregator_math_performance.py
python3 aggregator_math_time.py
