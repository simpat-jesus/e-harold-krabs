# Finance Assistant – Architecture

## Overview

The system ingests **PDF bank statements** and **CSV files**, extracts structured data with AI, stores it in PostgreSQL (with JSONB for raw data), and generates insights + dashboards.

## Flow Diagram

```mermaid
flowchart TD
    A[PDF/CSV Upload] --> B[Extractor Service]
    B -->|Parse text| C["AI Parser (Ollama/OpenAI)"]
    C -->|JSON| D[Transaction Processor]
    D -->|Insert| E[(PostgreSQL)]
    E --> F[Insights API]
    F --> G["Dashboard (Streamlit/React)"]
```

## Database Model

```mermaid
erDiagram
    TRANSACTIONS {
        int id PK
        date date
        string description
        float amount
        string category
        jsonb raw_data
        timestamp created_at
    }
```

* `raw_data`: Original parsed object (flexible schema).
* `category`: Can be assigned by AI or user-corrected.
