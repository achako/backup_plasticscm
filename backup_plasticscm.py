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

import os, datetime, logging, ConfigParser, glob, time, zipfile, shutil, paramiko
from subprocess import check_call
from operator import itemgetter
from email.MIMEText import MIMEText
from email.Header import Header
from email.Utils import formatdate
import smtplib

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
REMOTE_PORT			= 22
REMOTE_USER			= 'root'
REMOTE_PASSWORD		= 'root'
REMOTE_DIR			= './'
BACKUP_DEL_SIZE		= 1000
# mysql_user
USER_NAME   		= 'root'
PASSWORD    		= 'root'
#-------------------------------------------
LOG_NAME			= 'backuplog'
DUMP_FILE			= 'dump_plasticscm.sql'
DUMP_DATE			= '00-00-00-00-00'
BACKUP_DIR			= ''


#--------------------------------------
# sendErrorMail
#--------------------------------------
def send_mail( mailtext ):
	msg = MIMEText(mailtext.encode('utf-8'),'plain','utf-8')
	msg['Subject']=Header('backup error','utf-8')
	msg['From']='root@zisaba.com'
	msg['To']='hiraishi_asami@artdink.co.jp'
	msg['Date']=formatdate()

	sendmail = smtplib.SMTP('smtp.artdink.co.jp',25)
	sendmail.ehlo()
	sendmail.starttls()
	sendmail.ehlo()
	sendmail.login('ahiraishi','mumu1224')
	sendmail.sendmail(msg['From'],msg['To'],msg.as_string())

	exit()

#--------------------------------------
# delete_old_logfile
#--------------------------------------
def delete_old_logfile():
	filenames = glob.glob( os.path.join( BACKUP_LOG_DIR,'backuplog*' ) )
	file_lst = []
	for file in filenames:
		file = os.path.join( BACKUP_LOG_DIR, file )
		file_lst.append([file,os.stat( file ).st_size, time.ctime(os.stat(file).st_mtime)])

	delete_cnt = len( file_lst ) - BACKUP_CNT + 1
	
	if delete_cnt <= 0:
		return

	# order by old date
	lst = sorted( file_lst,key=itemgetter(2), reverse = True )
	
	for file in lst:
		os.remove( file[ 0 ] )
		logging.debug( "removed log :" + file[ 0 ] )
		delete_cnt -= 1
		if delete_cnt == 0:
			break

#--------------------------------------
# setup_backuplog
#--------------------------------------
def setup_backuplog():
	global BACKUP_LOG_DIR
	global DUMP_DATE
	# change directory to script directory
	current_dir = os.chdir( os.path.abspath( os.path.dirname(__file__) ) )
	
	# check BACKUP_LOG_DIR is exists and directory
	if os.path.exists( BACKUP_LOG_DIR ):
		if os.path.isdir( BACKUP_LOG_DIR ) is False:
			BACKUP_LOG_DIR = current_dir
	else:
		os.makedirs( BACKUP_LOG_DIR )
	if BACKUP_LOG_DIR.endswith( "/" ) is False:
		BACKUP_LOG_DIR += "/"

	# delete old log
	delete_old_logfile()

	now = datetime.datetime.now()
	DUMP_DATE = now.strftime("%Y-%m-%d-%H-%M")
	backuplog = BACKUP_LOG_DIR + LOG_NAME + DUMP_DATE + ".log"
	logging.basicConfig(filename=backuplog, level=logging.DEBUG, format="%(asctime)s [%(levelname)s]: %(message)s")

	# write header
	logging.debug( "Backup Start" )

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
		logging.debug( "REMOTE_DIR: " 		+ REMOTE_DIR )
	if DATABASE_TYPE == 'mysql':
		logging.debug( "USER_NAME: " 		+ USER_NAME )
		logging.debug( "PASSWORD: " 		+ PASSWORD )


