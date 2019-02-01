#!/bin/sh

cd /home/pi/PythonProjects/howeschool_app

git pull origin master

mongodump -d math_book_info -o dump
mongodump -d math_exercise_origins -o dump
mongodump -d math_performance -o dump
mongodump -d vocab -o dump
mongodump -d scripture_commentary -o dump
mongodump -d forms -o dump
mongodump -d banking -o dump
mongodump -d users -o dump

git add dump/.
git commit -m "standard mongo dump"
git push origin master

