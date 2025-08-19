import asyncio
import nest_asyncio

import streamlit as st

from mcp import ClientSession
from mcp.client.sse import sse_client
from utils.config_loader import config
from model import Agent

supervisor_agent = Agent()

nest_asyncio.apply()

async def query_model(chat_history):
    async with sse_client(url="http://127.0.0.1:8000/sse") as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools_result = await session.list_tools()
            supervisor_agent.bind_tools(tools_result.tools)
            result = await supervisor_agent.invoke(chat_history, session)
            return result

st.title("Your personal assisstant!")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt, "image": ""})

    response = asyncio.run(query_model(st.session_state.messages))
    
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})