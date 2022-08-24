# networkx example -> https://stackoverflow.com/q/63476246
# displaying network example ->

from utils import *
from networkx import all_neighbors

nodes = ["a", "b", "c", "d", "e", "f"]
edges = [
    ("a", "b"),
    ("b", "c"),
    ("c", "g"),
    ("b", "d"),
    ("c", "e"),
    ("d", "e"),
    ("e", "f"),
]

# NEIGHBORS are not suitable as it is a directed graph -> use predecessors / sucessors instead

g = create_digraph(nodes, edges)
print(check_nodes_are_connected(g, "a", "b"), "\n")
print(list(g.predecessors("e")), list(g.successors("e")))
print(list(all_neighbors(g, "e")))

show_graph(get_graph_pydot(g))

# dot is string containing DOT notation of graph
# Source(dot).view()
