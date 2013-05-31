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
from config_file import*

#--------------------------------------
# alter_all_mysql
# defrag all mysql database
#--------------------------------------
def alter_all_mysql( user_name, password ):
	_conn = MySQLdb.connect(user=user_name, passwd=password)
	_cur = _conn.cursor()
	_cur.execute('SHOW DATABASES')
	_databases = [database for database, in _cur if database != 'mysql']
	_cur.close()
	_conn.close()
	
	_debug_log	= LogFileManager()

	for _database in _databases:
		_conn = MySQLdb.connect(user=user_name, db=_database, passwd=password)
		_cur1 = _conn.cursor()
		_cur1.execute('SHOW TABLE STATUS')
		for t in _cur1:
			_tablename = t[0]
			_engine = t[1]
			if _engine and _engine.lower() == 'innodb':
				_debug_log.output( 'Debug', 'Defrag %s.%s' % (_database, _tablename) )
				_cur2 = _conn.cursor()
				_cur2.execute('ALTER TABLE %s ENGINE=INNODB' % _tablename)
				_cur2.close()
		_cur1.close()
		_conn.close()

if __name__ == '__main__':

	_conf	= ConfigFile( 'ALTER' )
	_result	= _conf.read_configuration()

	if _result != 1:
		alter_all_mysql( _conf.m_user_name, _conf.m_password )
