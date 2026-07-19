import streamlit as st
from pipeline import run_research_pipeline

from io import BytesIO

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
)

from reportlab.lib.styles import getSampleStyleSheet

# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="Multi-Agent Research System",
    page_icon="📄",
    layout="wide",
)

# ==========================================================
# SESSION STATE
# ==========================================================

DEFAULTS = {
    "messages": [],
    "logs": [],
    "running": False,
    "report": None,
    "feedback": None,
    "current_topic": "",
    "pipeline_finished": False,
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ==========================================================
# PDF GENERATOR
# ==========================================================


def generate_pdf(report: str, feedback: str):

    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer)

    styles = getSampleStyleSheet()

    story = []

    story.append(
        Paragraph(
            "Multi-Agent Research Report",
            styles["Title"],
        )
    )

    story.append(
        Paragraph(
            "<br/>",
            styles["BodyText"],
        )
    )

    story.append(
        Paragraph(
            report.replace("\n", "<br/>"),
            styles["BodyText"],
        )
    )

    story.append(
        Paragraph(
            "<br/><br/>",
            styles["BodyText"],
        )
    )

    story.append(
        Paragraph(
            "Critic Feedback",
            styles["Heading2"],
        )
    )

    story.append(
        Paragraph(
            feedback.replace("\n", "<br/>"),
            styles["BodyText"],
        )
    )

    doc.build(story)

    buffer.seek(0)

    return buffer


# ==========================================================
# AGENT CARD
# ==========================================================


def update_agent_card(
    container,
    icon,
    title,
    status,
    message,
):
    colors = {
        "waiting": "var(--secondary)",
        "running": "var(--primary)",
        "completed": "var(--success)",
        "error": "var(--error)",
    }

    container.markdown(
        f"""
    <div class="glass-card agent-card">
        <div class="agent-icon">{icon}</div>
        <div class="agent-info">
            <div class="agent-title">{title}</div>
            <div>
                <span class="agent-status status-{status}" style="color:{colors.get(status, 'var(--text-primary)')};">{status.upper()}</span>
            </div>
            <div class="agent-message">{message}</div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )


# ==========================================================
# CUSTOM CSS
# ==========================================================

st.markdown(
    """
<style>
:root {
  --background: #0f172a;
  --foreground: #f8fafc;
  --primary: #3b82f6;
  --primary-foreground: #ffffff;
  --secondary: #64748b;
  --secondary-foreground: #ffffff;
  --accent: #10b981;
  --accent-foreground: #ffffff;
  --destructive: #ef4444;
  --destructive-foreground: #ffffff;
  --border: rgba(255, 255, 255, 0.1);
  --input: rgba(255, 255, 255, 0.1);
  --ring: #3b82f6;
  --radius: 0.5rem;
}

.dark {
  --background: #0f172a;
  --foreground: #f8fafc;
  --primary: #3b82f6;
  --primary-foreground: #ffffff;
  --secondary: #64748b;
  --secondary-foreground: #ffffff;
  --accent: #10b981;
  --accent-foreground: #ffffff;
  --destructive: #ef4444;
  --destructive-foreground: #ffffff;
  --border: rgba(255, 255, 255, 0.1);
  --input: rgba(255, 255, 255, 0.1);
  --ring: #3b82f6;
  --radius: 0.5rem;
}

.stApp {
  background: var(--background);
  color: var(--foreground);
}

/* Glassmorphism card */
.glass-card {
  background: rgba(30, 41, 59, 0.5);
  backdrop-filter: blur(10px);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1.5rem;
  margin-bottom: 1rem;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.glass-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 32px rgba(0,0,0,0.2);
}

/* Agent card specific */
.agent-card {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.agent-icon {
  font-size: 1.5rem;
}

.agent-info {
  flex: 1;
}

.agent-title {
  font-weight: 600;
  margin-bottom: 0.25rem;
}

.agent-status {
  font-weight: 700;
  text-transform: uppercase;
  font-size: 0.875rem;
}

.agent-message {
  font-size: 0.875rem;
  color: var(--secondary-foreground);
}

/* Status colors */
.status-waiting { color: var(--secondary); }
.status-running {
  color: var(--primary);
  animation: pulse 2s infinite;
}
.status-completed { color: var(--accent); }
.status-error { color: var(--destructive); }

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.7; }
  100% { opacity: 1; }
}

