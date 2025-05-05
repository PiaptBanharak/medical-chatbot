import streamlit as st
import requests
import psycopg2
from sentence_transformers import SentenceTransformer
import json
import ollama

# Initialize sentence transformer
embedder = SentenceTransformer("BAAI/bge-m3")

# Database connection function
def get_conn():
    return psycopg2.connect(
        dbname="mydb",
        user="admin",
        password="1234",
        host="localhost",
        port="5432"
    )

# Query PostgreSQL for relevant documents based on query text
def query_postgresql(query_text, k=5):
    query_embedding = embedder.encode(query_text).tolist()
    conn = get_conn()
    cur = conn.cursor()
    query_embedding_str = "[" + ",".join(map(str, query_embedding)) + "]"
    sql_query = """
        SELECT content, embedding <=> %s::vector AS similarity_score
        FROM documents
        ORDER BY similarity_score ASC
        LIMIT %s;
    """
    cur.execute(sql_query, (query_embedding_str, k))
    results = cur.fetchall()
    cur.close()
    conn.close()
    return results

# Generate response by querying PostgreSQL and interacting with the Ollama API
def generate_response(query_text):
    retrieved_docs = query_postgresql(query_text)
    if not retrieved_docs:
        return "Sorry, I couldn't find relevant information in the database."
    
    context = "\n\n".join([f"- {doc[0]}" for doc in retrieved_docs])

    system_prompt = (
        "You are a professional and ethical medical doctor who provides accurate, safe, "
        "and easy-to-understand health advice to patients. When answering questions, you should use the patient’s medical records."
    )
   
    user_prompt = (
        f"Patient medical records:\n{context}\n\n"
        f"Question: {query_text}\n"
        f"Answer in Thai language."
    )
    response = requests.post(
        "http://localhost:11434/api/chat",
        json={
            "model": "llama3.2",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        }
    )
    if response.status_code == 200:
        try:
            contents = []
            for line in response.text.strip().splitlines():
                try:
                    obj = json.loads(line)
                    if "message" in obj and "content" in obj["message"]:
                        contents.append(obj["message"]["content"])
                except Exception:
                    continue
            return "".join(contents).strip() or "ขออภัย ไม่สามารถสรุปคำตอบได้"
        except Exception as e:
            return f"error: {str(e)}"
    else:
        return f"error: status code {response.status_code}"
# Streamlit UI
st.title("Medical Chatbot ")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input("พิมพ์คำถามของคุณที่นี่..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    with st.spinner("กำลังตอบ..."):
        try:
            reply = generate_response(prompt)
        except Exception as e:
            reply = f"เกิดข้อผิดพลาด: {e}"
    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.chat_message("assistant").write(reply)