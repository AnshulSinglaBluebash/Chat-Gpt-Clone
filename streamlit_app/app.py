import os

import requests
import streamlit as st


BASE_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000").rstrip("/")
LOGIN_URL = f"{BASE_URL}/auth/login"
CHAT_URL = f"{BASE_URL}/chat/send"


def init_session_state() -> None:
    st.session_state.setdefault("token", None)
    st.session_state.setdefault("messages", [])
    st.session_state.setdefault("session_id", None)


def get_error_detail(response: requests.Response, fallback: str) -> str:
    try:
        return response.json().get("detail", fallback)
    except ValueError:
        return fallback


def reset_chat_state() -> None:
    st.session_state.messages = []
    st.session_state.session_id = None


def login_user(email: str, password: str) -> bool:
    try:
        response = requests.post(
            LOGIN_URL,
            params={"email": email, "password": password},
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        st.session_state.token = data.get("access_token")
        reset_chat_state()
        return True
    except requests.HTTPError:
        st.error(get_error_detail(response, "Login failed"))
    except requests.RequestException as exc:
        st.error(f"Unable to connect to backend: {exc}")

    return False


def send_message(message: str) -> tuple[str | None, int | None]:
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    payload = {
        "message": message,
        "session_id": st.session_state.session_id,
    }

    try:
        response = requests.post(
            CHAT_URL,
            headers=headers,
            json=payload,
            timeout=60,
        )
        response.raise_for_status()
        data = response.json()
        return data.get("ai_reply", ""), data.get("session_id")
    except requests.HTTPError:
        detail = get_error_detail(response, "Chat request failed")
        if response.status_code == 401:
            st.error("Session expired. Please log in again.")
            logout_user(rerun=False)
        else:
            st.error(detail)
    except requests.RequestException as exc:
        st.error(f"Unable to connect to backend: {exc}")

    return None, None


def logout_user(rerun: bool = True) -> None:
    st.session_state.token = None
    reset_chat_state()
    if rerun:
        st.rerun()


def render_login() -> None:
    st.subheader("Login")
    with st.form("login_form", clear_on_submit=False):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login", use_container_width=True)

    if submitted:
        if not email or not password:
            st.error("Please enter both email and password.")
        elif login_user(email, password):
            st.success("Login successful.")
            st.rerun()


def render_chat() -> None:
    if not st.session_state.messages:
        st.info("Start a conversation by sending your first message.")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.chat_input("Type your message here...")
    if not prompt:
        return

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            ai_reply, session_id = send_message(prompt)

        if ai_reply is None:
            st.markdown("I couldn't get a response from the server.")
            st.session_state.messages.pop()
            return

        st.session_state.session_id = session_id
        st.markdown(ai_reply)
        st.session_state.messages.append({"role": "assistant", "content": ai_reply})


def main() -> None:
    st.set_page_config(page_title="ChatGPT Clone", page_icon="🤖", layout="centered")
    init_session_state()

    st.title("ChatGPT Clone")
    st.caption("Login and start chatting with your FastAPI backend.")

    with st.sidebar:
        st.header("Account")
        if st.session_state.token:
            st.success("You are logged in.")
            st.caption(f"Backend: {BASE_URL}")
            if st.session_state.session_id is not None:
                st.caption(f"Current session: {st.session_state.session_id}")
            if st.button("New Chat", use_container_width=True):
                reset_chat_state()
                st.rerun()
            if st.button("Logout", use_container_width=True):
                logout_user()
        else:
            st.info("Please log in to continue.")
            st.caption(f"Backend: {BASE_URL}")
            render_login()

    if not st.session_state.token:
        st.info("Log in from the sidebar to start chatting.")
        return

    render_chat()


if __name__ == "__main__":
    main()
