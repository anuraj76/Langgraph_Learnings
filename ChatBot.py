from langgraph.graph import StateGraph
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI

#load OpenAI API key
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(), override=True)


#Build a state class for our state graph
class State(TypedDict):
    messages: Annotated[list, add_messages]


graph_builder = StateGraph(State)

llm = ChatOpenAI(model='gpt-4o-mini', temperature=0.6)


def chatbot(state: State):
    return {"messages": [llm.invoke(state["messages"])]}


graph_builder.add_node("chatbot", chatbot)
graph_builder.set_entry_point("chatbot")
graph_builder.set_finish_point("chatbot")

graph = graph_builder.compile()

from IPython.display import Image, display

display(Image(graph.get_graph().draw_mermaid_png))

#Run the chatbot


# Run the chatbot
# while True:
#     user_input = input('User: ')
#     if user_input.lower() in ['quit', 'exit', 'bye', 'q']:
#         print('GoodBye')
#         break
#
#     for event in graph.stream({'messages': [('user', user_input)]}):
#         for value in event.values():
#             print(f'Assistant: {value["messages"][-1].content}')
#             print('-' * 20)  # This will print a line of 20 dashes20)


from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(), override=True)

from tavily import TavilyClient
import os

# Initialize Tavily Client
client = TavilyClient(os.getenv('TAVILY_API_KEY'))

# response = client.search('Whats Notredame Cathedral and where is it located?')
# print(response)
#
# for result in response['results']:
#     print(f"Title: {result['title']}, URL: {result['url']}")
#
# response = client.search(query='What is the weather like in New York City?',
#                          search_depth='advanced',
#                          max_results=7,
#                          include_images=True,
#                          include_answer=True,
#                          include_raw_content=False,
#                          )
# print(response)


# answer = client.qna_search(query='Who won football worldcup in 1999?')
# print(answer)

#Pass Tavily Results to LangChain

from langchain_community.adapters.openai import convert_openai_messages
from langchain_openai import OpenAI
#
# query = "What what is langchain explain me in simple words?"
#
# response = client.search(query, max_results=5,search_depth='advanced')['results']
# print(response)
#
# #Setting up OpenAI API prompt
# prompt = [
#     {
#         "role": "system",
#         "content": f'''You are AI research Assistant.
#         Your sole purpose it to write short but informative blogs posts for linkedIn,
#         These blogs should filled with humourous tone.'''
#     },
#     {
#         "role": "user",
#         "content": f'''Information:"""{response}"""
#         Using above information, create a short blog post on:{query}'''
#
#     }
# ]

# lc_messages = convert_openai_messages(prompt)
# # print(lc_messages)
#
#
# response = ChatOpenAI(model='gpt-4o-mini', temperature=0.7).invoke(lc_messages)
# print(response.content)

#Enhancing langgraph with tools

from langchain_community.tools.tavily_search import TavilySearchResults
tool = TavilySearchResults(max_results=3)
tools = [tool]

response = tool.invoke('How good and real is terminator film?')
print(response)
