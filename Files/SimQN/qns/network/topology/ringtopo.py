#    SimQN: a discrete-event simulator for the quantum networks
#    Copyright (C) 2021-2022 Lutong Chen, Jian Li, Kaiping Xue
#    University of Science and Technology of China, USTC.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.

from qns.entity.node.app import Application
from qns.entity.qchannel.qchannel import QuantumChannel
from qns.entity.node.node import QNode
from typing import Dict, List, Optional, Tuple
from qns.network.topology import Topology


class RingTopology(Topology):
    """
    RingTopology includes `nodes_number` Qnodes. The topology forms a closed ring.
    """
    def __init__(self, nodes_number, nodes_apps: List[Application] = [],
                 qchannel_args: Dict = {}, cchannel_args: Dict = {},
                 memory_args: Optional[List[Dict]] = {}):
        super().__init__(nodes_number, nodes_apps=nodes_apps,
                         qchannel_args=qchannel_args, cchannel_args=cchannel_args,
                         memory_args=memory_args)

    def build(self) -> Tuple[List[QNode], List[QuantumChannel]]:
        nl: List[QNode] = []
        ll: List[QuantumChannel] = []

        # Create nodes
        for i in range(self.nodes_number):
            n = QNode(f"n{i+1}")
            nl.append(n)

        # Connect in a ring
        for i in range(self.nodes_number):
            link = QuantumChannel(name=f"l{i+1}", **self.qchannel_args)
            ll.append(link)

            n1 = nl[i]
            n2 = nl[(i+1) % self.nodes_number]  # wraps around for last link
            n1.add_qchannel(link)
            n2.add_qchannel(link)

        # Attach applications and memories
        self._add_apps(nl)
        self._add_memories(nl)

        return nl, ll
