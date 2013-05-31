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

import os, zipfile, shutil, paramiko, traceback
from subprocess import check_call
from config_file import*
from log_file_manager import *
import alter_mysql


DUMP_FILE			= 'dump_plasticscm.sql'
BACKUP_DIR			= ''

def stop_plasticSCM():
	os.system( "/etc/init.d/plasticsd4 stop" )
	
def start_plasticSCM():
	os.system( "/etc/init.d/plasticsd4 start" )


#--------------------------------------
# check_backup_dir
# if not exists, make directory
#--------------------------------------
def check_backup_dir( dump_date, local_dir ):

	global BACKUP_DIR

	current_dir = os.chdir( os.path.abspath( os.path.dirname(__file__) ) )

	BACKUP_DIR = local_dir + "plasticscm" + dump_date  + "/"

	if os.path.exists( BACKUP_DIR ):
		if os.path.isdir( local_dir ) is False:
			BACKUP_DIR = current_dir + dump_date  + "/"
	else:
		os.makedirs( BACKUP_DIR )

#--------------------------------------
# dump_mysql
#--------------------------------------
def dump_mysql( dump_date, local_dir, user_name, password ):
	
	_logger = LogFileManager()
	_logger.output( 'Debug', "Start dump MySQL-------------" )
	check_backup_dir( dump_date, local_dir )
	try:
		#backup mysql
		_backup_path = BACKUP_DIR + DUMP_FILE
		command_str = 'mysqldump --events -u' + user_name + ' -p' + password + ' -x --all-databases --hex-blob > ' + _backup_path
		os.system( command_str )
	except:
		_logger.output( 'Error', traceback.format_exc() )
		return 1

	_logger.output( 'Debug', "End dump MySQL-------------" )

	return 0

#--------------------------------------
# copy_setting_files
#--------------------------------------
def copy_setting_files():
	DB_CONF 		= "/opt/plasticscm4/server/db.conf"
	SERVER_CONF 	= "/opt/plasticscm4/server/server.conf"
	USERS_CONF 		= "/opt/plasticscm4/server/users.conf"
	GROUPS_CONF 	= "/opt/plasticscm4/server/groups.conf"
	SQL_CONF		= "/etc/mysql/my.cnf"
	
	copy_db 	= BACKUP_DIR + os.path.basename( DB_CONF )
	copy_server = BACKUP_DIR + os.path.basename( SERVER_CONF )
	copy_users 	= BACKUP_DIR + os.path.basename( USERS_CONF )
	copy_groups = BACKUP_DIR + os.path.basename( GROUPS_CONF )
	copy_mysql 	= BACKUP_DIR + os.path.basename( SQL_CONF )

	shutil.copy( DB_CONF, 		copy_db )
	shutil.copy( SERVER_CONF, 	copy_server )
	shutil.copy( USERS_CONF, 	copy_users )
	shutil.copy( GROUPS_CONF, 	copy_groups )
	shutil.copy( SQL_CONF, 		copy_mysql )

#--------------------------------------
# zip
#--------------------------------------
def zip_backupfile():
	global BACKUP_DIR
	
	_logger = LogFileManager()

	_logger.output( 'Debug', "Start to compress backup file" )

	filenames = os.listdir( BACKUP_DIR )
	
	if len( filenames ) == 0:
		_logger.output( 'Error', "no file in backup directory." )
		return 1
	zipfile_path = BACKUP_DIR.rstrip( "/" ) + ".zip"
	zip = zipfile.ZipFile( zipfile_path, 'w', zipfile.ZIP_DEFLATED )
	
	for file in filenames:
		zip.write( zipfile_path, file )

	zip.close()
	
	# remove uncompress directory if compress
	shutil.rmtree( BACKUP_DIR )
	BACKUP_DIR = zipfile_path

	_logger.output( 'Debug', "Success compress:" + BACKUP_DIR )

	return 0

#--------------------------------------
# delete_backup_files
#--------------------------------------
def delete_backup_files( sftp_connection, remote_dir, backup_del_size ):
	
	# count backupfiles in remote directory
	filenames = sftp_connection.listdir( remote_dir )

	# get total size of remote directory
	# set fields of time & filesize
	file_lst = []
	total_size = 0
	for file in filenames:
		file = os.path.join( remote_dir, file )
		file_lst.append([file,sftp_connection.stat( file ).st_size, time.ctime( sftp_connection.stat(file).st_mtime )])
		total_size += sftp_connection.stat( file ).st_size

	_logger.output( 'Debug', "BackupDirectory's total size: " + str( total_size ) + "(Byte)" )
	
	if total_size >= backup_del_size * 1000000:
		# order by old date
		lst = sorted( file_lst, key=itemgetter(2), reverse = True )
		# if total size is larger than BACKUP_DEL_SIZE, delete a half of files
		cnt = 0
		for file in lst:
			if cnt % 2 == 0:
				sftp_connection.remove( file[ 0 ] )
				_logger.debug( "removed backup:" + file[ 0 ] )
			cnt += 1

#--------------------------------------
# send_remote_machine
#--------------------------------------
def send_remote_machine( conf ):

	_logger = LogFileManager()

	_logger.output( 'Debug', "Start to send backup file...." )
	# SFTP by using paramiko
	client = None
	sftp_connection = None
	try:
		client = paramiko.SSHClient()
		client.set_missing_host_key_policy( paramiko.AutoAddPolicy() )
		client.connect( conf.m_remote_host, port=conf.m_remote_port, username=conf.m_remote_user, password=conf.m_remote_password )
		sftp_connection = client.open_sftp()

		delete_backup_files( sftp_connection, conf.m_remote_dir, conf.m_backup_del_size )

		_remote_path = conf.m_remote_dir
		if _remote_path.endswith( "/" ) is False:
			_remote_path += "/"
		_remote_path += os.path.basename( BACKUP_DIR )

		# send_file
		_logger.output( 'Debug', "Send BackupFile" + BACKUP_DIR +" to " + _remote_path )
		sftp_connection.put( BACKUP_DIR, _remote_path )
	except:
		_logger.output( 'Debug', traceback.format_exc() )

	finally:
		if client:
			client.close()
		if sftp_connection:
			sftp_connection.close()

#--------------------------------------
# main
#--------------------------------------
if __name__ == "__main__":

	conf 	= ConfigFile( 'BACKUP' )
	result	= conf.read_configuration()

	_logger = LogFileManager()

	if result == 1:
		_logger.shutdown()
		sys.exit()
	
#	_logger.output( 'Debug', "PlasticSCM Stop" )
#	stop_plasticSCM()

	# defrag mysql
	alter_mysql.alter_all_mysql( conf.m_user_name, conf.m_password )

	if conf.m_database_type == 'mysql':
		result = dump_mysql( conf.m_dump_date, conf.m_local_dir, conf.m_user_name, conf.m_password )
		if result == 1:
			_logger.shutdown()
			sys.exit()
	
	result = copy_setting_files()
	
#	_logger.output( 'Debug', "PlasticSCM Start" )
#	start_plasticSCM()
	
	if conf.m_compress:
		result = zip_backupfile()	
		if result == 1:
			_logger.shutdown()
			sys.exit()
	
	if conf.m_use_remote_backup is True:
		result = send_remote_machine( conf )
		if result == 1:
			_logger.shutdown()
			sys.exit()
	
	_logger.shutdown()
	
