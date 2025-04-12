import pandas as pd
import numpy as np
import fitz  
import docx
import openai
import os
from PIL import Image
import base64
import io
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def process_file(uploaded_file):
    file_type = uploaded_file.name.split('.')[-1].lower()

    if file_type == "csv":
        df = pd.read_csv(uploaded_file)
        return df.apply(lambda row: f"{row['name']}: {row['description']}", axis=1).tolist()
    elif file_type == "pdf":
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        text = "\n".join([page.get_text() for page in doc])
        return text.split("\n\n")
    elif file_type == "docx":
        doc = docx.Document(uploaded_file)
        text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
        return text.split("\n\n")
    elif file_type == "txt":
        text = uploaded_file.read().decode("utf-8")
        return text.split("\n\n")
    else:
        return []

def embed_texts(text_list):
    try:
        response = openai.embeddings.create(
            input=text_list,
            model="text-embedding-3-small"
        )
        return [np.array(res.embedding) for res in response.data]
    except Exception as e:
        print("❌ Error in OpenAI embeddings:", e)
        return []

def get_openai_response(prompt, model="gpt-3.5-turbo"):
    try:
        response = openai.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("❌ Error generating OpenAI response:", e)
        return "There was an error generating the response."

def get_answer(question, docs, top_k=3, model="gpt-3.5-turbo"):
    if not docs:
        return "❌ No product catalog data found. Please upload files first.", []

    catalog_embeddings = embed_texts(docs)
    if not catalog_embeddings or len(catalog_embeddings) == 0 or all(e.size == 0 for e in catalog_embeddings):
        return "❌ No valid embeddings found for catalog.", []

    question_embedding = np.array(embed_texts([question])[0]).reshape(1, -1)

    try:
        sims = cosine_similarity(question_embedding, catalog_embeddings)[0]
    except ValueError as e:
        return f"❌ Similarity calculation failed: {e}", []

    top_indices = sims.argsort()[-top_k:][::-1]
    retrieved_docs = [docs[i] for i in top_indices]

    context = "\n".join(retrieved_docs)[:4000]

    prompt = f"""You are a product recommendation expert. Answer the question using the product catalog below.

- Mention specific product names if relevant.
- If multiple options, compare briefly.
- If nothing matches, say "Sorry, I couldn't find an exact match."

Product Catalog:
{context}

Question:
{question}

Answer:"""

    response = get_openai_response(prompt, model=model)
    return response, retrieved_docs

def categorize_chunks(chunks):
    categorized = []
    for chunk in chunks:
        prompt = f"Classify this product into a category like 'Racket', 'Shuttlecock', 'Apparel', etc.\n\nText:\n{chunk}\n\nCategory:"
        category = get_openai_response(prompt)
        categorized.append({"text": chunk[:100] + "...", "category": category})
    return categorized

def extract_text_from_image(uploaded_image):
    return "❌ Image understanding is not available. Please use text files instead (PDF, CSV, DOCX, or TXT)."

def translate_text(text, target_lang="English"):
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"Translate this into {target_lang}."},
                {"role": "user", "content": text}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("❌ Translation error:", e)
        return text
