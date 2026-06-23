import streamlit as st
import pandas as pd
import plotly.express as px
import time

# --------------------------------------------
# 1. Page Configuration (ต้องอยู่บรรทัดแรกเสมอ)
# --------------------------------------------
st.set_page_config(
    page_title="AI Text-to-SQL Analytics",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------
# 2. Mockup Data (ใช้สำหรับโชว์ Demo ระหว่างรอต่อ API จริง)
# --------------------------------------------
def generate_mock_data():
    return pd.DataFrame({
        "Country": ["United Kingdom", "Germany", "France", "EIRE", "Spain"],
        "Total_Sales": [85000, 32000, 28000, 15000, 9500],
        "Total_Orders": [120, 45, 38, 20, 12]
    })

# --------------------------------------------
# 3. Sidebar: Database Schema & Setup
# --------------------------------------------
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/8653/8653130.png", width=50) # ไอคอน AI Database
    st.title("⚙️ System Config")
    
    # ส่วนแสดง Schema ให้ User ทราบ
    st.markdown("### 📊 Database Schema")
    st.info("""
    **Table: OnlineRetail**
    * `InvoiceNo` (TEXT)
    * `StockCode` (TEXT)
    * `Description` (TEXT)
    * `Quantity` (INTEGER)
    * `InvoiceDate` (DATETIME)
    * `UnitPrice` (REAL)
    * `CustomerID` (TEXT)
    * `Country` (TEXT)
    """)
    
    st.markdown("---")
    st.markdown("### 🔌 API Connection")
    backend_url = st.text_input("Ngrok Backend URL:", value="https://your-ngrok-url.app")
    
    st.markdown("---")
    st.caption("Developed by: Tontan Tipakun")
    st.caption("Tech Stack: Streamlit, Qwen2.5-Coder, SQLite")

# --------------------------------------------
# 4. Main Interface: Header
# --------------------------------------------
st.title("🤖 AI-Powered Text-to-SQL")
st.markdown("*เปลี่ยนคำถามภาษาไทยให้เป็นคำสั่ง Database พร้อมสรุป Insight ในคลิกเดียว*")

# --------------------------------------------
# 5. Chat & Execution Interface
# --------------------------------------------
# สร้าง 2 คอลัมน์ (ซ้าย: แชทถามตอบ | ขวา: ผลลัพธ์กราฟและตาราง)
col_chat, col_result = st.columns([1, 1.2], gap="large")

with col_chat:
    st.subheader("💬 Ask Your Data")
    
    # กล่องข้อความแชทประวัติ
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "สวัสดีครับ! พิมพ์คำถามเกี่ยวกับยอดขาย (Online Retail) ให้ผมช่วยเขียน SQL และวิเคราะห์ข้อมูลได้เลยครับ"}]

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # รับ Input จากผู้ใช้
    user_query = st.chat_input("เช่น 'ขอดูยอดขายรวม 5 อันดับแรกแบ่งตามประเทศ'")

with col_result:
    st.subheader("📈 Automated Insights")
    result_container = st.container()

# --------------------------------------------
# 6. Core Execution Logic
# --------------------------------------------
if user_query:
    # 6.1 แสดงคำถามผู้ใช้
    st.session_state.messages.append({"role": "user", "content": user_query})
    with col_chat:
        with st.chat_message("user"):
            st.markdown(user_query)

    # 6.2 กระบวนการประมวลผล (จำลอง)
    with col_chat:
        with st.chat_message("assistant"):
            with st.spinner("🧠 AI กำลังคิด SQL Query..."):
                time.sleep(1.5) # จำลองเวลาที่ LLM รันบน Kaggle
                
                # จำลอง SQL ที่ได้จาก LLM
                mock_sql = """
                SELECT Country, SUM(Quantity * UnitPrice) as Total_Sales, COUNT(DISTINCT InvoiceNo) as Total_Orders
                FROM OnlineRetail
                GROUP BY Country
                ORDER BY Total_Sales DESC
                LIMIT 5;
                """
                st.markdown("**Generated SQL Query:**")
                st.code(mock_sql, language="sql")
                st.session_state.messages.append({"role": "assistant", "content": f"รันคำสั่ง SQL เสร็จสิ้น:\n```sql\n{mock_sql}\n```"})

    # 6.3 แสดงผลลัพธ์ Dashboard
    with result_container:
        with st.spinner("📊 กำลังสร้าง Visualization..."):
            time.sleep(1) # จำลองเวลาดึงข้อมูลจาก SQLite
            df_result = generate_mock_data()
            
            # วาดกราฟด้วย Plotly
            fig = px.bar(
                df_result, 
                x="Country", 
                y="Total_Sales", 
                color="Country",
                title="Top 5 Countries by Total Sales",
                template="plotly_dark" # บังคับให้กราฟเป็นตีมมืดเข้ากับเว็บ
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # แสดง Data Table (ซ่อนใน Expander เพื่อความสะอาดตา)
            with st.expander("📂 ดูตารางข้อมูลดิบ (Raw Data)"):
                st.dataframe(df_result, use_container_width=True)
            
            # AI Insight สรุปผล
            st.success("💡 **AI Insight:** ยอดขายส่วนใหญ่มาจาก United Kingdom อย่างมีนัยสำคัญ โดยมีสัดส่วนสูงกว่าประเทศอันดับสอง (Germany) เกือบ 3 เท่าตัว ควรพิจารณาเจาะตลาดหรือทำแคมเปญพิเศษรักษาฐานลูกค้าใน UK เป็นอันดับแรก")