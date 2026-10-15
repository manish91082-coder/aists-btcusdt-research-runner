# 🤖 AISTS BTCUSDT Research Runner

> **AI-powered BTC/USDT research execution environment using GitHub Actions**

[![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-Enabled-2088FF?logo=github-actions&logoColor=white)](https://github.com/manish91082-coder/aists-btcusdt-research-runner/actions)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Public Repo](https://img.shields.io/badge/Visibility-Public-green)](https://github.com/manish91082-coder/aists-btcusdt-research-runner)

---

## 📋 Overview

This repository is a **dedicated GitHub Actions-powered Python research execution environment** for AISTS (AI-based Strategy & Trading System) BTCUSDT research tasks.

- ✅ Run Python scripts directly on GitHub's cloud infrastructure
- ✅ Schedule automated research jobs via cron
- ✅ Read and store results as GitHub Artifacts
- ✅ Full Actions permissions for maximum flexibility
- ✅ Completely isolated from other projects

---

## 🚀 Quick Start

### Run a Python Script via GitHub Actions

1. Go to **Actions** tab → Select a workflow → Click **Run workflow**
2. Pass your script/parameters as inputs
3. Download results from **Artifacts** section

### Available Workflows

| Workflow | Trigger | Description |
|----------|---------|-------------|
| `python-runner.yml` | Manual / Push | Run any Python research script |
| `btcusdt-research.yml` | Manual / Scheduled | BTCUSDT data fetch & analysis |
| `scheduled-runner.yml` | Cron (daily) | Automated daily research job |

---

## 📁 Repository Structure

```
aists-btcusdt-research-runner/
├── .github/
│   └── workflows/
│       ├── python-runner.yml        # General Python runner
│       ├── btcusdt-research.yml     # BTCUSDT specific research
│       └── scheduled-runner.yml     # Scheduled automation
├── scripts/
│   └── sample_research.py           # Sample research script
├── results/                         # Output artifacts stored here
├── requirements.txt                 # Python dependencies
├── README.md
└── LICENSE
```

---

## ⚙️ Configuration

### Secrets & Variables
Add these in **Settings → Secrets and variables → Actions**:

| Secret Name | Description |
|-------------|-------------|
| `BINANCE_API_KEY` | Binance API key (optional) |
| `BINANCE_SECRET` | Binance secret key (optional) |
| `TELEGRAM_BOT_TOKEN` | Telegram alerts (optional) |

### Permissions
This repo has **maximum GitHub Actions permissions** enabled:
- ✅ Read & Write for all scopes
- ✅ Allow all actions and reusable workflows
- ✅ Artifact uploads enabled
- ✅ GitHub Pages deployable

---

## 🔧 Usage Examples

### Manual Trigger
```yaml
# In any workflow, use workflow_dispatch with inputs
on:
  workflow_dispatch:
    inputs:
      script_name:
        description: 'Python script to run'
        required: true
```

### Scheduled Research
```yaml
on:
  schedule:
    - cron: '0 0 * * *'  # Daily at midnight UTC
```

---

## 📊 Results & Artifacts

- All outputs are saved as **GitHub Actions Artifacts** (retained 90 days)
- Results can be downloaded via Actions UI or `gh` CLI:

```bash
gh run download --repo manish91082-coder/aists-btcusdt-research-runner
```

---

## 🤝 Contributing

This is a personal research repository. Fork and adapt as needed.

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.
