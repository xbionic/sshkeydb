#!/usr/bin/python

import sshdb

x = sshdb.sshdb()
meh = x.configCheck()
dbstr = x.parseConfig()
hash256 = x.makeSHA256Hash('~/.ssh/id_rsa.pub')

print dbstr
print hash256
print dir(x)
print dir(x.__subclasshook__)
