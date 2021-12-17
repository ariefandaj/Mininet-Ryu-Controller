#!/usr/bin/env python

from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSController
from mininet.node import CPULimitedHost, Host, Node
from mininet.node import OVSKernelSwitch, UserSwitch
from mininet.node import IVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink, Intf
from subprocess import call

def myNetwork():

    net = Mininet( topo=None,
                   build=False,
                   ipBase='10.0.0.0/8')

    info( '*** Adding controller\n' )
    c0=net.addController(name='c0',
                      controller=RemoteController,
                      ip='127.0.0.1',
                      protocol='tcp',
                      port=6633)

    info( '*** Add switches\n')
    #s1 = net.addSwitch('s1', ip='10.1.0.1', mac='00:00:00:00:00:11', cls=OVSKernelSwitch)
    #s2 = net.addSwitch('s2', ip='10.1.0.2', mac='00:00:00:00:00:12', cls=OVSKernelSwitch)
    #s3 = net.addSwitch('s3', ip='10.1.0.3', mac='00:00:00:00:00:13', cls=OVSKernelSwitch)
    #s4 = net.addSwitch('s4', ip='10.1.0.4', mac='00:00:00:00:00:14', cls=OVSKernelSwitch)
    #s5 = net.addSwitch('s5', ip='10.1.0.5', mac='00:00:00:00:00:15', cls=OVSKernelSwitch)
    #s6 = net.addSwitch('s6', ip='10.1.0.6', mac='00:00:00:00:00:16', cls=OVSKernelSwitch)
    #s7 = net.addSwitch('s7', ip='10.1.0.7', mac='00:00:00:00:00:17', cls=OVSKernelSwitch)
    #s8 = net.addSwitch('s8', ip='10.1.0.8', mac='00:00:00:00:00:18', cls=OVSKernelSwitch)
    #s9 = net.addSwitch('s9', ip='10.1.0.9', mac='00:00:00:00:00:19', cls=OVSKernelSwitch)

    s1 = net.addSwitch('s1', cls=OVSKernelSwitch)
    s2 = net.addSwitch('s2', cls=OVSKernelSwitch)
    s3 = net.addSwitch('s3', cls=OVSKernelSwitch)
    s4 = net.addSwitch('s4', cls=OVSKernelSwitch)
    s5 = net.addSwitch('s5', cls=OVSKernelSwitch)
    s6 = net.addSwitch('s6', cls=OVSKernelSwitch)
    s7 = net.addSwitch('s7', cls=OVSKernelSwitch)
    s8 = net.addSwitch('s8', cls=OVSKernelSwitch)
    s9 = net.addSwitch('s9', cls=OVSKernelSwitch)
    
    info( '*** Add hosts\n')
    h1 = net.addHost('h1', cls=Host, ip='10.0.0.1', mac='00:00:00:00:00:01', defaultRoute=None)
    #h2 = net.addHost('h2', cls=Host, ip='10.0.0.2', mac='00:00:00:00:00:02', defaultRoute=None)
    #h3 = net.addHost('h3', cls=Host, ip='10.0.0.3', mac='00:00:00:00:00:03', defaultRoute=None)
    #h4 = net.addHost('h4', cls=Host, ip='10.0.0.4', mac='00:00:00:00:00:04', defaultRoute=None)
    #h5 = net.addHost('h5', cls=Host, ip='10.0.0.5', mac='00:00:00:00:00:05', defaultRoute=None)
    #h6 = net.addHost('h6', cls=Host, ip='10.0.0.6', mac='00:00:00:00:00:06', defaultRoute=None)
    #h7 = net.addHost('h7', cls=Host, ip='10.0.0.7', mac='00:00:00:00:00:07', defaultRoute=None)
    #h8 = net.addHost('h8', cls=Host, ip='10.0.0.8', mac='00:00:00:00:00:08', defaultRoute=None)
    h9 = net.addHost('h9', cls=Host, ip='10.0.0.9', mac='00:00:00:00:00:09', defaultRoute=None)


    info( '*** Add links\n')
    net.addLink(s1, s3)
    net.addLink(s1, s2)
    net.addLink(s2, s5)
    net.addLink(s3, s4)
    net.addLink(s4, s5)
    net.addLink(s3, s5)
    net.addLink(s5, s6)
    net.addLink(s4, s6)
    net.addLink(s6, s8)
    net.addLink(s6, s7)
    net.addLink(s6, s9)
    #net.addLink(h7, s7)
    #net.addLink(h8, s8)
    net.addLink(h9, s9)
    #net.addLink(h6, s6)
    #net.addLink(h5, s5)
    #net.addLink(h4, s4)
    #net.addLink(h2, s2)
    net.addLink(h1, s1)
    #net.addLink(h3, s3)

    info( '*** Starting network\n')
    net.build()
    info( '*** Starting controllers\n')
    for controller in net.controllers:
        controller.start()

    info( '*** Starting switches\n')
    net.get('s1').start([c0])
    net.get('s2').start([c0])
    net.get('s3').start([c0])
    net.get('s4').start([c0])
    net.get('s5').start([c0])
    net.get('s6').start([c0])
    net.get('s7').start([c0])
    net.get('s8').start([c0])
    net.get('s9').start([c0])

    info( '*** Post configure switches and hosts\n')

    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    myNetwork()

