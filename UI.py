import streamlit as res_st
import pandas as pd
import plotly.express as px
import sqlite3
import requests
import json
import re

# 1. Page Configuration
res_st.set_page_config(
    page_title="AI Text-to-SQL Analytics",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. ฟังก์ชันยิงไปหา Local LLM บน Kaggle ผ่าน Ngrok
def ask_kaggle_llm(ngrok_url, system_prompt, user_prompt):
    if not ngrok_url:
        return None
    
    full_prompt = f"{system_prompt}\n\nUser Question: {user_prompt}\nSQL Query:"
    
    payload = {
        "model": "qwen2.5-coder:7b",
        "prompt": full_prompt,
        "stream": False,
        "options": {
            "temperature": 0.0  # ให้ผลลัพธ์คงที่และแม่นยำที่สุด
        }
    }
    
    try:
        url = ngrok_url.strip()
        if not url.endswith("/api/generate"):
            url = f"{url}/api/generate" if not url.endswith("/") else f"{url}api/generate"
            
        response = requests.post(url, json=payload, timeout=30)
        if response.status_code == 200:
            return response.json().get("response", "").strip()
        else:
            return f"Error: API ตอบกลับด้วย Status {response.status_code}"
    except Exception as e:
        return f"Error: ไม่สามารถเชื่อมต่อกับ Kaggle ได้ ({str(e)})"

# 3. ฟังก์ชันสำหรับล้างคำตอบของ AI ให้เหลือแต่ SQL เพียวๆ
def clean_sql_command(raw_response):
    if not raw_response:
        return ""
    sql_match = re.search(r"```sql(.*?)```", raw_response, re.DOTALL | re.IGNORECASE)
    if sql_match:
        return sql_match.group(1).strip()
    
    sql_match_v2 = re.search(r"```(.*?)```", raw_response, re.DOTALL)
    if sql_match_v2:
        return sql_match_v2.group(1).strip()
        
    return raw_response.replace(";", "").strip() + ";"

# 4. Sidebar Configuration
with res_st.sidebar:
    res_st.image("https://cdn-icons-png.flaticon.com/512/8653/8653130.png", width=50)
    res_st.title("⚙️ System Config")
    
    res_st.markdown("### 📊 Database Schema")
    res_st.info("""
    **Table: OnlineRetail**
    * `InvoiceNo` (TEXT)
    * `StockCode` (TEXT)
    * `Description` (TEXT)
    * `Quantity` (INTEGER)
    * `InvoiceDate` (TEXT)
    * `UnitPrice` (REAL)
    * `CustomerID` (TEXT)
    * `Country` (TEXT)
    """)
    
    res_st.markdown("---")
    res_st.markdown("### 🔌 API Connection")
    ngrok_input = res_st.text_input("Ngrok Backend URL:", value="", placeholder="https://xxxx.ngrok-free.app")
    
    res_st.markdown("---")
    res_st.caption("Developed by: Tontan Tipakun")
    res_st.caption("Tech Stack: Streamlit, Qwen2.5-Coder (Kaggle), SQLite (Local)")

# 5. Main UI Header
res_st.title("🤖 AI-Powered Text-to-SQL Dashboard")
res_st.markdown("*เปลี่ยนคำถามภาษาไทยให้เป็นคำสั่ง Database พร้อมสรุป Insight ในคลิกเดียว*")

# 6. Layout Setup
col_chat, col_result = res_st.columns([1, 1.2], gap="large")

with col_chat:
    res_st.subheader("💬 Ask Your Data")
    if "messages" not in res_st.session_state:
        res_st.session_state.messages = [{"role": "assistant", "content": "สวัสดีครับ! พิมพ์คำถามเกี่ยวกับยอดขายได้เลย เช่น 'ขอดูยอดขายรวมแยกตามประเทศ'"}]

    for msg in res_st.session_state.messages:
        with res_st.chat_message(msg["role"]):
            res_st.markdown(msg["content"])

    user_query = res_st.chat_input("พิมพ์คำถามภาษาไทยที่นี่...")

with col_result:
    res_st.subheader("📈 Automated Insights")
    result_container = res_st.container()

# 7. Core Logic & Execution Guard
if user_query:
    if not ngrok_input:
        res_st.warning("⚠️ กรุณากรอก Ngrok Backend URL ในแถบด้านซ้ายก่อนเริ่มใช้งาน")
    else:
        res_st.session_state.messages.append({"role": "user", "content": user_query})
        with col_chat:
            with res_st.chat_message("user"):
                res_st.markdown(user_query)

        # 7.1 เตรียม Prompt ส่งให้ AI เจน SQL
        system_prompt_sql = """You are an expert SQL developer. Generate ONLY a valid SQLite query based on the schema provided. 
        Do not provide any explanations, introductory text, or markdown code blocks.
        
        Database Schema:
        Table Name: OnlineRetail
        Columns: InvoiceNo (TEXT), StockCode (TEXT), Description (TEXT), Quantity (INTEGER), InvoiceDate (TEXT), UnitPrice (REAL), CustomerID (TEXT), Country (TEXT)
        
        Note: Total Sales calculation should be (Quantity * UnitPrice).
        """
        
        with col_chat:
            with res_st.chat_message("assistant"):
                with res_st.spinner("🧠 AI กำลังแปลภาษาไทยเป็น SQL..."):
                    raw_llm_response = ask_kaggle_llm(ngrok_input, system_prompt_sql, user_query)
                    sql_query = clean_sql_command(raw_llm_response)
                
                if "Error" in sql_query:
                    res_st.error(sql_query)
                else:
                    res_st.markdown("**Generated SQL Query:**")
                    res_st.code(sql_query, language="sql")
                    res_st.session_state.messages.append({"role": "assistant", "content": f"สร้าง SQL สำเร็จ:\n```sql\n{sql_query}\n```"})

        # 7.2 ดึงข้อมูลจริงจากไฟล์ที่ db.py สร้างขึ้น (online_retail.db)
        with col_result:
            if "Error" not in sql_query and sql_query:
                malicious_keywords = ["drop", "delete", "truncate", "update", "insert", "alter"]
                if any(word in sql_query.lower() for word in malicious_keywords):
                    res_st.error("⚠️ บล็อกคำสั่งอันตราย: ไม่อนุญาตให้แก้ไขฐานข้อมูล (Read-Only Only)")
                else:
                    with res_st.spinner("📊 กำลังดึงข้อมูลและวิเคราะห์อัตโนมัติ..."):
                        try:
                            # ดึงข้อมูลจากไฟล์ฐานข้อมูลจริงในโฟลเดอร์โปรเจกต์
                            conn = sqlite3.connect("online_retail.db")
                            df_result = pd.read_sql_query(sql_query, conn)
                            conn.close()
                            
                            if df_result.empty:
                                res_st.warning("ℹ️ ค้นพบข้อมูล แต่ไม่มีผลลัพธ์ตอบกลับจากฐานข้อมูล (Empty Dataset)")
                            else:
                                # วาดกราฟอัตโนมัติ
                                numeric_cols = df_result.select_dtypes(include=['number']).columns.tolist()
                                text_cols = df_result.select_dtypes(include=['object']).columns.tolist()
                                
                                if len(numeric_cols) > 0 and len(text_cols) > 0:
                                    fig = px.bar(
                                        df_result, 
                                        x=text_cols[0], 
                                        y=numeric_cols[0],
                                        title=f"Analysis: {numeric_cols[0]} by {text_cols[0]}",
                                        template="plotly_dark",
                                        color_discrete_sequence=["#00FFAA"]
                                    )
                                    res_st.plotly_chart(fig, use_container_width=True)
                                
                                # แสดงตารางข้อมูลดิบ
                                with res_st.expander("📂 ดูตารางข้อมูลดิบ (Raw Data)"):
                                    res_st.dataframe(df_result, use_container_width=True)
                                
                                # 7.3 ยิงให้ AI ช่วยสรุปความเห็นทางธุรกิจ (Insight)
                                system_prompt_insight = "You are a Senior Business Analyst. Summarize the following data results in Thai into 3 bullet points, focusing on business insights and recommendations."
                                user_prompt_insight = f"Data Table Results in JSON format:\n{df_result.head(10).to_json(orient='records')}"
                                
                                ai_insight = ask_kaggle_llm(ngrok_input, system_prompt_insight, user_prompt_insight)
                                if ai_insight and "Error" not in ai_insight:
                                    res_st.success(f"💡 **AI Automated Insight:**\n\n{ai_insight}")
                                    
                        except Exception as e:
                            res_st.error(f"❌ SQL Execution Error: ({str(e)})")