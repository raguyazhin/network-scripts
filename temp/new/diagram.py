import json
import networkx as nx
import plotly.graph_objects as go

# Load the JSON data
with open('data.json') as file:
    data = json.load(file)

# Create a directed graph
G = nx.DiGraph()

# Add nodes and edges based on the matching parentDeviceid with id
for group, devices in data.items():
    for device in devices:
        device_id = device['id']
        parent_id = device.get('parentDeviceid')
        G.add_node(device_id)

        if parent_id:
            G.add_edge(parent_id, device_id)

# Set node positions manually based on hierarchy
pos = nx.nx_pydot.graphviz_layout(G, prog='dot')

# Create edge trace
edge_trace = go.Scatter(
    x=[],
    y=[],
    line=dict(width=0.5, color='gray'),
    hoverinfo='none',
    mode='lines'
)

# Add edge coordinates to the trace
for edge in G.edges():
    x0, y0 = pos[edge[0]]
    x1, y1 = pos[edge[1]]
    edge_trace['x'] += tuple([x0, x1, None])
    edge_trace['y'] += tuple([y0, y1, None])

# Create node trace
node_trace = go.Scatter(
    x=[],
    y=[],
    text=[],
    mode='markers+text',
    hoverinfo='text',
    marker=dict(
        showscale=False,
        color='lightblue',
        size=10
    ),
    textposition='top center'
)

# Add node coordinates and labels to the trace
for node in G.nodes():
    x, y = pos[node]
    node_trace['x'] += tuple([x])
    node_trace['y'] += tuple([y])
    node_trace['text'] += tuple([node])

# Create figure
fig = go.Figure(
    data=[edge_trace, node_trace],
    layout=go.Layout(
        title='CDP Network Diagram (Hierarchy View)',
        titlefont_size=16,
        showlegend=False,
        hovermode='closest',
        margin=dict(b=20, l=5, r=5, t=40),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
    )
)

# Show the interactive network diagram
fig.show()
