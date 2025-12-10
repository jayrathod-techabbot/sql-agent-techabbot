# from http import client
# from sqlite3 import Date
import streamlit as st
import os
from dotenv import load_dotenv

# from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.utilities import SQLDatabase
from langchain_openai import AzureChatOpenAI

# from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain_community.utilities import SQLDatabase
from langchain_core.tools import Tool
from utils.prompt import (
    formatted_prompt as _mysql_prompt,
    PROMPT_SUFFIX,
    example_prompt,
)

# from langchain.agents import create_sql_agent
from langchain_community.agent_toolkits import create_sql_agent

# --- 1. Setup Environment and Database Connection ---
# Load environment variables (assumes .env file is present)
load_dotenv()

# Database credentials from environment variables
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

print("DB host url ",DB_HOST.split('.')[0])
if not all([DB_USER, DB_PASSWORD, DB_HOST, DB_NAME, GEMINI_API_KEY]):
    st.error(
        "Missing one or more required environment variables (DB_USER, DB_PASSWORD, DB_HOST, DB_NAME, GEMINI_API_KEY). Please check your .env file."
    )
    st.stop()


def execute_sql_query(query: str) -> str:
    """Execute a SQL query and return results"""
    try:
        result = db.run(query)
        return str(result)
    except Exception as e:
        return f"Error executing query: {str(e)}"


# Create custom tool
custom_query_tool = Tool(
    name="execute_sql_query",
    func=execute_sql_query,
    description="Executes a SQL query against the database and returns the results",
)

from utils.few_shots import shots
from langchain_community.vectorstores import FAISS
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from sqlalchemy import create_engine

# from langchain_huggingface import HuggingFaceEmbeddings
# # from langchain_community.embeddings import HuggingFaceEmbeddings
# to_vectorize = [" ".join(example.values()) for example in shots]
# embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
# vectorstore = FAISS.from_texts(to_vectorize, embeddings, metadatas=shots)
# example_selector = SemanticSimilarityExampleSelector(
#     vectorstore=vectorstore,
#     k=2,
# )

# Initialize LLM and Database
try:
    subscription_key = os.getenv("AZURE_OPENAI_API_KEY")
    print(f"Using Azure OpenAI Subscription Key: {subscription_key[-5:]}")
    model_name = "o4-mini"
    deployment = "o4-mini"
    llm = AzureChatOpenAI(
        azure_endpoint="https://jayr-miy3ohh3-eastus2.cognitiveservices.azure.com/",
        api_key=subscription_key,
        deployment_name=deployment,
        model_name=model_name,
        api_version="2024-12-01-preview",
    )


    DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
    CONNECT_ARGS = {
        "ssl": {
            "ssl_mode": "REQUIRED",
        }
    }
    engine = create_engine(DATABASE_URI, connect_args=CONNECT_ARGS)

    db = SQLDatabase(engine, sample_rows_in_table_info=3)

    new_sql_agent = create_sql_agent(
        llm=llm,
        db=db,
        agent_type="openai-tools",
        verbose=True,
        prefix=_mysql_prompt,
        suffix=PROMPT_SUFFIX,
        input_variables=["input", "table_info", "top_k"],
        # example_selector=example_selector,
        # example_prompt=example_prompt,
        extra_tools=[custom_query_tool],  # Add custom tools here
    )


except Exception as e:
    st.error(f"Error during initialization (LLM or Database): {e}")
    st.stop()

# --- 2. Streamlit Chatbot Interface ---


def main():
    """Main function to run the Streamlit app."""
    st.title("SQL Agent Chatbot 🤖")
    st.caption("Ask questions about your ERP database in natural language.")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("What would you like to know about the orders?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get response from the SQL Agent
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    # Run the agent with the user's query

                    print(f"User prompt: {prompt}")

                    response = new_sql_agent.invoke({"input": prompt})
                    print(response)  # Debug: Print full response
                    answer = response["output"]

                    import re

                    answer_text = re.search(r"Answer:\s*(.*)", answer, re.DOTALL)
                    # print(answer_text.group(1).strip())
                    st.markdown(answer_text.group(1).strip())

                    # Add assistant response to chat history
                    st.session_state.messages.append(
                        {"role": "assistant", "content": answer_text.group(1).strip()}
                    )

                except Exception as e:
                    error_message = f"An error occurred while processing the query: {e}"
                    st.error(error_message)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": error_message}
                    )


if __name__ == "__main__":
    main()
