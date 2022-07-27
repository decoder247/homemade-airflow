# networkx example -> https://stackoverflow.com/q/63476246
# displaying network example ->

from utils import *

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

g = create_digraph(nodes, edges)
print(check_nodes_are_connected(g, "a", "b"), "\n")

# show_graph(g)

# dot is string containing DOT notation of graph
# Source(dot).view()
