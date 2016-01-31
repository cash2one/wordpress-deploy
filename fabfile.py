"""
Deploys a fresh wordpress install served by nginx + php5-fpm.
Notes:
    -Intended for servers running Ubuntu.
    -Tested on Ubuntu 14.04LTS.
"""
from fabric.api import env, sudo, run, cd, put

env.use_ssh_config = True

# Site name - to be set from command line arg.
env.SITENAME = None

# Database Constants.
env.db_name = None
env.db_user = None
env.db_user_pwd = None
env.db_root_usr = "root"
env.db_root_pwd = None

# TMP dir on server for downloading, unpacking, etc.
env.TMP_DIR = "/var/tmp/wordpress"

# Wordpress Constants.
env.WORDPRESS_DWNLD_LINK = "wget http://wordpress.org/latest.tar.gz"

# Nginx
env.NGINX_ROOT = "/var/lib/tomcat7"

PKG_SETUP_CMD = \
    """
    PKG_OK=$(dpkg-query -W --showformat='${{Status}}\n' {0} |
        grep "install ok installed");
        if [ "" == "$PKG_OK" ]; then
            echo "No {0}. Setting up {0}."
            apt-get -y update;
            apt-get --force-yes --yes install {0}
        fi
    """

INSTALL_MYSQL = \
    """
    PKG_OK=$(dpkg-query -W --showformat='${{Status}}\n' mysql-server |
        grep "install ok installed");
        if [ "" == "$PKG_OK" ]; then
            echo "Setting up mysql-server.";
            sudo debconf-set-selections <<< \
                'mysql-server mysql-server/root_password password {0}'
            sudo debconf-set-selections <<< \
                'mysql-server mysql-server/root_password_again password {0}'
            sudo apt-get -y install mysql-server
        fi
    """


def setup_core():
    """
    Setups up the core environment for box.
    """
    # build essentials + git
    sudo(PKG_SETUP_CMD.format("build-essential python-dev unzip"))
    sudo(PKG_SETUP_CMD.format("nginx"))
    sudo(PKG_SETUP_CMD.format("php5-gd libssh2-php"))
    sudo(PKG_SETUP_CMD.format("php5-fpm"))


def setup_php_fpm():
    """
    Sets up config parameters for phpfpm
    """
    pass


def setup_nginx():
    """
    Sets up nginx to server wordpress site.
    """
    put
    pass


def install_mysql(db_root_pwd):
    """
    Install secure mysql
    """
    sudo(INSTALL_MYSQL.format(db_root_pwd))


def db(cmd):
    """
    Executes a remote sudo service postgres <cmd>
    """
    sudo("service mysql %s" % cmd)


def db_purge(usr, pwd, db_name):
    """
    WARNING: Drops the database. This is irrecoverable,
    so make sure you have recovery backups in place if you need
    to keep a copy of the data.
    """
    # resart db server to close any outsanding connections to
    # affected db
    db('restart')
    run(
        """
        yes | mysql -u {0} -p"{1}" -e"DROP DATABASE IF EXISTS {2}"
        """.format(
            usr, pwd, db_name),
    )


def db_setup(root_usr, root_pwd, db_name, usr, usr_pwd):
    """
    Sets up
    """
    run(
        """
        yes | mysql -u {0} -p"{1}" -e"CREATE DATABASE {2}"
        mysql -u {0} -p"{1}" -e\
            "CREATE USER {3}@localhost IDENTIFIED BY '{4}'"
        mysql -u {0} -p"{1}" -e\
            "GRANT ALL PRIVILEGES ON {2}.* {3}@localhost"
        mysql -u {0} -p"{1}" -e"FLUSH PRIVILEGES"
        """.format(
            root_usr, root_pwd, db_name, usr, usr_pwd),
    )


def setup_wordpress():
    """
    Sets up a clean openmrs install.
    """
    # Teardown and recreate tmp dir.
    run("rm -rf {0}; mkdir -p {0}".format(env.TMP_DIR))
    with cd(env.TMP_DIR):
        run("wget {0}".format(env.WORDPRESS_DWNLD_LINK))
        run("tar xzvf latest.tar.gz")
        run("cd ./wordpress; cp wp-config-sample.php wp-config.php")
        sudo("cp -rf wordpress /var/www/%s" % env.SITENAME)
        sudo("chown -R www-data /var/www/%s" % env.SITENAME)


def setup_plugin_dropbox_backup():
    """
    Automates the install and server setup for the
    dropbox back up plugin.
    """
    pass


def setup_box(sitename):
    """
    Setups up the env for an wordpress install.
    """
    env.SITENAME = sitename
    setup_core()
    setup_wordpress()
