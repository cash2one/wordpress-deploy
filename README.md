wordpress-deploy
==============

Fabric scripts for the semi-automated install and setup of a fresh wordpress 
install served by nginx using fastcgi.

Usage:

    fab -H user@host setup_core db_setup setup_wordpress setup_nginx


To install the dropbox backup plugin:
    
    fab -H user@host install_plugin_dropbox_backup
