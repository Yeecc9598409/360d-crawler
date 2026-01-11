import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime

# Local Modules
import database
import scraper
import scheduler
import mailer

# --- 初始化 (Backend) ---
# Ensure DB is ready
database.init_db()
# Start background scheduler
scheduler.start_scheduler()

# --- 頁面設定 ---
st.set_page_config(
    page_title="360d | 智能數據儀表板",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS 樣式 (Professional/ToughData Style) ---
st.markdown("""
<style>
    /* Import Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * { font-family: 'Inter', sans-serif; }
    
    /* Global Background */
    .stApp {
        background-color: #f8f9fa;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e9ecef;
    }
    
    /* Card Container */
    .css-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        margin-bottom: 1.5rem;
        border: 1px solid #e2e8f0;
    }

    /* Header Typography */
    h1, h2, h3 {
        color: #1e293b;
        font-weight: 700;
    }
    
    /* Custom Button (Red Accent) */
    .stButton > button {
        background-color: #ef4444; /* Red-500 */
        color: white;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        transition: all 0.2s;
    }
    .stButton > button:hover {
        background-color: #dc2626; /* Red-600 */
        box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
    }

    /* Metric Card */
    .metric-box {
        background: #f1f5f9;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        border: 1px solid #cbd5e1;
    }
    .metric-value { font-size: 1.5rem; font-weight: bold; color: #0f172a; }
    .metric-label { font-size: 0.8rem; color: #64748b; margin-top: 4px; }

</style>
""", unsafe_allow_html=True)

# --- 側邊欄 (設定 & 歷史) ---
with st.sidebar:
    st.image("https://img.icons8.com/color/96/data-configuration.png", width=64)
    st.title("360d 儀表板")
    st.markdown("---")
    
    # 1. API Configuration
    st.subheader("⚙️ 系統設定")
    env_key = os.getenv("GEMINI_API_KEY")
    api_key_input = st.text_input(
        "Gemini API Key", 
        value=env_key if env_key else "",
        type="password",
        placeholder="Enter key if not in .env"
    )
    if not api_key_input:
        st.warning("⚠️ 請輸入 API Key 以啟用功能")

    st.markdown("---")
    
    # 2. History Log
    st.subheader("📜 歷史紀錄")
    history_items = database.get_history(limit=10)
    
    if not history_items:
        st.info("尚無執行紀錄")
    else:
        for item in history_items:
            # Parse timestamp for display
            ts = datetime.strptime(item['timestamp'], "%Y-%m-%d %H:%M:%S")
            ts_str = ts.strftime("%m/%d %H:%M")
            status_emoji = "✅" if item['status'] == 'success' else "❌" if item['status'] == 'failed' else "🤖"
            
            with st.expander(f"{status_emoji} {ts_str} - {item['topic']}"):
                st.caption(f"URL: {item['url']}")
                st.caption(f"結果: {item['summary']}")
                st.json(item['data_json'], expanded=False)

# --- 主畫面 ---
st.markdown("## 🔍 智能數據提取 (Intelligent Extraction)")
st.markdown("透過 Gemini AI 自動從目標網頁提取結構化資訊。")

# Create Tabs
tab1, tab2 = st.tabs(["🚀 手動執行 (Manual)", "🤖 自動化排程 (Automation)"])

# --- TAB 1: 手動執行 ---
with tab1:
    with st.container():
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        col1, col2 = st.columns([3, 1])
        
        with col1:
            target_url = st.text_input(
                "目標網址 (Target URL)", 
                value="https://www.roccrane.org.tw/",
                placeholder="https://example.com"
            )
        
        with col2:
            topic = st.selectbox(
                "提取主題 (Topic)",
                options=["News/Articles", "Products/Pricing", "Company Info"],
                format_func=lambda x: {
                    "News/Articles": "📰 新聞/文章",
                    "Products/Pricing": "🏷️ 產品/價格",
                    "Company Info": "🏢 公司資訊"
                }[x]
            )
            
        if st.button("開始提取 (Start Scraping)", use_container_width=True):
            if not api_key_input:
                st.error("❌ 請先設定 API Key")
            elif not target_url:
                st.error("❌ 請輸入目標網址")
            else:
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Step 1
                status_text.text("正在連線至目標網站...")
                progress_bar.progress(30)
                
                # Step 2: Extract
                status_text.text("AI 正在分析內容 (請稍候)...")
                data, error = scraper.fetch_and_extract(target_url, topic, api_key_input)
                progress_bar.progress(90)
                
                if error:
                    st.error(f"執行失敗: {error}")
                    database.add_history(target_url, topic, [], status="failed")
                else:
                    progress_bar.progress(100)
                    st.success(f"成功提取 {len(data)} 筆資料！")
                    database.add_history(target_url, topic, data, status="success")
                    
                    # Store in session state for downloading (optional improvement)
                    st.session_state['last_data'] = data
                    
                    # Display Data
                    st.markdown("### 📊 提取結果")
                    df = pd.DataFrame(data)
                    st.dataframe(df, use_container_width=True)
                    
                    # Download Buttons
                    c1, c2 = st.columns(2)
                    with c1:
                        st.download_button(
                            "📥 下載 CSV",
                            data=df.to_csv(index=False).encode('utf-8-sig'),
                            file_name="360d_export.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
                status_text.empty()
        st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 2: 自動化排程 ---
with tab2:
    st.markdown('<div class="css-card">', unsafe_allow_html=True)
    st.markdown("### ⏱️ 設定定期提取任務")
    st.info("設定後，系統將在背景自動執行，並將結果寄送至指定信箱。")
    
    with st.form("schedule_form"):
        s_url = st.text_input("目標網址", value=target_url)
        s_topic = st.selectbox(
            "提取主題",
            ["News/Articles", "Products/Pricing", "Company Info"],
            key="sched_topic"
        )
        s_email = st.text_input("通知信箱 (Email)", placeholder="yourname@example.com")
        s_days = st.number_input("執行頻率 (天)", min_value=1, value=1)
        
        submitted = st.form_submit_button("📅 建立排程任務")
        
        if submitted:
            if not s_email or "@" not in s_email:
                st.error("請輸入有效的 Email 地址")
            else:
                database.add_schedule(s_url, s_topic, s_email, s_days)
                st.success(f"✅ 排程已建立！每 {s_days} 天將自動提取一次並寄信通知。")
                time.sleep(1)
                st.rerun()

    # Show Active Schedules
    st.divider()
    st.markdown("### 📋 執行中的任務")
    schedules = database.get_due_schedules() # This gets DUE ones, let's make a get_all helper? 
    # Actually for UI we want all active. 
    # Let's use raw SQL here for simplicity or add a helper. 
    # I'll add a quick inline fetch for display.
    
    conn = database.get_connection()
    active_scheds = conn.execute("SELECT * FROM schedules WHERE is_active=1 ORDER BY created_at DESC").fetchall()
    conn.close()
    
    if not active_scheds:
        st.text("目前無自訂排程。")
    else:
        for job in active_scheds:
            with st.container():
                c1, c2, c3, c4 = st.columns([3, 2, 2, 1])
                c1.markdown(f"**{job['url']}**")
                c2.caption(f"主題: {job['topic']}")
                c3.caption(f"每 {job['frequency_days']} 天 (下次: {job['next_run'][:10]})")
                c4.markdown("🟢 運行中")
                st.divider()

    st.markdown('</div>', unsafe_allow_html=True)
