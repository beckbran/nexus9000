#!/usr/bin/env python
#
# Copyright (C) 2014 Cisco Systems Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# This script prints interface throughput/packet rate statistics in an
# easy to read list format on NX-OS platforms.  To use:
#
# 		1. Copy script to NX-OS switch bootflash:
# 		2. Execute using:
# source interface_rate.py
# 			   				- or -
# python bootflash:interface_rate.py
#
from __future__ import division
import sys
import time
try:
    from cli import cli
except ImportError:
    from cisco import cli
import xml.etree.cElementTree as ET

interfaces = raw_input("Interface(s): ")


# Handle cli() type inconsistencies
def make_cli_wrapper(f):
    if type(f("show clock")) is tuple:
        def cli_wrapper(*args, **kwargs):
            return f(*args, **kwargs)[1]
        return cli_wrapper
    return f

cli = make_cli_wrapper(cli)

# Get interface information in XML format
print
print 'Collecting and processing interface statistics ...'
print


# Load and parse XML

# Find and display interface rate information
if_manager = '{http://www.cisco.com/nxos:1.0:if_manager}'
table = "{0:16}{1:9}{2:9}{3:9}{4:9}{5:10}{6:12}{7:9}{8:9}{9:9}{10:10}{11:12}"
print '-----------------------------------------------------------------------------------------------------------------------'
print table.format("Port", "Intvl", "Rx Mbps", "Rx %", "Rx pps", "Rx disc %", "Rx MPkts", "Tx Mbps", "Tx %", "Tx pps", "Tx disc %", "Tx MPkts",)
print '-----------------------------------------------------------------------------------------------------------------------'

initFlag = 0
row = 0
while True:
    sys.stdout.flush()
    raw = cli('show interface ' + interfaces + ' | xml | exclude "]]>]]>"')
    tree = ET.ElementTree(ET.fromstring(raw))
    data = tree.getroot()
    if initFlag == 1:
        sys.stdout.write("\033[F" * row)
        row = 0
    for i in data.iter(if_manager + 'ROW_interface'):
        try:
            interface = i.find(if_manager + 'interface').text
            bw = int(i.find(if_manager + 'eth_bw').text)
            rx_intvl = i.find(if_manager + 'eth_load_interval1_rx').text
            rx_bps = int(i.find(if_manager + 'eth_inrate1_bits').text)
            rx_mbps = round((rx_bps / 1000000), 1)
            try:
			    rx_pcnt = round((rx_bps / 1000) * 100 / bw, 1)
            except:
			    rx_pcnt = 0
            rx_pps = i.find(if_manager + 'eth_inrate1_pkts').text
            tx_intvl = i.find(if_manager + 'eth_load_interval1_tx').text
            tx_bps = int(i.find(if_manager + 'eth_outrate1_bits').text)
            tx_mbps = round((tx_bps / 1000000), 1)
            tx_pcnt = round((tx_bps / 1000) * 100 / bw, 1)
            tx_pps = i.find(if_manager + 'eth_outrate1_pkts').text
            eth_inpkts = i.find(if_manager + 'eth_inpkts').text
            eth_outpkts = i.find(if_manager + 'eth_outpkts').text
            eth_outdiscard = i.find(if_manager + 'eth_outdiscard').text
            eth_indiscard = i.find(if_manager + 'eth_indiscard').text
            try:
                in_discard = round((int(eth_indiscard) / int(eth_inpkts)) * 100, 1)
            except:
			    in_discard = 0
            try:
                out_discard = round((int(eth_outdiscard) / int(eth_outpkts)) * 100, 1)
            except:
			    out_discard = 0
            in_mcast = i.find(if_manager + 'eth_inmcast').text
            out_mcast = i.find(if_manager + 'eth_outmcast').text
            print table.format(interface, rx_intvl + '/' + tx_intvl, str(rx_mbps), str(rx_pcnt) + '%', rx_pps, str(in_discard) + '%', str(in_mcast), str(tx_mbps), str(tx_pcnt) + '%', tx_pps, str(out_discard) + '%', str(out_mcast))
            sys.stdout.flush()
            row += 1
        except AttributeError:
            pass
    initFlag = 1
    time.sleep(2)
