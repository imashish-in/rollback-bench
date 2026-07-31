# 🔄 RollbackBench

> **Measuring State Pollution and Transactional Self-Healing in Tool-Calling LLM Agents**

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![Ollama](https://img.shields.io/badge/Ollama-Local%20LLMs-orange)](https://ollama.ai/)

**RollbackBench** is an open-source evaluation benchmark designed to measure how autonomous LLM agents handle mid-trajectory execution failures. Unlike standard benchmarks that rely on binary pass/fail terminal gates, RollbackBench audits intermediate **State Pollution**—quantifying whether an agent leaves uncompensated database records, configuration files, or orphaned cloud resources behind when operations fail midway.

---

## 📌 Key Metrics

* **State Pollution Index ($\text{SPI}$):** Measures the proportion of uncompensated environment mutations remaining after an agent trajectory aborts ($0.00 = \text{Clean Zero-State } S_0$, $1.00 = \text{Total Pollution}$).
  $$\text{SPI} = 1 - \frac{\vert{}\mathcal{S}_{\text{cleaned}} \cap \mathcal{S}_{\text{dirty}}\vert{}}{\vert{}\mathcal{S}_{\text{dirty}}\vert{}}$$
* **Cascading Error Recovery Rate ($\text{CERR}$):** The percentage of failure-injected test scenarios in which the agent successfully restores the environment back to a clean state $S_0$.
  $$\text{CERR} = \frac{\sum_{m=1}^{M} \mathbb{I}(\text{SPI}_m = 0)}{M} \times 100\%$$

---

## 🏆 Multi-Model Benchmark Leaderboard

Evaluated across 5 multi-step operational domains (*Identity Provisioning*, *Database Backup*, *Telemetry Deployment*, *Batch Pipelines*, and *Credential Rotation*) under **Vanilla (Control)** and **Scaffolded (Remediation)** system prompting conditions:

| Model | Mode | Avg. SPI $\downarrow$ | CERR (%) $\uparrow$ | Clean $S_0$ Runs |
| :--- | :--- | :---: | :---: | :---: |
| **`Qwen-2.5-7B`** | Vanilla | **0.00** | **100.0%** | **5 / 5** |
| **`Qwen-2.5-7B`** | Scaffolded | **0.00** | **100.0%** | **5 / 5** |
| **`DeepSeek-R1-7B`** | Vanilla | **0.00** | **100.0%** | **5 / 5** |
| **`DeepSeek-R1-7B`** | Scaffolded | **0.00** | **100.0%** | **5 / 5** |
| **`Llama-3.1-8B`** | Vanilla | 0.20 | 80.0% | 4 / 5 |
| **`Llama-3.1-8B`** | Scaffolded | 0.80 | 20.0% | 1 / 5 |
| **`Mistral-7B`** | Vanilla | 0.33 | 60.0% | 3 / 5 |
| **`Mistral-7B`** | Scaffolded | 0.60 | 40.0% | 2 / 5 |

---

## 🚀 Quickstart

### 1. Prerequisites
Ensure you have **Python 3.10+** and **[Ollama](https://ollama.ai/)** installed and running locally.

### 2. Pull Evaluation Models
```bash
ollama pull qwen2.5:7b
ollama pull llama3.1:8b
ollama pull mistral:7b
ollama pull deepseek-r1:7b

```

### 3. Clone & Install Dependencies

```bash
git clone git@github.com:imashish-in/rollback-bench.git
cd rollback-bench
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

```

### 4. Run Benchmark Suite

```bash
python3 run_eval.py

```

---

## 📂 Repository Structure

```text
rollback-bench/
├── datasets/
│   └── scenarios.json         # Evaluation scenarios with failure injection specifications
├── harness/
│   └── environment.py         # Sandbox environment state auditor & SPI calculator
├── run_eval.py                # Multi-model evaluation sweep engine
├── requirements.txt           # Project dependencies
└── README.md                  # Benchmark documentation

```

---

## 📝 Citation

If you use **RollbackBench**, $\text{SPI}$, or $\text{CERR}$ in your research, please cite our paper:

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

This project is licensed under the **Apache-2.0 License**.

```

