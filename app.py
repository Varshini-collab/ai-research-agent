"""
AI Business Research Agent - Streamlit Dashboard
Run: streamlit run app.py
"""
import streamlit as st
import json
import time
from datetime import datetime

# Page config
st.set_page_config(
    page_title="AI Business Research Agent",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.main-title { font-size: 2rem; font-weight: 700; color: #1a1a2e; margin-bottom: 0; }
.sub-title  { font-size: 1rem; color: #6b7280; margin-top: 0; }
.metric-card {
    background: #f8fafc; border: 1px solid #e2e8f0;
    border-radius: 12px; padding: 1rem 1.25rem;
}
.tag {
    display: inline-block; background: #eff6ff; color: #1d4ed8;
    border-radius: 20px; padding: 2px 12px; font-size: 0.8rem;
    margin: 2px; font-weight: 500;
}
.source-link { font-size: 0.82rem; color: #6b7280; }
.stProgress > div > div > div { background-color: #4f46e5; }
</style>
""", unsafe_allow_html=True)


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Settings")
    st.markdown("---")

    model_options = ["llama3.2", "llama3.1", "mistral", "gemma2", "phi3"]
    selected_model = st.selectbox("🤖 Ollama Model", model_options, index=0)

    st.markdown("### Search Settings")
    max_results = st.slider("Results per query", 4, 15, 8)
    max_scrape = st.slider("Pages to scrape per query", 1, 5, 3)

    st.markdown("### Optional")
    bing_key = st.text_input("Bing API Key (optional)", type="password",
                              help="Leave blank to use DuckDuckGo only")

    st.markdown("---")
    st.markdown("### 🔌 Ollama Status")

    try:
        from agent.llm import is_ollama_running, list_models
        if is_ollama_running():
            st.success("✅ Ollama is running")
            models = list_models()
            if models:
                st.caption("Available: " + ", ".join(models[:5]))
        else:
            st.error("❌ Ollama not running")
            st.caption("Start with: `ollama serve`")
    except Exception:
        st.warning("⚠️ Cannot check Ollama")

    st.markdown("---")
    st.markdown("**AI Business Research Agent**")
    st.caption("Powered by Ollama + DuckDuckGo")


# ── Main Header ───────────────────────────────────────────────────────────────
st.markdown('<p class="main-title">🔍 AI Business Research Agent</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Market & Industry Analysis powered by Ollama (llama3.2) + Web Search</p>',
            unsafe_allow_html=True)
st.markdown("---")


# ── Search Input ──────────────────────────────────────────────────────────────
col_input, col_btn = st.columns([5, 1])
with col_input:
    topic = st.text_input(
        "Research Topic",
        placeholder="e.g.  Electric Vehicle market in India  |  Global SaaS industry  |  Renewable energy sector",
        label_visibility="collapsed",
    )
with col_btn:
    run_btn = st.button("🚀 Research", type="primary", use_container_width=True)

# Quick examples
st.caption("💡 Try: &nbsp; `EV market India` &nbsp;|&nbsp; `AI software industry 2025` &nbsp;|&nbsp; `Global fintech market`")


# ── Run Research ──────────────────────────────────────────────────────────────
if run_btn and topic.strip():

    # Import agent
    try:
        from agent import run as agent_run
    except ImportError as e:
        st.error(f"Import error: {e}. Make sure all agent files are in the `agent/` folder.")
        st.stop()

    # Progress display
    progress_bar = st.progress(0)
    status_text = st.empty()
    start_time = time.time()

    def update_progress(msg: str, pct: int):
        progress_bar.progress(pct)
        elapsed = time.time() - start_time
        status_text.markdown(f"⏳ **{msg}** &nbsp; `{elapsed:.1f}s`")

    st.markdown("---")

    with st.spinner(""):
        try:
            result = agent_run(
                topic=topic.strip(),
                model=selected_model,
                bing_api_key=bing_key or None,
                max_results=max_results,
                max_scrape=max_scrape,
                progress_callback=update_progress,
            )
        except Exception as e:
            st.error(f"Research failed: {str(e)}")
            st.exception(e)
            st.stop()

    progress_bar.progress(100)
    elapsed_total = time.time() - start_time
    status_text.markdown(f"✅ **Research complete** in `{elapsed_total:.1f}s`")

    research = result["research"]
    report = result["report"]
    plan = result["plan"]

    # Store in session state for persistence
    st.session_state["last_result"] = result
    st.session_state["last_topic"] = topic

    # ── KPI Row ───────────────────────────────────────────────────────────────
    st.markdown("### 📊 Research Summary")
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("📏 Market Size", research.get("market_size", "N/A")[:40] if research.get("market_size") else "N/A")
    k2.metric("🏢 Key Players", len(research.get("key_players", [])))
    k3.metric("📈 Trends Found", len(research.get("trends", [])))
    k4.metric("⚡ Opportunities", len(research.get("opportunities", [])))
    k5.metric("🔗 Sources", len(research.get("sources", [])))

    st.markdown("---")

    # ── Tabs ──────────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📄 Full Report", "📊 Insights", "🏢 Key Players", "📋 Raw Data", "🔗 Sources"
    ])

    # TAB 1 — Full Report
    with tab1:
        st.markdown("### 📄 Market Analysis Report")
        st.caption(f"Generated: {datetime.now().strftime('%d %b %Y, %H:%M')} | Model: {selected_model}")
        st.markdown("---")
        if report:
            st.markdown(report)
        else:
            st.warning("Report could not be generated.")

        # Download button
        st.download_button(
            "⬇️ Download Report (.md)",
            data=report,
            file_name=f"research_{topic[:30].replace(' ', '_')}.md",
            mime="text/markdown",
        )

    # TAB 2 — Insights
    with tab2:
        st.markdown("### 📊 Extracted Insights")

        col_l, col_r = st.columns(2)

        with col_l:
            st.markdown("#### 📈 Market Trends")
            trends = research.get("trends", [])
            if trends:
                for t in trends:
                    st.markdown(f"▸ {t}")
            else:
                st.caption("No trends found.")

            st.markdown("#### ⚡ Opportunities")
            opps = research.get("opportunities", [])
            if opps:
                for o in opps:
                    st.markdown(f"▸ {o}")
            else:
                st.caption("No opportunities found.")

        with col_r:
            st.markdown("#### ⚠️ Challenges & Risks")
            challenges = research.get("challenges", [])
            if challenges:
                for c in challenges:
                    st.markdown(f"▸ {c}")
            else:
                st.caption("No challenges found.")

            st.markdown("#### 📐 Statistics")
            stats = research.get("statistics", [])
            if stats:
                for s in stats:
                    st.markdown(f"▸ {s}")
            else:
                st.caption("No statistics found.")

        st.markdown("#### 🔮 Market Forecast")
        forecast = research.get("forecast", "")
        if forecast:
            st.info(forecast)
        else:
            st.caption("No forecast data found.")

        st.markdown("#### 🗺️ Research Plan Used")
        with st.expander("View query plan"):
            for q in plan.get("queries", []):
                st.markdown(f"**{q['focus'].title()}** → `{q['query']}`")

    # TAB 3 — Key Players
    with tab3:
        st.markdown("### 🏢 Key Industry Players")
        players = research.get("key_players", [])
        if players:
            cols = st.columns(3)
            for i, player in enumerate(players):
                cols[i % 3].markdown(
                    f'<span class="tag">🏢 {player}</span>',
                    unsafe_allow_html=True
                )
        else:
            st.caption("No key players extracted.")

        st.markdown("---")
        st.markdown("#### Market Size")
        ms = research.get("market_size", "Not available")
        st.info(f"💰 {ms}")

    # TAB 4 — Raw Data
    with tab4:
        st.markdown("### 📋 Raw Research Data (JSON)")
        st.caption("Complete structured data extracted by the agent.")
        # Remove the full sections to keep it readable
        display_data = {k: v for k, v in research.items() if k != "sections"}
        st.json(display_data)

        st.download_button(
            "⬇️ Download Raw Data (.json)",
            data=json.dumps(research, indent=2),
            file_name=f"data_{topic[:30].replace(' ', '_')}.json",
            mime="application/json",
        )

    # TAB 5 — Sources
    with tab5:
        st.markdown("### 🔗 Research Sources")
        sources = research.get("sources", [])
        if sources:
            for i, s in enumerate(sources, 1):
                title = s.get("title") or s.get("url", "Unknown")
                url = s.get("url", "")
                st.markdown(
                    f"{i}. [{title}]({url})" if url else f"{i}. {title}",
                    unsafe_allow_html=False,
                )
        else:
            st.caption("No sources recorded.")

elif run_btn and not topic.strip():
    st.warning("Please enter a research topic first.")


# ── Previous Result ───────────────────────────────────────────────────────────
elif "last_result" in st.session_state and not run_btn:
    st.info(f"💾 Showing last result: **{st.session_state.get('last_topic', '')}**  — Enter a new topic and click Research to refresh.")