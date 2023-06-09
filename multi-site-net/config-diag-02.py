#!../.venv/bin/python3
# encoding: utf-8

from seedemu.layers import Base, Routing, Ebgp, PeerRelationship, Ibgp, Ospf
from seedemu.services import WebService
from seedemu.core import Emulator, Binding, Filter
from seedemu.compiler import Docker

emu     = Emulator()
base    = Base()
routing = Routing()
ebgp    = Ebgp()
ibgp    = Ibgp()
ospf    = Ospf()
web     = WebService()


# Define the function to generate keepalived.conf content
def generate_keepalived_conf(state, interface, virtual_router_id, priority, virtual_ip):
    return f"""vrrp_instance VI_{virtual_ip} {{
    state {state}
    interface {interface}
    virtual_router_id {virtual_router_id}
    priority {priority}
    advert_int 1
    virtual_ipaddress {{
        {virtual_ip}
    }}
}}

"""


def add_software(h,sw=[]):
    # 'mysql-server'
    # 'iptables'
    default_software = ['nmap','telnet','telnetd','net-tools', 'traceroute']
    for s in default_software + sw:
        h.addSoftware(s)


###############################################################################
# core network (AS-100)
as100 = base.createAutonomousSystem(100)
as100_net0 = as100.createNetwork('net0')

# Create 4 routers: r1 and r4
as100_r1 = as100.createRouter('r1').joinNetwork('net0')
as100_r2 = as100.createRouter('r2').joinNetwork('net0')
as100_r3 = as100.createRouter('r3').joinNetwork('net0')
as100_r4 = as100.createRouter('r4').joinNetwork('net0')

###############################################################################
# AS-201 # large data center
as201      = base.createAutonomousSystem(201)  
as201_net0 = as201.createNetwork('net-201-0', '10.0.0.0/24')
as201_net1 = as201.createNetwork('net-201-1', '10.0.1.0/24')

as201_r1   = as201.createRouter('r1')
add_software(as201_r1)
add_software(as201_r1, ['keepalived']) #, 'iptables'])

as201_r2   = as201.createRouter('r2')
add_software(as201_r2)
add_software(as201_r2, ['keepalived']) #, 'iptables'])

as201_r1.joinNetwork('net-201-0', "10.0.0.2")
as201_r1.joinNetwork('net-201-1', "10.0.1.2")
as201_r2.joinNetwork('net-201-0', "10.0.0.3")
as201_r2.joinNetwork('net-201-1', "10.0.1.3")

# Generate keepalived.conf content for each router
r1_conf  = generate_keepalived_conf("MASTER", "net-201-0", 51, 200, "10.0.0.1/24")
r2_conf  = generate_keepalived_conf("BACKUP", "net-201-0", 51, 100, "10.0.0.1/24")
r1_conf += generate_keepalived_conf("MASTER", "net-201-1", 52, 200, "10.0.1.1/24")
r2_conf += generate_keepalived_conf("BACKUP", "net-201-1", 52, 100, "10.0.1.1/24")

as201_r1.setFile(content=r1_conf, path="/etc/keepalived/keepalived.conf")
as201_r2.setFile(content=r2_conf, path="/etc/keepalived/keepalived.conf")


###############################################################################
# AS-202    # large office, headquarter OR another data center
as202      = base.createAutonomousSystem(202)  
as202_net0 = as202.createNetwork('net-202-0', '10.0.2.0/24')
as202_net1 = as202.createNetwork('net-202-1', '10.0.3.0/24')

as202_r1   = as202.createRouter('r1')
add_software(as202_r1)
add_software(as202_r1, ['keepalived']) #, 'iptables'])

as202_r2   = as202.createRouter('r2')
add_software(as202_r2)
add_software(as202_r2, ['keepalived']) #, 'iptables'])

as202_r1.joinNetwork('net-202-0', "10.0.2.2")
as202_r1.joinNetwork('net-202-1', "10.0.3.2")
as202_r2.joinNetwork('net-202-0', "10.0.2.3")
as202_r2.joinNetwork('net-202-1', "10.0.3.3")

# Generate keepalived.conf content for each router
r1_202_conf  = generate_keepalived_conf("MASTER", "net-202-0", 53, 200, "10.0.2.1/24")
r2_202_conf  = generate_keepalived_conf("BACKUP", "net-202-0", 53, 100, "10.0.2.1/24")
r1_202_conf += generate_keepalived_conf("MASTER", "net-202-1", 54, 200, "10.0.3.1/24")
r2_202_conf += generate_keepalived_conf("BACKUP", "net-202-1", 54, 100, "10.0.3.1/24")

as202_r1.setFile(content=r1_202_conf, path="/etc/keepalived/keepalived.conf")
as202_r2.setFile(content=r2_202_conf, path="/etc/keepalived/keepalived.conf")

