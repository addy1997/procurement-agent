# Procurement-Supervisor Agent

A serverless AI-driven procurement orchestration system deployed on AWS Lambda (Python 3.12). A multi-agent supervisor routes incoming procurement requests to specialised sub-agents for supplier discovery, compliance validation, inventory synchronisation, and contract negotiation.

## Architecture

![System Architecture](docs/architecture.png)

The system operates across two layers:

| Layer | Components |
|---|---|
| **Serverless AI Orchestration** | API Gateway → AWS Lambda (Procurement-Supervisor Agent) → Amazon S3 deployment |
| **Enterprise-Grade Data Processing** | Compliance-Validator, Inventory-Orchestrator, Contract-Supervisor sub-agents |

### Procurement-Supervisor Agent internals

| Module | Responsibility |
|---|---|
| Intent Analysis (LLM) | Parses raw procurement queries into structured intents |
| Task Delegation | Decides which sub-agent acts next |
| Sub-Agent Routing | Dispatches work and collects results |
| Data Synthesis | NumPy + Pydantic normalisation and ranking |
| Error Handling | Centralised retry and failure capture |
| Multi-Agent Orchestrator | Feedback loop that runs until the goal is reached |

### Sub-agents

| Agent | Responsibility |
|---|---|
| **Laptop-Finder Agent** | Discovers suppliers matching hardware specifications via MongoDB vector search |
| **Compliance-Validator Agent** | Verifies vendor certifications and safety compliance using Groq LLM |
| **Inventory-Orchestrator Agent** | Synchronises stock levels across internal ERP systems |
| **Contract-Supervisor Agent** | Manages RFQ scheduling and negotiation workflows |

## Repository Structure

```
procurement-agent/
├── main.py                              # Lambda entry point (LangGraph workflow)
├── requirements.txt
├── .env                                 # Local secrets (never committed)
│
├── agents/                              # All agent classes
│   ├── __init__.py
│   ├── supervisor.py                    # Procurement-Supervisor (orchestrator)
│   ├── laptop_finder.py                 # Laptop-Finder Agent
│   ├── compliance_validator.py          # Compliance-Validator Agent
│   ├── inventory_orchestrator.py        # Inventory-Orchestrator Agent
│   ├── contract_supervisor.py           # Contract-Supervisor Agent
│   └── registry.py                      # Seeds agent registry in MongoDB
│
├── core/                                # Supervisor internals
│   ├── intent_analysis.py               # LLM-based intent parsing
│   ├── task_delegation.py               # Next-agent decision logic
│   ├── data_synthesis.py                # NumPy/Pydantic ranking
│   ├── error_handling.py                # Centralised error capture
│   └── orchestrator.py                  # Multi-agent feedback loop
│
├── integrations/                        # External system connectors (aiohttp)
│   ├── supplier_api.py                  # External Supplier APIs
│   ├── erp_connector.py                 # Internal DBs / ERP Systems
│   ├── compliance_db.py                 # Compliance Databases
│   └── logistics_api.py                 # 3rd-Party Logistics
│
├── llm/
│   └── groq_client.py                   # Groq LLM wrapper with conversation memory
│
├── config/
│   └── config_manager.py                # AWS SSM Parameter Store / env-var loader
│
├── scripts/                             # Offline utilities (not deployed to Lambda)
│   ├── seed_data.py
│   ├── bulk_seed.py
│   ├── create_embeddings.py
│   ├── experience_collections_seed.py
│   ├── check_setup.py
│   ├── check_voyage_ai_setup.py
│   └── aws_check.py
│
├── tests/
│   └── test_search.py
│
├── infra/                               # Deployment tooling
│   ├── build_lambda.py
│   └── zip.py
│
└── docs/
    └── architecture.png                 # System architecture diagram
```

## Tech Stack

| Concern | Technology |
|---|---|
| Runtime | Python 3.12 / AWS Lambda |
| Orchestration | LangGraph |
| LLM | Groq (`llama-3.3-70b-versatile`) |
| Embeddings | Voyage AI (`voyage-3`) |
| Vector store | MongoDB Atlas (vector search indexes) |
| HTTP (async) | aiohttp |
| Data processing | NumPy, Pydantic |
| Cloud infra | AWS Lambda, S3, API Gateway, SSM Parameter Store |
| AWS SDK | Boto3 |

## Setup

### Prerequisites

- Python 3.12
- AWS account with Lambda, S3, API Gateway, and SSM Parameter Store access
- [Groq API key](https://console.groq.com/)
- [Voyage AI API key](https://www.voyageai.com/)
- MongoDB Atlas instance with vector search enabled

### Install dependencies

```bash
pip install -r requirements.txt
```

### Configure secrets

Set the following as environment variables or in AWS SSM Parameter Store (loaded automatically by `config/config_manager.py`):

| Key | Description |
|---|---|
| `GROQ_API_KEY` | Groq LLM API key |
| `VOYAGE_API_KEY` | Voyage AI embeddings key |
| `MONGODB_URI` | MongoDB Atlas connection string |
| `ERP_ENDPOINTS` | Comma-separated ERP base URLs |
| `SUPPLIER_API_URL` | External supplier API base URL |
| `COMPLIANCE_DB_URL` | Compliance database base URL |
| `LOGISTICS_API_URL` | 3rd-party logistics API base URL |

### Seed the database

```bash
python scripts/seed_data.py               # seed supplier records
python scripts/create_embeddings.py       # generate vector embeddings
python agents/registry.py                 # register sub-agents in MongoDB
```

### Deploy to AWS Lambda

```bash
python infra/build_lambda.py
```

The script packages the source into `procurbot_final.zip`, uploads it to the configured S3 bucket, and updates the Lambda function via the S3 URI.

## Usage

Invoke via API Gateway or directly as a Lambda test event:

```json
{
  "query": "Find suppliers for industrial laptops under £40,000 with ISO 9001 certification"
}
```

The supervisor routes the request through the sub-agent pipeline and returns:

```json
{
  "statusCode": 200,
  "body": {
    "recommendation": "Based on compliance validation and supplier discovery..."
  }
}
```

## License

MIT
