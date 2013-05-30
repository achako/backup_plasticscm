#######################################
# backup_plastic_scm.py
#
#######################################

#!/usr/bin/env python


# sudo plasticsd4 stop
# cp /opt/PlasticSCM/server/db.conf	LOCAL_DIR
# cp /opt/PlasticSCM/server/server.conf LOCAL_DIR
# cp /opt/PlasticSCM/server/users.conf LOCAL_DIR
# cp /opt/PlasticSCM/server/groups.conf LOCAL_DIR
# alter before backup
# mysqldump -u USERNAME -p PASSWORD database_name --hex-blob > LOCAL_DIR/dump_database_name.sql
# sudo plasticsd4 start
# zip  directory
# send to remote machine

import ConfigParser
from subprocess import check_call

CONFIG_FILE 	= 'settings.ini'
DATABASE_TYPE 	= 'mysql'
LOCAL_DIR		= '~/backup_tmp/'
COMPRESS		= 'true'
USE_REMOTE_BACKUP	= 'false'
REMOTE_HOST 	= 'localhost'
REMOTE_USER		= 'root'
REMOTE_PASSWORD	= 'root'
BACKUP_DIR		= '~/backup/plasticSCM/'
#mysql
USER_NAME   	= 'root'
PASSWORD    	= 'root'

# read configuration file
def read_configuration():

	if !os.path.exists(CONFIG_FILE):
		
		return 1

	conf = ConfigParser.SafeConfigParser()
	conf.read(CONFIG_FILE)
	
	if conf.has_option( "backup_attribute", "database_type" ):
		DATABASE_TYPE	= conf.get('backup_attribute', 'database_type')
	if conf.has_option( "backup_attribute", "local_dir"):
		LOCAL_DIR		= conf.get("backup_attribute", "local_dir")
	if conf.has_option( "backup_attribute", "local_dir"):
		COMPRESS		= conf.get("backup_attribute", "compress")
	if conf.has_option( "backup_attribute", "local_dir"):
		USE_REMOTE_BACKUP	= conf.get("remote_backup", "use_remote_backup")
	
	if USE_REMOTE_BACKUP == 'true':
		REMOTE_HOST			= conf.get('remote_backup', 'remote_host')
		REMOTE_USER			= conf.get('remote_backup', 'remote_user')
		REMOTE_PASSWORD		= conf.get('remote_backup', 'remote_password')
		BACKUP_DIR			= conf.get('backup_attribute', 'backup_dir')
	
	if DATABASE_TYPE == 'mysql':
		USER_NAME 		= conf.get('mysql_user', 'username')
		PASSWORD 		= conf.get('mysql_user', 'password')

if __name__ == "__main__":
	result =read_configuration()
	
	if result == 1
		sys.exit()

