import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config

st.set_page_config(page_title="GCP Cloud Architecture Designer", layout="wide")
st.title("🏗️ Interactive GCP Solution Architecture Designer (MVP)")

# ---------------------- Two-column layout ----------------------
col_input, col_diagram = st.columns([1, 3])  # Left side sliders, right side diagram

with col_input:
    st.header("Inputs")
    users = st.slider("Concurrent Users", 1, 20000, 500)
    rps = st.slider("Request Rate (RPS)", 1, 5000, 120)
    latency_ms = st.slider("Latency SLO (ms)", 50, 2000, 300, step=50)
    data_gb_day = st.slider("Data Ingest (GB/day)", 1, 5000, 80)
    rag_corpus_gb = st.slider("RAG Corpus Size (GB)", 1, 10000, 200)
    freshness_min = st.slider("Data Freshness Target (minutes)", 1, 1440, 30)
    streaming_pct = st.slider("Streaming vs Batch (%) — Streaming", 0, 100, 60)
    availability = st.select_slider("Availability Target", options=["99.0%", "99.9%", "99.99%"], value="99.9%")
    rpo_min = st.slider("DR: RPO (minutes)", 0, 1440, 15)
    rto_min = st.slider("DR: RTO (minutes)", 0, 1440, 30)
    security = st.select_slider("Security Sensitivity", options=["Low", "Medium", "High"], value="High")
    compliance = st.select_slider("Compliance", options=["None", "PII", "PHI/PCI"], value="PII")
    budget = st.select_slider("Budget Tier", options=["Low", "Medium", "High"], value="Medium")
    model_size = st.select_slider("Model Size Class", options=["S", "M", "L"], value="M")
    embed_refresh_hours = st.slider("Embedding Refresh (hours)", 1, 168, 24)

# ---------------------- Architecture logic ----------------------
def architecture_logic():
    api_layer = ["Cloud Run (FastAPI)"] if latency_ms > 150 else ["Vertex AI Endpoints"]
    ingestion = ["Cloud Storage", "Pub/Sub"] if streaming_pct >= 50 else ["Cloud Storage", "Batch Dataflow"]
    processing = ["Dataflow (Streaming)" if freshness_min < 15 else "BigQuery + Composer"]
    storage = ["BigQuery", "Cloud SQL", "Firestore"]
    vector_db = "Vertex AI Matching Engine" if rag_corpus_gb > 50 else "pgvector on Cloud SQL"
    embedding_pipeline = "Cloud Run Embedding Workers"
    llm_serving = "Vertex AI Endpoints" if model_size == "L" else "Cloud Run (Light LLM)"
    agentic_ai = ["Workflows orchestrator", "Serverless agents", "Pub/Sub triggers"]
    mlops = ["Vertex AI Experiments", "Model Registry", "Cloud Monitoring + Logging"]
    cicd = ["GitHub Actions → Cloud Build → Deploy", "Terraform Infra as Code"]
    dr = ["Multi-region backups", "Cold/Warm standby"]
    rag_stack = ["Retriever (FAISS or Matching Engine)", f"Vector DB: {vector_db}", "Context Builder", "RAG Policy"]
    return {
        "API Layer": api_layer,
        "Ingestion": ingestion,
        "Processing": processing,
        "Storage": storage,
        "Vector DB": vector_db,
        "Embedding Pipeline": embedding_pipeline,
        "RAG Stack": rag_stack,
        "LLM Serving": llm_serving,
        "Agentic AI": agentic_ai,
        "MLOps": mlops,
        "CI/CD": cicd,
        "DR/Resilience": dr
    }

arch = architecture_logic()

# ---------------------- Real-time Interactive GCP Architecture ----------------------
with col_diagram:
    st.header("Proposed GCP Architecture")

    # Build nodes
    nodes = []
    edges = []
    for cluster, comps in arch.items():
        for i, c in enumerate(comps if isinstance(comps,list) else [comps]):
            node_id = f"{cluster}_{i}"
            nodes.append(Node(id=node_id, label=f"{c}\n({cluster})"))

    # Define edges
    flow_edges = [
        ("API Layer", "Agentic AI"), 
        ("Agentic AI", "RAG Stack"), 
        ("RAG Stack", "LLM Serving"),
        ("Ingestion", "Processing"), 
        ("Processing", "Storage"), 
        ("Storage", "RAG Stack"),
        ("MLOps", "LLM Serving"),
        ("CI/CD", "API Layer"),
        ("DR/Resilience", "Storage")
    ]

    for src, tgt in flow_edges:
        src_nodes = arch[src] if isinstance(arch[src], list) else [arch[src]]
        tgt_nodes = arch[tgt] if isinstance(arch[tgt], list) else [arch[tgt]]
        for i_s, s in enumerate(src_nodes):
            for i_t, t in enumerate(tgt_nodes):
                edges.append(Edge(source=f"{src}_{i_s}", target=f"{tgt}_{i_t}"))

    config = Config(width=1400, height=800, directed=True, physics=False)
    agraph(nodes=nodes, edges=edges, config=config)
