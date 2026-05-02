# 🤖 Procurement-Supervisor Agent

A serverless AI-driven procurement orchestration agent designed to automate supplier discovery, compliance checks, and procurement workflows. Built for high performance using Python 3.12 and deployed on AWS Lambda.

## 🌟 Key Features

- **Intelligent Orchestration:** Dynamically interprets procurement requests and routes tasks to specialized sub-agents.
- **Supplier Discovery:** Automated search and validation of potential vendors based on specific criteria.
- **Serverless Architecture:** Fully event-driven deployment using AWS Lambda and S3.
- **Optimized Workflows:** Uses customized prompt engineering and memory management to handle complex supply chain queries.

## 🛠 Tech Stack

- **Language:** Python 3.12
- **Cloud Provider:** AWS (Lambda, S3, IAM)
- **Core Libraries:**
  - NumPy & Pydantic — Data Validation & Processing
  - Aiohttp & PyYAML — Asynchronous networking and configuration
  - Boto3 — AWS SDK integration

## 📁 Project Structure

```
procurement-agent/
├── main.py                        # Lambda entry point
├── supervisor.py                  # Orchestrator / supervisor agent
├── sourcer_agent.py               # Supplier discovery sub-agent
├── risk_analyst.py                # Risk & compliance analysis sub-agent
├── agent_registry.py              # Registry of available sub-agents
├── groq_llm.py                    # Groq LLM client wrapper
├── config_manager.py              # AWS SSM Parameter Store config loader
├── create_embeddings.py           # Embedding generation via Voyage AI
├── seed_data.py                   # Seed procurement data
├── bulk_seed.py                   # Bulk data seeding utility
├── experience_collections_seed.py # Experience/knowledge base seeding
├── build_lambda.py                # Lambda deployment build script
├── zip.py                         # Packaging utility
├── aws_check.py                   # AWS connectivity checker
├── check_setup.py                 # Environment setup validator
├── check_voyage_ai_setup.py       # Voyage AI setup validator
└── test_search.py                 # Search functionality tests
```

## ⚙️ Setup

### Prerequisites

- Python 3.12
- AWS account with Lambda, S3, and SSM Parameter Store access
- [Groq API key](https://console.groq.com/)
- [Voyage AI API key](https://www.voyageai.com/)
- MongoDB instance

### Install dependencies

```bash
pip install -r requirements.txt
```

### Configure secrets

Secrets are loaded from environment variables or AWS SSM Parameter Store via `config_manager.py`. Set the following:

| Key | Description |
|-----|-------------|
| `GROQ_API_KEY` | Groq LLM API key |
| `VOYAGE_API_KEY` | Voyage AI embeddings key |
| `MONGODB_URI` | MongoDB connection string |

### Deploy to AWS Lambda

```bash
python build_lambda.py
```

## 🚀 Usage

Invoke the Lambda function with a procurement request payload:

```json
{
  "query": "Find suppliers for industrial steel components under $50,000"
}
```

The supervisor agent routes the request to the appropriate sub-agents and returns a structured procurement report.

## 📄 License

MIT
