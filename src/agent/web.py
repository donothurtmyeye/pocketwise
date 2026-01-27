import streamlit as st
import json
from datetime import datetime
from cli import process_input

def main():
    st.set_page_config(page_title="PocketWise")
    st.title("🤖 Welcome to PocketWise - Your Personal Finance Companion")
    # 初始化 session state 来存储历史记录
    if "tool_history" not in st.session_state:
        st.session_state.tool_history = []

    user_input = st.chat_input("You:")
    if user_input:
        result = process_input(user_input)

        if "tool_call_history" in result:
            st.session_state.tool_history = result["tool_call_history"]

        human_message = st.chat_message("human")
        human_message.write(user_input)

        ai_message = st.chat_message("ai")
        ai_message.write(result["messages"][-1].content)

    # --- 侧边栏显示工具调用历史 ---
    with st.sidebar:
        st.header("🛠️ Tool Call History")
        if st.session_state.tool_history:
            # 逆序显示，最新的在上面
            for record in reversed(st.session_state.tool_history):
                st.subheader(f"`{record['name']}`")
                st.text("Arguments:")
                st.code(json.dumps(record['arguments'], indent=2, ensure_ascii=False), language="json")
                st.text("Result:")
                st.code(record['result'], language="text", height = 200)
                st.caption(f"Timestamp: {datetime.fromtimestamp(float(record['timestamp']))}")
                st.divider()
        else:
            st.info("No tool calls executed yet.")


if __name__ == "__main__":
    main()
