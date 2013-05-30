#######################################
# alter_mysql.py
#
# execute mysql command ALTER TABLE table_name ENGINE=InnoDB;
# all database
# http://sakuratan.biz/archives/4536
#######################################

#!/usr/bin/env python

import os
import MySQLdb
import ConfigParser

CONFIG_FILE = 'settings.ini'
USER_NAME = 'root'
PASSWORD = 'root'

#--------------------------------------
# read_configuration
# read configuration file
#--------------------------------------
def read_mysql_configuration():

	if os.path.exists(CONFIG_FILE) is False:
		print("config file is not exists")
		return 1

	conf = ConfigParser.SafeConfigParser()
	conf.read( CONFIG_FILE )

	if conf.has_option("mysql_user", "username") is False or conf.has_option("mysql_user", "password") is False:
		print("conf.has_option[username]or[password]")
		return 1

	USER_NAME 	= conf.get("mysql_user", "username")
	PASSWORD 	= conf.get("mysql_user", "password")
	return 0

#--------------------------------------
# alter_all_mysql
# defrag all mysql database
#--------------------------------------
def alter_all_mysql():
    conn = MySQLdb.connect(user=USER_NAME, passwd=PASSWORD)
    cur = conn.cursor()
    cur.execute('SHOW DATABASES')
    databases = [database for database, in cur if database != 'mysql']
    cur.close()
    conn.close()

    for database in databases:
        conn = MySQLdb.connect(user=USER_NAME, db=database, passwd=PASSWORD)
        cur1 = conn.cursor()
        cur1.execute('SHOW TABLE STATUS')
        for t in cur1:
            tablename = t[0]
            engine = t[1]
            if engine and engine.lower() == 'innodb':
                print 'Defrag %s.%s' % (database, tablename)
                cur2 = conn.cursor()
                cur2.execute('ALTER TABLE %s ENGINE=INNODB' % tablename)
                cur2.close()
        cur1.close()
        conn.close()


if __name__ == '__main__':

	result = read_mysql_configuration()

	if result == 1:
		print("ConfigFile read error")
	else:
		alter_all_mysql()