# 🤖 Africa Code Assistant

**Offline AI Coding Assistant for African Developers**

[![ADTC 2026](https://img.shields.io/badge/ADTC-2026-blue)](https://africadeeptech.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green)](https://opensource.org/licenses/MIT)

---

## 🌍 Overview

Africa Code Assistant is a fully offline desktop application that brings AI-powered coding assistance to developers, students, and professionals across Africa. It runs on low-cost laptops (8GB RAM, no GPU) and supports **Hausa, Yoruba, and Igbo** languages.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 💻 **Code Generation** | Generate Python, Java, JavaScript, C++, SQL, HTML/CSS |
| 📖 **Code Explanation** | Line-by-line breakdown for beginners |
| 🐛 **Debugging** | Identify and fix syntax/logic errors |
| ⚡ **Optimization** | Improve performance and readability |
| 🔄 **Code Translation** | Between 10 programming languages |
| 📚 **RAG Documentation** | Offline search for Python, Pandas, NumPy |
| 🌍 **African Languages** | Hausa, Yoruba, Igbo UI |
| 🎯 **Quiz Mode** | Practice coding challenges |
| 📁 **Project Assistant** | Project structure and boilerplate |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- 8GB RAM (minimum)
- 4GB free disk space

### Installation

```bash
# Clone the repository
git clone https://github.com/reuben-adukson123/africa-code-assistant.git
cd africa-code-assistant

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download model
python scripts/download_model.py

# Build RAG index
python scripts/setup_rag_index.py

# Run the application
python run.py