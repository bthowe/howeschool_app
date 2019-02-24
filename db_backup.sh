mongodump -d math_book_info -o /media/pi/HOWESCHOOL/database_files
mongodump -d math_exercise_origins -o /media/pi/HOWESCHOOL/database_files
mongodump -d math_performance -o /media/pi/HOWESCHOOL/database_files
mongodump -d vocab -o /media/pi/HOWESCHOOL/database_files
mongodump -d scripture_commentary -o /media/pi/HOWESCHOOL/database_files
mongodump -d forms -o /media/pi/HOWESCHOOL/database_files
mongodump -d banking -o /media/pi/HOWESCHOOL/database_files
mongodump -d users -o /media/pi/HOWESCHOOL/database_files
sudo supervisorctl stop mongod