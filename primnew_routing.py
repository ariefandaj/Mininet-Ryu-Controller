from ryu.lib import hub
#from collector import Collector
from random import randint
from ryu.base import app_manager
from ryu.controller import mac_to_port
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER
from ryu.controller.handler import MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.mac import haddr_to_bin
from ryu.lib.packet import ipv6
from ryu.lib.packet import arp
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ether_types
from ryu.topology import api as ryu_api
from ryu.topology.event import EventLinkAdd, EventLinkDelete
import networkx as nx
import link_cost
import pause
import time
from mst import *
from shortestpath import *
indikator = 1
isCalc = 1
start_time2 = time.time()
_src_ip = ''
_dst_ip = ''
_src_host = ''
_dst_host = ''
_parser = ''
_isFirstRun = True


class RouteApp(app_manager.RyuApp):

    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(RouteApp, self).__init__(*args, **kwargs)
        self.mac_to_port = {}
        self.mymac = {}
        self.thread = {}
        self.thread['update'] = hub.spawn_after(11, self._stat_request)

     # method untuk menambahkan flow
    def add_flow(self, datapath, match, actions, priority=1, buffer_id=None):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
                                    priority=priority, match=match,
                                    instructions=inst)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                    match=match, instructions=inst)
        datapath.send_msg(mod)

    # method untuk mencari host
    def find_host(self, mac_addr):
        hosts = ryu_api.get_all_host(self)
        for host in hosts:
            if host.mac == mac_addr:
                return host

        return None
    # method untuk melakukan flooding apabila host yang dituju tidak diketahui

    def flood_packet(self, dp, msg):
        ofproto = dp.ofproto
        out_port = ofproto.OFPP_FLOOD
        actions = [dp.ofproto_parser.OFPActionOutput(out_port)]
        data = None

        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        out = dp.ofproto_parser.OFPPacketOut(
            datapath=dp, buffer_id=msg.buffer_id, in_port=msg.in_port,
            actions=actions, data=data)
        dp.send_msg(out)

    # method untuk mendapatkan seluruh link yang ada di dalam topologi
    def get_all_links(self):

        # menggunakan modul dari ryu untuk mendapatkan link atara setiap node
        all_links = ryu_api.get_all_link(self)
        result = []
        for link in all_links:

            src = '{}.{}'.format(link.src.dpid, link.src.port_no)
            dst = '{}.{}'.format(link.dst.dpid, link.dst.port_no)

            # membaca cost dari inputan manual
            cst = link_cost.data_link_cost(link.src.dpid, link.dst.dpid)

            # memasukkan cost kedalam weight dari link
            result.append(
                (src, dst, {'weight': cst}))

        # membuat link berdasarkan port dan datapath dari switch
        all_switches = ryu_api.get_all_switch(self)
        link_to_add = []

        for switch in all_switches:
            ports = switch.ports

            for port in ports:
                for _port in ports:
                    if port != _port:
                        src = '{}.{}'.format(port.dpid, port.port_no)
                        dst = '{}.{}'.format(_port.dpid, _port.port_no)
                        # mengisi weight untuk internal link switch dengan 0
                        link_to_add.append((src, dst, {'weight': 0}))

        # link antar node dan internal switch kemudian dikombinasikan
        result.extend(link_to_add)

        return result

    # method untuk menghitung jarak terpendek
    def cal_shortest_path(self, src_host, dst_host):
        src_port = src_host.port
        dst_port = dst_host.port

        all_links = self.get_all_links()
        self.logger.info("[all link]")
        self.logger.info(all_links)
        self.logger.info('')

        # Graph dari seluruh link dibuat
        
        #mencari mst menggunakan algoritma prim
        mst = prim(all_links)
        #mst = prim2()
        self.logger.info("MST (algorithm = prim)")
        self.logger.info(mst)
        self.logger.info('-----------------------------------')

        src = '{}.{}'.format(src_port.dpid, src_port.port_no)
        dst = '{}.{}'.format(dst_port.dpid, dst_port.port_no)
        self.logger.info("[src]{} [dst]{}".format(dst, src))
        rute = []

        # self.logger.info('[has path?] {}'.format(nx.has_path(graph, src, dst)))
        graph=nx.Graph()
        graph.add_edges_from(mst)
        self.logger.info('[has path?] {}'.format(nx.has_path(graph, src, dst)))
        if nx.has_path(graph, src, dst):
            global isCalc
            # Mencari rute terpendek dari hasil mst prim
            if isCalc == 1:

                global start_time2
                start_time2 = time.time()
                isCalc += 1

                # mengambil path terpendek dengan menggunakan modul yang ada di networkx
                dist, path = short_path(graph, src, dst, weight='weight')
                
                self.logger.info("Total cost : {}".format(dist))
                
                
                # mengembalikan jalur terpendek
                return (path)
        return None

    # method untuk mendapatkan datapath
    def get_dp(self, dpid):
        switch = ryu_api.get_switch(self, dpid)[0]
        return switch.dp

    # method untuk mengirimkan packet out
    def packet_out(self, dp, msg, out_port):
        ofproto = dp.ofproto
        actions = [dp.ofproto_parser.OFPActionOutput(out_port)]
        data = None

        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        out = dp.ofproto_parser.OFPPacketOut(
            datapath=dp, buffer_id=msg.buffer_id, in_port=msg.in_port,
            actions=actions, data=data)
        dp.send_msg(out)

    # method untuk menginstall jalur berdasarkan jalur yang sudah dicari
    def install_path(self, parser, src_ip, dst_ip, path):
        global _isFirstRun
        match_ip = parser.OFPMatch(
            eth_type=ether_types.ETH_TYPE_IP,
            ipv4_src=src_ip,
            ipv4_dst=dst_ip
        )
        match_arp = parser.OFPMatch(
            eth_type=ether_types.ETH_TYPE_ARP,
            arp_spa=src_ip,
            arp_tpa=dst_ip
        )
        for node in path:
            dpid = int(node.split('.')[0])
            port_no = int(node.split('.')[1])
            # print src_ip, "->", dst_ip, "via ", dpid, " out_port=", port_no
            dp = self.get_dp(dpid)
            actions = [dp.ofproto_parser.OFPActionOutput(port_no)]
            self.add_flow(dp, match_ip, actions)
            self.add_flow(dp, match_arp, actions)
        self.installing = False

        if(_isFirstRun):
            _isFirstRun = False

    #method yang dijalankan ketika ada link baru ditambahkan
    @set_ev_cls(EventLinkAdd, MAIN_DISPATCHER)
    def link_addhandler(self, ev):
        start = time.time()
        self.logger.info('%s', ev)
        switches = ryu_api.get_all_switch(self)
        for switch in switches:
            [self.remove_flows(switch.dp, n) for n in [0, 1]]
            self.install_controller(switch.dp)

        #mengecek apakah program baru pertama kali dijakan, jika tidak maka recovery akan dijalankan
        if(_isFirstRun == False):

            parser = _parser
            
            #mencari jarak terdekat 
            shortest_path = self.cal_shortest_path(
                _src_host, _dst_host)

            self.logger.info(
                "---------------------- Recovery Start ---------------------")
            self.logger.info(shortest_path)
            #mencari jarak terdekat 
            self.install_path(
                parser, _src_ip, _dst_ip, shortest_path[1::2])

            # membuat reverse path bagi packet
            reverse_path = list(reversed(shortest_path))
            self.install_path(
                parser, _dst_ip, _src_ip, reverse_path[1::2])
            self.logger.info(reverse_path)
            self.logger.info("Recovery Time " + (time.time() - start).__str__())
            self.logger.info(
                "---------------------- Recovery End---------------------")
    #method yang dijalankan ketika ada link yang hilang
    @set_ev_cls(EventLinkDelete, MAIN_DISPATCHER)
    def link_deletehandler(self, ev):
        start = time.time()
        self.logger.info('%s', ev)

        switches = ryu_api.get_all_switch(self)
        for switch in switches:
            [self.remove_flows(switch.dp, n) for n in [0, 1]]
            self.install_controller(switch.dp)

        if(_isFirstRun == False):

            parser = _parser
            shortest_path = self.cal_shortest_path(
                _src_host, _dst_host)

            self.logger.info(
                "---------------------- Recovery Start ---------------------")
            self.logger.info(shortest_path)
            self.install_path(
                parser, _src_ip, _dst_ip, shortest_path[1::2])

            # membuat reverse path bagi packet
            reverse_path = list(reversed(shortest_path))
            self.install_path(
                parser, _dst_ip, _src_ip, reverse_path[1::2])
            self.logger.info(reverse_path)
            self.logger.info("Recovery Time " + (time.time() - start).__str__())
            self.logger.info(
                "---------------------- Recovery End---------------------")

    def remove_flows(self, datapath, table_id):
        global indikator
        global start_time2
        global isCalc
        isCalc = 1
        indikator = 1
        start_time2 = time.time()
        parser = datapath.ofproto_parser
        ofproto = datapath.ofproto
        empty_match = parser.OFPMatch()
        instructions = []
        flow_mod = self.remove_table_flows(datapath, table_id,
                                           empty_match, instructions)
        # print "deleting all flow entries in table ", table_id
        datapath.send_msg(flow_mod)

    def remove_table_flows(self, datapath, table_id, match, instructions):

        ofproto = datapath.ofproto
        flow_mod = datapath.ofproto_parser.OFPFlowMod(datapath, 0, 0, table_id,
                                                      ofproto.OFPFC_DELETE, 0, 0,
                                                      1,
                                                      ofproto.OFPCML_NO_BUFFER,
                                                      ofproto.OFPP_ANY,
                                                      ofproto.OFPG_ANY, 0,
                                                      match, instructions)
        return flow_mod

    def install_controller(self, datapath):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
        mod = datapath.ofproto_parser.OFPFlowMod(
            datapath=datapath, match=match, cookie=0,
            command=ofproto.OFPFC_ADD, idle_timeout=0, hard_timeout=0,
            priority=0, instructions=inst)
        datapath.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        self.install_controller(datapath)

    # method yang dipanggil ketika packet_in
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):

        start_time = time.time()

        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)
        arp_pkt = pkt.get_protocol(arp.arp)
        ipv6_pkt = pkt.get_protocol(ipv6.ipv6)

        # avoid broadcast from LLDP
        if eth.ethertype == 35020:
            return

        if ipv6_pkt:  # Drop the IPV6 Packets.
            match = parser.OFPMatch(eth_type=eth.ethertype)
            actions = []
            self.add_flow(datapath, match, actions)
            return None

        dst = eth.dst
        src = eth.src
        dpid = datapath.id

        self.mac_to_port.setdefault(dpid, {})

        self.mac_to_port[dpid][src] = in_port

        if src not in self.mymac.keys():
            self.mymac[src] = (dpid, in_port)

        out_port = ofproto.OFPP_FLOOD
        global indikator
        if indikator == 1:
            
            global _src_ip
            global _dst_ip
            global _src_host
            global _dst_host
            global _parser

            if arp_pkt:

                src_ip = arp_pkt.src_ip
                dst_ip = arp_pkt.dst_ip

                if dst in self.mymac.keys():

                    if dst in self.mac_to_port[dpid]:

                        self.logger.info(
                            '-------------------------------------------------------------------------------')
                        self.logger.info(
                            'installing path from {} to {}'.format(src, dst))

                        dst_host = self.find_host(dst)
                        src_host = self.find_host(src)

                        # calculate shortest path
                        shortest_path = self.cal_shortest_path(
                            src_host, dst_host)

                        self.logger.info('')
                        self.logger.info('Rute : ')
                        #self.logger.info(shortest_path)
                        #self.logger.info('')

                        # menyimpan src dan dst ke variable global
                        _src_ip = src_ip
                        _dst_ip = dst_ip
                        _src_host = src_host
                        _dst_host = dst_host
                        _parser = parser

                        self.install_path(
                            parser, src_ip, dst_ip, shortest_path[1::2])
                        # create reverse path
                        reverse_path = list(reversed(shortest_path))
                        self.install_path(
                            parser, dst_ip, src_ip, reverse_path[1::2])
                        self.logger.info(reverse_path)
                        
                        # packet out this packet
                        node = shortest_path[1]
                        dpid = int(node.split('.')[0])
                        out_port = int(node.split('.')[1])
                        
                        print("Time", time.time() - start_time2)
                        self.logger.info(
                            '-------------------------------------------------------------------------------')
                        indikator += 1

        actions = [parser.OFPActionOutput(out_port)]

        if out_port != ofproto.OFPP_FLOOD:
            match = parser.OFPMatch(in_port=in_port, eth_dst=dst)
            self.add_flow(datapath, match, actions)

        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        out = parser.OFPPacketOut(
            datapath=datapath, buffer_id=msg.buffer_id, in_port=in_port,
            actions=actions, data=data)
        datapath.send_msg(out)

    def _stat_request(self):
        def send_flow_stats_request(datapath):
            ofp = datapath.ofproto
            ofp_parser = datapath.ofproto_parser
            table_id = 0xff
            out_port = ofp.OFPP_NONE
            match = ofp_parser.OFPMatch(in_port=1)
            req = ofp_parser.OFPFlowStatsRequest(
                datapath, 0, match, table_id, out_port)
            datapath.send_msg(req)
