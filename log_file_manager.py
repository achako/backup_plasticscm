#######################################
# log_file_manager.py
#
#######################################

#!/usr/bin/env python
import os, sys, logging, glob, time, traceback
from email.MIMEText import MIMEText
from email.Header import Header
from email.Utils import formatdate
from operator import itemgetter
import smtplib

class LogFileManager(object):

	__log_name 		= 'backuplog'
	__output_log 	= False
	
	def __new__( clsObj ):
		if not hasattr( clsObj, "__instance__" ):
			clsObj.__instance__ = super( LogFileManager, clsObj ).__new__( clsObj )
		return clsObj.__instance__

	#--------------------------------------
	# delete_old_logfile
	#--------------------------------------
	def __delete_old_logfile( self, log_dir, backup_cnt ):
		_find_name = self.__log_name + '*'
		print( "_find_name: " + _find_name )
		filenames = glob.glob( os.path.join( log_dir, _find_name ) )
		file_lst = []
		for file in filenames:
			file = os.path.join( log_dir, file )
			file_lst.append([file,os.stat( file ).st_size, time.ctime(os.stat(file).st_mtime)])

		delete_cnt = len( file_lst ) - backup_cnt + 1
		print( "delete_cnt: " + str( delete_cnt ) )
		
		if delete_cnt <= 0:
			return
			
		# order by old date
		lst = sorted( file_lst, key=itemgetter(2), reverse = True )
		
#		for file in lst:
#			print( file[ 0 ] + " | " + str( file[ 1 ] ) + " | " + file[ 2 ] )
		
		for file in lst:
			os.remove( file[ 0 ] )
			logging.debug( "removed log :" + file[ 0 ] )
			delete_cnt -= 1
			if delete_cnt == 0:
				break

	#--------------------------------------
	# setup_backuplog
	#--------------------------------------
	def setup_backuplog( self, log_dir, dump_date, backup_cnt ):
		# delete old log
		self.__delete_old_logfile( log_dir, backup_cnt )

		_backuplog = log_dir + self.__log_name + dump_date + ".log"
		self.output( 'Debug', "make logfile:\t" + os.path.abspath( _backuplog ) )
		try:
			logging.basicConfig(filename=_backuplog, level=logging.DEBUG, format="%(asctime)s [%(levelname)s]: %(message)s")
		except:
			print( traceback.format_exc() )
			return 1
		
#		list = os.listdir( log_dir )
#		for file in list:
#			print( file )

		# write header
		logging.debug( "Backup Start" )
		
		self.__output_log = True
		return 0
		
	#--------------------------------------
	# shutdown
	#--------------------------------------
	def shutdown( self ):
		logging.shutdown()
	
	#--------------------------------------
	# sendErrorMail
	#--------------------------------------
	def send_mail( self, mailtext ):
		msg 			= MIMEText(mailtext.encode('utf-8'),'plain','utf-8')
		msg['Subject']	= Header('backup error','utf-8')
		msg['From']		= 'root@zisaba.com'
		msg['To']		= 'hiraishi_asami@artdink.co.jp'
		msg['Date']		= formatdate()

		sendmail = smtplib.SMTP('smtp.artdink.co.jp',25)
		sendmail.ehlo()
		sendmail.starttls()
		sendmail.ehlo()
		sendmail.login('ahiraishi','mumu1224')
		sendmail.sendmail(msg['From'],msg['To'],msg.as_string())

		exit()
			
	#--------------------------------------
	# __read_backup_attributes
	#--------------------------------------
	def set_currect_dir( self ):
		# change directory to script directory
		os.chdir( os.path.abspath( os.path.dirname(__file__) ) )
		_current_dir = os.getcwd()
		self.output( 'Debug', "Current Directory:" + _current_dir )
	
	#--------------------------------------
	# __logging_file
	#--------------------------------------
	def __logging_file( self, error_type, message ):
		if error_type == 'Debug':
			logging.debug( message )
		elif error_type == 'Warning':
			logging.warning( message )
		elif error_type == 'Error':
			logging.error( message )
#			self.send_mail( message )
			sys.exit()

	#--------------------------------------
	# __print_message
	#--------------------------------------
	def __print_message( self, error_type, message ):
		_output_message = "[" + error_type +"]: " + message
		print( _output_message )

	#--------------------------------------
	# output
	#--------------------------------------
	def output( self, error_type, message ):
		if self.__output_log is True:
			self.__logging_file( error_type, message )
#			self.__print_message( error_type, message )
		else:
			self.__print_message( error_type, message )
		


