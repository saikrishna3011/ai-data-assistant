import streamlit as st
from agent import ask_question
import pandas as pd

st.set_page_config(page_title="AI Data Assistant", page_icon="🤖")
st.title("🤖 AI Data Assistant")
st.caption("Ask questions about your data in plain English")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if prompt := st.chat_input("e.g. What were the top 5 products last quarter?"):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Querying your data..."):
            try:
                answer, sql, df = ask_question(prompt)
            except Exception as e:
                answer = f"Something went wrong: {str(e)}"
                sql = ""
                df = pd.DataFrame()

        st.write(answer)

        if sql:
            with st.expander("See the SQL query"):
                st.code(sql, language="sql")

        if not df.empty:
            with st.expander("See raw data"):
                st.dataframe(df)

    st.session_state.messages.append({"role": "assistant", "content": answer})