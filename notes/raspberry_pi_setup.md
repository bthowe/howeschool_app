* Install Raspian: https://www.raspberrypi.org/help/noobs-setup/2/
* clone git repository
    * make new directory in home called PythonProjects
    * git clone <directory name>
* install python libraries (sudo pip3 install ...)
    * pandas, flask_pymongo, flask_bootstrap, flask_login, yagmail, flask_wtf, gunicorn 
* downgrade pymongo
    * sudo pip3 install pymongo==3.4.0
* mongodb
    * sudo apt-get install mongodb
    * mkdir /data/db/
    * sudo chown -R mongodb:mongodb /data/db
    * then start with sudo mongod
    * restore databases
        * mongorestore --db vocab --verbose dump/vocab
* supervisor
    * follow the directions here: https://www.vultr.com/docs/installing-and-configuring-supervisor-on-ubuntu-16-04
    * two .conf file 
        * mongo.conf: 
            * command=sudo mongod
            * For some reason, /etc/mongodb.conf exists and kicks off on restart.
                * I just moved this file to the scratch directory in howeschool_app and left the one in supervisor 
        * command.conf:
            * directory=/home/pi/PythongProjects/howeschool_app
            * sudo gunicorn --bind 0.0.0.0:8001 command:app
    * It wasn't starting on restart so I followed https://unix.stackexchange.com/questions/281774/ubuntu-server-16-04-cannot-get-supervisor-to-start-automatically
        * sudo systemctl enable supervisor
        * sudo systemctl start supervisor
* setup latex thing: https://github.com/aslushnikov/latex-online
    * curl -L https://raw.githubusercontent.com/aslushnikov/latex-online/master/util/latexonline > laton && chmod 755 laton
    * then move the laton file to somewhere in your path
        * cd /usr/local/bin
        * mv ~/PythonPaths/howeschool_app/laton .
* cron jobs
    * crontab -e
        *     1 22 * * * sudo poweroff
        *     0 22 * * * bash /home/pi/PythonProjects/howeschool_app/db_backup.sh
        *     58 21 * * SAT /usr/bin/python3 /home/pi/PythonProjects/howeschool_app/weekly_bank_deposit.py
    * don't need daily performance db create
* SSH
    * sudo raspi-config
        - Interface Settings
        - SSH
        - Enable
    
    
