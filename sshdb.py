#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 Michael Dierks (michael dot dierks at gmail dot com)
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
import re


def configCheck():
    """ Checks if the configfile ist present
    Returns 1 if not present
    Returns 0 if present
    """
    config = ConfigParser.RawConfigParser()
    checkconf = os.path.exists(os.path.expanduser('~/.sshkeydb.conf'))
    if checkconf == False:
        print "Configfile not found please create a defaultconf"
        return 1
    else:
        return 0


def parseConfig():
    """
    Returns a connectionstring or
    if the keyword EDITTHIS is found a 1
    """
    config = ConfigParser.RawConfigParser()
    config.read([os.path.expanduser('~/.sshkeydb.conf')])
    databasename = config.get('postgresql', 'database')
    dbuser = config.get('postgresql', 'user')
    dbhost = config.get('postgresql', 'host')
    dbpass = config.get('postgresql', 'password')
    dbport = config.get('postgresql', 'port')
    if dbpass == 'EDITTHIS':
        return 1
    connectingString = "dbname=%s user=%s password=%s host=%s port=5432" % \
    (databasename, dbuser, dbpass, dbhost)
    return connectingString


def connectDB(connectingString):
    """
    Returns a connection object or
    1 if the connecting fails
    """
    try:
        conn = psycopg2.connect(connectingString)
        return conn
    except psycopg2.OperationalError:
        print("Could not connect to the server"),
        return 1


def makeSHA256Hash(n):
    """
    makeSHA256Hash(fileLocation)
    Returns a SHA256 hash of the file and a string
    """
    try:
        keyssh = open(n, 'r')
        readFile = keyssh.read()
        keychecksum = hashlib.sha256(readFile).hexdigest()
        return keychecksum, readFile
    except IOError:
        print("File not found in %s") % n
        return 1


def insertQuery(conn, users):
    """
    Need 2 arguments a connectionobject and a dict
    """
    cursor = conn.cursor()
    try:
        myQuery = \
        "insert into users values('%(key)s', '%(role)s', '%(keySum)s', \
        '%(path)s', '%(realname)s')" % users
        cursor.execute(myQuery)
        conn.commit()
        return 0
    except psycopg2.IntegrityError:
        return 42


def getRoles(conn, getRole):
    """ Needs a connection object and a role(e.g. admin) """
    cursor = conn.cursor()
    cursor.execute(getRole)
    myresults = cursor.fetchall()
    return myresults


def hashCheck(readFile):
    """
    Expects as argument a string
    Returns a sha256 hash
    """
    keysum = hashlib.sha256(readFile).hexdigest()
    return keysum


def genList():
    """
    Returns a list of keys
    """
    auth = open(os.path.expanduser('~/.ssh/authorized_keys'), 'r')
    n = []
    for i in auth:
        n.append(i)
    auth.close()
    return n


def createConfigFile():
    """ Creates a default config file ~/.sshkeydb.conf """
    config = ConfigParser.RawConfigParser()
    config.add_section('postgresql')
    config.set('postgresql', 'database', 'sshkey')
    config.set('postgresql', 'user', os.getenv('USER'))
    config.set('postgresql', 'password', 'EDITTHIS')
    config.set('postgresql', 'host', 'localhost')
    config.set('postgresql', 'port', '5432')
    try:
        with open(os.path.expanduser('~/.sshkeydb.conf'), 'wb') as configfile:
            config.write(configfile)
        return 0
    except:
        print("Cannot write the defaultconfig")
        return 1


def isPublicKey(keypath):
    """
    Checking the string on the pattern ssh-rsa and
    ssh-dsa on success the function return a zero
    """
    key = open(keypath, 'r')
    readFile = key.read()
    matchkey = re.search
    ('^(ecdsa-sha2-nistp(p256|p384|p521)|ssh-(rsa|dsa))', readFile)
    if matchkey == None:
        return 1
    else:
        return 0
