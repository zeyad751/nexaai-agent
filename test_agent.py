
from src.agent import graph
from langchain_core.messages import AIMessage, ToolMessage, HumanMessage

result = graph.invoke({
    "messages": [
        {
            "role": "user",
            "content": (
               "Why did PRJ-014 fail?"
            )
        }
    ]
})



print("\n========== FINAL ANSWER ==========")

final_message = result["messages"][-1]

if isinstance(final_message.content, list):
    for block in final_message.content:
        if isinstance(block, dict) and block.get("type") == "text":
            print(block["text"])
else:
    print(final_message.content)


print("\n========== AGENT TRACE ==========")

for message in result["messages"]:

    if isinstance(message, HumanMessage):
        print("\n[USER QUESTION]")
        print(message.content)

    elif isinstance(message, AIMessage):

        # Capture tool calls
        if message.tool_calls:
            print("\n[TOOL CALLS]")
            for tool_call in message.tool_calls:
                print("Tool:", tool_call["name"])
                print("Arguments:", tool_call["args"])

        # Capture readable AI messages
        elif message.content:
            print("\n[AI MESSAGE]")
            if isinstance(message.content, list):
                for block in message.content:
                    if isinstance(block, dict) and block.get("type") == "text":
                        print(block["text"])
            else:
                print(message.content)

    elif isinstance(message, ToolMessage):
        print("\n[TOOL RESULT]")
        print("Tool:", message.name)
        print("Result:", message.content)

