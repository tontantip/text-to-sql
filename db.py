import sqlite3
import pandas as pd
from datetime import datetime, timedelta

def create_database():
    database_name = "online_retail.db"
    print(f"📦 กำลังตั้งค่าฐานข้อมูล: {database_name}...")
    
    # 1. เชื่อมต่อฐานข้อมูล (หากยังไม่มีไฟล์ ระบบจะสร้างให้ใหม่อัตโนมัติ)
    conn = sqlite3.connect(database_name)
    cursor = conn.cursor()
    
    # 2. สร้างตาราง OnlineRetail ตาม Schema ที่ส่งให้ AI
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS OnlineRetail (
        InvoiceNo TEXT,
        StockCode TEXT,
        Description TEXT,
        Quantity INTEGER,
        InvoiceDate TEXT,
        UnitPrice REAL,
        CustomerID TEXT,
        Country TEXT
    )
    """)
    
    # 3. จัดเตรียมข้อมูลจำลอง (Mock Data) ที่มีความหลากหลายเพื่อให้ AI ได้ลอง Query สนุกๆ
    # จำลองวันที่ย้อนหลังเพื่อให้มีมิติเรื่องของเวลา (Time-series)
    today = datetime.now()
    
    mock_records = [
        # United Kingdom (ยอดขายหลัก)
        ("536365", "85123A", "WHITE HANGING HEART T-LIGHT HOLDER", 6, (today - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S"), 2.55, "17850", "United Kingdom"),
        ("536365", "71053", "WHITE METAL LANTERN", 6, (today - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S"), 3.39, "17850", "United Kingdom"),
        ("536366", "22633", "HAND WARMER UNION JACK", 8, (today - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"), 1.85, "17850", "United Kingdom"),
        ("536367", "84879", "ASSORTED COLOUR BIRD LIGHTS", 32, today.strftime("%Y-%m-%d %H:%M:%S"), 1.69, "13047", "United Kingdom"),
        
        # Germany
        ("536527", "22809", "SET OF 6 T-LIGHTS SANTA", 6, (today - timedelta(days=5)).strftime("%Y-%m-%d %H:%M:%S"), 2.95, "12662", "Germany"),
        ("536527", "84945", "MULTI COLOUR SILVER T-LIGHT HOLDER", 12, (today - timedelta(days=5)).strftime("%Y-%m-%d %H:%M:%S"), 0.85, "12662", "Germany"),
        
        # France
        ("536370", "22728", "ALARM CLOCK BAKELIKE PINK", 24, (today - timedelta(days=4)).strftime("%Y-%m-%d %H:%M:%S"), 3.75, "12583", "France"),
        ("536370", "22727", "ALARM CLOCK BAKELIKE RED", 24, (today - timedelta(days=4)).strftime("%Y-%m-%d %H:%M:%S"), 3.75, "12583", "France"),
        
        # EIRE (Ireland)
        ("536544", "21773", "DECORATIVE ROSE BATHROOM BOTTLE", 4, (today - timedelta(days=3)).strftime("%Y-%m-%d %H:%M:%S"), 2.51, "14911", "EIRE"),
        
        # Spain
        ("536944", "22383", "LUNCH BAG SUKI DESIGN", 10, (today - timedelta(days=10)).strftime("%Y-%m-%d %H:%M:%S"), 1.65, "12557", "Spain")
    ]
    
    # แปลงเป็น DataFrame และบันทึกลง SQL Table
    df = pd.DataFrame(mock_records, columns=[
        "InvoiceNo", "StockCode", "Description", "Quantity", 
        "InvoiceDate", "UnitPrice", "CustomerID", "Country"
    ])
    
    # นำข้อมูลใส่ตาราง (if_exists='replace' หมายถึงจะเขียนทับข้อมูลเก่าทุกครั้งที่รันไฟล์นี้ใหม่)
    df.to_sql("OnlineRetail", conn, if_exists="replace", index=False)
    
    # 4. ทดลองดึงข้อมูลขึ้นมาตรวจสอบเพื่อความมั่นใจ
    print("✅ บันทึกข้อมูลเข้าตาราง OnlineRetail เรียบร้อยแล้ว!")
    print("\n--- ตัวอย่างข้อมูล 3 แถวแรกใน Database ---")
    check_df = pd.read_sql_query("SELECT * FROM OnlineRetail LIMIT 3;", conn)
    print(check_df)
    
    # ปิดการเชื่อมต่อ
    conn.close()
    print("\n🔒 ปิดการเชื่อมต่อฐานข้อมูลสำเร็จ พร้อมใช้งานร่วมกับ Streamlit แล้วครับ")

if __name__ == "__main__":
    create_database()