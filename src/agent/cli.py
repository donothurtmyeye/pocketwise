from graph import build_graph
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()
config = {"configurable": {"thread_id": "user_001"}}
app = build_graph(checkpointer)
def process_input(user_input):
    inputs = {
        "user_id": "student_01",
        "messages": [("user", user_input)]
    }
    result = app.invoke(inputs, config=config)
    return result

# def main():
#     checkpointer = MemorySaver()
#     config = {"configurable": {"thread_id": "user_001"}}
#     app = build_graph(checkpointer)
#     print("🤖 Welcome to PocketWise - Your Personal Finance Companion")
#     user_id = input(
#         "Enter your User ID (or press Enter for 'student_01'): ").strip() or "student_01"
#     print(f"Logged in as: {user_id}")
#     print("Type 'exit' or 'quit' to stop.")
#     print("-" * 50)
#     while True:
#         user_input = input("\n👤 You: ")
#         if user_input.lower() in ["exit", "quit"]:
#             break
#         inputs = {
#             "user_id": "student_01",
#             "messages": [("user", user_input)]
#         }
#         print("🤖 PocketWise: ", end="", flush=True)
#         result = app.invoke(inputs, config=config)
#         print(result["messages"][-1].content, flush=True)
#
# if __name__ == "__main__":
#     main()


# import streamlit as st
# import json
# from datetime import datetime

# def main():
#     st.set_page_config(page_title="PocketWise")
#     st.title("🤖 Welcome to PocketWise - Your Personal Finance Companion")
#     # 初始化 session state 来存储历史记录
#     if "tool_history" not in st.session_state:
#         st.session_state.tool_history = []
#
#     user_input = st.chat_input("You:")
#     if user_input:
#         inputs = {
#             "user_id":"student_01",
#             "messages":[("user",user_input)]
#         }
#         result = app.invoke(inputs, config=config)
#
#         if "tool_call_history" in result:
#             st.session_state.tool_history = result["tool_call_history"]
#
#         human_message = st.chat_message("human")
#         human_message.write(user_input)
#
#         ai_message = st.chat_message("ai")
#         ai_message.write(result["messages"][-1].content)
#
#     # --- 侧边栏显示工具调用历史 ---
#     with st.sidebar:
#         st.header("🛠️ Tool Call History")
#         if st.session_state.tool_history:
#             # 逆序显示，最新的在上面
#             for record in reversed(st.session_state.tool_history):
#                 st.subheader(f"`{record['name']}`")
#                 st.text("Arguments:")
#                 st.code(json.dumps(record['arguments'], indent=2, ensure_ascii=False), language="json")
#                 st.text("Result:")
#                 st.code(record['result'], language="text", height = 200)
#                 st.caption(f"Timestamp: {datetime.fromtimestamp(float(record['timestamp']))}")
#                 st.divider()
#         else:
#             st.info("No tool calls executed yet.")
#
#
# if __name__ == "__main__":
#     main()
