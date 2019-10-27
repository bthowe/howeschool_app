mongodump -d math_book_info -o /media/pi/HOWESCHOOL/database_files
mongodump -d math_exercise_origins -o /media/pi/HOWESCHOOL/database_files
mongodump -d math_performance -o /media/pi/HOWESCHOOL/database_files
mongodump -d vocab -o /media/pi/HOWESCHOOL/database_files
mongodump -d scripture_commentary -o /media/pi/HOWESCHOOL/database_files
mongodump -d forms -o /media/pi/HOWESCHOOL/database_files
mongodump -d banking -o /media/pi/HOWESCHOOL/database_files
mongodump -d users -o /media/pi/HOWESCHOOL/database_files

mongoexport --host localhost --db forms --collection Scriptures --csv --out /media/pi/HOWESCHOOL/database_files_csv/forms/forms_Scriptures.csv --fields scripture,week_start_date,scripture_ref
mongoexport --host localhost --db forms --collection Weekly --csv --out /media/pi/HOWESCHOOL/database_files_csv/forms/forms_Weekly.csv --fields mon_job,tue_job,wed_job,thu_job,fri_job,sat_job,mon_question,tue_question,wed_question,thu_question,fri_question,sat_question,calvin_book,samuel_book,kay_book,week_start_date,scripture_ref,scripture

mongoexport --host localhost --db banking --collection Calvin --csv --out /media/pi/HOWESCHOOL/database_files_csv/banking/banking_Calvin.csv --fields type,amount,kid,date,description
mongoexport --host localhost --db banking --collection Samuel --csv --out /media/pi/HOWESCHOOL/database_files_csv/banking/banking_Samuel.csv --fields type,amount,kid,date,description
mongoexport --host localhost --db banking --collection Kay --csv --out /media/pi/HOWESCHOOL/database_files_csv/banking/banking_Kay.csv --fields type,amount,kid,date,description

mongoexport --host localhost --db math_book_info --collection Algebra_1 --csv --out /media/pi/HOWESCHOOL/database_files_csv/math_book_info/math_book_info_Algebra_1.csv --fields book,chapter,num_lesson_probs,num_mixed_probs
mongoexport --host localhost --db math_book_info --collection Algebra_1_2 --csv --out /media/pi/HOWESCHOOL/database_files_csv/math_book_info/math_book_info_Algebra_1_2.csv --fields book,chapter,num_lesson_probs,num_mixed_probs
mongoexport --host localhost --db math_book_info --collection Math_5_4 --csv --out /media/pi/HOWESCHOOL/database_files_csv/math_book_info/math_book_info_Math_5_4.csv --fields book,chapter,num_lesson_probs,num_mixed_probs
mongoexport --host localhost --db math_book_info --collection Math_7_6 --csv --out /media/pi/HOWESCHOOL/database_files_csv/math_book_info/math_book_info_Math_7_6.csv --fields book,chapter,num_lesson_probs,num_mixed_probs
mongoexport --host localhost --db math_book_info --collection Math_8_7 --csv --out /media/pi/HOWESCHOOL/database_files_csv/math_book_info/math_book_info_Math_8_7.csv --fields book,chapter,num_lesson_probs,num_mixed_probs

mongoexport --host localhost --db math_exercise_origins --collection Algebra_1 --csv --out /media/pi/HOWESCHOOL/database_files_csv/math_exercise_origins/math_exercise_origins_Algebra_1.csv --fields book,chapter,origin_list
mongoexport --host localhost --db math_exercise_origins --collection Algebra_1_2 --csv --out /media/pi/HOWESCHOOL/database_files_csv/math_exercise_origins/math_exercise_origins_Algebra_1_2.csv --fields book,chapter,origin_list
mongoexport --host localhost --db math_exercise_origins --collection Math_5_4 --csv --out /media/pi/HOWESCHOOL/database_files_csv/math_exercise_origins/math_exercise_origins_Math_5_4.csv --fields book,chapter,origin_list
mongoexport --host localhost --db math_exercise_origins --collection Math_7_6 --csv --out /media/pi/HOWESCHOOL/database_files_csv/math_exercise_origins/math_exercise_origins_Math_7_6.csv --fields book,chapter,origin_list
mongoexport --host localhost --db math_exercise_origins --collection Math_8_7 --csv --out /media/pi/HOWESCHOOL/database_files_csv/math_exercise_origins/math_exercise_origins_Math_8_7.csv --fields book,chapter,origin_list

mongoexport --host localhost --db math_performance --collection Algebra_1 --csv --out /media/pi/HOWESCHOOL/database_files_csv/math_performance/math_performance_Algebra_1.csv --fields kid,book,start_chapter,start_problem,end_chapter,end_problem,date,start_time,end_time,miss_lst
mongoexport --host localhost --db math_performance --collection Algebra_1_2 --csv --out /media/pi/HOWESCHOOL/database_files_csv/math_performance/math_performance_Algebra_1_2.csv --fields kid,book,start_chapter,start_problem,end_chapter,end_problem,date,start_time,end_time,miss_lst
mongoexport --host localhost --db math_performance --collection Math_7_6 --csv --out /media/pi/HOWESCHOOL/database_files_csv/math_performance/math_performance_Math_7_6.csv --fields kid,book,start_chapter,start_problem,end_chapter,end_problem,date,start_time,end_time,miss_lst

mongoexport --host localhost --db scripture_commentary --collection Calvin --csv --out /media/pi/HOWESCHOOL/database_files_csv/scripture_commentary/scripture_commentary_Calvin.csv --fields name,date,start_book,start_chapter,start_verse,end_book,end_chapter,end_verse,comment 
mongoexport --host localhost --db scripture_commentary --collection Samuel --csv --out /media/pi/HOWESCHOOL/database_files_csv/scripture_commentary/scripture_commentary_Samuel.csv --fields name,date,start_book,start_chapter,start_verse,end_book,end_chapter,end_verse,comment
mongoexport --host localhost --db scripture_commentary --collection Kay --csv --out /media/pi/HOWESCHOOL/database_files_csv/scripture_commentary/scripture_commentary_Kay.csv --fields name,date,start_book,start_chapter,start_verse,end_book,end_chapter,end_verse,comment

mongoexport --host localhost --db users --collection users --csv --out /media/pi/HOWESCHOOL/database_files_csv/users/users_users.csv --fields name,password,access

mongoexport --host localhost --db vocab --collection Main --csv --out /media/pi/HOWESCHOOL/database_files_csv/vocab/vocab_Main.csv --fields def,word,page,timestamp,lesson,practice,button,quiz
mongoexport --host localhost --db vocab --collection Practice --csv --out /media/pi/HOWESCHOOL/database_files_csv/vocab/vocab_Practice.csv --fields card_front,page,card_back,num_batches,index,batch_index,batch_size,button,timestamp
mongoexport --host localhost --db vocab --collection Quiz --csv --out /media/pi/HOWESCHOOL/database_files_csv/vocab/vocab_Quiz.csv --fields completed,chosen_card,timestamp,alternatives,answer_card,page,button,correct,index,prompt,radio_button_chosen

# sudo supervisorctl stop mongod
