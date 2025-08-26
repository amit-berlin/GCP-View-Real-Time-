import streamlit as st
import json
from datetime import datetime
from streamlit_agraph import agraph, Node, Edge, Config

st.set_page_config(page_title="GCP Cloud Architecture Designer (MVP)", layout="wide")
st.title("🏗️ GCP Cloud Architecture Designer + Agentic AI Verifier (MVP)")
st.caption("Adjust sliders → real-time interactive GCP architecture diagram + BOM + verification")

# ---------------------- 15 Input Sliders ----------------------
st.subheader("1️⃣ Architecture Inputs (15 sliders)")
col1, col2, col3 = st.columns(3)

with col1:
    users = st.slider("Concurrent Users", 1, 20000, 500)
    rps = st.slider("Request Rate (RPS)", 1, 5000, 120)
    latency_ms = st.slider("Latency SLO (ms)", 50, 2000, 300, step=50)
    data_gb_day = st.slider("Data Ingest (GB/day)", 1, 5000, 80)
    rag_corpus_gb = st.slider("RAG Corpus Size (GB)", 1, 10000, 200)

with col2:
    freshness_min = st.slider("Data Freshness Target (minutes)", 1, 1440, 30)
    streaming_pct = st.slider("Streaming vs Batch (%) — Streaming", 0, 100, 60)
    availability = st.select_slider("Availability Target", options=["99.0%", "99.9%", "99.99%"], value="99.9%")
    rpo_min = st.slider("DR: RPO (minutes)", 0, 1440, 15)
    rto_min = st.slider("DR: RTO (minutes)", 0, 1440, 30)

with col3:
    security = st.select_slider("Security Sensitivity", options=["Low", "Medium", "High"], value="High")
    compliance = st.select_slider("Compliance", options=["None", "PII", "PHI/PCI"], value="PII")
    budget = st.select_slider("Budget Tier", options=["Low", "Medium", "High"], value="Medium")
    model_size = st.select_slider("Model Size Class", options=["S", "M", "L"], value="M")
    embed_refresh_hours = st.slider("Embedding Refresh (hours)", 1, 168, 24)

# ---------------------- Architecture Decision Logic ----------------------
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

# ---------------------- Real-time Interactive Flowchart ----------------------
st.subheader("2️⃣ Real-time Interactive Flowchart")

# Build nodes
nodes = []
edges = []
for cluster, comps in arch.items():
    for i, c in enumerate(comps if isinstance(comps,list) else [comps]):
        node_id = f"{cluster}_{i}"
        nodes.append(Node(id=node_id, label=f"{c}\n({cluster})"))

# Define edges (arrows)
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

config = Config(width=1200, height=600, directed=True, physics=False)
agraph(nodes=nodes, edges=edges, config=config)

# ---------------------- Bill of Materials & Rationale ----------------------
st.subheader("3️⃣ Bill of Materials & Rationale")
st.json(arch)

# ---------------------- Agentic AI Verification ----------------------
st.subheader("4️⃣ Free LLM / Agentic AI Verification")
st.info("⚠️ Free LLM agent uses local knowledge snippets; may not catch latest GCP updates.")

def agentic_verifier(arch_dict):
    feedback = []
    if "Cloud SQL" in arch_dict["Storage"] and rag_corpus_gb > 500:
        feedback.append("⚠️ Suggest Vertex AI Matching Engine for large RAG corpus instead of Cloud SQL.")
    if model_size == "L" and arch_dict["LLM Serving"] == "Cloud Run (Light LLM)":
        feedback.append("⚠️ Large models on Cloud Run may hit resource limits; consider Vertex AI endpoints.")
    if streaming_pct > 70 and "Dataflow (Streaming)" not in arch_dict["Processing"]:
        feedback.append("⚠️ High streaming %; consider adding Dataflow streaming transforms.")
    if not feedback:
        feedback.append("✅ Architecture looks reasonable given free LLM verification constraints.")
    return feedback

agent_feedback = agentic_verifier(arch)
for f in agent_feedback:
    st.write(f)

# ---------------------- Download Outputs ----------------------
st.subheader("5️⃣ Download BOM + Flowchart")
bom_json = json.dumps({
    "architecture": arch,
    "agent_feedback": agent_feedback,
    "inputs": {
        "users": users, "rps": rps, "latency_ms": latency_ms,
        "data_gb_day": data_gb_day, "rag_corpus_gb": rag_corpus_gb,
        "freshness_min": freshness_min, "streaming_pct": streaming_pct,
        "availability": availability, "rpo_min": rpo_min, "rto_min": rto_min,
        "security": security, "compliance": compliance,
        "budget": budget, "model_size": model_size, "embed_refresh_hours": embed_refresh_hours
    },
    "generated_at": datetime.utcnow().isoformat()+"Z"
}, indent=2)

st.download_button("⬇️ Download BOM + Verification (JSON)", bom_json, "gcp_architecture_bom.json", "application/json")
