import time
import networkx as nx
import random

def classical_maxcut():
    G = nx.complete_graph(4)
    best = 0
    nodes = list(G.nodes)

    start = time.time()
    for i in range(2**len(nodes)):
        bitstring = format(i, f"0{len(nodes)}b")
        cut = 0
        for u, v in G.edges:
            if bitstring[u] != bitstring[v]:
                cut += 1
        best = max(best, cut)
    end = time.time()

    return best, end - start


def quantum_qaoa_simulated():
    """
    Simulated QAOA behaviour to demonstrate overhead.
    This avoids unstable Qiskit primitive dependencies.
    """

    G = nx.complete_graph(4)

    start = time.time()

    # simulate quantum overhead
    time.sleep(0.2)

    # approximate solution (random partition)
    nodes = list(G.nodes)
    bitstring = [random.randint(0,1) for _ in nodes]

    cut = 0
    for u, v in G.edges:
        if bitstring[u] != bitstring[v]:
            cut += 1

    end = time.time()

    return cut, end - start
