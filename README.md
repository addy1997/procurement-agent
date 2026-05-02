# Procurement-Supervisor Agent

A serverless AI-driven procurement orchestration system deployed on AWS Lambda (Python 3.12). A multi-agent supervisor routes incoming procurement requests to specialised sub-agents for supplier discovery, compliance validation, inventory synchronisation, and contract negotiation.

## Architecture

![System Architecture](https://github.com/addy1997/procurement-agent/blob/main/docs/System_Architecture.png)

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

### Install git hooks (one-time, after cloning)

```bash
bash scripts/setup_hooks.sh
```

This installs a pre-commit hook that blocks accidental commits of `.env` files and `venv/` directories.

### Get your API keys

You need accounts and API keys from three services before running anything locally. The project does **not** ship any keys — you must supply your own.

| Service | Where to get your key | Used for |
|---|---|---|
| **Groq** | [console.groq.com](https://console.groq.com/) → API Keys | LLM inference (free tier available) |
| **Voyage AI** | [dashboard.voyageai.com](https://dashboard.voyageai.com/) → API Keys | Text embeddings (free tier: 200M tokens) |
| **MongoDB Atlas** | [cloud.mongodb.com](https://cloud.mongodb.com/) → Database → Connect | Vector store + task persistence (free M0 cluster available) |

> **Voyage AI free tier note:** the free plan allows 3 requests per minute. The supervisor already inserts a 22-second cooldown between embedding calls to stay within this limit. If you upgrade to a paid plan you can reduce or remove those sleeps in `agents/supervisor.py`.

### Create your `.env` file

Create a file named `.env` in the project root (it is git-ignored and will never be committed):

```bash
cp .env.example .env   # if .env.example exists, or create from scratch:
touch .env
```

Then open `.env` and fill in your keys:

```dotenv
# .env — never commit this file

# Groq (https://console.groq.com/keys)
GROQ_API_KEY=gsk_...

# Voyage AI (https://dashboard.voyageai.com/api-keys)
VOYAGE_API_KEY=pa-...

# MongoDB Atlas connection string
# Format: mongodb+srv://<user>:<password>@<cluster>.mongodb.net/?appName=<app>
MONGODB_URI=mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/?appName=Cluster0

# Optional — only needed for integrations/erp_connector.py
ERP_ENDPOINTS=https://erp1.example.com,https://erp2.example.com

# Optional — only needed for integrations/supplier_api.py
SUPPLIER_API_URL=https://api.supplier-directory.example.com
SUPPLIER_API_KEY=

# Optional — only needed for integrations/compliance_db.py
COMPLIANCE_DB_URL=https://compliance.example.com
COMPLIANCE_DB_KEY=

# Optional — only needed for integrations/logistics_api.py
LOGISTICS_API_URL=https://logistics.example.com
LOGISTICS_API_KEY=
```

The application loads this file automatically via `python-dotenv`. On AWS Lambda, set these as Lambda environment variables or store them in SSM Parameter Store — `config/config_manager.py` checks environment variables first, then falls back to SSM.

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

## Running Locally

### 1. Clone the repository

```bash
git clone https://github.com/addy1997/procurement-agent.git
cd procurement-agent
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Install git hooks (one-time)

```bash
bash scripts/setup_hooks.sh
```

### 5. Create your `.env` file

```bash
cp .env.example .env
```

Open `.env` and fill in your Groq API key, Voyage AI API key, and MongoDB URI (see [Get your API keys](#get-your-api-keys) below).

### 6. Seed the database (first run only)

This populates MongoDB with supplier records, generates vector embeddings, and registers the sub-agents. You need a working `.env` before running these.

```bash
python scripts/seed_data.py               # insert supplier records
python scripts/create_embeddings.py       # generate and store embeddings
python agents/registry.py                 # register sub-agents in MongoDB
```

### 7. Run the agent

**Full pipeline** (Laptop-Finder → Compliance-Validator → synthesis):

```bash
python agents/supervisor.py
```

**Interactive chatbot** (single-turn RAG over the supplier database):

```bash
python llm/groq_client.py
```

Type your query at the `You:` prompt. Type `exit` to quit.

**Simulate a Lambda invocation** locally:

```bash
python -c "
from agents.supervisor import lambda_handler
import json
result = lambda_handler({'query': 'Find laptop suppliers in London'}, None)
print(json.loads(result['body'])['recommendation'])
"
```

### Rate limits on the free tier

Voyage AI's free plan allows **3 requests per minute**. The supervisor inserts a 22-second cooldown between embedding calls automatically — expect each full pipeline run to take about 45–60 seconds.

---

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
