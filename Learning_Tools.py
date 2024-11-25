from langgraph.graph import StateGraph
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode, tools_condition


#load OpenAI API key
from dotenv import load_dotenv, find_dotenv

from ChatBot import tools

load_dotenv(find_dotenv(), override=True)

from langchain_community.tools.tavily_search import TavilySearchResults
tool = TavilySearchResults(max_results=3)
tools = [tool]

#Build a state class for our state graph
class State(TypedDict):
    messages: Annotated[list, add_messages]


graph_builder = StateGraph(State)

llm = ChatOpenAI(model='gpt-4o-mini', temperature=0.6)

llm_with_tools = llm.bind_tools(tools)

def chatbot(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}


graph_builder.add_node("chatbot", chatbot)

tool_node = ToolNode(tools=tools)
graph_builder.add_node('tools', tool_node)

graph_builder.add_conditional_edges('chatbot', tools_condition)

graph_builder.add_edge('tools', 'chatbot')

graph_builder.set_entry_point("chatbot")
graph_builder.set_finish_point("chatbot")

graph = graph_builder.compile()

# from IPython.display import Image, display
#
# display(Image(graph.get_graph().draw_mermaid_png))

#Run the chatbot
while True:
    user_input = input('User: ')
    if user_input.lower() in ['quit', 'exit', 'bye', 'q']:
        print('GoodBye')
        break

    for event in graph.stream({'messages': [('user', user_input)]}):
        for value in event.values():
            print(f'Assistant: {value["messages"][-1].content}')
            print('-' * 20)  # This will print a line of 20 dashes20)