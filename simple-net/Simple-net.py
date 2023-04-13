#!/usr/bin/env python3
# encoding: utf-8

from seedemu.layers import Base, Routing, Ebgp, Ibgp, Ospf, PeerRelationship, Dnssec
from seedemu.services import WebService, DomainNameService, DomainNameCachingService
from seedemu.services import CymruIpOriginService, ReverseDomainNameService, BgpLookingGlassService
from seedemu.compiler import Docker, Graphviz
from seedemu.hooks import ResolvConfHook
from seedemu.core import Emulator, Service, Binding, Filter
from seedemu.layers import Router
from seedemu.raps import OpenVpnRemoteAccessProvider
from seedemu.utilities import Makers
from typing import List, Tuple, Dict


# Initialize the emulator and layers
emu     = Emulator()
base    = Base()
routing = Routing()
ebgp    = Ebgp()
ibgp    = Ibgp()
ospf    = Ospf()
web     = WebService()
ovpn    = OpenVpnRemoteAccessProvider()

###############################################################################
# Create an Internet Exchange
base.createInternetExchange(100)

###############################################################################
# Create and set up AS-150

# Create an autonomous system 
as150 = base.createAutonomousSystem(150)

# Create a network 
as150.createNetwork('net0')
as150.createNetwork('vlan1', prefix = '155.247.1.0/24')
as150.createNetwork('vlan2', prefix = '155.247.2.0/24')
as150.createNetwork('vlan3', prefix = '155.247.3.0/24')
as150.createNetwork('vlan4', prefix = '155.247.4.0/24')

# Create a router and connect it to two networks
router0 = as150.createRouter('router0').joinNetwork('net0').joinNetwork('ix100')
router0.joinNetwork('vlan1')
router0.joinNetwork('vlan2')
router0.joinNetwork('vlan3')
router0.joinNetwork('vlan4')

# Create a host called web and connect it to a network
as150.createHost('web').joinNetwork('vlan1', address = '155.247.1.10')
as150.createHost('dns').joinNetwork('vlan2', address = '155.247.2.10')
as150.createHost('dbs').joinNetwork('vlan3', address = '155.247.3.10')
as150.createHost('firewall').joinNetwork('vlan4', address = '155.247.4.10')

# Create a web service on virtual node, give it a name
# This will install the web service on this virtual node
web.install('web150')

# Bind the virtual node to a physical node 
emu.addBinding(Binding('web150', filter = Filter(nodeName = 'web', asn = 150)))


# Database server
dbs = as150.getHost('dbs')
dbs.addSoftware('nmap')
dbs.addSoftware('telnet')
dbs.addSoftware('telnetd')
dbs.addSoftware('net-tools')
dbs.addSoftware('mysql-server')
#dbs.addBuildCommand('service mysql stop')
#dbs.addBuildCommand('-d /var/lib/mysql/ mysql')
#dbs.addBuildCommand('service mysql start')


# Firewall server

firewall = as150.getHost('firewall')
firewall.addSoftware('nmap')
firewall.addSoftware('telnet')
firewall.addSoftware('telnetd')
firewall.addSoftware('net-tools')
firewall.addSoftware('iptables')
 
###############################################################################
# Create and set up AS-151
# It is similar to what is done to AS-150

as151 = base.createAutonomousSystem(151)
as151.createNetwork('net1')
as151.createRouter('router1').joinNetwork('net1').joinNetwork('ix100')
as151.createHost('host_root').joinNetwork('net1', address = '10.151.0.10')

###############################################################################
# Create and set up AS-152
# It is similar to what is done to AS-150

as152 = base.createAutonomousSystem(152)
as152.createNetwork('net2')
as152.createRouter('router2').joinNetwork('net2').joinNetwork('ix100')
#as152.createHost('web').joinNetwork('net2')
as152.createHost('host_edu').joinNetwork('net2', address = '10.152.0.10')
as152.createHost('host_issue').joinNetwork('net2', address = '10.152.0.11')
HOSTwithISSUE = as152.getHost('host_issue')


as153 = base.createAutonomousSystem(153)
as153.createNetwork('net3')
as153.createRouter('router3').joinNetwork('net3').joinNetwork('ix100')
as153.createHost('host_temple').joinNetwork('net3', address = '10.153.0.10')

###############################################################################
# Peering these ASes at Internet Exchange IX-100

ebgp.addRsPeer(100, 150)
ebgp.addRsPeer(100, 151)
ebgp.addRsPeer(100, 152)
ebgp.addRsPeer(100, 153)


###############################################################################
# Rendering 

emu.addLayer(base)
emu.addLayer(routing)
emu.addLayer(ebgp)
emu.addLayer(web)


emu.dump('base-component.bin')
emu.render()

###############################################################################
# Compilation

emu.compile(Docker(), './output', override = True)