#--------------------------------------
# read configuration file
#--------------------------------------
def read_configuration():
	global BACKUP_LOG_DIR
	global BACKUP_CNT
	global DATABASE_TYPE
	global LOCAL_DIR
	global COMPRESS
	global BACKUP_DEL_SIZE
	global USE_REMOTE_BACKUP
	global REMOTE_HOST
	global REMOTE_PORT
	global REMOTE_USER
	global REMOTE_PASSWORD
	global REMOTE_DIR
	global USER_NAME
	global PASSWORD

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
	if conf.has_option( "backup_attribute", "backup_del_size"):
		BACKUP_DEL_SIZE	= conf.getint("backup_attribute", "backup_del_size")

	# remote_backup
	if conf.has_option( "remote_backup", "use_remote_backup"):
		USE_REMOTE_BACKUP	= conf.getboolean("remote_backup", "use_remote_backup")
	if USE_REMOTE_BACKUP is True:
		if conf.has_option( "remote_backup", "remote_host"):
			REMOTE_HOST			= conf.get("remote_backup", "remote_host")
		if conf.has_option( "remote_backup", "remote_port"):
			REMOTE_PORT		= conf.getint("remote_backup", "remote_port")
		if conf.has_option( "remote_backup", "remote_user"):
			REMOTE_USER			= conf.get("remote_backup", "remote_user")
		if conf.has_option( "remote_backup", "remote_password"):
			REMOTE_PASSWORD		= conf.get("remote_backup", "remote_password")
		if conf.has_option( "remote_backup", "remote_dir"):
			REMOTE_DIR			= conf.get("backup_attribute", "remote_dir")
		
	#mysql_user
	if DATABASE_TYPE == 'mysql':
		USER_NAME 		= conf.get("mysql_user", "username")
		PASSWORD 		= conf.get("mysql_user", "password")
	
	output_config()
	return 0


#--------------------------------------
# check_backup_dir
# if not exists, make directory
#--------------------------------------
def check_backup_dir():

	global LOCAL_DIR
	global BACKUP_DIR

	current_dir = os.chdir( os.path.abspath( os.path.dirname(__file__) ) )

	if LOCAL_DIR.endswith( "/" ) is False:
		LOCAL_DIR += "/"
	BACKUP_DIR = LOCAL_DIR + DUMP_DATE + "/"

	if os.path.exists( BACKUP_DIR ):
		if os.path.isdir( LOCAL_DIR ) is False:
			BACKUP_DIR = current_dir + DUMP_DATE + "/"
	else:
		os.makedirs( BACKUP_DIR )

#--------------------------------------
# dump_mysql
#--------------------------------------
def dump_mysql():
	check_backup_dir()
	try:
		#backup mysql
		backup_path = BACKUP_DIR + DUMP_FILE
		command_str = 'mysqldump --events -u' + USER_NAME + ' -p' + PASSWORD + ' -x --all-databases --hex-blob > ' + backup_path
		os.system( command_str )
	except:
		logging.error( traceback.format_exc() )
		send_mail( traceback.format_exc() )
		return 1

	return 0

#--------------------------------------
# zip
#--------------------------------------
def zip_backupfile():
	global BACKUP_DIR
	if COMPRESS is False:
		return 0

	logging.debug( "Start to compress backup file" )

	filenames = os.listdir( BACKUP_DIR )
	
	if len( filenames ) == 0:
		logging.error( "no file in backup directory." )
		return 1
	zipfile_path = BACKUP_DIR.rstrip( "/" ) + ".zip"
	zip = zipfile.ZipFile( zipfile_path, 'w', zipfile.ZIP_DEFLATED )
	
	for file in filenames:
		zip.write( zipfile_path, file )

	zip.close()
	
	# remove uncompress directory if compress
	shutil.rmtree( BACKUP_DIR )
	BACKUP_DIR = zipfile_path

	logging.debug( "Success compress:" + BACKUP_DIR )

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
	result = read_configuration()
	
	if result == 1:
		sys.exit()
	
	if DATABASE_TYPE == 'mysql':
		result = dump_mysql()
	
	if result == 1:
		sys.exit()
	
	result = zip_backupfile()
	
	if result == 1:
		sys.exit()
	
	
