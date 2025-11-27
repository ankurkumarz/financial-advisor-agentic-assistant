# Architectural Summary: Financial Advisor Agentic Assistant (FA³AI)

## High-Level Overview
The Financial Advisor Agentic Assistant (FA³AI) is a multi-agent system designed to assist wealth advisors by unifying data analysis, document retrieval, and compliance checking. It leverages Google's Agent Development Kit (ADK) and Gemini models to orchestrate a team of specialized agents. The system is exposed via a FastAPI web server and supports Agent-to-Agent (A2A) communication.

## Key Building Blocks

### 1. Core Application Layer
*   **FastAPI Server**: The entry point for the application, handling HTTP requests and routing them to the main agent.
*   **Google ADK (Agent Development Kit)**: The framework used for defining, instantiating, and orchestrating agents.
*   **A2A (Agent-to-Agent) Communication**: Enables the main agent to delegate tasks to sub-agents effectively.

### 2. Agent Hierarchy
The system follows a hierarchical multi-agent architecture:

*   **Financial Advisor Agent (Orchestrator)**
    *   **Role**: The primary interface for the user. It analyzes requests and delegates tasks to the appropriate sub-agents.
    *   **Capabilities**: Task decomposition, delegation, and response synthesis.

*   **Sub-Agents**:
    1.  **Compliance Checker Agent**
        *   **Role**: Ensures all generated advice adheres to regulatory standards.
        *   **Tools**:
            *   `compliance_checklist_tool`: Verifies content against a checklist.
            *   `disclaimer_template_tool`: Appends necessary legal disclaimers.
    2.  **CRM Leads Insights Agent**
        *   **Role**: Analyzes customer data to provide insights on leads and prospects.
        *   **Tools**:
            *   `CRMDataframeTool`: Performs SQL-like operations (filter, aggregate, describe) on customer datasets.
        *   **Data Source**: `global_banking_customer_analytics.csv` (loaded via KaggleHub or local storage).
    3.  **Enterprise Docs Agent** (Financial Enterprise Docs Retriever)
        *   **Role**: Retrieves relevant financial documents, policies, and product information.
        *   **Tools**:
            *   `VectorSearchTool`: Performs semantic search on indexed documents.
        *   **Infrastructure**:
            *   **Database**: ChromaDB (Persistent Vector Store).
            *   **Embeddings**: Google Generative AI Embeddings (`models/text-embedding-004`).
    4.  **Google Research Agent**
        *   **Role**: Performs external web research to supplement internal knowledge.
        *   **Tools**: Google Search (implied).

### 3. Data & Storage Layer
*   **ChromaDB**: A vector database used to store and retrieve embeddings of enterprise documents (PDFs, JSONs).
*   **Local File System**: Stores the CRM CSV dataset and raw document files.
*   **In-Memory State**: Agents maintain conversation history and context during execution.

## Data Flow
1.  **Ingestion**:
    *   Enterprise documents are parsed (PDF/JSON), chunked, embedded using Gemini, and stored in ChromaDB.
    *   CRM data is loaded into a Pandas DataFrame for analysis.
2.  **Request Handling**:
    *   User sends a query via the FastAPI endpoint.
    *   **Financial Advisor Agent** receives the query and determines the intent.
3.  **Delegation & Execution**:
    *   If **CRM data** is needed, the *CRM Leads Insights Agent* queries the DataFrame.
    *   If **internal knowledge** is needed, the *Enterprise Docs Agent* searches ChromaDB.
    *   If **external info** is needed, the *Google Research Agent* searches the web.
4.  **Synthesis & Compliance**:
    *   The **Financial Advisor Agent** aggregates the results.
    *   The **Compliance Checker Agent** reviews the draft response and appends disclaimers.
5.  **Response**:
    *   The final, compliant response is returned to the user.

## Technology Stack
*   **Language**: Python 3.13+
*   **Web Framework**: FastAPI
*   **AI/ML Frameworks**:
    *   Google ADK (Agent Development Kit)
    *   Google Generative AI (Gemini Models)
*   **Data Processing**:
    *   Pandas (Data Analysis)
    *   PyPDF (Document Parsing)
    *   KaggleHub (Dataset Downloading)
*   **Database**: ChromaDB (Vector Database)
*   **Infrastructure**: Uvicorn (ASGI Server)
