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

[mysql_user]
# MySQLにログインするためのユーザーです(デフォルトはroot)
username=plastic
# MySQLにログインするためのパスワードです(デフォルトはroot)
password=plastic


