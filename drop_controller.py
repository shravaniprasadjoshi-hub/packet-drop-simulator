"""
Packet Drop Simulator - POX Controller
Drops all traffic from h1 (10.0.0.1) to h2 (10.0.0.2)
All other traffic is forwarded normally
"""

from pox.core import core
from pox.lib.addresses import IPAddr, EthAddr
import pox.openflow.libopenflow_01 as of
from pox.lib.revent import EventMixin
from pox.lib.util import dpidToStr

log = core.getLogger()

# --- CONFIGURATION ---
BLOCKED_SRC_IP = '10.0.0.1'   # h1
BLOCKED_DST_IP = '10.0.0.2'   # h2
DROP_PRIORITY  = 100           # Higher = checked first
FORWARD_PRIORITY = 10          # Lower = checked second


class PacketDropController(EventMixin):

    def __init__(self):
        self.listenTo(core.openflow)
        # mac_to_port table: {dpid: {mac: port}}
        self.mac_to_port = {}
        log.info("PacketDropController started")
        log.info(f"DROP RULE: {BLOCKED_SRC_IP} --> {BLOCKED_DST_IP} BLOCKED")

    def _handle_ConnectionUp(self, event):
        """Called when a switch connects to the controller"""
        dpid = dpidToStr(event.dpid)
        log.info(f"Switch {dpid} connected")

        # Install the DROP rule immediately when switch connects
        self.install_drop_rule(event)

    def install_drop_rule(self, event):
        """Install a flow rule that drops h1 -> h2 traffic"""

        msg = of.ofp_flow_mod()

        # Match: packets from h1 going to h2
        msg.match.dl_type = 0x0800          # IPv4 packets only
        msg.match.nw_src  = IPAddr(BLOCKED_SRC_IP)
        msg.match.nw_dst  = IPAddr(BLOCKED_DST_IP)

        # Action: empty action list = DROP
        # (no action = drop in OpenFlow)
        msg.actions = []

        # Priority and timeouts
        msg.priority   = DROP_PRIORITY
        msg.hard_timeout = 0   # Never expires
        msg.idle_timeout = 0   # Never expires

        event.connection.send(msg)
        log.warning(
            f"DROP RULE INSTALLED: "
            f"{BLOCKED_SRC_IP} --> {BLOCKED_DST_IP} on switch "
            f"{dpidToStr(event.dpid)}"
        )

    def _handle_PacketIn(self, event):
        """Called for every packet the switch doesn't know how to handle"""

        packet    = event.parsed
        dpid      = event.dpid
        in_port   = event.port

        if not packet.parsed:
            return

        # Learn MAC -> port mapping
        self.mac_to_port.setdefault(dpid, {})
        self.mac_to_port[dpid][packet.src] = in_port

        # Check if packet is IPv4
        ip_packet = packet.find('ipv4')
        if ip_packet:
            src_ip = str(ip_packet.srcip)
            dst_ip = str(ip_packet.dstip)

            # Log but don't forward blocked traffic
            # (drop rule in switch handles it, this is just for logging)
            if src_ip == BLOCKED_SRC_IP and dst_ip == BLOCKED_DST_IP:
                log.warning(f"BLOCKED packet: {src_ip} --> {dst_ip}")
                return

        # Forward packet normally using learned MAC table
        if packet.dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][packet.dst]

            # Install a forward flow rule
            msg = of.ofp_flow_mod()
            msg.match = of.ofp_match.from_packet(packet, in_port)
            msg.priority = FORWARD_PRIORITY
            msg.idle_timeout = 30
            msg.hard_timeout = 60
            msg.actions.append(of.ofp_action_output(port=out_port))
            msg.data = event.ofp
            event.connection.send(msg)
        else:
            # Flood if we don't know the destination
            msg = of.ofp_packet_out()
            msg.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
            msg.data = event.ofp
            msg.in_port = in_port
            event.connection.send(msg)


def launch():
    core.registerNew(PacketDropController)
    log.info("Packet Drop Simulator Controller Launching...")

