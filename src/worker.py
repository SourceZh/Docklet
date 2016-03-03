#!/usr/bin/python3

# first init env
import env, tools
config = env.getenv("CONFIG")
tools.loadenv(config)

# must import logger after initlogging, ugly
from log import initlogging
initlogging("docklet-worker")
from log import logger

import xmlrpc.server, subprocess, os, sys, time
import etcdlib, network, container, imagemgr
import monitor

##################################################################
#                       Worker
# Description : Worker starts at worker node to listen rpc request and complete the work
# Init() :
#      get master ip
#      initialize rpc server
#      register rpc functions
#      initialize network
#      initialize lvm group
# Start() : 
#      register in etcd
#      setup GRE tunnel
#      start rpc service
##################################################################
class Worker(object):
    def __init__(self, etcdclient, addr, port):
        self.addr = addr
        self.port = port
        logger.info ("begin initialize on %s" % self.addr)

        self.fspath = env.getenv('FS_PREFIX')
        self.poolsize = env.getenv('DISKPOOL_SIZE')

        self.etcd = etcdclient
        self.master = self.etcd.getkey("service/master")[1]

        # register self to master
        self.etcd.setkey("machines/runnodes/"+self.addr, "waiting")
        time.sleep(0.1)
        [ status, value ] = self.etcd.getkey("machines/runnodes/"+self.addr)
        if value.startswith("init"):
            # check token to check global directory
            [status, token_1] = self.etcd.getkey("token")
            tokenfile = open(self.fspath+"/global/token", 'r')
            token_2 = tokenfile.readline().strip()
            if token_1 != token_2:
                logger.error("check token failed, global directory is not a shared filesystem")
                sys.exit(1)
        else:
            logger.error ("worker register in machines/runnodes failed, maybe master not start")
            sys.exit(1)
        logger.info ("worker registered in master and checked the token")

        Containers = container.Container(self.addr, etcdclient)
        imgmgr = imagemgr.ImageMgr()
        if value == 'init-new':
            logger.info ("init worker with mode:new")
            # check global directory do not have containers on this worker
            [both, onlylocal, onlyglobal] = Containers.diff_containers()
            if len(both+onlyglobal) > 0:
                logger.error ("mode:new will clean containers recorded in global, please check")
                sys.exit(1)
            [status, info] = Containers.delete_allcontainers()
            if not status:
                logger.error ("delete all containers failed")
                sys.exit(1)
            # create new lvm VG at last
            imgmgr.newvg(self.poolsize,"docklet-group",self.fspath+"/local/docklet-storage")
            #subprocess.call([self.libpath+"/lvmtool.sh", "new", "group", "docklet-group", self.poolsize, self.fspath+"/local/docklet-storage"])
        elif value == 'init-recovery':
            logger.info ("init worker with mode:recovery")
            # recover lvm VG first
            imgmgr.recoveryvg("docklet-group",self.fspath+"/local/docklet-storage")
            #subprocess.call([self.libpath+"/lvmtool.sh", "recover", "group", "docklet-group", self.fspath+"/local/docklet-storage"])
            [status, meg] = Containers.check_allcontainers()
            if status:
                logger.info ("all containers check ok")
            else:
                logger.info ("not all containers check ok")
                sys.exit(1)
        else:
            logger.error ("worker init mode:%s not supported" % value)
            sys.exit(1)
        # initialize rpc
        # xmlrpc.server.SimpleXMLRPCServer(addr) -- addr : (ip-addr, port)
        # if ip-addr is "", it will listen ports of all IPs of this host
        logger.info ("initialize rpcserver %s:%d" % (self.addr, self.port))
        # logRequests=False : not print rpc log
        self.rpcserver = xmlrpc.server.SimpleXMLRPCServer((self.addr, self.port), logRequests=False)
        self.rpcserver.register_introspection_functions()
        self.rpcserver.register_instance(Containers)
        # register functions or instances to server for rpc
        #self.rpcserver.register_function(function_name)

        # initialize the network
        # if worker and master run on the same node, reuse bridges
        #                     don't need to create new bridges
        if (self.addr == self.master):
            logger.info ("master also on this node. reuse master's network")
        else:
            logger.info ("initialize network")
            [status, result] = self.etcd.getkey("network/workbridge")
            if not status:
                logger.error ("get bridge IP failed, please check whether master set bridge IP for worker")
            self.bridgeip = result
            # create bridges for worker
            logger.info ("initialize bridge with ip %s" % self.bridgeip)
            network.netsetup("init", self.bridgeip)
            logger.info ("setup GRE tunnel to master %s" % self.master)
            network.netsetup("gre", self.master)

    # start service of worker
    def start(self):
        self.etcd.setkey("machines/runnodes/"+self.addr, "work")
        # start serving for rpc
        logger.info ("begins to work")
        self.rpcserver.serve_forever()
        
    
if __name__ == '__main__':

    etcdaddr = env.getenv("ETCD")
    logger.info ("using ETCD %s" % etcdaddr )

    clustername = env.getenv("CLUSTER_NAME")
    logger.info ("using CLUSTER_NAME %s" % clustername )

    # get network interface
    net_dev = env.getenv("NETWORK_DEVICE")
    logger.info ("using NETWORK_DEVICE %s" % net_dev )

    ipaddr = network.getip(net_dev)
    if ipaddr==False:
        logger.error("network device is not correct")
        sys.exit(1)
    else:
        logger.info("using ipaddr %s" % ipaddr)
    # init etcdlib client
    try:
        etcdclient = etcdlib.Client(etcdaddr, prefix = clustername)
    except Exception:
        logger.error ("connect etcd failed, maybe etcd address not correct...")
        sys.exit(1)
    else:
        logger.info("etcd connected")
    
    # init collector to collect monitor infomation
    collector = monitor.Collector(etcdaddr,clustername,ipaddr)
    collector.start()

    cpu_quota = env.getenv('CONTAINER_CPU')
    logger.info ("using CONTAINER_CPU %s" % cpu_quota )

    mem_quota = env.getenv('CONTAINER_MEMORY')
    logger.info ("using CONTAINER_MEMORY %s" % mem_quota )

    worker_port = env.getenv('WORKER_PORT')
    logger.info ("using WORKER_PORT %s" % worker_port )

    con_collector = monitor.Container_Collector(etcdaddr,clustername,ipaddr,cpu_quota,mem_quota)
    con_collector.start()
    logger.info("CPU and Memory usage monitor started")

    logger.info("Starting worker")
    worker = Worker(etcdclient, addr = ipaddr, port=worker_port)
    worker.start()
