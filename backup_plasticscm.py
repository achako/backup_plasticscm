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
# get_dir_basename
#--------------------------------------
def get_dir_basename( dir_path ):
	_logger = LogFileManager()

	_logger.output( 'Debug', "get_dir_basename...." )
	
	_cd_dirlist = dir_path.split( "/" )
	_ret_dir = ""
	if dir_path.endswith( "/" ):
		_logger.output( 'Debug', "get_dir_basename...." )
		_ret_dir = _cd_dirlist[ len( _cd_dirlist ) - 2 ]
	else:
		_ret_dir = _cd_dirlist[ len( _cd_dirlist ) - 1 ]

	_logger.output( 'Debug', "return :" + _ret_dir )

	return _ret_dir

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
		command_str = 'mysqldump --events -x --all-databases --default-character-set=utf8 --hex-blob -u' + user_name + ' -p' + password + ' > ' + _backup_path
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
	
	_zip = None
	try:
		_zipfile_path = BACKUP_DIR.rstrip( "/" ) + ".zip"
		_zip = zipfile.ZipFile( _zipfile_path, 'w', zipfile.ZIP_DEFLATED )
		for _root_path, _dirs, _files in os.walk( BACKUP_DIR ):
			for _file in _files:
				_path = _root_path + '/' + _file
				if _path == BACKUP_DIR:
					continue
				_logger.output( 'Debug', "zip file:" + _path )
				_arc_name = os.path.relpath( _path, os.path.dirname( BACKUP_DIR ))
				_logger.output( 'Debug', "arc_file:" + _arc_name )
				_zip.write( _path, _arc_name )
			for _directory in _dirs:
				_path = _root_path + '/' + _directory + '/'
				_logger.output( 'Debug', "zip file:" + _path )
				_arc_name = os.path.relpath( _path, os.path.dirname( BACKUP_DIR ) ) + os.path.sep
				_logger.output( 'Debug', "arc_file:" + _arc_name )
				_zip.writestr( _path, _arc_name )
	except:
		_logger.output( 'Error', traceback.format_exc() )
	finally:
		if not _zip == None:
			_zip.close()
	
	# remove uncompress directory if compress
	shutil.rmtree( BACKUP_DIR )
	BACKUP_DIR = _zipfile_path

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
	_logger.output( 'Debug', "DeleteBackupSize: " + str( backup_del_size * 1000000 ) + "(Byte)" )
	
	if total_size >= backup_del_size * 1000000:
		_logger.output( 'Debug', "total size over DeleteBackupSize: deete start..." )
		# order by old date
		lst = sorted( file_lst, key=itemgetter(2), reverse = True )
		# if total size is larger than BACKUP_DEL_SIZE, delete a half of files
		cnt = 0
		for file in lst:
			if cnt % 2 == 1:
				sftp_connection.remove( file[ 0 ] )
				_logger.debug( "removed backup:" + file[ 0 ] )
			cnt += 1
		_logger.output( 'Debug', "Delete backup file end...." )

#--------------------------------------
# send_remote_machine
#--------------------------------------
def send_remote_machine( conf ):

	_logger = LogFileManager()

	_logger.output( 'Debug', "Start to send backup file( remote backup )...." )
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

		_logger.output( 'Debug', "Send BackupFile" + BACKUP_DIR +" to " + _remote_path )
		# send_file
		if conf.m_compress is True:
			_logger.output( 'Debug', "send compress files..." )
			sftp_connection.put( BACKUP_DIR, _remote_path )
		else:
			#make directory
			_logger.output( 'Debug', "send uncompress files..." )
#			_cp_dir = _get_dir_basename( BACKUP_DIR )
#			_logger.output( 'Debug', "makedir " + _cp_dir )
#			sftp_connection.mkdir( _cp_dir )
			# copy files
			_files = os.listdir( BACKUP_DIR )
			for _child in _files:
#				if os.path.isfile( _child ):
				_logger.output( 'Debug', "copy file " + BACKUP_DIR + _child )
				sftp_connection.put( BACKUP_DIR + _child, _remote_path )
			
	except:
		_logger.output( 'Error', "Failed to send backupfile to remote server" )
		_logger.output( 'Error', traceback.format_exc() )
		return 1
	finally:
		if client:
			client.close()
		if sftp_connection:
			sftp_connection.close()

	_logger.output( 'Debug', "End to send backup file...." )
	
	return 0

#--------------------------------------
# send_file_server
#--------------------------------------
def send_file_server( conf ):
	_logger = LogFileManager()

	_logger.output( 'Debug', "Start to send backup file( file server )...." )

	strcommand = ""

	if BACKUP_DIR.endswith( ".zip" ):
		_cd_dir = os.path.dirname( BACKUP_DIR )
		_send_file = os.path.basename( BACKUP_DIR )
		strcommand = "lcd " + _cd_dir +";put " + _send_file + ";"
	elif os.path.isdir( BACKUP_DIR ):
		_cp_dir = get_dir_basename( BACKUP_DIR )
		strcommand = "lcd " + BACKUP_DIR + ";lcd ../;recurse on;prompt off;mput " + _cp_dir + ";"
	else:
		return 1
	
	smb_conf = ""

	if conf.m_backup_user != "" and conf.m_backup_password != "":
		smb_conf = conf.m_backup_password + " -U " + conf.m_backup_user + " "
	if conf.m_backup_dir != "":
		smb_conf += "-D " + conf.m_backup_dir + " "

	smbcommand = "smbclient " + conf.m_backup_host + " " + smb_conf + "-c \"" + strcommand + "quit\""
	_logger.output( 'Debug', "smbcommand : " + smbcommand )

	result = os.system( smbcommand )
	
	if result == 1:
		_logger.output( 'Error', "Failed to send backupfile to file server" )
		_logger.output( 'Error', traceback.format_exc() )
		return 1
	
	return 0

#--------------------------------------
# delete_local_backup
#--------------------------------------
def delete_local_backup( conf ):
	strcommand = ""
	if conf.m_compress:
		shutil.rmtree( BACKUP_DIR )
	else:
		# remove compress file
		os.remove( BACKUP_DIR )


#--------------------------------------
# main
#--------------------------------------
if __name__ == "__main__":

	_logger = LogFileManager()
	_logger.set_currect_dir()

	conf 	= ConfigFile( 'BACKUP' )
	result	= conf.read_configuration()

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

	if conf.m_use_file_server is True:
		result = send_file_server( conf )
		if result == 1:
			_logger.shutdown()
			sys.exit()
			
	if conf.m_use_remote_backup is False and conf.m_use_file_server is False:
		delete_local_backup( conf )

	_logger.shutdown()
	
