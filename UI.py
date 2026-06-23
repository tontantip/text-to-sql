import streamlit as res_st
import pandas as pd
import plotly.express as px
import sqlite3
import requests
import os
import re

# 1. Page Configuration
res_st.set_page_config(page_title="AI Text-to-SQL Analytics", page_icon="🤖", layout="wide")

# 2. ฟังก์ชันยิงไปหา Local LLM บน Kaggle ผ่าน Ngrok
def ask_kaggle_llm(ngrok_url, system_prompt, user_prompt):
    if not ngrok_url: return None
    payload = {
        "model": "qwen2.5-coder:7b",
        "prompt": f"{system_prompt}\n\nUser Question: {user_prompt}\nSQL Query:",
        "stream": False,
        "options": {"temperature": 0.0}
    }
    try:
        url = ngrok_url.strip().rstrip('/')
        endpoint = f"{url}/api/generate"
        response = requests.post(endpoint, json=payload, timeout=45)
        if response.status_code == 200:
            return response.json().get("response", "").strip()
        return f"Error: API status {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"

# 3. ฟังก์ชันสำหรับล้าง SQL
def clean_sql_command(raw_response):
    # พยายามดึง SQL จาก markdown block ก่อน
    sql_match = re.search(r"```sql\s*(.*?)\s*```", raw_response, re.DOTALL | re.IGNORECASE)
    if sql_match: return sql_match.group(1).strip()
    
    # หากไม่เจอ ให้คืนค่าข้อความที่ได้มา (คาดหวังว่าเป็น SQL เลย)
    return raw_response.strip().replace("```", "")

# 4. Sidebar Configuration
with res_st.sidebar:
    res_st.title("⚙️ System Config")
    ngrok_input = res_st.text_input("Ngrok Backend URL:", placeholder="[https://xxxx.ngrok-free.app](https://xxxx.ngrok-free.app)")
    res_st.info("ตรวจสอบว่าไฟล์ `online_retail.db` อยู่ในโฟลเดอร์เดียวกับสคริปต์")

# 5. Main UI
res_st.title("🤖 AI-Powered Text-to-SQL")

if "messages" not in res_st.session_state:
    res_st.session_state.messages = [{"role": "assistant", "content": "สวัสดีครับ! ถามข้อมูลขายได้เลย"}]

for msg in res_st.session_state.messages:
    with res_st.chat_message(msg["role"]):
        res_st.markdown(msg["content"])

if user_query := res_st.chat_input("ถามคำถามของคุณ..."):
    if not ngrok_input:
        res_st.warning("⚠️ กรุณากรอก Ngrok URL")
    else:
        res_st.session_state.messages.append({"role": "user", "content": user_query})
        with res_st.chat_message("user"): res_st.markdown(user_query)

        # Generate SQL
        system_prompt = "You are a SQL expert. Return ONLY valid SQLite SQL query. No explanation."
        with res_st.spinner("🧠 Generating SQL..."):
            raw_res = ask_kaggle_llm(ngrok_input, system_prompt, user_query)
            sql_query = clean_sql_command(raw_res)

        # Execute
        if not os.path.exists("online_retail.db"):
            res_st.error("❌ ไม่พบไฟล์ฐานข้อมูล online_retail.db")
        elif any(k in sql_query.lower() for k in ["drop", "delete", "insert", "update"]):
            res_st.error("⚠️ ห้ามใช้คำสั่งแก้ไขฐานข้อมูล")
        else:
            try:
                conn = sqlite3.connect("online_retail.db")
                df = pd.read_sql_query(sql_query, conn)
                conn.close()
                
                res_st.code(sql_query, language="sql")
                
                if not df.empty:
                    st_col1, st_col2 = res_st.columns([1, 1])
                    with st_col1:
                        res_st.dataframe(df)
                    with st_col2:
                        if len(df.columns) >= 2:
                            fig = px.bar(df, x=df.columns[0], y=df.columns[1])
                            res_st.plotly_chart(fig, use_container_width=True)
                else:
                    res_st.warning("ไม่พบข้อมูล")
            except Exception as e:
                res_st.error(f"SQL Error: {e}")