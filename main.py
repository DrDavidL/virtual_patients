from langchain.chains import LLMChain
from langchain.llms import OpenAI
from langchain.memory import ConversationBufferMemory
from langchain.memory.chat_message_histories import StreamlitChatMessageHistory
from langchain.prompts import PromptTemplate
import streamlit as st
from collections import defaultdict
from prompts import *

st.set_page_config(page_title="AI Patients", page_icon="📖")
st.title("📖 Chat with AI Patients")

# """

# [Built on](https://github.com/langchain-ai/streamlit-agent/blob/main/streamlit_agent/basic_memory.py).
# """


# learning_method = st.radio("Select an option:", ("Interact with an AI simulated patient", "More to Come (nothing yet)"), index=0)



# if learning_method == "Interact with an AI simulated patient":         
system_context = st.radio("Select an AI patient who comes to the ED with:", ("abdominal pain", "chest pain", "bloody diarrhea", "random symptoms", "You choose!"), horizontal = True, index=0)
    
if system_context == "abdominal pain":
    template = abd_pain_pt_template

if system_context == "chest pain":
    template = chest_pain_pt_template

if system_context == "bloody diarrhea":
    template = bloody_diarrhea_pt_template
    
if system_context == "random symptoms":
    template = random_symptoms_pt_template

if system_context == "You choose!":
    symptoms = st.text_input("Enter a list of symptoms separated by commas")
    # Create a defaultdict that returns an empty string for missing keys
    template = chosen_symptoms_pt_template.replace('{symptoms}', symptoms)


# Set up memory
msgs = StreamlitChatMessageHistory(key="langchain_messages")
memory = ConversationBufferMemory(chat_memory=msgs)
if len(msgs.messages) == 0:
    msgs.add_ai_message("I can't believe I'm in the ER!")

# view_messages = st.expander("View the message contents in session state")

# Get an OpenAI API Key before continuing
if "OPENAI_API_KEY" in st.secrets:
    openai_api_key = st.secrets.OPENAI_API_KEY
else:
    openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password")
if not openai_api_key:
    st.info("Enter an OpenAI API Key to continue")
    st.stop()



prompt = PromptTemplate(input_variables=["history", "human_input"], template=template)
llm_chain = LLMChain(llm=OpenAI(openai_api_key=openai_api_key), prompt=prompt, memory=memory)

# Render current messages from StreamlitChatMessageHistory
for msg in msgs.messages:
    st.chat_message(msg.type).write(msg.content)

# If user inputs a new prompt, generate and draw a new response
if prompt := st.chat_input():
    st.chat_message("user").write(prompt)
    # Note: new messages are saved to history automatically by Langchain during run
    response = llm_chain.run(prompt)
    st.chat_message("assistant").write(response)

clear_memory = st.button("Start Over")
if clear_memory:
    st.session_state.langchain_messages = []