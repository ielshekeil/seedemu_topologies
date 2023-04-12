#!/usr/bin/env python3
# encoding: utf-8

from seedemu.layers import Base, Routing, Ebgp, PeerRelationship, Ibgp, Ospf
from seedemu.services import WebService
from seedemu.core import Emulator, Binding, Filter
from seedemu.raps import OpenVpnRemoteAccessProvider
from seedemu.compiler import Docker

emu     = Emulator()
base    = Base()
routing = Routing()
ebgp    = Ebgp()
ibgp    = Ibgp()
ospf    = Ospf()
"""
web     = WebService()
ovpn    = OpenVpnRemoteAccessProvider()
"""
###############################################################################
# core network (AS-100)
as100 = base.createAutonomousSystem(100)
as100_net0 = as100.createNetwork('net0')

# Create 4 routers: r1 and r4
as100_r1 = as100.createRouter('r1')
as100_r1.joinNetwork('net0')

as100_r2 = as100.createRouter('r2')
as100_r2.joinNetwork('net0')

as100_r3 = as100.createRouter('r3')
as100_r3.joinNetwork('net0')

as100_r4 = as100.createRouter('r4')
as100_r4.joinNetwork('net0')

###############################################################################
# AS-201 # large data center
as201      = base.createAutonomousSystem(201)  
as201_net0 = as201.createNetwork('net-201-0', '10.0.0.0/24')
as201_net1 = as201.createNetwork('net-201-1', '10.0.1.0/24')

as201_r1   = as201.createRouter('r1')
as201_r2   = as201.createRouter('r2')

as201_r1.joinNetwork('net-201-0')
as201_r1.joinNetwork('net-201-1')
as201_r2.joinNetwork('net-201-0')
as201_r2.joinNetwork('net-201-1')
###############################################################################
# AS-202    # large office, headquarter OR another data center
as202      = base.createAutonomousSystem(202)  
as202_net0 = as202.createNetwork('net-202-0', '10.0.2.0/24')
as202_net1 = as202.createNetwork('net-202-1', '10.0.3.0/24')

as202_r1   = as202.createRouter('r1')
as202_r2   = as202.createRouter('r2')

as202_r1.joinNetwork('net-202-0')
as202_r1.joinNetwork('net-202-1')
as202_r2.joinNetwork('net-202-0')
as202_r2.joinNetwork('net-202-1')

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
as204_r1.crossConnect(100, 'r4', '10.50.0.43/29')
as100_r4.crossConnect(204, 'r1', '10.50.0.44/29')

# as205_r1 to as100_r3
as100_r4.crossConnect(205, 'r1', '10.50.0.50/29')
as205_r1.crossConnect(100, 'r4', '10.50.0.51/29')

###############################################################################
# BGP peering

ebgp.addCrossConnectPeering(100, 201, PeerRelationship.Provider)
ebgp.addCrossConnectPeering(100, 202, PeerRelationship.Provider)
ebgp.addCrossConnectPeering(100, 203, PeerRelationship.Provider)
ebgp.addCrossConnectPeering(100, 204, PeerRelationship.Provider)
ebgp.addCrossConnectPeering(100, 205, PeerRelationship.Provider)


###############################################################################
# Create hosts in each network

as201_h1 = as201.createHost('host1')
as201_h1.joinNetwork('net-201-0')
as201_h2 = as201.createHost('host2')
as201_h2.joinNetwork('net-201-1')
as202_h1 = as202.createHost('host3')
as202_h1.joinNetwork('net-202-0')
as202_h2 = as202.createHost('host4')
as202_h2.joinNetwork('net-202-1')
as203_h1 = as203.createHost('host5')
as203_h1.joinNetwork('net-203-0')
as204_h1 = as204.createHost('host6')
as204_h1.joinNetwork('net-204-0')
as204_h2 = as204.createHost('host7')
as204_h2.joinNetwork('net-204-1')
as205_h1 = as205.createHost('host8')
as205_h1.joinNetwork('net-205-0')


###############################################################################
# Rendering

emu.addLayer(base)
emu.addLayer(routing)
emu.addLayer(ebgp)
emu.addLayer(ibgp)
emu.addLayer(ospf)
#emu.addLayer(web)

emu.render()

###############################################################################
# Compilation

emu.compile(Docker(), './output')
