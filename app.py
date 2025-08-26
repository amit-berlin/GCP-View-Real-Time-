import streamlit as st
import json
from datetime import datetime
import graphviz

st.set_page_config(page_title="GCP Cloud Architecture Designer (MVP)", layout="wide")
st.title("🏗️ GCP Cloud Architecture Designer + Agentic AI Verifier (MVP)")
st.caption("Adjust sliders → real-time GCP architecture diagram + BOM + agentic verification")

# ---------------------- 20 Backend Steps ----------------------
st.subheader("📜 How This Works (20 Steps)")

steps = [
    "1. User sets 15 architecture parameters via sliders (users, latency, RAG size, etc.).",
    "2. Each slider input maps to architecture components and scale decisions.",
    "3. System identifies API layer and serving layer (Cloud Run / Vertex AI Endpoints).",
    "4. Determines ingestion pipelines (streaming vs batch) based on data volume and freshness.",
    "5. Determines processing layer (Dataflow, Dataproc, BigQuery, Cloud Composer).",
    "6. Chooses storage layer (Cloud SQL, BigQuery, Firestore, Vector DB).",
    "7. Configures RAG pipeline architecture (Retriever + Vector DB + LLM).",
    "8. Configures Agentic AI orchestration (LangChain/LangGraph style, serverless agents).",
    "9. Selects embedding pipeline (CPU workers or Vertex AI embeddings endpoints).",
    "10. Maps model serving infrastructure (Cloud Run / Vertex AI depending on size/latency).",
    "11. Sets MLOps & monitoring layer (Vertex AI Experiments, logging, metrics).",
    "12. Sets CI/CD pipelines (GitHub Actions → Cloud Build → Deploy).",
    "13. Determines DR & resilience strategy (multi-region, backups, RPO/RTO).",
    "14. Generates full GCP architecture DOT diagram (Graphviz) dynamically.",
    "15. Generates Bill of Materials (BOM) detailing all selected components.",
    "16. Generates rationale for each component selection based on slider inputs.",
    "17. Runs a lightweight free open-source LLM agent to verify architecture.",
    "18. Agent cross-checks architecture against local knowledge snippets (GCP docs, blogs).",
    "19. Displays agent’s feedback (warnings or confirmations) in real-time.",
    "20. Final output: architecture diagram + BOM + Agent feedback for interview demonstration."
]

with st.expander("Show 20 Steps"):
    for s in steps:
        st.markdown(f"- {s}")

st.warning("""
⚠️ Accuracy Note: Using free LLMs (like FLAN-T5) or small HuggingFace models:
- Knowledge is limited to pre-trained datasets, may miss latest GCP updates.
- Cannot crawl live web pages in free Streamlit.
- RAG verification uses local snippets only, so correctness is approximate.
""")

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

# ---------------------- Graphviz Architecture Diagram (Real-time) ----------------------
st.subheader("2️⃣ Real-time Architecture Diagram")

def build_dot(arch_dict):
    dot = "digraph G { rankdir=LR; node [shape=box, style=rounded, fillcolor=\"#EEF5FF\"];\n"
    for cluster, nodes in arch_dict.items():
        dot += f'subgraph cluster_{cluster.replace(" ", "_")} {{ label="{cluster}"; style=rounded; color="#999999";\n'
        for i, n in enumerate(nodes if isinstance(nodes,list) else [nodes]):
            dot += f'"{cluster}_{i}" [label="{n}"];\n'
        dot += "}\n"
    # edges
    edges = [("API Layer", "Agentic AI"), ("Agentic AI", "RAG Stack"), ("RAG Stack", "LLM Serving"),
             ("Ingestion", "Processing"), ("Processing", "Storage"), ("Storage", "RAG Stack")]
    for a,b in edges:
        dot += f'"cluster_{a.replace(" ", "_")}" -> "cluster_{b.replace(" ", "_")}" [style=dashed];\n'
    dot += "}"
    return dot

dot = build_dot(arch)
st.graphviz_chart(dot, use_container_width=True)  # Real-time updates as sliders move

# ---------------------- Bill of Materials & Explanation ----------------------
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

# ---------------------- Download BOM / DOT ----------------------
st.subheader("5️⃣ Download Outputs")
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
st.download_button("⬇️ Download DOT Diagram", dot, "gcp_architecture.dot", "text/plain")