###############################################################################
# AS-203
as203      = base.createAutonomousSystem(203)  # remote office 1
as203_net0 = as203.createNetwork('net-203-0', '10.1.1.0/24')

as203_r1   = as203.createRouter('r1').joinNetwork('net-203-0')

###############################################################################
# AS-204
as204      = base.createAutonomousSystem(204)  # remote office 2
as204_net0 = as204.createNetwork('net-204-0', '10.1.2.0/24')
as204_net1 = as204.createNetwork('net-204-1', '10.1.3.0/24')
as204_r1   = as204.createRouter('r1')
as204_r1.joinNetwork('net-204-0')
as204_r1.joinNetwork('net-204-1')

###############################################################################
# AS-205
as205      = base.createAutonomousSystem(205)  # remote office 3
as205_net0 = as205.createNetwork('net-205-0', '10.1.4.0/24')
as205_r1   = as205.createRouter('r1')
as205_r1.joinNetwork('net-205-0')

###############################################################################
# Inter AS cross connect

# as201_r1 to as100_r1
as201_r1.crossConnect(100, 'r1', '10.50.1.2/29')
as100_r1.crossConnect(201, 'r1', '10.50.1.3/29')

# as201_r2 to as100_r2
as201_r2.crossConnect(100, 'r2', '10.50.0.2/29')
as100_r2.crossConnect(201, 'r2', '10.50.0.3/29')

# as202_r1 to as100_r1
as202_r1.crossConnect(100, 'r1', '10.50.0.10/29')
as100_r1.crossConnect(202, 'r1', '10.50.0.11/29')

# as202_r2 to as100_r2
as202_r2.crossConnect(100, 'r2', '10.50.0.18/29')
as100_r2.crossConnect(202, 'r2', '10.50.0.19/29')

# as203_r1 to as100_r3
as203_r1.crossConnect(100, 'r3', '10.50.0.26/29')
as100_r3.crossConnect(203, 'r1', '10.50.0.27/29')

# as204_r1 to as100_r3
as204_r1.crossConnect(100, 'r3', '10.50.0.34/29')
as100_r3.crossConnect(204, 'r1', '10.50.0.35/29')

# as204_r1 to as100_r4
as204_r1.crossConnect(100, 'r4', '10.50.1.34/29')
as100_r4.crossConnect(204, 'r1', '10.50.1.35/29')

# as205_r1 to as100_r3
as205_r1.crossConnect(100, 'r4', '10.50.0.50/29')
as100_r4.crossConnect(205, 'r1', '10.50.0.51/29')

###############################################################################
# BGP peering

ebgp.addCrossConnectPeering(100, 201, PeerRelationship.Unfiltered) # Provider)
ebgp.addCrossConnectPeering(100, 202, PeerRelationship.Unfiltered) # Provider)
ebgp.addCrossConnectPeering(100, 203, PeerRelationship.Unfiltered) # Provider)
ebgp.addCrossConnectPeering(100, 204, PeerRelationship.Unfiltered) # Provider)
ebgp.addCrossConnectPeering(100, 205, PeerRelationship.Unfiltered) # Provider)


###############################################################################
# Create hosts in each network

as201_h1 = as201.createHost('web').joinNetwork('net-201-0')
add_software(as201_h1)
as201_h2 = as201.createHost('dbs').joinNetwork('net-201-1')
add_software(as201_h2, ['mysql-server'])

web.install('web201')
emu.addBinding(Binding('web201', filter = Filter (nodeName='web', asn=201)))

as202_h1 = as202.createHost('host3').joinNetwork('net-202-0')
add_software(as202_h1)

as202_h2 = as202.createHost('host4').joinNetwork('net-202-1')
add_software(as202_h2)

as203_h1 = as203.createHost('host5').joinNetwork('net-203-0')
add_software(as203_h1)

as204_h1 = as204.createHost('host6').joinNetwork('net-204-0')
add_software(as204_h1)

as204_h2 = as204.createHost('host7').joinNetwork('net-204-1')
add_software(as204_h2)

as205_h1 = as205.createHost('host8').joinNetwork('net-205-0')
add_software(as205_h1)


as201_h1.appendStartCommand('route delete default gw 10.0.0.2 net-201-0')
as201_h1.appendStartCommand('route add default gw 10.0.0.1 net-201-0')
as201_h2.appendStartCommand('route delete default gw 10.0.1.2 net-201-0')
as201_h2.appendStartCommand('route add default gw 10.0.1.1 net-201-0')
as202_r1.appendStartCommand('/etc/init.d/keepalived start')
as202_r2.appendStartCommand('/etc/init.d/keepalived start')

###############################################################################
# Rendering

emu.addLayer(base)
emu.addLayer(routing)
emu.addLayer(ebgp)
emu.addLayer(ibgp)
emu.addLayer(ospf)
emu.addLayer(web)

emu.render()

###############################################################################
# Compilation

emu.compile(Docker(), './output')
