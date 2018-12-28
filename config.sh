#!/usr/bin/env bash

ORIGIN_SETTINGS_FILE=origin_settings.py
FINAL_SETTINGS_FILE=settings.py

# DB
PARAM_MYSQL_DB_NAME=db_name
PARAM_MYSQL_USER=user_name
PARAM_MYSQL_PASSWORD=password
PARAM_MYSQL_HOST=host

# SMTP
PARAM_SMTP_PASSWORD=password

function config_dev {
    # SMTP
    sed -i -e "s/param_smtp_password/$PARAM_SMTP_PASSWORD/g" $FINAL_SETTINGS_FILE
}

function config_prod {
    # DEBUG
    sed -i -e "s/DEBUG = True/DEBUG = False/g" $FINAL_SETTINGS_FILE
    
    # MYSQL
    sed -i -e "s/param_mysql_db_name/$PARAM_MYSQL_DB_NAME/g" $FINAL_SETTINGS_FILE
    sed -i -e "s/param_mysql_user/$PARAM_MYSQL_USER/g" $FINAL_SETTINGS_FILE
    sed -i -e "s/param_mysql_password/$PARAM_MYSQL_PASSWORD/g" $FINAL_SETTINGS_FILE
    sed -i -e "s/param_mysql_host/$PARAM_MYSQL_HOST/g" $FINAL_SETTINGS_FILE
    
    #SMTP    
    sed -i -e "s/param_smtp_password/$PARAM_SMTP_PASSWORD/g" $FINAL_SETTINGS_FILE
}

cd cs_plus
cp $ORIGIN_SETTINGS_FILE $FINAL_SETTINGS_FILE

mode=$1

case $mode in
    dev)
	config_dev
	;;
    prod)
	config_prod
	;;
    *)
	echo dev/prod
	esac
