#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import ConfigParser
import sshdb
import argparse

if sys.argv[1] == '':
    myRole = "admin"
else:
    myRole = sys.argv[1]

global myresults


def main():
    configPresent = sshdb.configCheck()
    if configPresent != 0:
        sys.exit("No configfile found, please use \
        sshdbconfig.py to create a default config")
    # parse config und connect
    connectingString = sshdb.parseConfig()
    if connectingString[0] == 1:
        sys.exit("Please edit your configfile")
    if connectingString[0] == 'postgresql':
        conn = sshdb.connectpsql(connectingString[1])
    if connectingString[0] == 'mysql':
        import MySQLdb
        conn = MySQLdb.connect(read_default_file="~/sshkeydb.conf")

    cursor = conn.cursor()
    listall = "select realname, role, keypath, checksum, active from users where role = '%s'" % myRole
    cursor.execute(listall)
    myresults = cursor.fetchall()
    for i in myresults:
        print "Realname: %s" % i[0]
        print "role: %s" % i[1]
        print "keypath: %s" % i[2]
        print "checksum: %s" % i[3]
        print "Active: %s" % i[4]
        print "--------------------------------------------------------------------------"

if __name__ == '__main__':
    main()
