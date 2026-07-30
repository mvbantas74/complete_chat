import json
import uuid
from typing import List, Dict
from google import genai
from google.genai import types
import streamlit as st

col1, col2 = st.columns(2)
is_thinking_enabled = col2.toggle("Enable thinking", value=True)
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
        contents = []
        for item in content:
            contents.append(types.Content(
                role = item['role'] if item['role'] == 'user' else "model",
                parts = [types.Part.from_text(text=item['content'])]
            ))
        return self.client.models.generate_content_stream(
            model=self.model,
            contents=contents,
            config = types.GenerateContentConfig(
                temperature=0.0,
                system_instruction="""
From now on, adopt an ultra-concise communication style.
Rules:
1. No greetings or introductions.
2. Answer the subject directly.
3. Minimize the word count without losing the essence of the information.
""",
                thinking_config=types.ThinkingConfig(
                    include_thoughts=True,
                    thinking_level="high" if is_thinking_enabled else "minimal"
                )
            )
        )

    @staticmethod
    def parse_generator(generator):
        return StreamSplitter(generator)

with st.sidebar:
    selected_model = st.selectbox("Select Model", options=['gemma-4-31b-it', 'gemma-4-26b-a4b-it', 'gemini-flash-lite-latest'])
    if not selected_model:
        st.warning("Please select a model.")
        
chat_instance = Gemini(selected_model)


if 'messages' not in st.session_state:
    st.session_state.messages = []

def empty_chat():
    st.session_state.messages = []


if col2.button("New chat"):
    empty_chat()


if st.session_state.messages:
    for message in st.session_state.messages:
        role, content = message['role'], message['content']
        with st.chat_message(role):
            if "thinking" in message:
                with st.status("... done thinking!", state="complete", type="compact"):
                    st.write(message['thinking'])
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
            if is_thinking_enabled:
                with st.status("Thinking...", expanded=True, type="compact") as status:
                    thinking_response = st.write_stream(splitter.get_thinking_stream())
                    status.update(label="Done thinking!", expanded=False, state="complete")
            response = st.write_stream(splitter.get_reply_stream())
    except Exception as e:
        st.error(e)
    if response:
        new_response = {"role": "assistant", "content": response}
        if thinking_response:
            new_response['thinking'] = thinking_response
        st.session_state.messages.append(new_response)
        

with st.sidebar:
    st.info("DEBUG", icon="ℹ️")
    st.write(st.session_state.messages)
    


col1.download_button( 
        label="Download data as JSON", 
        data=json.dumps(st.session_state.messages, indent=2, ensure_ascii=False),
        file_name=f"{uuid.uuid4()}.json", 
        mime="application/json" 
    )
