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


