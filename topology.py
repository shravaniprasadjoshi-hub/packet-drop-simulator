#!/usr/bin/env python3
"""
Packet Drop Simulator - Custom Topology
3 hosts connected to 1 switch
"""

from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink

def create_topology():
    # Create network with Remote Controller (POX)
    net = Mininet(
        controller=RemoteController,
        switch=OVSSwitch,
        link=TCLink
    )

    info('*** Adding Controller\n')
    net.addController(
        'c0',
        controller=RemoteController,
        ip='127.0.0.1',
        port=6633
    )

    info('*** Adding Switch\n')
    s1 = net.addSwitch('s1')

    info('*** Adding Hosts\n')
    h1 = net.addHost('h1', ip='10.0.0.1/24')
    h2 = net.addHost('h2', ip='10.0.0.2/24')
    h3 = net.addHost('h3', ip='10.0.0.3/24')

    info('*** Adding Links\n')
    net.addLink(h1, s1)
    net.addLink(h2, s1)
    net.addLink(h3, s1)

    info('*** Starting Network\n')
    net.start()

    info('\n*** Network Ready ***\n')
    info('Hosts: h1=10.0.0.1, h2=10.0.0.2, h3=10.0.0.3\n')
    info('Drop rule: h1 --> h2 is BLOCKED\n')
    info('h1 --> h3 should work normally\n\n')

    CLI(net)

    info('*** Stopping Network\n')
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    create_topology()

