""" 
    TTServer.py 

    This library is part of the Zenpacks.community.TokyoTyrant zenpack by
    B Maqueira. It provides "ttyrant" & "ttyrantStats" classes to access 
    ttyrant statistics. It also provides utility classes to handle 
    custom error exceptions.
"""
import sys
import telnetlib

class Error(Exception):
    """ Base Class for my exceptions """
    def __init__(self, value):
        self.msg = value

    def __str__(self):
        return repr(self.msg)

    pass

class ConnectionError(Error):
    def __init__(self, msg):
        self.msg  = msg

class ttyrant(object):
    """ Class to connect to ttyrant """
    def __init__(self, host='localhost', port=1978, timeout=3):
        self.host = host
        self.port = port
        self.timeout = float(timeout)
        self.tn = telnetlib.Telnet()
        self.getStats()

    def getStats(self):
        try:
            self.tn.open(self.host, self.port)
            self.tn.read_until('Escape character is \'^]\'.', self.timeout)
            self.tn.write("stats\n")

            stats = self.tn.read_until('END', self.timeout)
            self.tn.write('quit')
            self.tn.close()
        except Exception, e:
            raise ConnectionError( "Operation failed during connection to %s: %s" % (self.host, e) )
            return
        self.stats = self.parseStats(stats)
        self.tn.close()

    def parseStats(self, stats):
        return ttyrantStats(stats)

    def get(self, statsKey):
        if not statsKey == None:
            return self.stats.get(statsKey)
        else:
            return None

class ttyrantStats(object):
    """ build some ttyrant stats """
    def __init__(self, statsStack):
        self.stats = {'hit_percent':0, 'get_set_ratio':0, 'missed_percent':0}
        for statline in statsStack.split("\n"):
            st = statline.split(' ')
            if len(st) > 1:
                try:
                   self.stats[st[1]] = float(st[2])
                except:
                   self.stats[st[1]] = st[2]

        if self.stats.has_key('cmd_get_hits')\
            and self.stats.has_key('cmd_get')\
            and self.stats['cmd_get'] > 0:
            self.stats['hit_percent'] = 100 * self.stats['cmd_get_hits'] / self.stats['cmd_get']

        if self.stats.has_key('cmd_set')\
            and self.stats.has_key('cmd_get')\
            and self.stats['cmd_set'] > 0:
            self.stats['get_set_ratio'] = self.stats['cmd_get'] / self.stats['cmd_set']

        if self.stats.has_key('cmd_get_misses')\
            and self.stats.has_key('cmd_get')\
            and self.stats['cmd_get'] > 0:
            self.stats['missed_percent'] = 100 * self.stats['cmd_get_misses'] / self.stats['cmd_get']

    def get(self, statKey):
        if self.stats.has_key(statKey):
            return self.stats[statKey]
        else:
            return None

