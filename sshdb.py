#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 Michael Dierks (michael dierks at gmail dot com)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License version 2
# as published by the Free Software Foundation
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.
#

import ConfigParser
import hashlib
import sys
import os
import psycopg2

def configCheck():
    config = ConfigParser.RawConfigParser()
    checkconf = os.path.exists(os.path.expanduser('~/.sshkeydb.conf'))
    if checkconf == False:
        print "Configfile not found please create a defaultconf"
        return 1
    else:
        return 0
#        config.add_section('postgresql')
#        config.set('postgresql', 'database', 'sshkey')
#        config.set('postgresql', 'user', os.getenv('USER'))
#        config.set('postgresql', 'password', 'EDITTHIS')
#        config.set('postgresql', 'host', 'localhost')
#        config.set('postgresql', 'port', '5432')
#        with open(os.path.expanduser('~/.sshkeydb.conf'), 'wb') as configfile:
#            config.write(configfile)
#        sys.exit("Edit your configfile now")

def parseConfig():
    config = ConfigParser.RawConfigParser()
    config.read([os.path.expanduser('~/.sshkeydb.conf')])
    databasename=config.get('postgresql','database')
    dbuser=config.get('postgresql','user')
    dbhost=config.get('postgresql','host')
    dbpass=config.get('postgresql','password')
    dbport=config.get('postgresql','port')
    if dbpass == 'EDITTHIS':
        return 1
    connectingString = "dbname=%s user=%s password=%s host=%s port=5432" % (databasename, dbuser, dbpass, dbhost)
    return connectingString

def connectDB(connectingString):
        try:
                conn = psycopg2.connect(connectingString);
                return conn 
        except psycopg2.OperationalError:
                print("Could not connect to the server"),
                return 42

def createSHA256(n):
    try:
        keyssh = open(n, 'r')
        readFile=keyssh.read()
        keychecksum = hashlib.sha256(readFile).hexdigest()
        return keychecksum, readFile
    except IOError:
        print("File not found in %s") % n 
        return 1
         
def insertQuery(conn, users):
    # Database stuff if key not exists insert, else close the db-connection and make a clean exit
    cursor = conn.cursor()
    try:
        myQuery = "insert into users values ('%(key)s', '%(role)s', '%(keySum)s', '%(path)s', '%(realname)s')" % users
        cursor.execute(myQuery)
        conn.commit()
        sys.stdout.write("Commited key successful in the database")
        return 0
    except psycopg2.IntegrityError:
        print("SSH-key exists in the database"),
        return 42

def fQuery(conn, getRole):
    cursor = conn.cursor()
    cursor.execute(getRole)
    myresults = cursor.fetchall()
    return myresults

def hashCheck(readFile):
    hashMe = hashlib.sha256(readFile).hexdigest()
    return hashMe

def genList():
    auth = open(os.path.expanduser('~/.ssh/authorized_keys2'), 'ra')
    n=[]
    for i in auth:
        n.append(i)
    auth.close()
    return n

def createConfigFile():
    config = ConfigParser.RawConfigParser()
    config.add_section('postgresql')
    config.set('postgresql', 'database', 'sshkey')
    config.set('postgresql', 'user', os.getenv('USER'))
    config.set('postgresql', 'password', 'EDITTHIS')
    config.set('postgresql', 'host', 'localhost')
    config.set('postgresql', 'port', '5432')
    with open(os.path.expanduser('~/.sshkeydb.conf'), 'wb') as configfile:
        config.write(configfile)
    return 0

if __name__ == '__main__':
        main()
