# cjc-kiva
An exercise in accessing and manipulating kiva data.

This code requires python3 and has been tested on ubuntu 14.04, not in a virtualenv.

Requirements:

    apt-get install mysql-server
    pip3 install pymysql
    pip3 install requests
    pip3 install sqlalchemy

Finally, I haven't been able to get automatic db create to happen, so

    mysql << EOF
    create database if not exists kivatest;
    EOF
    
To run any script, cd to the directory and 'python script' or 'python3 script'

    cd code
    python schedule_funded_loan.py
    python check_loans.py
