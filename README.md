wordpress-deploy
==============

Fabric scripts for the semi-automated install and setup of a fresh wordpress 
install served by nginx using fastcgi.

Usage:

    fab -H user@host setup_core db_setup setup_wordpress setup_nginx


To fresh install mysql:

    fab -H user@host --set db_root_pwd=ROOT_PASS install_mysql

To setup wordpress site mysql db:

    fab -H user@host --set db_root_pwd=ROOT_PASS,db_name=SITENAME,\
        db_user=NAME,db_user_pwd=DB_USER_PASS db_setup

Wordpress + nginx setup

    fab -H user@host --set site_name=SITENAME \
        setup_wordpress setup_nginx


To install the dropbox backup plugin:
    
    fab -H user@host install_plugin_dropbox_backup
