import numpy as np
import networkx as nx
from tqdm import tqdm

import metis

def euclidean_distance(a, b):
    return np.linalg.norm(np.array(a) - np.array(b))

def knn_graph(df, k, verbose=False):
    points = [p[1:] for p in df.itertuples()]
    g = nx.Graph()
    if verbose: print "Building kNN graph (k = %d)" % (k)
    iterpoints = tqdm(enumerate(points), total=len(points)) if verbose else enumerate(points)
    for i, p in iterpoints:
        distances = map(lambda x: euclidean_distance(p, x), points)
        closests = np.argsort(distances)[1:k+1] # second trough kth closest
        for c in closests:
            g.add_edge(i, c, weight=distances[c])
        g.node[i]['pos'] = p
    return g

def part_graph(graph, k, df=None):
    edgecuts, parts = metis.part_graph(graph, k)
    for i, p in enumerate(graph.nodes()):
        graph.node[p]['cluster'] = parts[i]
    if df is not None:
        df['cluster'] = nx.get_node_attributes(graph, 'cluster').values()
    return graph

def get_cluster(graph, clusters):
    nodes = [n for n in graph.node if graph.node[n]['cluster'] in clusters]
    return nodes

def connecting_edges(partitions, graph):
    cut_set = []
    for a in partitions[0]:
        for b in partitions[1]:
            if a in graph:
                if b in graph[a]:
                    cut_set.append((a, b))
    return cut_set

def min_cut_bisector(graph):
    graph = graph.copy()
    graph = part_graph(graph, 2)
    partitions = get_cluster(graph, [0]), get_cluster(graph, [1])
    return connecting_edges(partitions, graph)

def get_weights(graph, edges):
    return [graph[edge[0]][edge[1]]['weight'] for edge in edges]

def bisection_weights(graph, cluster):
    cluster = graph.subgraph(cluster)
    edges = min_cut_bisector(cluster)
    weights = get_weights(cluster, edges)
    return weights