/* Buttons */
.stButton>button {
  background: var(--primary);
  color: var(--primary-foreground);
  border: none;
  border-radius: var(--radius);
  padding: 0.5rem 1rem;
  font-weight: 600;
  transition: all 0.2s ease;
}

.stButton>button:hover {
  background: #2563eb;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(59,130,246,0.3);
}

.stButton>button:active {
  transform: translateY(0);
}

/* Download buttons */
.stDownloadButton>button {
  background: var(--secondary);
  color: var(--secondary-foreground);
}

.stDownloadButton>button:hover {
  background: #475569;
}

/* Inputs */
.stSelectbox>div>div {
  background: rgba(30, 41, 59, 0.5);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  color: var(--foreground);
}

.stSelectbox>div>div>div {
  color: var(--foreground);
}

.stChatInput>div>div>input {
  background: rgba(30, 41, 59, 0.5);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  color: var(--foreground);
}

.stChatInput>div>div>input:focus {
  box-shadow: 0 0 0 2px var(--primary);
}

/* Chat messages */
.stChatMessage {
  background: rgba(30, 41, 59, 0.5);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1rem;
  margin: 0.5rem 0;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Metrics */
[data-testid="stMetric"] {
  background: rgba(30, 41, 59, 0.5);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1rem;
}

/* Expander */
.streamlit-expanderHeader {
  background: rgba(30, 41, 59, 0.5);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  color: var(--foreground);
}

.streamlit-expanderContent {
  background: rgba(30,41,59,0.3);
  border-top: 1px solid var(--border);
}

/* Sidebar */
section[data-testid="stSidebar"] {
  background: rgba(15,23,42,0.8);
  backdrop-filter: blur(10px);
}

/* Header */
.main-header {
  text-align: center;
  padding: 2rem 0;
  background: linear-gradient(135deg, rgba(30,41,59,0.5), rgba(15,23,42,0.8));
  border-radius: var(--radius);
  margin-bottom: 2rem;
  backdrop-filter: blur(10px);
  border: 1px solid var(--border);
}

/* Footer */
.footer {
  text-align: center;
  color: var(--secondary-foreground);
  font-size: 0.875rem;
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border);
}

/* Tab styling */
.stTabs [data-baseweb="tab-list"] {
  gap: 8px;
}

.stTabs [data-baseweb="tab"] {
  background: rgba(30, 41, 59, 0.5);
  border-radius: var(--radius);
  padding: 0.5rem 1rem;
  color: var(--foreground);
}

.stTabs [aria-selected="true"] {
  background: var(--primary);
  color: white;
}

/* Additional utility classes */
.text-primary { color: var(--primary); }
.text-secondary { color: var(--secondary); }
.text-accent { color: var(--accent); }
.text-destructive { color: var(--destructive); }

.bg-primary { background: var(--primary); }
.bg-secondary { background: var(--secondary); }
.bg-accent { background: var(--accent); }
.bg-destructive { background: var(--destructive); }

