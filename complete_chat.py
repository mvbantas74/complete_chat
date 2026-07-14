from typing import List, Dict

from google import genai
import streamlit as st

class StreamSplitter:
    def __init__(self, stream):
        self.stream = iter(stream)
        self.current_chunk = None
        self.has_more = True
        self._advance()

    def _advance(self):
        try:
            self.current_chunk = next(self.stream)
        except StopIteration:
            self.has_more = False
            self.current_chunk = None

    def get_thinking_stream(self):
        while self.has_more:
            try:
                if self.current_chunk.candidates[0].content.parts[0].thought:
                    yield self.current_chunk.candidates[0].content.parts[0].text
                    self._advance()
                else:
                    break
            except Exception as e:
                pass

    def get_reply_stream(self):
        while self.has_more:
            if self.current_chunk.text:
                yield self.current_chunk.text
            self._advance()
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
            generation_config={
                "thinking_level": "high"
            }
        )

    @staticmethod
    def parse_generator(generator):
        return StreamSplitter(generator)
        """
        in_thinking = False
        for chunk in generator:
            try:
                if chunk.candidates[0].content.parts[0].thought:
                    in_thinking = True
                    yield chunk.candidates[0].content.parts[0].text
            except Exception as e:
                pass
            if chunk.text:
                if in_thinking:
                    yield "\n\n## *Done thinking!*\n\n"
                    in_thinking = False
                yield chunk.text
        """


with st.sidebar:
    selected_model = st.selectbox("Select Model", options=['gemini-flash-lite-latest', 'gemma-4-26b-a4b-it', 'gemma-4-31b-it'])
    if not selected_model:
        st.warning("Please select a model.")
        
chat_instance = Gemini(selected_model)

if 'messages' not in st.session_state:
    st.session_state.messages = []

if st.session_state.messages:
    for message in st.session_state.messages:
        role, content = message['role'], message['content']
        with st.chat_message(role):
            st.write(content)

prompt = st.chat_input()

if prompt:
    response = ""
    thinking_response = ""
    user_text = {"role": "user", "content": prompt}
    st.session_state.messages.append(user_text)
    with st.chat_message("user"):
        st.markdown(prompt)
    try:
        splitter = chat_instance.parse_generator(chat_instance.call_api(st.session_state.messages))
        with st.chat_message("assistant"):
            with st.status("Thinking...", expanded=True, type="compact") as status:
                thinking_response = st.write_stream(splitter.get_thinking_stream())
                status.update(label="Done thinking!", expanded=False, state="complete")
            response = st.write_stream(splitter.get_reply_stream())
    except Exception as e:
        st.error(e)
    if response:
        st.session_state.messages.append({"role": "assistant", "content": response})
