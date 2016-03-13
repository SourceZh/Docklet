import monitor,cProfile

etcdaddr = "localhost:2379"
clustername = "docklet-vc"
ipaddr = "10.0.2.15"

collector = monitor.Collector(etcdaddr,clustername,ipaddr,True)
cProfile.run("collector.run()")
cProfile.run("collector.collect_osinfo()")
con_collector = monitor.Container_Collector(etcdaddr, clustername,
        ipaddr, 100000, 200,True)
cProfile.run("con_collector.run()")
