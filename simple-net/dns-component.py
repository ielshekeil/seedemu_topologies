#!/usr/bin/env python3
# encoding: utf-8

from seedemu.core import Emulator
from seedemu.services import DomainNameService, DomainNameCachingService

emu = Emulator()

###########################################################
# Create a DNS layer
dns = DomainNameService()
dns.install('a-root-server').addZone('.')
dns.install('a-edu-server').addZone('edu.')
dns.install('ns1-temple-edu').addZone('temple.edu.')

dns.getZone('temple.edu.').addRecord('app1 A 155.247.1.11') 
dns.getZone('temple.edu.').addRecord('app2 A 155.247.1.12') 

# Customize the display names (for visualization purpose)
emu.getVirtualNode('a-root-server').setDisplayName('Root-A')
emu.getVirtualNode('a-edu-server').setDisplayName('EDU')
emu.getVirtualNode('ns1-temple-edu').setDisplayName('temple.edu')

###########################################################
emu.addLayer(dns)
emu.dump('dns-component.bin')