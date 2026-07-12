from typing import List, Dict

from google import genai
import streamlit as st

class Gemini:
    def __init__(self, model: str):
        self.model = model
        self.client = genai.Client(api_key=st.secrets['G_API_KEY'])

    def call_api(self, content: List[Dict]):
        gemini_format = ""
        for item in content:
            gemini_format += f"`{item['role']}`: {item['content']}"
            gemini_format += "\n"
        return self.client.models.generate_content_stream(
            model=self.model,
            contents=gemini_format,
        )

    @staticmethod
    def parse_generator(generator):
        for item in generator:
            yield item.text

chat_instance = Gemini("gemini-3-flash")

if 'messages' not in st.session_state:
    st.session_state.messages = []

prompt = st.chat_input()

if prompt:
    response = ""
    user_text = {"role": "user", "content": prompt}
    st.session_state.messages.append(user_text)
    with st.chat_message("user"):
        st.markdown(prompt)
    try:
        with st.chat_message("assistant"):
            response = st.write_stream(chat_instance.parse_generator(chat_instance.call_api(st.session_state.messages)))
    except Exception as e:
        st.error(e)
    if response:
        st.session_state.messages.append({"role": "assistant", "content": response})
