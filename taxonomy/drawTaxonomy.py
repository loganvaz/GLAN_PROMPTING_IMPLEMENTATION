import graphviz
import json
import os

def add_nodes(graph, node, parent=None, level=0):
    if node.topic is not None:
        node.topic = node.topic.replace("\n", " ").replace(":"," ").strip()
        # Add the node to the graph
        graph.node(node.topic)

        # Add an edge from the parent to the node
        if parent is not None:
            graph.edge(parent, node.topic)

        # Add a subgraph for the current level if it doesn't exist
        with graph.subgraph() as s:
            s.attr(rank='same')
            s.node(node.topic)

        # Recursively add the children of the node
        for child in node.children[:3]:
            add_nodes(graph, child, parent=node.topic, level=level+1)

def visualize_json(json_file):
    with open(json_file) as f:
        data = json.load(f)

    graph = graphviz.Digraph()  # Use Digraph for a directed graph
    add_nodes(graph, data)
    graph.render('graph', view=True)  # Render the graph to a file and open it

visualize_json(os.path.join('storage', 'createdTaxonomy.json'))