import streamlit as st
from utils.frontend_utils import post_prompt_to_backend
from utils.config_loader import ConfigLoader

CONFIG_PATH = "configs/config.yaml"

config = ConfigLoader(config_path=CONFIG_PATH)

st.title("Your personal assisstant Nima!")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt, "image": ""})


    response = post_prompt_to_backend(st.session_state.messages, config.get('BACKEND_API_URL'), image=None)

    with st.chat_message("user"):
        st.markdown(prompt)

    #with st.chat_message("assistant"):

    #   response = st.write_stream(api_response)
    #st.session_state.messages.append({"role": "assistant", "content": response})