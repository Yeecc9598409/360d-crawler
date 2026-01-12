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
database.init_db()
scheduler.start_scheduler()

# --- 頁面設定 ---
st.set_page_config(
    page_title="360d | 智能數據儀表板",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS 優化 (Polished UI) ---
st.markdown("""
<style>
    /* Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700&family=Inter:wght@400;500;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', 'Noto Sans TC', sans-serif;
    }

    /* 背景與主色調 */
    .stApp {
        background-color: #f0f2f6;
    }
    
    /* 側邊欄 */
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        box-shadow: 2px 0 10px rgba(0,0,0,0.05);
    }
    
    /* 卡片樣式 */
    .css-card {
        background-color: #ffffff;
        padding: 2rem;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
        margin-bottom: 1.5rem;
        border: 1px solid #eef2f6;
    }

    /* 標題樣式 */
    h1, h2, h3 {
        color: #1a202c;
        font-weight: 700;
        letter-spacing: -0.02em;
    }
    h2 { font-size: 1.8rem; margin-bottom: 0.5rem; }
    p { color: #4a5568; line-height: 1.6; }

    /* 輸入框 Label 優化 */
    .stTextInput label, .stSelectbox label, .stNumberInput label {
        color: #2d3748 !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        margin-bottom: 0.25rem;
    }
    
    /* 按鈕樣式 (更現代的藍紫色) */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.6rem 2rem;
        border-radius: 10px;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(118, 75, 162, 0.3);
        transition: transform 0.2s, box-shadow 0.2s;
        width: 100%;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(118, 75, 162, 0.4);
        color: white;
    }
    .stButton > button:active {
        transform: translateY(0);
    }

    /* 訊息框 */
    .stAlert {
        border-radius: 10px;
        border: none;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    /* 分頁 Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        height: 3rem;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 4px;
        color: #718096;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: transparent;
        color: #5a67d8;
        border-bottom: 3px solid #5a67d8;
    }

</style>
""", unsafe_allow_html=True)

# --- 側邊欄 ---
with st.sidebar:
    st.title("⚙️ 設定與紀錄")
    
    # API Key Configuration
    st.subheader("🔑 API 金鑰設定")
    
    # 1. Try to load from Environment (Secure Mode)
    env_key = os.getenv("GEMINI_API_KEY")
    
    if env_key:
        st.success("✅ API Key 已從系統環境變數安全載入")
        api_key_input = env_key # Use the secure key
    else:
        # 2. Fallback to Manual Input (Dev Mode)
        st.warning("⚠️ 未偵測到環境變數，目前為手動模式")
        api_key_input = st.text_input(
            "Gemini API Key", 
            type="password",
            placeholder="請在此貼上您的 Key (僅供測試)",
            help="為了安全起見，正式部署請務必在 Zeabur/Docker 設定環境變數 GEMINI_API_KEY，此欄位將自動隱藏。"
        )
        if not api_key_input:
            st.caption("[👉 點此免費獲取 Key](https://aistudio.google.com/app/apikey)")
    
    st.divider()
    
    # History Log
    st.subheader("📜 最近執行紀錄")
    history_items = database.get_history(limit=5)
    
    if not history_items:
        st.caption("尚無資料")
    else:
        for item in history_items:
            ts = datetime.strptime(item['timestamp'], "%Y-%m-%d %H:%M:%S")
            time_str = ts.strftime("%m/%d %H:%M")
            status_color = "🟢" if item['status'] == 'success' else "🔴"
            
            with st.expander(f"{status_color} {time_str}"):
                st.write(f"**主題**: {item['topic']}")
                st.caption(f"網址: {item['url']}")
                st.caption(f"筆數: {item['summary']}")

# --- 主標題 ---
st.markdown("""
    <h1 style='text-align: center; margin-bottom: 2rem;'>
        🔭 360d 智能數據儀表板
    </h1>
""", unsafe_allow_html=True)

# Create Tabs
tab1, tab2 = st.tabs(["🚀 即時提取 (Instant Scrape)", "📅 定期排程 (Automation)"])

# --- TAB 1: 手動執行 ---
with tab1:
    st.markdown('<div class="css-card">', unsafe_allow_html=True)
    st.write("### 🎯 設定提取目標")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        target_url = st.text_input(
            "🌐 目標網址 (Website URL)", 
            value="https://www.roccrane.org.tw/",
            placeholder="請輸入完整網址，例如 https://example.com"
        )
    with col2:
        topic_options = {
            "News/Articles": "📰 新聞與文章列表",
            "Products/Pricing": "🏷️ 產品與價格表",
            "Company Info": "🏢 公司聯絡資訊"
        }
        topic = st.selectbox(
            "📂 提取類別 (Topic)",
            options=list(topic_options.keys()),
            format_func=lambda x: topic_options[x]
        )

    st.write("") # Spacer
    if st.button("✨ 開始智能分析 (Analyze Now)", type="primary"):
        if not api_key_input:
            st.warning("⚠️ 請先設定 API Key (建議使用環境變數)。")
        elif not target_url:
            st.warning("⚠️ 請輸入目標網址。")
        else:
            with st.status("🤖 AI 正在工作中...", expanded=True) as status:
                st.write("連線至網站...")
                time.sleep(0.5)
                st.write("讀取並清洗網頁內容...")
                # Call Scraper
                data, error = scraper.fetch_and_extract(target_url, topic, api_key_input)
                
                if error:
                    status.update(label="❌ 執行失敗", state="error", expanded=True)
                    st.error(f"錯誤代碼: {error}")
                    database.add_history(target_url, topic, [], status="failed")
                else:
                    status.update(label="✅ 分析完成！", state="complete", expanded=False)
                    database.add_history(target_url, topic, data, status="success")
                    
                    st.success(f"成功提取 {len(data)} 筆結構化數據")
                    
                    # Data Display
                    df = pd.DataFrame(data)
                    st.dataframe(df, use_container_width=True, hide_index=True)
                    
                    # Downloads
                    csv = df.to_csv(index=False).encode('utf-8-sig')
                    st.download_button(
                        "📥 下載 Excel/CSV",
                        data=csv,
                        file_name=f"360d_export_{int(time.time())}.csv",
                        mime="text/csv"
                    )
    st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 2: 自動化排程 ---
with tab2:
    st.markdown('<div class="css-card">', unsafe_allow_html=True)
    st.write("### ⏰ 新增自動化任務")
    st.info("設定排程後，系統將在背景自動監控此網頁，並定期將最新數據寄送給您。")
    
    with st.form("scheduler_form"):
        c1, c2 = st.columns(2)
        with c1:
            s_url = st.text_input("🔗 監控網址 (URL)", value=target_url)
            s_email = st.text_input("📧 通知信箱 (Email)", placeholder="name@company.com")
        with c2:
            s_topic = st.selectbox(
                "📂 監控類別 (Topic)", 
                options=list(topic_options.keys()), 
                format_func=lambda x: topic_options[x]
            )
            s_days = st.number_input("⏱️ 執行頻率 (每X天)", min_value=1, value=1, help="例如：輸入 1 代表每天執行一次")
        
        st.write("")
        submit_btn = st.form_submit_button("✅ 啟動排程 (Activate Schedule)")
        
        if submit_btn:
            if not s_email or "@" not in s_email:
                st.error("請輸入正確的 Email 格式")
            elif not api_key_input:
                st.error("排程需要 API Key 才能在背景執行，請先設定。")
            else:
                database.add_schedule(s_url, s_topic, s_email, s_days)
                st.success(f"已建立任務！將每 {s_days} 天監控一次並發送報告。")
                time.sleep(1)
                st.rerun()
    
    st.divider()
    
    st.subheader("📋 目前執行中的任務")
    conn = database.get_connection()
    jobs = conn.execute("SELECT * FROM schedules WHERE is_active=1 ORDER BY created_at DESC").fetchall()
    conn.close()
    
    if not jobs:
        st.caption("目前沒有排程任務")
    else:
        for job in jobs:
            with st.container():
                cols = st.columns([4, 2, 2, 1])
                cols[0].write(f"**{job['url']}**")
                cols[1].caption(f"類別: {job['topic']}")
                cols[2].caption(f"頻率: 每 {job['frequency_days']} 天")
                cols[3].caption("🟢 運行中")
                st.markdown("---")
    st.markdown('</div>', unsafe_allow_html=True)
