"""
Deploys a fresh wordpress install served by nginx + php5-fpm.
Notes:
    -Intended for servers running Ubuntu.
    -Tested on Ubuntu 14.04 LTS.
"""
from fabric.api import env, sudo, run, cd, put
from fabric.contrib.files import exists

env.use_ssh_config = True

# Site name - to be set from command line arg.
env.site_name = None

# Database Constants.
env.db_name = None
env.db_user = None
env.db_user_pwd = None
env.db_root_usr = "root"
env.db_root_pwd = None

# TMP dir on server for downloading, unpacking, etc.
env.TMP_DIR = "/var/tmp/wordpress"

# Wordpress Constants.
env.WORDPRESS_DWNLD_LINK = "http://wordpress.org/latest.tar.gz"

# Nginx
env.nginx_root = "/etc/nginx/"

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
    sudo(PKG_SETUP_CMD.format("php5-mysqlnd-ms"))


def setup_php_fpm():
    """
    Sets up config parameters for phpfpm
    """
    pass


def setup_nginx():
    """
    Sets up nginx to serve wordpress site.
    """
    put(
        "./nginx/sites-available/site_name",
        "%s/sites-available/" % env.nginx_root, use_sudo=True)
    sudo(
        """
        cd {0}/sites-available;
        sed  -i 's/\@\@SITENAME\@\@/{1}/g' site_name
        mv {0}/sites-available/site_name {0}/sites-available/{1}
        """.format(
            env.nginx_root, env.site_name
        )
    )
    if not exists('%s/sites-enabled/%s' % (env.nginx_root, env.site_name)):
        sudo('ln -s {0}/sites-available/{1} {0}/sites-enabled/{1}'.
             format(env.nginx_root, env.site_name))
    sudo("service nginx restart")


def install_mysql():
    """
    Install secure mysql
    """
    sudo(INSTALL_MYSQL.format(env.db_root_pwd))


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


def db_setup(
):
    """
    Sets up
    """
    run(
        """
        yes | mysql -u {0} -p"{1}" -e"CREATE DATABASE IF NOT EXISTS {2}"

        mysql -u {0} -p"{1}" -e\
            "GRANT ALL PRIVILEGES ON {2}.* TO {3}@localhost identified by '{4}'"
        mysql -u {0} -p"{1}" -e"FLUSH PRIVILEGES"
        """.format(
            "root", env.db_root_pwd, env.db_name, env.db_user,
            env.db_user_pwd),
    )


def setenv(**kwargs):
    for key, val in kwargs.items():
        print "Setting env var %s to %s" % (key, val)
        env[key] = val


def setup_wordpress():
    """
    Sets up a clean openmrs install.
    """
    # Teardown and recreate tmp dir.
    run("rm -rf {0}; mkdir -p {0}".format(env.TMP_DIR))
    assert env.site_name
    with cd(env.TMP_DIR):
        run("wget {0}".format(env.WORDPRESS_DWNLD_LINK))
        run("tar xzvf latest.tar.gz")
        run(
            """
            cd ./wordpress
            cp wp-config-sample.php wp-config.php
            sed  -i 's/database_name_here/{0}/g' wp-config.php
            sed  -i 's/username_here/{1}/g' wp-config.php
            sed  -i 's/password_here/{2}/g' wp-config.php
            """.format(
                env.db_name, env.db_user, env.db_user_pwd
            )
        )
        sudo("mkdir -p /var/www/%s" % env.site_name)
        sudo("cp -rf wordpress/* /var/www/%s" % env.site_name)
        sudo("chown -R www-data:www-data /var/www/%s" % env.site_name)


def install_plugin_dropbox_backup():
    """
    Automates the install and server setup for the
    dropbox back up plugin.
    """
    plugin_name = "wordpress-backup-to-dropbox"
    download_link = "https://downloads.wordpress.org/plugin/" +\
        "%s.zip" % plugin_name
    # Install needed packages if not present.
    sudo(PKG_SETUP_CMD.format("curl"))
    sudo(PKG_SETUP_CMD.format("libcurl3"))
    sudo(PKG_SETUP_CMD.format("libcurl3-dev"))
    sudo(PKG_SETUP_CMD.format("php5-curl"))
    with cd(env.TMP_DIR):
        run("rm -rf %s*" % plugin_name)
        run("wget %s" % download_link)
        run("unzip %s.zip" % plugin_name)
        sudo("mkdir -p /var/www/%s/wp-content/backups" % env.site_name)
        sudo("chown www-data /var/www/%s/wp-content/backups" % env.site_name)
        sudo("cp -rf {0} /var/www/{1}/wp-content/plugins".format(
            plugin_name, env.site_name)
        )
        sudo("chgrp -R www-data /var/www/%s/wp-content" %
             env.site_name)
