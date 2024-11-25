from IPython.lib.pretty import pretty
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(), override=True)

# Import necessary libraries
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

#create a chat prompt template
generation_prompt = ChatPromptTemplate.from_messages(
    [
        (
        'system',
        '''You are twitter expert, Assigned to craft outstanding tweets.
        Generate most engaging and impactful tweets based on user's request.
        If user provides feedback, then refine and enhance your previous attempt accordingly for max engagement'''
        ), MessagesPlaceholder(variable_name='messages')
    ]

)

llm = ChatOpenAI(model='gpt-4o-mini', temperature=0.7)

#usiing LCEL to create the generate_chain

generate_chain = generation_prompt | llm

#(generate_chain)

tweet = ''
# request = HumanMessage(
#     content='latest tech gadgets'
# )
#
# for chunk in generate_chain.stream(
#         {'messages': [request]}
# ):
#     print(chunk.content, end='')
#     tweet += chunk.content

#Create a reflection chain
reflection_prompt = ChatPromptTemplate.from_messages(
    [
        (
            'system',
            '''You are a Twitter influencer known for your engaging content and sharp insights.
            Review and critique the user’s tweet.
            Provide constructive feedback, focusing on enhancing its depth, style, and overall impact.
            Offer specific suggestions to make the tweet more compelling and engaging for their audience.'''
        ),
        MessagesPlaceholder(variable_name='messages'),
    ]
)

reflect_chain  = reflection_prompt | llm

reflected = ''

# for chunk in reflect_chain.stream(
#         {'messages': [request,HumanMessage(content=tweet)]}
# ):
#     print(chunk.content, end='')
#     reflected += chunk.content
#
# for chunk in generate_chain.stream(
#     {'messages': [request, AIMessage(content=tweet), HumanMessage(content=reflected)]}
# ):
#     print(chunk.content, end='')


#Define the Graph

from typing import List,Sequence
from langgraph.graph import END, MessageGraph

#define a function for generation node
def generation_node(state:Sequence[BaseMessage]):
    return generate_chain.invoke({'messages': state})




# defining a function for the reflection node
def reflection_node(messages: Sequence[BaseMessage]) -> List[BaseMessage]:
    # messages we need to adjust
    cls_map = {'ai': HumanMessage, 'human': AIMessage}
    # First message is the original user request. We keep it the same for all nodes
    translated = [messages[0]] + [
    cls_map[msg.type](content=msg.content) for msg in messages[1:]
    ]
    res = reflect_chain.invoke({'messages': translated})
    # We treat the output (AI message) of this as human feedback for the generator
    return HumanMessage(content=res.content)

# initializing the MessageGraph and adding two nodes to the graph: generate and reflect.
builder = MessageGraph()
builder.add_node('generate', generation_node)
builder.add_node('reflect', reflection_node)

# setting the generate node as the starting point
builder.set_entry_point('generate')

MAX_ITERATIONS = 5
def should_continue(state: List[BaseMessage]):
    if len(state) > MAX_ITERATIONS:
        return END
    return 'reflect'

# adding a conditional edge to the graph
builder.add_conditional_edges('generate', should_continue)
builder.add_edge('reflect', 'generate')

# compiling the graph
graph = builder.compile()

#Run the App
inputs = HumanMessage(content='Generate a tweet about Cricket T20 world cup')
response = graph.invoke(inputs)

for resp in response:
    print(resp.content)
    print('\n' + '-' * 100 + '\n')