.hover-lift {
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.hover-lift:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 32px rgba(0,0,0,0.2);
}
</style>
""",
    unsafe_allow_html=True,
)

# ==========================================================
# SIDEBAR
# ==========================================================

with st.sidebar:
    st.markdown('<div class="glass-card"><h2>⚙️ Settings</h2></div>', unsafe_allow_html=True)

    research_length = st.selectbox(
        "Research Length",
        [
            "Short",
            "Medium",
            "Long",
        ],
        index=1,
    )

    citation_style = st.selectbox(
        "Citation Style",
        [
            "APA",
            "MLA",
            "IEEE",
            "Chicago",
            "Harvard",
        ],
    )

    st.divider()

    st.markdown('<div class="glass-card"><h3>🤖 Agent Status</h3></div>', unsafe_allow_html=True)

    search_placeholder = st.empty()
    reader_placeholder = st.empty()
    writer_placeholder = st.empty()
    critic_placeholder = st.empty()

    update_agent_card(
        search_placeholder,
        "🔍",
        "Search Agent",
        "waiting",
        "Waiting...",
    )

    update_agent_card(
        reader_placeholder,
        "📖",
        "Reader Agent",
        "waiting",
        "Waiting...",
    )

    update_agent_card(
        writer_placeholder,
        "✍",
        "Writer Agent",
        "waiting",
        "Waiting...",
    )

    update_agent_card(
        critic_placeholder,
        "🧠",
        "Critic Agent",
        "waiting",
        "Waiting...",
    )

    st.divider()

    if st.button("🗑 Clear Conversation"):
        st.session_state.messages = []
        st.session_state.logs = []
        st.session_state.report = None
        st.session_state.feedback = None
        st.session_state.current_topic = ""
        st.session_state.running = False
        st.session_state.pipeline_finished = False
        st.rerun()

# ==========================================================
# MAIN HEADER
# ==========================================================

st.markdown(
    '''
    <div class="main-header">
        <h1>📄 Multi-Agent Research System</h1>
        <p>Research any topic using multiple AI agents.</p>
    </div>
    ''',
    unsafe_allow_html=True,
)

# ==========================================================
# LIVE LOG PANEL
# ==========================================================

st.subheader("📜 Live Pipeline Logs")
log_placeholder = st.empty()
log_placeholder.code(
    "\n".join(st.session_state.logs[-30:]),
    language="text",
)

# ==========================================================
# CHAT HISTORY
# ==========================================================

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ==========================================================
# USER INPUT
# ==========================================================

topic = st.chat_input("Ask me to research anything...")

if topic:
    st.session_state.current_topic = topic
    st.session_state.logs = []
    st.session_state.pipeline_finished = False
    st.session_state.messages.append(
        {
            "role": "user",
            "content": topic,
        }
    )
    st.session_state.running = True
    st.rerun()

# ==========================================================
# PROGRESS CALLBACK
# ==========================================================

def progress_callback(
    agent: str,
    status: str,
    message: str,
):
    """
    This callback is invoked by pipeline.py whenever an
    agent changes its state.
    """

    mapping = {
        "Search Agent": (
            search_placeholder,
            "🔍",
        ),
        "Reader Agent": (
            reader_placeholder,
            "📖",
        ),
        "Writer Agent": (
            writer_placeholder,
            "✍",
        ),
        "Critic Agent": (
            critic_placeholder,
            "🧠",
        ),
    }

    if agent in mapping:
        placeholder, icon = mapping[agent]
        update_agent_card(
            placeholder,
            icon,
            agent,
            status,
            message,
        )

    log_entry = (
        f"[{agent}] "
        f"{status.upper()} : "
        f"{message}"
    )

    st.session_state.logs.append(log_entry)

    # Keep only the latest logs
    st.session_state.logs = (
        st.session_state.logs[-100:]
    )

    log_placeholder.code(
        "\n".join(
            st.session_state.logs
        ),
        language="text",
    )


# ==========================================================
# PIPELINE EXECUTION
# ==========================================================

if (
    st.session_state.running
    and
    not st.session_state.pipeline_finished
):

    with st.chat_message("assistant"):
        status_box = st.empty()
        status_box.info("🚀 Starting research pipeline...")

        try:
            result = run_research_pipeline(
                topic=st.session_state.current_topic,
                research_length=research_length,
                citation_style=citation_style,
                progress_callback=progress_callback,
            )

            status_box.success("✅ Research completed successfully.")

            st.session_state.report = result.get("report", "")
            st.session_state.feedback = result.get("feedback", "")

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": "Research completed successfully.",
                }
            )

        except Exception as e:
            status_box.error(f"❌ Pipeline failed\n\n{e}")

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": f"Pipeline failed.\n\n{e}",
                }
            )
        finally:
            st.session_state.running = False
            st.session_state.pipeline_finished = True
            st.rerun()


# ==========================================================
# KEEP AGENT STATUS AFTER COMPLETION
# ==========================================================

if st.session_state.pipeline_finished:
    update_agent_card(
        search_placeholder,
        "🔍",
        "Search Agent",
        "completed",
        "Completed",
    )
    update_agent_card(
        reader_placeholder,
        "📖",
        "Reader Agent",
        "completed",
        "Completed",
    )
    update_agent_card(
        writer_placeholder,
        "✍",
        "Writer Agent",
        "completed",
        "Completed",
    )
    update_agent_card(
        critic_placeholder,
        "🧠",
        "Critic Agent",
        "completed",
        "Completed",
    )


# ==========================================================
# KEEP LOG WINDOW UPDATED
# ==========================================================

if st.session_state.logs:
    log_placeholder.code(
        "\n".join(
            st.session_state.logs
        ),
        language="text",
    )


# ==========================================================
# OUTPUT PLACEHOLDERS
# ==========================================================

report_container = st.container()
feedback_container = st.container()

# ==========================================================
# RESEARCH REPORT
# ==========================================================

if st.session_state.report:
    with report_container:
        st.markdown("---")
        st.header("📄 Research Report")
        st.markdown(st.session_state.report, unsafe_allow_html=False)
        st.markdown("")

        pdf = generate_pdf(
            st.session_state.report,
            st.session_state.feedback or "",
        )

        download_col1, download_col2 = st.columns(2)

        with download_col1:
            st.download_button(
                label="📄 Download PDF",
                data=pdf,
                file_name="research_report.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

        with download_col2:
            st.download_button(
                label="📝 Download Markdown",
                data=st.session_state.report,
                file_name="research_report.md",
                mime="text/markdown",
                use_container_width=True,
            )


# ==========================================================
# CRITIC FEEDBACK
# ==========================================================

if st.session_state.feedback:
    with feedback_container:
        st.markdown("---")
        st.header("🧠 Critic Feedback")
        st.success(st.session_state.feedback)


# ==========================================================
# SHOW CURRENT LOGS
# ==========================================================

if st.session_state.logs:
    with st.expander("📜 Complete Pipeline Logs", expanded=False):
        st.code("\n".join(st.session_state.logs), language="text")

# ==========================================================
# METRICS
# ==========================================================

if st.session_state.report:
    word_count = len(st.session_state.report.split())
    character_count = len(st.session_state.report)
    estimated_pages = max(1, round(word_count / 500, 1))

    st.markdown("---")
    metric1, metric2, metric3 = st.columns(3)

    metric1.metric("Words", f"{word_count:,}")
    metric2.metric("Characters", f"{character_count:,}")
    metric3.metric("Estimated Pages", f"{estimated_pages}")

# ==========================================================
# SIDEBAR STATUS SUMMARY
# ==========================================================

with st.sidebar:
    st.divider()
    st.subheader("📊 Session")
    st.write(f"Messages: **{len(st.session_state.messages)}**")
    st.write(f"Logs: **{len(st.session_state.logs)}**")
    if st.session_state.report:
        st.success("Latest research report available.")

# ==========================================================
# FOOTER
# ==========================================================

st.markdown("---")
st.markdown(
    """
<div class="footer">
Multi-Agent Research System<br>
Agents: 🔍 Search Agent • 📖 Reader Agent • ✍ Writer Agent • 🧠 Critic Agent<br>
Built with Streamlit + Python
</div>
""",
    unsafe_allow_html=True,
)