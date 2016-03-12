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
            # Level 2 : line with 4 spaces
            elif line[4] != ' ':
                blocks = line.split()
                if blocks[0] == 'inet':
                    if 'inet' not in links[thislink]:
                        links[thislink]['inet'] = []
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
            ret = subprocess.run(['ip', 'link', 'show'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=False, check=True)
            links = ipcontrol.parse(ret.stdout.decode('utf-8'))
            return [True, list(links.keys())]
        except subprocess.CalledProcessError as suberror:
            return [False, "list links failed : %s" % suberror.stdout.decode('utf-8')]
            
    @staticmethod
    def link_exist(linkname):
        try:
            subprocess.run(['ip', 'link', 'show', 'dev', linkname], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=False, check=True)
            return True
        except subprocess.CalledProcessError:
            return False

    @staticmethod
    def link_info(linkname):
        try:
            ret = subprocess.run(['ip', 'address', 'show', 'dev', str(linkname)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=False, check=True)
            return [True, ipcontrol.parse(ret.stdout.decode('utf-8'))[linkname]]
        except subprocess.CalledProcessError as suberror:
            return [False, "get link info failed : %s" % suberror.stdout.decode('utf-8')]

    @staticmethod
    def link_state(linkname):
        try:
            ret = subprocess.run(['ip', 'link', 'show', 'dev', str(linkname)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=False, check=True)
            return [True, ipcontrol.parse(ret.stdout.decode('utf-8'))[linkname]['state']]
        except subprocess.CalledProcessError as suberror:
            return [False, "get link state failed : %s" % suberror.stdout.decode('utf-8')]

    @staticmethod
    def link_ips(linkname):
        [status, info] = ipcontrol.link_info(linkname)
        if status:
            if 'inet' not in info:
                return [True, []]
            else:
                return [True, info['inet']]
        else:
            return [False, info]

    @staticmethod
    def up_link(linkname):
        try:
            subprocess.run(['ip', 'link', 'set', 'dev', str(linkname), 'up'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=False, check=True)
            return [True, linkname]
        except subprocess.CalledProcessError as suberror:
            return [False, "set link up failed : %s" % suberror.stdout.decode('utf-8')]

    @staticmethod
    def down_link(linkname):
        try:
            subprocess.run(['ip', 'link', 'set', 'dev', str(linkname), 'down'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=False, check=True)
            return [True, linkname]
        except subprocess.CalledProcessError as suberror:
            return [False, "set link down failed : %s" % suberror.stdout.decode('utf-8')]

    @staticmethod
    def add_addr(linkname, address):
        try:
            subprocess.run(['ip', 'address', 'add', address, 'dev', str(linkname)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=False, check=True)
            return [True, linkname]
        except subprocess.CalledProcessError as suberror:
            return [False, "add address failed : %s" % suberror.stdout.decode('utf-8')]

    @staticmethod
    def del_addr(linkname, address):
        try:
            subprocess.run(['ip', 'address', 'del', address, 'dev', str(linkname)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=False, check=True)
            return [True, linkname]
        except subprocess.CalledProcessError as suberror:
            return [False, "delete address failed : %s" % suberror.stdout.decode('utf-8')]


class ovscontrol(object):
    @staticmethod
    def list_bridges():
        pass


