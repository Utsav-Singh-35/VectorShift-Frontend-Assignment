from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

class Pipeline(BaseModel):
    nodes: list
    edges: list

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/')
def read_root():
    return {'Ping': 'Pong'}

@app.post('/pipelines/parse')
def parse_pipeline(pipeline: Pipeline):
    nodes = pipeline.nodes or []
    edges = pipeline.edges or []
    num_nodes = len(nodes)
    num_edges = len(edges)

    # Build adjacency list keyed by node id
    node_ids = [n.get('id') for n in nodes if isinstance(n, dict) and 'id' in n]
    graph = {nid: [] for nid in node_ids}

    for e in edges:
        src = e.get('source')
        tgt = e.get('target')
        if src is None or tgt is None:
            continue
        if src not in graph or tgt not in graph:
            # skip edges referencing unknown nodes
            continue
        graph[src].append(tgt)

    # Kahn's algorithm for cycle detection
    indegree = {nid: 0 for nid in node_ids}
    for src in graph:
        for tgt in graph[src]:
            indegree[tgt] += 1

    queue = [nid for nid, deg in indegree.items() if deg == 0]
    visited = 0
    while queue:
        n = queue.pop(0)
        visited += 1
        for m in graph[n]:
            indegree[m] -= 1
            if indegree[m] == 0:
                queue.append(m)

    is_dag = (visited == len(node_ids))

    return {"num_nodes": num_nodes, "num_edges": num_edges, "is_dag": is_dag}
