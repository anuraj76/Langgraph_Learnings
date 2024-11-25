from IPython.core.debugger import prompt
from langchain_community.tools import TavilySearchResults
from langgraph.graph import StateGraph
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.checkpoint.memory import MemorySaver

#load OpenAI API key
from dotenv import load_dotenv, find_dotenv

from ChatBot import graph_builder, tools
from Learning_Tools import llm_with_tools, value

load_dotenv(find_dotenv(), override=True)


#Build a state class for our state graph


class State(TypedDict):
    messages: Annotated[list, add_messages]

graph_builder = StateGraph(State)

llm = ChatOpenAI(model='gpt-4o-mini', temperature=0.6)
tool = [TavilySearchResults(max_results=3)]
tools = [tool]
llm_with_tools = llm.bind_tools(tools)
def chatbot(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

graph_builder.add_node('chatbot', chatbot)
tool_node = ToolNode(tools=[tool])
graph_builder.add_node('tools', tool_node)

graph_builder.add_conditional_edges('chatbot', tools_condition)

graph_builder.add_edge('tools', 'chatbot')
graph_builder.set_entry_point('chatbot')
graph_builder.set_finish_point('chatbot')




#Adding Memory to our chatbot
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.checkpoint.memory import MemorySaver

memory = SqliteSaver.from_conn_string(':memory:')
graph = graph_builder.compile(checkpointer=MemorySaver())

config = {'configrable': {'thread_id:': '1'}}

prompt = 'Hi, My name is Anuraj, You are mt Calculas tutor'

events = graph.stream({'messages': [('user', prompt)]}, **config, stream_mode='values')

for event in events:
    event['messages'][-1].preety_print()