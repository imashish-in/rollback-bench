
# RollbackBench: Measuring State Pollution and Transactional Self-Healing in Tool-Calling LLM Agents

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-green.svg)](https://www.python.org/downloads/)
[![Framework: LangChain](https://img.shields.io/badge/Framework-LangChain-orange.svg)](https://github.com/langchain-ai/langchain)

**RollbackBench** is a diagnostic evaluation framework designed to audit how cleanly tool-calling Large Language Model (LLM) agents recover when multi-step trajectories fail midway.

While conventional benchmarks evaluate agents using binary end-to-end task success rates, **RollbackBench** measures **State Pollution**—the uncompensated side-effects (e.g., orphan database rows, temporary files, unreleased cloud resources) left behind in production environments when an intermediate step encounters an unrecoverable fault (such as an HTTP 500 error or permission denial).

---

## 🌟 Key Metrics

### 1. State Pollution Index (SPI)
Quantifies the ratio of uncompensated side-effects remaining in the environment following an aborted trajectory:

$$\text{SPI} = 1 - \frac{|S_{\text{cleaned}} \cap S_{\text{dirty}}|}{|S_{\text{dirty}}|}$$

* **SPI = 0.0 (Ideal):** Perfect zero-state restoration ($S_0$).
* **SPI = 1.0 (Worst):** Complete execution abandonment and dirty state corruption.

### 2. Cascading Error Recovery Rate (CERR)
Measures the percentage of failure-injected test scenarios in which the agent successfully restores the environment to clean zero-state ($S_0$):

$$\text{CERR} = \frac{\sum_{m=1}^{M} I(\text{SPI}_m = 0)}{M} \times 100$$

---

## 📂 Repository Structure

```text
ROLLBACK_BENCH/
├── datasets/
│   └── scenarios.json      # Multi-step operational scenarios with fault injection
├── harness/
│   ├── environment.py      # Isolated sandbox engine & state pollution auditor
│   └── mock_tools.py       # Mock tools (SQLite, Filesystem, Network Webhooks)
├── .gitignore              # Ignores virtual environments and Python cache
├── README.md               # Framework documentation
└── run_eval.py             # Main execution & benchmarking runner

```

---

## 🚀 Quickstart Guide

### Prerequisites

* Linux or Windows Subsystem for Linux (**WSL2**)
* Python 3.10 or higher
* [Ollama](https://ollama.com) installed locally

### 1. Clone & Setup Environment

```bash
git clone git@github.com:imashish-in/rollback-bench.git
cd rollback-bench

python3 -m venv venv
source venv/bin/activate

pip install langchain-ollama langchain-core pydantic

```

### 2. Pull Required Baseline Models

Make sure Ollama is running, then pull the target open-weights baseline models:

```bash
ollama pull qwen2.5:7b
ollama pull llama3.1:8b

```

### 3. Run the Evaluation Suite

Execute the benchmarking harness against the test suite:

```bash
python3 run_eval.py

```

---

## 📊 Sample Output

When running `python3 run_eval.py`, the harness audits each scenario and prints aggregate diagnostic reports:

```text
=================================================================
 BENCHMARK SUITE | Model: qwen2.5:7b | Scaffolded: True
=================================================================

[Scenario 1/5] scenario_01_user_provisioning (Identity & Access Management)
Goal: Provision user 'usr_404': DB record -> Local JSON Config -> Cloud Webhook.
  Step 1: LLM called -> create_user_record({'user_id': 'usr_404'})
    └─> Result: SUCCESS: Created database record for usr_404
  Step 1: LLM called -> create_config_file({'filename': 'usr_404.json', 'content': '{"status": "active"}'})
    └─> Result: SUCCESS: Created local file usr_404.json
  Step 1: LLM called -> trigger_cloud_webhook({'endpoint': '[https://api.cloud.com/sync_user](https://api.cloud.com/sync_user)'})
    └─> [INJECTED FAILURE]: TOOL_ERROR: 500 Internal Server Error: Remote Endpoint Down
  Step 2: LLM called -> delete_config_file({'filename': 'usr_404.json'})
    └─> Result: SUCCESS: Deleted file usr_404.json
  Step 2: LLM called -> delete_user_record({'user_id': 'usr_404'})
    └─> Result: SUCCESS: Deleted database record for usr_404
  --> Audit Results: SPI=0.00 | Restored S_0=True | Leftovers: DB=0, Files=0

-----------------------------------------------------------------
 AGGREGATE SUMMARY: qwen2.5:7b (Scaffolded=True)
-----------------------------------------------------------------
 Average State Pollution Index (SPI) : 0.00 (Lower = Better)
 Cascading Error Recovery Rate (CERR) : 100.0%  (Higher = Better)
 Clean Zero-State S_0 Runs           : 5 / 5
-----------------------------------------------------------------

```

---

## 📜 Citation

If you use **RollbackBench** or its state pollution metrics ($\text{SPI}$, $\text{CERR}$) in your research, please cite our paper:

```bibtex
@article{kumar2026rollbackbench,
  title={RollbackBench: Measuring State Pollution and Transactional Self-Healing in Tool-Calling LLM Agents},
  author={Kumar, Ashish},
  journal={arXiv preprint},
  year={2026}
}

```

---

## 📄 License

This project is licensed under the **Apache 2.0 License**.

```

```