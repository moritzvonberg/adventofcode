from __future__ import annotations
from typing import Set
import networkx as nx
import matplotlib.pyplot as plt


class Cave():
    def __init__(self, log_paths=False) -> None:
        self.nodes = dict()
        self.current_node = None
        self.visit_stack = []
        self.start_node = None
        self.end_node = None
        self.count = 0
        self.log_paths = log_paths
        self.paths = set()

    def __getitem__(self, cave_node: str):
        if cave_node not in self.nodes:
            raise KeyError(cave_node)
        return self.nodes[cave_node]

    def __setitem__(self, name: str, value: CaveNode):
        self.nodes[name] = value

    def __contains__(self, cave_node: str):
        return cave_node in self.nodes

    def add_connection(self, node1: str, node2: str):
        if node1 not in self:
            self.add_node(node1)
        if node2 not in self:
            self.add_node(node2)
        self[node1].connect(self[node2])
    
    def add_node(self, name: str):
        self[name] = CaveNode(name, name.isupper())

    def __iter__(self):
        return self.nodes.__iter__()

    def items(self):
        return self.nodes.items()

    def count_paths(self):
        self.current_node = self['start']
        self.start_node = self['start']
        self.end_node = self['end']

        if not self.path_exists_to_end():
            return 0
        self.do_dfs()
        return self.count

    def do_dfs(self):
        self.visit_current_node()
        # we don't need to check if there's a connection to end if we're moving
        # from a revisitable node
        if not self.visit_stack[-1].revisitable and not self.path_exists_to_end():
            self.unvisit_current_node()
            return
        for neighbor in self.current_node.visitable_neighbors():
            # don't want to keep counting after we have visited end node
            # because it's not revisitable
            if neighbor == self['end']:
                self.add_path()
                continue
            self.current_node = neighbor
            self.do_dfs()
        if self.current_node == self['start']:
            return
        self.unvisit_current_node()
        

    def path_exists_to_end(self):
        if self.current_node == self.end_node or self.current_node.is_connected_to(self.end_node):
            return True
        visited_nodes = {self.current_node}
        nodes_to_check = list(self.current_node.visitable_neighbors())
        while nodes_to_check:
            checking_node = nodes_to_check.pop()
            if checking_node.is_connected_to(self.end_node):
                return True
            visited_nodes.add(checking_node)
            for neighbor in checking_node.visitable_neighbors():
                if neighbor not in visited_nodes and neighbor not in nodes_to_check:
                    nodes_to_check.append(neighbor)
        return False

    def add_path(self):
        self.count += 1
        
        if self.log_paths:    
            path = "-".join((str(node) for node in self.visit_stack)) + "-end"
            if path in self.paths:
                raise Exception(f"attempted to add {path} for a second time")
            self.paths.add(path)

    def visit_current_node(self):
        self.current_node.visit()
        self.visit_stack.append(self.current_node)
    
    def unvisit_current_node(self):
        self.current_node.unvisit()
        self.visit_stack.pop()
        self.current_node = self.visit_stack[-1]


class CaveNode():
    
    small_cave_visited_twice = False

    def __init__(self, name: str, revisitable: bool, connected_nodes: Set[bool]=None) -> None:
        self.name = name
        self.revisitable = revisitable
        self.connected_nodes = connected_nodes if connected_nodes else list()
        self.visit_count = 0

    def __hash__(self):
        return self.name.__hash__()
    
    def __eq__(self, other: CaveNode):
        return self.name == other.name

    def is_connected_to(self, other:CaveNode):
        return other in self.connected_nodes

    def connect(self, other: CaveNode):
        self.connected_nodes.append(other)
        other.connected_nodes.append(self)

    def can_be_visited(self):
        if self.revisitable:
            return True
        if not CaveNode.small_cave_visited_twice and self.name not in ("start", "end"):
            return self.visit_count < 2
        else:
            return self.visit_count == 0
    
    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.name

    def visit(self):
        if not self.can_be_visited():
            raise Exception(f"Attempted to visit non visitable node {self}")
        self.visit_count += 1
        if not self.revisitable and self.visit_count == 2:
            CaveNode.small_cave_visited_twice = True

    def unvisit(self):
        if self.visit_count <= 0:
            raise Exception(f"Attempted to unvisit node {self} but {self} was already unvisited")
        if not self.revisitable and self.visit_count == 2:
            CaveNode.small_cave_visited_twice = False
        self.visit_count -= 1


    def visitable_neighbors(self):
        for node in self.connected_nodes:
            if node.can_be_visited():
                yield node

visualization = nx.Graph()
cave = Cave(log_paths=True)
with open("2021/day 12/input.txt", 'r') as infile:
    edges = []
    for line in infile.readlines():
        node1, node2 = line.strip().split('-')
        if not node1 in cave:
            cave.add_node(node1)
        if not node2 in cave:
            cave.add_node(node2)
        cave[node1].connect(cave[node2])
        edges.append((node1, node2))
    visualization.add_edges_from(edges)

print(cave.count_paths())
#sanity check
print(len(cave.paths))

# code to redraw visualization
# nx.draw(visualization, with_labels=True)
# plt.show()
