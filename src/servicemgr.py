#!/usr/bin/python3

import os, json
from servicetool import load_service, judge_clustersize
from log import logger

class ServiceMgr(object):
    def __init__(self, servicelist):
        if servicelist == None:
            servicelist = ''
        self.services = servicelist.split(';')
        self.size = judge_clustersize(self.services)
        self.commands = []
        for index in range(0, self.size):
            command = ''
            for service in self.services:
                serviceconf = load_service(service)
                if serviceconf == None:
                    continue
                i = index
                if i > serviceconf['size'] - 1:
                    i = serviceconf['size'] - 1
                command = command + serviceconf['containers'][i]['cmd'] + '\n'
            self.commands.append(command)


    def get_size(self):
        return self.size

    def has_service(self, service):
        return service in self.services

    def get_services(self):
        return self.services

    def get_commands(self):
        return self.commands

    def get_command(self, index):
        return self.commands[index]

if __name__ == '__main__':
    serviceconf = ServiceMgr('ssh')
    print (serviceconf.get_size())
    print (serviceconf.get_services())
    print (serviceconf.get_commands())
