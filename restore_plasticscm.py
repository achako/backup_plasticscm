#######################################
# restore_plastic_scm.py
#
#######################################

#!/usr/bin/env python
import sys, os, zipfile, shutil
from log_file_manager import *
from config_file import*


#--------------------------------------
# use_info()
#--------------------------------------
def use_info():
	_logger = LogFileManager()
	_logger.output( 'Debug', "How to use---------------" )
	_logger.output( 'Debug', "./restore_plasticscm.py [backup_directory_path]" )

#--------------------------------------
# unzip_file
#--------------------------------------
def unzip_file( backup_path ):

	_logger = LogFileManager()
	_logger.output( 'Debug', "Start to uncompress backup file" )

	_restore_dir = ""

	try:
		_zip = zipfile.ZipFile( backup_path, 'r', zipfile.ZIP_DEFLATED )
		_restore_dir = backup_path.replace( ".zip", "" )
		_restore_dir += "/"
		
		if not os.path.exists( _restore_dir ):
			os.makedirs( "make uncompress directory: " + _restore_dir )
		_logger.output( 'Debug', "--zip files--" )
		for _file in _zip.namelist():
		
			_list_file = _restore_dir + _file
			_logger.output( 'Debug', "uncompress: " + _list_file )
			
			_file_dir = os.path.dirname( _list_file )
			if not os.path.exists( _file_dir ):
				_logger.output( 'Debug', "make direcrtory: " + _file_dir )
				os.makedirs( _file_dir )
			uzf = file( _list_file, 'wb' )
			uzf.write( _zip.read( _file ) )
			uzf.close()
	except:
		_logger.output( 'Error', traceback.format_exc() )
		return 1, _restore_dir
	finally:
		_zip.close()

	_logger.output( 'Debug', "End to uncompress backup file" )

	return 0, _restore_dir

#--------------------------------------
# copy_setting_files
#--------------------------------------
def copy_setting_files( restore_path ):

	_logger = LogFileManager()
	_logger.output( 'Debug', "Start to copy setting file" )

	DB_CONF 		= "/opt/plasticscm4/server/db.conf"
	SERVER_CONF 	= "/opt/plasticscm4/server/server.conf"
	USERS_CONF 		= "/opt/plasticscm4/server/users.conf"
	GROUPS_CONF 	= "/opt/plasticscm4/server/groups.conf"
	SQL_CONF		= "/etc/mysql/my.cnf"

	files = os.listdir( restore_path )
	for file in files:
	
		try:
			_logger.output( 'Debug', file )
			_cp_file = restore_path + file
			if file == os.path.basename( DB_CONF ):
				_logger.output( 'Debug', DB_CONF + ": " + _cp_file )
				if not os.access( DB_CONF, os.W_OK ):
					os.chmod( DB_CONF,0755 )
				shutil.copy( _cp_file, 		DB_CONF )
			elif file == os.path.basename( SERVER_CONF ):
				_logger.output( 'Debug', SERVER_CONF + ": " + _cp_file )
				if not os.access( SERVER_CONF, os.W_OK ):
					os.chmod( SERVER_CONF, 0755 )
				shutil.copy( _cp_file, 		SERVER_CONF )
			elif file == os.path.basename( USERS_CONF ):
				_logger.output( 'Debug', USERS_CONF + ": " + _cp_file )
				if not os.access( SERVER_CONF, os.W_OK ):
					os.chmod( SERVER_CONF, 0755 )
				shutil.copy( _cp_file, 		USERS_CONF )
			elif file == os.path.basename( GROUPS_CONF ):
				_logger.output( 'Debug', GROUPS_CONF + ": " + _cp_file )
				if not os.access( SERVER_CONF, os.W_OK ):
					os.chmod( SERVER_CONF, 0755 )
				shutil.copy( _cp_file, 		GROUPS_CONF )
			elif file == os.path.basename( SQL_CONF ):
				_logger.output( 'Debug', SQL_CONF + ": " + _cp_file )
				if not os.access( SERVER_CONF, os.W_OK ):
					os.chmod( SERVER_CONF, 0755 )
				shutil.copy( _cp_file, 		SQL_CONF )
		except:
			_logger.output( 'Error', traceback.format_exc() )
			continue

	_logger.output( 'Debug', "End to copy setting file" )

	return 0

#--------------------------------------
# find_dump_file
#--------------------------------------
def find_dump_file( restore_path ):
	_files = os.listdir( restore_path )
	
	for _file in _files:
		if _file.endswith( ".sql" ):
			print( _file )
			_ret_file = restore_path + _file
			print( _ret_file )
			return _ret_file
	
	return ""

#--------------------------------------
# restore_mysql
#--------------------------------------
def restore_mysql( restore_path, user_name, password ):

	_logger = LogFileManager()

	# find dump file
	dump_file = find_dump_file( restore_path )
	
	if len( dump_file ) == 0:
		_logger.output( 'Error', "there is no dump file in " + restore_path )
		return 1

	_logger.output( 'Debug', "Start restore MySQL-------------" )
	try:
		_command_str = 'mysql --default-character-set=utf8 -u ' + user_name + ' -p' + password + ' < ' + dump_file
		_logger.output( 'Debug', _command_str )
		os.system( _command_str )
	except:
		_logger.output( 'Error', traceback.format_exc() )
		return 1

	_logger.output( 'Debug', "End restore MySQL-------------" )
	return 0

#--------------------------------------
# main
#--------------------------------------
if __name__ == "__main__":

	_logger = LogFileManager()
	conf 	= ConfigFile( 'ALTER' )

	# python ./restore_plasticscm.py [backup_path]
	_param = sys.argv

	if len( _param ) < 2:
		_logger.output( 'Warning', "arg[backup_directory_path] is not found" )
		use_info()
		sys.exit()
	
	_result = 0
	
	# param[ 1 ] is [backup_path]
	_backup_path 	= _param[ 1 ]
	_backup_path 	= os.path.abspath( _backup_path )
	
	# read config file
	_logger.set_currect_dir()
	_result			= conf.read_configuration()
	
	_restore_dir = _backup_path
	# if compressed file unzip
	if _backup_path.endswith( ".zip" ):
		_result, _restore_dir = unzip_file( _backup_path )
		
	if _result == 1:
		sys.exit()

	# restore mysql
	_result = restore_mysql( _restore_dir, conf.m_user_name, conf.m_password )
	if _result == 1:
		sys.exit()

	# copy setting file
	_result = copy_setting_files( _restore_dir )
	if _result == 1:
		sys.exit()


