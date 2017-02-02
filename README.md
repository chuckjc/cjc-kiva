# cjc-kiva
An exercise in accessing and manipulating kiva data.

This code requires python3 and has been tested on ubuntu 14.04, not in a virtualenv.

Requirements:

    apt-get install mysql-server  # set root password
    cat > ~/.my.cnf <EOF
    [client]
    user=root
    password=root
    EOF
    pip3 install pymysql
    pip3 install requests
    pip3 install sqlalchemy
    pip3 install python-dateutil

Finally, I haven't been able to get automatic db create to happen, so

    mysql << EOF
    create database if not exists kivatest;
    EOF
    
You may need to modify code/db/model.py to add mysql credentials to the url.
    
To run any script, cd to the directory and 'python script' or 'python3 script'

    cd code
    python schedule_funded_loan.py  # main program to select and schedule a funded loan
    python check_loans.py           # data integrity check
    python test_kivaquery.py        # unit test here and below
    python test_kivascheduler.py
    cd db
    python test_model.py
