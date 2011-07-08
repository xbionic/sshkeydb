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

import sys
import os
import hashlib
import ConfigParser
import argparse
import sshdb
import MySQLdb

def main():
    configPresent = sshdb.configCheck()
    if configPresent != 0:
        sys.exit(
        "No configfile found, please use sshdbconfig.py \
        to create a default config")

    # parse config und connect
    connectingString = sshdb.parseConfig()
    whichdb = connectingString[0]
    if whichdb == 1:
        sys.exit("Please edit your configfile")

    if whichdb == 'postgresql':
        conn = sshdb.connectpsql(connectingString[1])

    if whichdb == 'mysql':
        conn = MySQLdb.connect(db="sshkey", read_default_file="~/my.cnf")

    # Searching for the ssh key using the default keys

    try:
        keyExists = os.path.exists(os.path.expanduser('~/.ssh/id_rsa.pub'))
        if keyExists == True:
            keypath = os.path.expanduser('~/.ssh/id_rsa.pub')
    except:
        keyExists = os.path.exists(os.path.expanduser('~/.ssh/id_dsa.pub'))
        if keyExists == True:
            keypath = os.path.expanduser('~/.ssh/id_rsa.pub')
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('--key', '-k', dest='keytossh',
        help='Path to the Key (default: ~/.ssh/id_rsa.pub)', default=keypath)
        parser.add_argument('--role', '-r', dest='role',
        help='Role of the user (default: admin)', default='admin')
        parser.add_argument('--realname', '-R', dest='realname',
        help='Name of the key owner', default='')
        args = parser.parse_args()
        keypath = args.keytossh
        theRole = args.role
        theName = args.realname
    except:
        sys.exit("Wrong commandline arguments")

    checkKey = sshdb.isPublicKey(keypath)

    if checkKey == 0:
        print "Key is OK"
    else:
        sys.exit("Key is no publickey. I am stopping here")

    #Check if the key exists, make a checksum and read it
    hashSHA256 = sshdb.makeSHA256Hash(keypath)
    if hashSHA256[0] == 1:
        sys.stdout.write("Key not found in %s" % keypath)
    users = ({"key": hashSHA256[1], "role": theRole, "keySum": hashSHA256[0], \
    "path": keypath, "realname": theName})
    theQuery = sshdb.myQuery(users)
    queryReturnCode = sshdb.insertQuery(conn, theQuery)
    if queryReturnCode == 0:
        sys.stdout.write("Commited key successful in the database\n")
    elif queryReturnCode == 42:
        sys.stdout.write("SSH-key exists in the database\n")
    conn.close()
    sys.exit("Goodbye")

if __name__ == '__main__':
            main()
