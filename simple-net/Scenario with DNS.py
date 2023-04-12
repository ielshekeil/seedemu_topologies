#!/usr/bin/env python3
# encoding: utf-8

from seedemu.core import Emulator, Binding, Filter, Action
from seedemu.mergers import DEFAULT_MERGERS
from seedemu.hooks import ResolvConfHook
from seedemu.compiler import Docker
from seedemu.services import DomainNameService, DomainNameCachingService
from seedemu.layers import Base

emuA = Emulator()
emuB = Emulator()

# Load the pre-built components and merge them
emuA.load('../scenario/base-component.bin')
emuB.load('../dns-component/dns-component.bin')
emu = emuA.merge(emuB, DEFAULT_MERGERS)


# Bind the virtual nodes in the DNS infrastructure layer to physical nodes.
# Action.FIRST will look for the first acceptable node that satisfies the filter rule.
# There are several other filters types that are not shown in this example.

emu.addBinding(Binding('a-root-server', filter=Filter(asn=151), action=Action.FIRST))
emu.addBinding(Binding('a-edu-server', filter=Filter(asn=152), action=Action.FIRST))
emu.addBinding(Binding('ns1-temple-edu', filter=Filter(asn=153), action=Action.FIRST))

#####################################################################################
# Create one local DNS server (virtual node) --> Local DNS server = 'dns' with ip addr = 155.247.2.10.
ldns = DomainNameCachingService()
ldns.install('global-dns-1')

# Customize the display name (for visualization purpose)
emu.getVirtualNode('global-dns-1').setDisplayName('Global DNS-1')

base: Base = emu.getLayer('Base')
emu.addBinding(Binding('global-dns-1', filter = Filter(asn=150, nodeName="dns")))
base.getAutonomousSystem(150).setNameServers(['155.247.2.10'])


# Add the ldns layer
emu.addLayer(ldns)

# Dump to a file
emu.dump('base_with_dns.bin')


###############################################
# Render the emulation and further customization
emu.render()


###############################################
# Render the emulation

emu.compile(Docker(), './output', override = True)
