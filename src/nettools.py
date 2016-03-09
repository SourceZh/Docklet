#!/usr/bin/python3

import subprocess

class ipcontrol(object):
    @staticmethod
    def parse(cmdout):
        links = {}
        thislink = None
        for line in cmdout.splitlines():
            # empty line
            if len(line)==0:
                continue
            # Level 1 : first line of one link
            if line[0] != ' ': 
                blocks = line.split()
                thislink = blocks[1].strip(':')
                links[thislink] = {}
                links[thislink]['state'] = blocks[blocks.index('state')+1] if 'state' in blocks else 'UNKNOWN'
                links[thislink]['inet'] = []
            # Level 2 : line with 4 spaces
            elif line[4] != ' ':
                blocks = line.split()
                if blocks[0] == 'inet':
                    links[thislink]['inet'].append(blocks[1])
                # we just need inet (IPv4)
                else:  
                    pass
            # Level 3 or more : no need for us
            else:
                pass
        return links

    @staticmethod
    def list_links():
        try:
            ret = subprocess.run(['ip', 'address'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=False, check=True)
            return iptool.parse(ret.stdout.decode('utf-8'))
        except subprocess.CalledProcessError as suberror:
            print ("list links failed : %s" % suberror.stdout.decode('utf-8'))
            return {}

    @staticmethod
    def get_link(linkname):
        try:
            ret = subprocess.run(['ip', 'address', 'show', str(linkname)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=False, check=True)
            return iptool.parse(ret.stdout.decode('utf-8'))[linkname]
        except subprocess.CalledProcessError as suberror:
            print ("get link info failed : %s" % suberror.stdout.decode('utf-8'))
            return False

    @staticmethod
    def add_addr(linkname, address):
        pass


class ovscontrol(object):
    @staticmethod
    def list_bridges():
        pass


