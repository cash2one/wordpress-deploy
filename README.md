wordpress-deploy
==============

Fabric scripts for the semi-automated install and setup of a fresh wordpress 
install served by nginx using fastcgi.

Install core dependencies on server:

    fab -H user@host setup_core

To fresh install mysql:

    fab -H user@host setenv:db_root_pwd=DBROOTPWD install_mysql

To setup wordpress site mysql db:

    fab -H angel@do-small-3 setenv:db_name=DBNAME,db_root_pwd=DBROOTPWD\
        db_user=DBUSER,db_user_pwd=DBPWD db_setup

Wordpress + nginx setup:

    fab -H angel@do-small-3 setenv:db_name=DBNAME,\
        db_user=DBUSER,db_user_pwd=DBPWD,site_name=SITENAME,\
        nginx_root=NGINX_ROOT setup_wordpress setup_nginx
        
with NGINX_ROOT set to where the config files are contained, typically "/etc/nginx/"

To install the dropbox backup plugin:
    
    fab -H user@host setenv:site_name=SITENAME install_plugin_dropbox_backup
