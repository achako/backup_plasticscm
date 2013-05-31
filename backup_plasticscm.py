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

import os, zipfile, shutil, paramiko
from subprocess import check_call
from config_file import*

DUMP_FILE			= 'dump_plasticscm.sql'
BACKUP_DIR			= ''

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
# zip
#--------------------------------------
def zip_backupfile( compress ):
	global BACKUP_DIR
	
	if compress is False:
		return 0
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
# send_remote_machine
#--------------------------------------
def send_remote_machine():

	if USE_REMOTE_BACKUP is False:
		return
	logging.debug( "Start to send backup file" )
	# SFTP by using paramiko
	client = None
	sftp_connection = None
	try:
		client = paramiko.SSHClient()
		client.set_missing_host_key_policy( paramiko.AutoAddPolicy() )
		client.connect( REMOTE_HOST, port=REMOTE_PORT, username=REMOTE_USER, password=REMOTE_PASSWORD )
		sftp_connection = client.open_sftp()

		# count backupfiles in remote directory
		filenames = sftp_connection.listdir( REMOTE_DIR )

		# get total size of remote directory
		# set fields of time & filesize
		total_size = 0
		for file in filenames:
			file = os.path.join( REMOTE_DIR, file )
			file_lst.append([file,sftp_connection.stat( file ).st_size, time.ctime( sftp_connection.stat(file).st_mtime )])
			total_size += sftp_connection.stat( file ).st_size
		
		if total_size >= BACKUP_DEL_SIZE * 1000000:
			# order by old date
			lst = sorted( file_lst,key=itemgetter(2), reverse = True )
			# if total size is larger than BACKUP_DEL_SIZE, delete a half of files
			cnt = 0
			for file in lst:
				if cnt % 2 == 0:
					sftp_connection.remove( file[ 0 ] )
					logging.debug( "removed backup:" + file[ 0 ] )
				cnt += 1

		# send_file
		sftp_connection.put( BACKUP_DIR, REMOTE_DIR )
	except:
		logging.error( traceback.format_exc() )
		send_mail( traceback.format_exc() )

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
	
	if result == 1:
		sys.exit()

	if conf.m_database_type == 'mysql':
		result = dump_mysql( conf.m_dump_date, conf.m_local_dir, conf.m_user_name, conf.m_password )
	if result == 1:
		sys.exit()
	
	result = zip_backupfile( conf.m_compress )
	
	if result == 1:
		sys.exit()
		
