# 🧠 CatalogIQ – AI-Powered Product Catalog Assistant

**CatalogIQ** is a smart assistant that helps users query product catalogs using natural language. It supports multi-language questions, categorizes product data, and provides source-backed answers using Retrieval-Augmented Generation (RAG) with OpenAI.

---

## ✨ Features

- 📄 Upload and analyze product files: PDF, CSV, DOCX, TXT  
- 🖼 Upload catalog screenshots (OCR support planned)  
- 💬 Ask product-related questions in **any language**  
- 🌐 Multilingual support for inputs and outputs  
- 📚 View exact source chunks used for each response  
- 🗂 Auto-categorize catalog items (e.g., Racket, Apparel)

---

## 🚀 Quick Start

### 1. Clone the Repo
```bash
git clone https://github.com/your-username/catalogiq.git
cd catalogiq
```

### 2. Setting up the enviornment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

```
### 3. API Key
**Add your OPENAI_API_KEY in the .env file**
```

```
### 4. Run the app
**Streamlit run app.py**
```