#!/usr/bin/python3

import os, json

from log import logger

def load_service(service):
    if service == '':
        return None
    fileurl = os.environ['DOCKLET_HOME'] + "/conf/services/" + service + ".service"
    #fileurl = "../conf/services/" + service + ".service"
    if not os.path.isfile(fileurl):
        logger.info ("open file %s.service failed" %(service))
        #print ("open file %s.service failed" %(service))
        return None
    servicefile = open(fileurl, 'r')
    serviceconf = json.loads(servicefile.read())
    return serviceconf

def judge_clustersize(services):
    size = 1
    for service in services:
        serviceconf = load_service(service)
        #print (serviceconf)
        if serviceconf == None:
            #logger.info ("can not determine the size of the cluster")
            #print ("can not determine the size of the cluster")
            continue
        else:
            if serviceconf['size'] > size:
                size = serviceconf['size']
            else:
                continue
    return size

def create_command(lxc_name, username, clustername, clusterid, hostname, ip, gateway, vlanid, command):
    command = command.replace('LXC_NAME', lxc_name)
    command = command.replace('USERNAME', username)
    command = command.replace('CLUSTERNAME', clustername)
    command = command.replace('CLUSTERID', clusterid)
    command = command.replace('HOSTNAME', hostname)
    command = command.replace('IP', ip)
    command = command.replace('GATEWAY', gateway)
    command = command.replace('VLANID', vlanid)
    command = command.replace('%', '')
    return command

if __name__ == '__main__':
    print (create_command('lxc_name', 'username', 'clustername', 'clusterid', 'hostname', 'ip', 'gateway', 'vlanid', "/home/start-singlejupyter.sh %USERNAME% %PORT% docklet-jupyter-cookie /workspace/%USERNAME%/%CLUSTERNAME% /jupyter %AUTHURL% %IP%"))
