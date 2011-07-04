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
import psycopg2
import ConfigParser
import sshdb
import argparse

def main():
    configPresent=sshdb.configCheck()
    if configPresent != 0:
        sys.exit("No configfile found, please use sshdbconfig.py to create a default config")
    # parse config und connect
    connectingString = sshdb.parseConfig()
    if connectingString == 1:
        sys.exit("Please edit your configfile")
    conn = sshdb.connectDB(connectingString)

    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('--role', '-r', dest='role', help='Role of the user (default: admin)', default='admin')
        parser.add_argument('--realname', '-R', dest='realname', help='Name of the key owner', default='')
        args = parser.parse_args()
        theRole=args.role
        theName=args.realname
    except:
        sys.exit("Wrong commandline arguments")
    
    try:
        keyList=sshdb.genList()
        getRole = "select role, realname, keyfile, keypath, checksum from users where role='%s'" % theRole
        cursor = conn.cursor()
        cursor.execute(getRole)
        myresults = cursor.fetchall()
        for key in myresults:
            getKey=key[2]
            try:
                foo=keyList.index(key[2])
            except ValueError:
                keychecksum = hashlib.sha256(getKey).hexdigest()
                if key[4] == keychecksum:
                    print "Checksum ok"
                else:
                    print "Checksum is different"
                    sys.exit("Aborting")
                auth = open(os.path.expanduser('~/.ssh/authorized_keys2'), 'a')
                auth.write(key[2])
                auth.close()
                print "here we go"
            except:
                pass
    except:
        print "Database Error"
    sys.exit()

if __name__ == '__main__':
    main()
