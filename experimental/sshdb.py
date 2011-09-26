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

import hashlib
import sys
import os
import re
import MySQLdb
import psycopg2
import ConfigParser
pathToConfig = "~/sshkeydb.conf"
config = ConfigParser.RawConfigParser()


class sshdb(object):
        def __init__(self, name="sshdb", \
                    role="admin", \
                    keypath='~/.ssh/id_dsa.pub'):
                self.name = name
                self.role = role
                self.keypath = keypath

        def connectpsql(self, connectingString):
            """
            Returns a connection object or 1 if the connecting fails
            """
            try:
                conn = psycopg2.connect(connectingString)
                return conn
            except psycopg2.OperationalError:
                print("Could not connect to the server"),
                return 1

        def connectMySql(self, connectingString):
            """
            Returns a connection object or 1 if the connecting fails
            """
            mysqldb = MySQLdb.connect(connectingString)
            return mysqldb

        def makeSHA256Hash(self, keypath='~/.ssh/id_rsa.pub'):
            """
            makeSHA256Hash(fileLocation)
            Returns a SHA256 hash of the file and a string as list
            """
            pathToFile = os.path.expanduser(keypath)
            print pathToFile
            hashValue = []
            try:
                keyssh = open(pathToFile, 'r')
                readFile = keyssh.read()
                keychecksum = hashlib.sha256(readFile).hexdigest()
                hashValue.append(keychecksum)
                hashValue.append(readFile)
                return hashValue
            except IOError:
                print("File not found in %s") % pathToFile
                hashValue.append(1)
                return hashValue

        def myQuery(self, users):
                myQuery = \
                "insert into users values('%(key)s', '%(role)s', \
                '%(keySum)s', '%(path)s', '%(realname)s');" % users
                return myQuery

        def insertQuery(conn, queryString):
            """
            Need 2 arguments a connectionobject and a string
            """
            cursor = conn.cursor()
            try:
                cursor.execute(queryString)
                conn.commit()
                return 0
            except psycopg2.IntegrityError:
                return 42
            except:
                return 42

        def getRoles(self, conn, getRole):
            """ Needs a connection object and a role(e.g. admin) """
            cursor = conn.cursor()
            cursor.execute(getRole)
            myresults = cursor.fetchall()
            return myresults

        def hashCheck(self, readFile):
            """
            Expects as argument a string
            Returns a sha256 hash
            """
            keysum = hashlib.sha256(readFile).hexdigest()
            return keysum

        def genList(self):
            """
            Returns a list of keys
            """
            auth = open(os.path.expanduser('~/.ssh/authorized_keys'), 'r')
            n = []
            for i in auth:
                n.append(i)
            auth.close()
            return n

        def isPublicKey(self, keypath):
            """
            Checking the string on the pattern ssh-rsa and
            ssh-dsa on success the function return a zero
            """
            key = open(keypath, 'r')
            readFile = key.read()
            matchkey = \
            re.search('^(ecdsa-sha2-nistp(p256|p384|p521)|ssh-(rsa|dsa))', \
                     readFile)
            if matchkey == None:
                return 1
            else:
                return 0

    def configCheck(self):
        """
        Checks if the configfile ist present
        Returns 1 if not present
        Returns 0 if present
        """
        checkconf = os.path.exists(os.path.expanduser(pathToConfig))
        print checkconf
        if checkconf == False:
            raise File_not_found("File not found"")
            return 1
        else:
            return 0

    def parseConfig(self):
        """
        Returns a connectionstring or
        if the keyword EDITTHIS is found a 1 (postgresql)
        For mysql use the my.cnf file for the connection
        """
        fetchConfig = []
        config.read([os.path.expanduser(pathToConfig)])
        wantedDB = config.get('db', 'wanteddb')
        if wantedDB == 'postgresql':
            databasename = config.get('postgresql', 'database')
            dbuser = config.get('postgresql', 'user')
            dbhost = config.get('postgresql', 'host')
            dbpass = config.get('postgresql', 'password')
            if dbpass == 'EDITTHIS':
                return 1
            dbport = config.get('postgresql', 'port')
            connectingString = "dbname=%s user=%s password=%s host=%s \
            port=%s" % (databasename, dbuser, dbpass, dbhost, dbport)
            fetchConfig.append(wantedDB)
            fetchConfig.append(connectingString)
            return fetchConfig
        if wantedDB == 'mysql':
            fetchConfig.append(wantedDB)
            return fetchConfig

    def createConfigFile(self):
        """ Creates a default config file ~/sshkeydb.conf """
        config = ConfigParser.RawConfigParser()
        config.add_section('db')
        config.set('db', 'wanteddb', 'postgresql')
        config.add_section('postgresql')
        config.set('postgresql', 'database', 'sshkey')
        config.set('postgresql', 'user', os.getenv('USER'))
        config.set('postgresql', 'password', 'EDITTHIS')
        config.set('postgresql', 'host', 'localhost')
        config.set('postgresql', 'port', '5432')
        config.add_section('client')
        config.set('client', 'database', 'sshkey')
        config.set('client', 'user', os.getenv('USER'))
        config.set('client', 'password', 'EDITTHIS')
        config.set('client', 'host', 'localhost')
        try:
            configfile = open(os.path.expanduser(pathToConfig), 'wb')
            config.write(configfile)
            return 0
        except:
            print("Cannot write the defaultconfig")
            return 1
