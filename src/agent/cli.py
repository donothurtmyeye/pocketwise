from graph import build_graph
from langgraph.checkpoint.memory import MemorySaver


def main():
    print("🤖 Welcome to PocketWise - Your Personal Finance Companion")
    user_id = input(
        "Enter your User ID (or press Enter for 'student_01'): ").strip() or "student_01"
    checkpointer = MemorySaver()
    config = {"configurable": {"thread_id": "user_001"}}
    app = build_graph(checkpointer)

    print(f"Logged in as: {user_id}")
    print("Type 'exit' or 'quit' to stop.")
    print("-" * 50)

    while True:
        user_input = input("\n👤 You: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        inputs = {
            "user_id":user_id,
            "messages":[("user",user_input)]
        }
        print("🤖 PocketWise: ", end="", flush=True)

        result = app.invoke(inputs,config=config)
        print(result["messages"][-1].content, flush=True)



if __name__ == "__main__":
    main()