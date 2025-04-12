import openai
import os
import numpy as np
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def embed_texts(text_list):
    try:
        response = openai.embeddings.create(
            input=text_list,
            model="text-embedding-3-small"
        )
        return [np.array(res.embedding) for res in response.data]

    except Exception as e:
        print("❌ Error in OpenAI embeddings:", e)
        return [np.zeros(1536) for _ in text_list]

def get_openai_response(prompt):
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
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
