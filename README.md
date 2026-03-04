# TubeGuardAI 🛡️

**TubeGuardAI** is an producion-grade Automated Video Compliance QA Pipeline. Orchestrated by **LangGraph**, it is designed to audit video content against complex regulatory standards using a **Multimodal RAG** (Retrieval-Augmented Generation) architecture.

By synthesizing visual cues, transcripts, and OCR (Optical Character Recognition) data from video, TubeGuardAI transforms unstructured video into structured, actionable compliance reports with production-grade observability.

This project uses tools from **Microsoft Azure: Cloud Computing Services**

---

## 🚀 Key Features

* **Multimodal Ingestion**: Extracts deep insights (transcripts, OCR, and visual Cues) from video using **Azure AI Video Indexer**.
* **Agentic Orchestration**: Leverages **LangGraph** to manage complex, stateful reasoning flow for auditing.
* **Intelligent Retrieval**: Uses **Azure AI Search** and **Azure OpenAI (Embedding model)** to pull relevant regulatory rules based on video context.
* **Deterministic Reasoning**: Powered by **Azure OpenAI (LLM)** to detect violations and generate precise, evidence-based reports.
* **Full-Stack Observability**: 
    * **LangSmith**: Granular tracing for LLM workflow optimization.
    * **Azure Application Insights**: Real-time telemetry, logging, and performance monitoring.

### API Layer (FastAPI)

TubeGuardAI exposes its agentic workflow through a high-performance **FastAPI** backend, enabling seamless integration with frontend applications and enterprise dashboards.

#### Key Features:
* **Asynchronous Orchestration**: Designed to handle long-running video AI tasks using non-blocking execution patterns.
* **Pydantic Data Validation**: Strict schema enforcement for `AuditRequest` and `AuditResponse` models, ensuring 100% Type Safety.
* **Production Telemetry**: Integrated with **Azure Application Insights** via a custom telemetry module to track request latency, success rates, and system health.
* **Automatic Documentation**: Interactive Swagger UI and ReDoc generated automatically for rapid developer onboarding.
* **Robust Error Handling**: Centralized exception management using FastAPI `HTTPException` to provide actionable feedback to clients.

#### API Endpoints:
| Method | Endpoint |                        Description                                |
|  ---   |   ---    |                            ---                                    |
| `POST` | `/audit` | Triggers the LangGraph compliance workflow for a given video URL. |
| `GET`  | `/health`| Service heartbeat and health check. |

---

## 🏗️ System Architecture

The pipeline follows a sophisticated workflow to ensure high-fidelity compliance checks:

1.  **Data Ingestion**(Azure Blob Storage): Raw video files are uploaded to an Azure Blob Storage container.
1.  **Data Extraction**: Videos are processed through Azure Video Indexer to generate Transcription, OCR data and Visual Cues.
2.  **Regulatory RAG**: The system queries a vector database of compliance documents to find rules applicable to the specific video content.
3.  **Audit Logic (LangGraph)**: An agentic flow evaluates the video data against the retrieved rules from pdfs files.
4.  **Structured Output**: The final audit is delivered as a **JSON Compliance Report**, ready for downstream integration.

---

## 🛠️ Tech Stack

| Component | Technology |
| :--- | :--- |
| **Orchestration** | [LangGraph](https://github.com/langchain-ai/langgraph) |
| **Storage** | Azure Blob Storage |
| **LLM** | Azure OpenAI ('GPT-4o') |
| **Video Intelligence** | Azure AI Video Indexer |
| **Vector Database** | Azure AI Search |
| **Embeddings** | Azure OpenAI ('text-embedding-3-small') |
| **Observability** | LangSmith & Azure Application Insights |
| **Language** | Python 3.12 |

---

## 📋 Prerequisites

Before running the pipeline, ensure you have the following:

* An active **Azure Subscription**.
* **Azure OpenAI** deployment (GPT-4o and Embedding model).
* **Azure AI Search** service instance.
* **Azure Video Indexer** account.
* **LangSmith** API Key for debugging and tracing.

---

## ⚙️ Installation & Setup

This project uses `uv` as the python package manager

### Install uv:

`curl -LsSf https://astral.sh/uv/install.sh | sh`

### Verify the installation:

`echo 'export PATH="$HOME/snap/code/221/.local/bin:$PATH"' >> ~/.bashrc && source ~/.bashrc`

`uv --version`

## Clone the repository or Download as zip file

`https://github.com/yoursrealkiran/TubeGuardAI.git`

`cd TubeGuardAI`

## Environment Setup

### Create a Virual Environment

#### In the terminal, run the below command to create a virtual environment

`uv venv`

#### Activate the environment

`source .venv/bin/activate`

#### Install Dependencies

`uv sync`

## Running the Application

### 1. To run the script

Run the script to begin the audit:

`uv run python main.py`

### 2. To run using FastAPI backend and to see output in Swagger UI

`uv run uvicorn backend.src.api.server:app --reload`

Open `/audit` endpoint in Swagger UI, enter YouTube URL and execute to begin audit.

