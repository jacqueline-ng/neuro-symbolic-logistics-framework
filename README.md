# A Neuro-Symbolic Multi-Agent Workflow for Autonomous Supply Chain Mitigation

This repository hosts the replication artifacts, orchestration workflows, and diagnostic code for the methodology paper submitted to *MethodsX*.

## Repository Structure
- `knowledge_base/`: Grounded Standard Operating Procedure (SOP v1.1) in Markdown format.
- `scripts/`: Python scripts and Jupyter notebooks covering:
  - SOP ingestion and vectorization (`stage1_SOP_Ingestion.ipynb`).
  - Predictive diagnostics and SHAP extraction (`stage2_Predictive_Diagnostics.ipynb`).
  - Automated RAGAS evaluation runner (`run_ragas_adapted.py`).
- `workflows/`: n8n agent orchestration schemas (`00_main_orchestrator.json`, `01_sop_rag_retrieval.json`, `02_planner_agent.json`, `03_evaluator agent.json`).
- `data/`: Curated late delivery benchmark test suite and experimental audit ledger.

## System Prerequisites
- Python 3.10+
- Container runtime (Docker Desktop / WSL2)
- Qdrant Vector Database (`docker run -p 6333:6333 qdrant/qdrant`)
- Local LLM Runtime: Ollama with Phi-3 Mini (`ollama run phi3:mini`)
- Workflow Orchestrator: n8n (`docker run -p 5678:5678 n8nio/n8n`)

## Quickstart & Replication

1. **Clone the repository:**
   ```bash
   git clone https://github.com/jacqueline-ng/neuro-symbolic-logistics-framework.git
   cd neuro-symbolic-logistics-framework
   pip install -r requirements.txt
   ```
2.  **Ingest SOP Knowledge Base:**
    Place Standard_Operating_Procedure_v1_1.docx (provided with manuscript supplementary files) into the root directory.
    Execute scripts/stage1_SOP_Ingestion.ipynb to chunk and embed SOP v1.1 into the local Qdrant collection (dataco_supply_chain_sops).

4.  **Import Workflows into n8n:**
    Open the n8n web interface at http://localhost:5678.
    For each workflow JSON in /workflows/ (00_main_orchestrator.json, 01_sop_rag_retrieval.json, 02_planner_agent.json, 03_evaluator agent.json), go to Workflows -> Import from File.
    Configure the local Ollama node credentials pointing to your running Phi-3 instance ([http://host.docker.internal:11434](http://host.docker.internal:11434) or local host network).
    Activate all workflows to initialize webhook endpoints.

5.  **Trigger Predictive Diagnostics & Benchmark Suite:**
    Open and run scripts/stage2_Predictive_Diagnostics.ipynb.
    This notebook trains the XGBoost late delivery classifier, extracts global and local SHAP feature drivers, and executes the interactive test harness to dispatch test cases from data/curated_late_delivery_test_suite.csv to the orchestrator webhook.
    Execution traces, reflection iterations, and audit metrics are recorded in data/Logistics_Audit_Ledger.csv.
