import uasyncio
import bbl.v7rc as v7rc

# V7rc initialization with custom ESSID and password
# You can also provide a custom callback function for UDP messages
start = v7rc.init_ap(
    essid='cyber_V7RC',
    password='12341234',
    udp_ip='192.168.4.1',
    udp_port=6188,
    use_default_led=True
)

uasyncio.run(start())