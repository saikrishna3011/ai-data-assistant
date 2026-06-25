import streamlit as st
from agent import ask_question

st.set_page_config(page_title="AI Data Assistant", page_icon="🤖")
st.title("🤖 AI Data Assistant")
st.caption("Ask questions about your data in plain English")

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Input
if prompt := st.chat_input("e.g. What were the top 5 products last quarter?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.write(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("Querying your data..."):
            answer, sql, df = ask_question(prompt)
        
        st.write(answer)
        
        with st.expander("See the SQL query"):
            st.code(sql, language="sql")
        
        with st.expander("See raw data"):
            st.dataframe(df)
    
    st.session_state.messages.append({"role": "assistant", "content": answer})