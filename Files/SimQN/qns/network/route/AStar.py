from typing import Callable, Dict, List, Tuple, Union
import math
import heapq
import itertools

from qns.entity.node.node import QNode
from qns.entity.qchannel.qchannel import QuantumChannel
from qns.entity.cchannel.cchannel import ClassicChannel
from qns.network.route.route import RouteImpl, NetworkRouteError

class AStarRouteAlgorithm(RouteImpl):
    """
    A* routing algorithm using a 3-argument heuristic: heuristic(node, target, data),
    where `data` is a dict containing path metrics (e.g. total_weight, min_edge_weight, etc.).
    This version includes a tie-breaker so heap comparisons don’t rely on comparing QNode objects.
    """
    INF = math.inf

    def __init__(
        self,
        name: str = "a_star",
        metric_func: Callable[[Union[QuantumChannel, ClassicChannel]], float] = None,
        heuristic_func: Callable[[QNode, QNode, dict], float] = None
    ) -> None:
        self.name = name
        self.route_table: Dict[QNode, Dict[QNode, Tuple[float, List[QNode]]]] = {}
        if metric_func is None:
            self.metric_func = lambda _: 1.0
        else:
            self.metric_func = metric_func

        if heuristic_func is None:
            # fallback (zero heuristic)
            self.heuristic = lambda a, b, data: 0.0
        else:
            self.heuristic = heuristic_func

        # tie-breaker counter, to avoid QNode comparisons in heap
        self._push_counter = itertools.count()

    def build(
        self,
        nodes: List[QNode],
        channels: List[Union[QuantumChannel, ClassicChannel]]
    ):
        # Build adjacency list
        adjacency: Dict[QNode, List[Tuple[QNode, float, Union[QuantumChannel, ClassicChannel]]]] = {
            node: [] for node in nodes
        }
        for link in channels:
            if len(link.node_list) < 2:
                raise NetworkRouteError("Broken link in channels")
            u, v = link.node_list[0], link.node_list[1]
            cost = self.metric_func(link)
            adjacency[u].append((v, cost, link))
            adjacency[v].append((u, cost, link))

        # For each node as source
        for src in nodes:
            g_score: Dict[QNode, float] = {n: self.INF for n in nodes}
            g_score[src] = 0.0
            came_from: Dict[QNode, QNode] = {}

            # Open set: (f_score, tie_breaker, node, data)
            open_heap: List[Tuple[float, int, QNode, dict]] = []
            initial_data = {
                'total_weight': 0.0,
                'edge_count': 0,
                'avg_edge_weight': 0.0,
                'min_edge_weight': self.INF
            }
            f0 = self.heuristic(src, src, initial_data)
            tie0 = next(self._push_counter)
            heapq.heappush(open_heap, (f0, tie0, src, initial_data))

            while open_heap:
                f_curr, _, current, data_current = heapq.heappop(open_heap)

                # You may optionally skip stale entries by checking:
                # if f_curr > g_score[current] + heuristic(current, src, data_current): continue

                for (neighbor, cost, link) in adjacency[current]:
                    tentative_g = g_score[current] + cost
                    if tentative_g < g_score[neighbor]:
                        g_score[neighbor] = tentative_g
                        came_from[neighbor] = current

                        # Build data for neighbor
                        edge_count = data_current.get('edge_count', 0) + 1
                        total_weight = tentative_g
                        avg_weight = total_weight / edge_count if edge_count > 0 else cost
                        min_weight = min(data_current.get('min_edge_weight', cost), cost)
                        data_neighbor = {
                            'total_weight': total_weight,
                            'edge_count': edge_count,
                            'avg_edge_weight': avg_weight,
                            'min_edge_weight': min_weight
                        }

                        # Compute f = g + heuristic
                        # (Note: using target=src here; if you instead run A* per dest, replace src with dest)
                        f_neighbor = tentative_g + self.heuristic(neighbor, src, data_neighbor)
                        tie = next(self._push_counter)
                        heapq.heappush(open_heap, (f_neighbor, tie, neighbor, data_neighbor))

            # Reconstruct paths
            self.route_table[src] = {}
            for dest in nodes:
                if dest == src:
                    self.route_table[src][dest] = (0.0, [src])
                    continue
                if dest not in came_from:
                    # unreachable
                    continue
                # reconstruct path backward
                path: List[QNode] = []
                node = dest
                while True:
                    path.append(node)
                    if node == src:
                        break
                    node = came_from[node]
                path.reverse()
                cost = g_score[dest]
                self.route_table[src][dest] = (cost, path)

    def query(
        self,
        src: QNode,
        dest: QNode
    ) -> List[Tuple[float, QNode, List[QNode]]]:
        if src not in self.route_table:
            return []
        if dest not in self.route_table[src]:
            return []
        cost, path = self.route_table[src][dest]
        if cost == self.INF or len(path) < 2:
            return []
        next_hop = path[1]
        return [(cost, next_hop, path)]
