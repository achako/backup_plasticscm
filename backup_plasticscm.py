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

import os
import datetime
import logging
import ConfigParser
import glob
from subprocess import check_call

# Setting File------------------------------
# backup_attribute
CONFIG_FILE 		= 'settings.ini'
DATABASE_TYPE 		= 'mysql'
LOCAL_DIR			= '~/backup_tmp/'
COMPRESS			= True
BACKUP_CNT			= 3
BACKUP_LOG_DIR 		= './'
# remote_backup
USE_REMOTE_BACKUP	= False
REMOTE_HOST 		= 'localhost'
REMOTE_USER			= 'root'
REMOTE_PASSWORD		= 'root'
BACKUP_DIR			= './'
# mysql_user
USER_NAME   		= 'root'
PASSWORD    		= 'root'
#-------------------------------------------
LOG_NAME			= 'backuplog'


#--------------------------------------
# delete_old_logfile
#--------------------------------------
def delete_old_logfile():
	filenames = glob.glob( os.path.join( BACKUP_LOG_DIR,'backuplog*' ) )
	file_lst = []
	for file in filenames:
		file = os.path.join( BACKUP_LOG_DIR, file )
		file_lst.append([file,os.stat( file ).st_size,time.ctime(os.stat(file).st_mtime)])

	delete_cnt = len( file_lst ) - BACKUP_CNT + 1
	
	if delete_cnt <= 0:
		return

	# order by old date
	lst = sorted( file_lst,key=itemgetter(2), reverse = True )
	
	for file in lst:
		os.remove( file[ 0 ] )
		logger.debug( "removed log :" + file[ 0 ] )
		delete_cnt -= 1
		if delete_cnt == 0:
			break


#--------------------------------------
# setup_backuplog
#--------------------------------------
def setup_backuplog():
	global BACKUP_LOG_DIR
	# change directory to script directory
	current_dir = os.chdir( os.path.abspath( os.path.dirname(__file__) ) )
	
	# check BACKUP_DIR is exists and directory
	if os.path.exists( BACKUP_LOG_DIR ):
		if os.path.isdir( BACKUP_LOG_DIR ) is False:
			BACKUP_LOG_DIR = current_dir
	else:
		os.mkdirs( BACKUP_LOG_DIR )

	# delete old log
	delete_old_logfile()

	now = datetime.datetime.now()
	backuplog = BACKUP_LOG_DIR + LOG_NAME + now.strftime("%Y-%m-%d-%H-%M") + ".log"
	logging.basicConfig(filename=backuplog, level=logging.DEBUG, filemode='w', format="%(asctime)s [%(levelname)s]: %(message)s")

	# write header
	header_message = "\n#================================================\n\
						# Backup Start: " + now.strftime("%Y/%m/%d %H:%M:%S") + "\n\
						#================================================\n\n"
	logging.debug( header_message )


#--------------------------------------
# output_config
#--------------------------------------
def output_config():
	logging.debug( "BACKUP_LOG_DIR: " 	+ BACKUP_LOG_DIR )
	logging.debug( "BACKUP_CNT: " 		+ str( BACKUP_CNT ) )
	logging.debug( "DATABASE_TYPE: " 	+ DATABASE_TYPE )
	logging.debug( "LOCAL_DIR: " 		+ LOCAL_DIR )
	logging.debug( "COMPRESS: " 		+ str( COMPRESS ) )
	
	logging.debug( "USE_REMOTE_BACKUP: " + str( USE_REMOTE_BACKUP ) )
	if USE_REMOTE_BACKUP is True:
		logging.debug( "REMOTE_HOST: " 		+ REMOTE_HOST )
		logging.debug( "REMOTE_USER: " 		+ REMOTE_USER )
		logging.debug( "REMOTE_PASSWORD: " 	+ REMOTE_PASSWORD )
		logging.debug( "BACKUP_DIR: " 		+ BACKUP_DIR )
	if DATABASE_TYPE == 'mysql':
		logging.debug( "USER_NAME: " 		+ USER_NAME )
		logging.debug( "PASSWORD: " 		+ PASSWORD )


#--------------------------------------
# read configuration file
#--------------------------------------
def read_configuration():

	if os.path.exists(CONFIG_FILE) is False:
		setup_backuplog()
		logging.error( "configfile is not exists" )
		return 1

	conf = ConfigParser.SafeConfigParser()
	conf.read(CONFIG_FILE)

	# backup_attribute
	if conf.has_option( "backup_attribute", "backup_log"):
		BACKUP_LOG_DIR	= conf.get("backup_attribute", "backup_log")
	if conf.has_option( "backup_attribute", "log_save_cnt"):
		BACKUP_CNT		= conf.getint("backup_attribute", "log_save_cnt")

	# setup logsettings
	setup_backuplog()
	
	if conf.has_option( "backup_attribute", "database_type" ):
		DATABASE_TYPE	= conf.get("backup_attribute", "database_type")
	if conf.has_option( "backup_attribute", "local_dir"):
		LOCAL_DIR		= conf.get("backup_attribute", "local_dir")
	if conf.has_option( "backup_attribute", "compress"):
		COMPRESS		= conf.getboolean("backup_attribute", "compress")
		
	# remote_backup
	if conf.has_option( "remote_backup", "use_remote_backup"):
		USE_REMOTE_BACKUP	= conf.getboolean("remote_backup", "use_remote_backup")
	if USE_REMOTE_BACKUP is True:
		if conf.has_option( "remote_backup", "remote_host"):
			REMOTE_HOST			= conf.get("remote_backup", "remote_host")
		if conf.has_option( "remote_backup", "remote_user"):
			REMOTE_USER			= conf.get("remote_backup", "remote_user")
		if conf.has_option( "remote_backup", "remote_password"):
			REMOTE_PASSWORD		= conf.get("remote_backup", "remote_password")
		if conf.has_option( "remote_backup", "backup_dir"):
			BACKUP_DIR			= conf.get("backup_attribute", "backup_dir")
		
	#mysql_user
	if DATABASE_TYPE == 'mysql':
		USER_NAME 		= conf.get("mysql_user", "username")
		PASSWORD 		= conf.get("mysql_user", "password")
	
	output_config()
	return 0

if __name__ == "__main__":
	result = read_configuration()
	
	if result == 1:
		sys.exit()
		
