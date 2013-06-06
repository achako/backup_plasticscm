//***********************************
// plasticSCM Backup Script
//**********************************
PlasticSCMのデータベースと設定ファイルをバックアップするためのスクリプトです。

//=================================
// バックアップするデータ
//=================================
・MySQLデータベース全て
・データベース設定ファイル( /opt/PlasticSCM/server/sb.conf )
・ユーザー設定ファイル( /opt/PlasticSCM/server/users.conf )
・グループ設定ファイル( /opt/PlasticSCM/server/groups.conf )
・MySQL設定ファイル( /etc/mysql/my.cnf )

//=================================
// 各ファイルの説明
//=================================
settings.ini
	バックアップ、デフラグスクリプトの設定ファイルです。
alter_mysql.py
	MySQLのデフラグスクリプトです。
backup_plasticscm.py
	PlasticSCMのバックアップスクリプトです。
	MySQLのデフラグを行ってからバックアップをします。
restore_plasticscm.py
	バックアップしたデータをリストアするスクリプトです。
	引数にリストアするバックアップデータを指定します。
	例) Python ./restore_plasticscm.py plasticscm2013-06-03-16-58.zip

//=================================
// 設定手順
//=================================

・バックアップスクリプトをダウンロード
	git clone git://github.com/achako/backup_plasticscm.git
	masterブランチに切り替える
	git checkout master

・必要なものをインストール
	Python
		//-----------------
		// paramiko
		//-----------------
		sudo apt-get install python-paramiko
		//-----------------
		// MySQLdb
		//-----------------
			wget http://jaist.dl.sourceforge.net/proj...n-1.2.3.tar.gz
			tar xzvf MySQL-python-1.2.3.tar.gz
			Python --version
			sudo aptitude install python*.*-dev
			cd MySQL-python-1.2.3
			vi ./site.sfg
				コメントアウトをはずして書き換える
				mysql_config = /usr/bin/mysql_config
			sudo python setup.py install
	NASに転送する場合
		sudo apt-get install samba
		sudo apt-get install  smbclient
		sudo aptitude -y install sysv-rc-conf    ←smbdの自動起動用
・設定ファイルに必要事項を入力する(設定ファイルの説明参照)
・一定時間ごとにスクリプトを走らせるようにする
	crontab -e    でエディタ立ち上げ
	分	時	日	月	曜日	コマンド
 	*	2 	* 	 *	 1-7	python backup_plasticscm.py
  	↑は毎日2時にスクリプトが走るようになっている
	実行間隔や実行時間は各自で調整
	実行日時の設定は以下のリンクを参照
	http://www.express.nec.co.jp/linux/distributions/knowledge/system/crond.html


//=================================
// setting.ini
//=================================
[backup_attribute]
# PlasticSCMで使用しているデータベースを指定します(現在はMySQLの対応のみです)
database_type=mysql
# PC内のバックアップ先ディレクトリ
# もし、他のPCやファイルサーバーにバックアップする場合は、このディレクトリは一時保存用として使用されます
local_dir=/home/vmrd/backup_tmp
# zipに圧縮したい場合はTrueに、非圧縮の場合はFalseにします(デフォルトはFalse)
compress=True
# バックアップデータの数が指定されたサイズ(MByte)を超えたら半分のデータを削除します
backup_del_size=1000
# バックアップディレクトリ、またはzipファイルの接頭辞です。(デフォルトはplasticscm)
backup_prefix=plasticscm

[log_attribute]
# バックアップログを保存するディレクトリを指定します(デフォルトはスクリプトと同じディレクトリ)
backup_log=./
# バックアップログを保存する数です。保存数を超えたら古いものから自動的に削除されます。
log_save_cnt=5

[email_attribute]
# エラー時に送信する場合はTrue
use_email=False
# 件名
email_subject=
# 差出人のアドレス
email_from=
# 宛先のアドレス
email_to=
# ユーザー名
email_login_user=
# ユーザーのパスワード
email_login_password=
# SMTPサーバー
email_smtp_server=
# SMTPポート番号
email_port=25

# 他のPCにバックアップする場合はこちらを設定します
[remote_backup]
# 他のPCにバックアップを保存する場合はTrueにします。(デフォルトはFalse)
use_remote_backup=False
# 転送先のPCのホスト名です
remote_host=
# 転送先のポート番号です
remote_port=
# 転送先のユーザー名です
remote_user=
# 転送先のユーザーのパスワードです
remote_password=
# 転送先で保存するディレクトリです
remote_dir=

# NASなどのファイルサーバーにsmbclientを使って転送します
[file_server_backup]
# ファイルサーバーにバックアップする場合はTrueにします。
use_file_server=False
# ファイルサーバーのホスト名と共有フォルダ名です
backup_host=
# ファイルサーバーのバックアップ先のディレクトリ名(共有ファイルからのパス)を指定します
backup_dir=
# アクセス制限がある場合はユーザーIDを設定します
backup_user=
# アクセス制限がある場合はユーザーIDのパスワードを設定します
backup_password=

[mysql_user]
# MySQLにログインするためのユーザーです(デフォルトはroot)
username=root
# MySQLにログインするためのパスワードです(デフォルトはroot)
password=root


