import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="A Genenerative AI Initiative for Report Doc Assistant", layout="wide")

# ---------------- SESSION STATE ----------------
if "token" not in st.session_state:
    st.session_state.token = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ---------------- LOGIN ----------------
if not st.session_state.token:
    st.title("Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        try:
            res = requests.post(
                f"{API_URL}/login",
                json={
                    "username": username.strip(),
                    "password": password.strip()
                }
            )

            data = res.json()

            if "token" in data:
                st.session_state.token = data["token"]
                st.success("Login successful!")
                st.rerun()
            else:
                st.error(data.get("error", "Login failed"))

        except Exception as e:
            st.error(f"Error: {e}")

    st.stop()

# ---------------- MAIN UI ----------------
st.title("A Genenerative AI Initiative for Report Doc Assistant")

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.header("Upload PDF")

    uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

    if uploaded_file:
        try:
            files = {"file": uploaded_file}
            res = requests.post(f"{API_URL}/upload", files=files)

            if res.status_code == 200:
                st.success("Uploaded successfully")
            else:
                st.error("Upload failed")

        except Exception as e:
            st.error(str(e))

    st.markdown("---")

    if st.button("Logout"):
        st.session_state.token = None
        st.rerun()

# ---------------- CHAT ----------------
st.subheader("Ask Questions")

query = st.text_input("Enter your question")

if st.button("Ask") and query:

    st.session_state.chat_history.append(("user", query))

    try:
        # -------- STREAMING --------
        response = requests.get(
            f"{API_URL}/ask-stream",
            params={"query": query},
            stream=True
        )

        answer = ""
        placeholder = st.empty()

        for chunk in response.iter_content(chunk_size=1):
            if chunk:
                text = chunk.decode("utf-8")
                answer += text
                placeholder.markdown(f"**Answer:** {answer}")

        st.session_state.chat_history.append(("bot", answer))

    except Exception as e:
        st.error(f"Streaming Error: {e}")
        st.stop()

    # -------- FETCH SOURCES + CONFIDENCE --------
    try:
        full_res = requests.get(
            f"{API_URL}/ask",
            params={"query": query}
        )

        data = full_res.json()

        # Confidence
        st.subheader("Confidence")
        st.progress(data.get("confidence", 0))

        # Sources
        st.subheader("Source Highlights")

        for src in data.get("sources", []):
            st.markdown(f"""
            <div style="
                background-color:#000105;
                padding:10px;
                border-radius:8px;
                margin-bottom:10px;
                border-left:5px solid #ffc107;">
                {src}
            </div>
            """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Source Error: {e}")

# ---------------- CHAT HISTORY ----------------
st.markdown("---")
st.subheader("Chat History")

for role, msg in st.session_state.chat_history:
    if role == "user":
        st.markdown(f"**You:** {msg}")
    else:
        st.markdown(f"**Bot:** {msg}")