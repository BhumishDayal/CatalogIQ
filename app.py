import os
import streamlit as st
from rag_engine import (
    process_file,
    get_answer,
    categorize_chunks,
    extract_text_from_image,
    translate_text,
    get_openai_response,
)

st.set_page_config(page_title="CatalogIQ", layout="wide")
st.title("🧠 CatalogIQ – A smart Product Catalog Assistant")

# About section
with st.expander("ℹ️ About this app"):
    st.markdown("""
Welcome to **CatalogIQ** – an AI-powered assistant for product catalogs.

**What it does:**
- 📄 Upload product files (PDF, CSV, DOCX, TXT)
- 🖼 Upload catalog screenshots for OCR
- 💬 Ask questions in any language
- 🤖 Receives smart follow-ups if needed
- 🌍 Get answers in your preferred language
- 📚 Sources shown from your own catalog

Made by **Bhumish Dayal**
    """)

# Session states
if "history" not in st.session_state:
    st.session_state.history = []
if "docs" not in st.session_state:
    st.session_state.docs = []
if "step" not in st.session_state:
    st.session_state.step = "question"
if "current_question" not in st.session_state:
    st.session_state.current_question = ""
if "clarification" not in st.session_state:
    st.session_state.clarification = ""
if "follow_up" not in st.session_state:
    st.session_state.follow_up = ""

# Sidebar
st.sidebar.title("⚙️ Settings")
top_k = st.sidebar.slider("Top Chunks to Retrieve", 1, 10, 3)
model = st.sidebar.selectbox("OpenAI Model", ["gpt-3.5-turbo", "gpt-4"])
lang = st.sidebar.selectbox("Language", ["English", "German", "Spanish", "French", "Hindi"])

# Layout
col1, col2 = st.columns([2, 3])

with col1:
    st.subheader("📤 Upload Files")
    uploaded_files = st.file_uploader("Upload .csv, .pdf, .docx, .txt", type=["csv", "pdf", "docx", "txt"], accept_multiple_files=True)
    uploaded_images = st.file_uploader("🖼 Upload Catalog Images", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

    all_chunks = []
    if uploaded_files:
        for file in uploaded_files:
            all_chunks.extend(process_file(file))
        st.session_state.docs = all_chunks
        st.success(f"✅ Loaded {len(uploaded_files)} file(s) successfully!")

    if uploaded_images:
        for image in uploaded_images:
            text = extract_text_from_image(image)
            all_chunks.append(text)
        st.session_state.docs.extend(all_chunks)
        st.success(f"🖼 Processed {len(uploaded_images)} image(s).")

    if st.button("🧠 Categorize Products"):
        categories = categorize_chunks(st.session_state.docs)
        st.markdown("### 🗂 Categorized Products")
        for cat in categories:
            st.markdown(f"- **{cat['category']}**: {cat['text']}")

    if st.button("🗑 Clear Chat"):
        st.session_state.history = []
        st.session_state.step = "question"
        st.session_state.current_question = ""
        st.session_state.clarification = ""
        st.session_state.follow_up = ""

with col2:
    st.subheader("💬 Ask About Your Products")

    if st.session_state.step == "question":
        with st.form("ask_form", clear_on_submit=False):
            user_question = st.text_input("Ask a question:", key="main_question_form")
            ask_clicked = st.form_submit_button("💬 Ask")

        if ask_clicked and user_question:
            translated = translate_text(user_question, target_lang="English")

            clarification_prompt = f"""You are a smart assistant.
The user asked: "{translated}"

If the question is vague, unclear, or could benefit from more context, return a clarifying question.
If it's clear, just return "None".

Clarifying Question:"""
            clarification = get_openai_response(clarification_prompt)

            st.session_state.current_question = user_question
            st.session_state.clarification = clarification
            st.session_state.step = "clarify" if clarification.lower() != "none" else "final_answer"
            st.rerun()

    elif st.session_state.step == "clarify":
        st.markdown(f"🤖 **Clarifying Question:** {st.session_state.clarification}")
        follow_up = st.text_input("🧠 Your answer:", key="clarify_input")
        if follow_up:
            st.session_state.follow_up = follow_up
            st.session_state.step = "final_answer"
            st.rerun()

    elif st.session_state.step == "final_answer":
        if not st.session_state.docs:
            st.error("❗ Please upload product catalog files before asking questions.")
        else:
            with st.spinner("Generating answer..."):
                q = translate_text(st.session_state.current_question, "English")
                fq = f"{q}\n\nExtra context: {st.session_state.follow_up}"
                answer, sources = get_answer(fq, st.session_state.docs, top_k=top_k, model=model)
                translated_answer = translate_text(answer, target_lang=lang)

                st.session_state.history.append({
                    "question": st.session_state.current_question,
                    "clarification": st.session_state.clarification if st.session_state.clarification.lower() != "none" else None,
                    "follow_up": st.session_state.follow_up if st.session_state.follow_up else None,
                    "answer": translated_answer,
                    "sources": sources
                })

                st.session_state.step = "question"
                st.session_state.current_question = ""
                st.session_state.clarification = ""
                st.session_state.follow_up = ""
                st.rerun()

    for i, chat in enumerate(reversed(st.session_state.history), 1):
        st.markdown(f"### Q{i}: {chat['question']}")
        if chat.get("clarification"):
            st.markdown(f"🧠 *Clarification:* {chat['clarification']}")
        if chat.get("follow_up"):
            st.markdown(f"🗣 *You answered:* {chat['follow_up']}")
        st.markdown(f"""
        <div style='background-color: #f0f2f6; padding: 1em; border-radius: 10px;'>
            {chat['answer']}
        </div>
        """, unsafe_allow_html=True)
        with st.expander("📚 Context Used"):
            for j, src in enumerate(chat["sources"], 1):
                st.markdown(f"**Chunk {j}:** {src}")

# Footer
st.markdown(
    "<hr style='margin-top: 2em;'>"
    "<div style='text-align: center; font-size: 0.9em; color: gray;'>"
    "Made by <strong>Bhumish Dayal</strong>"
    "</div>",
    unsafe_allow_html=True
)
