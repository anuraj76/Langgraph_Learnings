from logging import raiseExceptions

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(), override=True)

#Import necessary Libraries
import os
import openai
import re
import httpx

#Provide API key
from openai import OpenAI
client = OpenAI()

#model_name = "gpt-4o-mini"  # Updated to a valid model name
#prompt = "Tell me in short about James bond"

#chat_completion = client.chat.completions.create(
#    model=model_name,
#    messages=[
#        {
#            "role": "user",
#            "content": prompt
#       }
#    ]
#)

#print(chat_completion.choices[0].message.content)

#define Agent class

class Agent:
    def __init__(self, system=''):
        self.system = system
        self.message = []

        if self.system:
            self.message.append({"role": "system", "content": system})

    def __call__(self, prompt):
        # Check if prompt is a list and convert it to a string if it is
        if isinstance(prompt, list):
            prompt = ' '.join(prompt)
        
        self.message.append({"role": "user", "content": prompt})
        result = self.execute()
        self.message.append({"role": "assistant", "content": result})
        return result

    def execute(self):
        chat_completion = client.chat.completions.create(
            model='gpt-4o-mini',  # Make sure this is a valid model name
            temperature=0.7,
            messages=self.message  # Changed from self.messages to self.message
        )
        return chat_completion.choices[0].message.content


#Create a Prompt
prompt = '''
You run in a loop of Thought, Action, PAUSE, Observation.
At the end of the loop you output an Answer
Use Thought to describe your thoughts about the question you have been asked.
Use Action to run one of the actions available to you - then return PAUSE.
Observation will be the result of running those actions.

Your available actions are:

calculate:
e.g. calculate: 4 * 7 / 3
Runs a calculation and returns the number - uses Python so be sure to use floating point syntax if necessary

get_cost:
e.g. get_cost: book
returns the cost of a book

wikipedia:
e.g. wikipedia: LangChain
Returns a summary from searching Wikipedia

Always look things up on Wikipedia if you have the opportunity to do so.

Example session #1:

Question: How much does a pen cost?
Thought: I should look the pen cost using get_cost
Action: get_cost: pen
PAUSE

You will be called again with this:

Observation: A pen costs $5

You then output:

Answer: A pen costs $5


Example session #2

Question: What is the capital of France?
Thought: I should look up France on Wikipedia
Action: wikipedia: France
PAUSE

You will be called again with this:

Observation: France is a country. The capital is Paris.

You then output:

Answer: The capital of France is Paris
'''.strip()


#CREATE TOOLS
# 1. the calculate() function takes in a string, evaluates that string, and returns the result
def calculate(what):
    return eval(what)


# 2. the get_cost() function returns the cost for a pen, a book, and a stapler
def get_cost(thing):
    if thing in 'pen':
        return ('A pen costs $5')
    elif thing in 'book':
        return ('A book costs $20')
    elif thing in 'stapler':
        return ('A stapler costs $10')
    else:
        return ('A random thing for writing costs $12.')


# 3. the wikipedia() function uses the Wikipedia API to search for a specific query on Wikipedia
def wikipedia(q):
    response = httpx.get('https://en.wikipedia.org/w/api.php', params={
        'action': 'query',
        'list': 'search',
        'srsearch': q,
        'format': 'json'
    })
    results = response.json().get('query').get('search', [])

    if not results:
        return None
    return results[0]['snippet']


#print(wikipedia('Bitcoin'))

#dictionary that can map function names to their corresponding functions
known_actions = {
                 'calculate': calculate,
                 'get_cost': get_cost,
                 'wikipedia': wikipedia}

#Testing the Agent
my_agent = Agent(prompt)
#
# print(agent("How much does a pen cost?"))
# print(agent("What is the capital of Germany?"))
# print(agent("Tell me the history of United kingdom."))

# result = my_agent("What is the capital of France?")
# print(result)

#creating next prompt that will be used as observation and passed to language model
#
# next_prompt = f"Observation: {get_cost('pen')}"
#
# print(my_agent(next_prompt))
#
# print(my_agent.message)  # This will print the messages

# abot = Agent(prompt)
#
# question = '''I want to buy a pen and a book. How much do they cost?'''
#
# # print(abot(question))
#
#
# next_prompt = f"Observation: {get_cost('pen')}"
# # print(next_prompt)
#
# print(abot(next_prompt))

#Automating the agent to ask questions based on the given prompt.

#define regex pattern for finding the action string
action_re = re.compile(r'^Action:(\w+): (.*)$')

def query(question, max_turn=5):
    i = 0
    bot = Agent(prompt)
    next_prompt = question

    while i < max_turn:
        i += 1
        result = bot(next_prompt)
        print(result)

        #use regex to parse the response from the agent
        actions = [
            action_re.match(a) for a in result.split('\n') if action_re.match(a)
        ]

        if actions:
            action, action_input = actions[0].groups()
            if action in known_actions:
                print(f'Executing action: {action} with input: {action_input}')
                observation = known_actions[action](action_input)
                print(f'Observation: {observation}')
                next_prompt = f"Observation: {observation}"
            else:
                print(f'Unknown action: {action}: {action_input}')
                return
        else:
            print('No action found in the response.')
            return

    print("Maximum turns reached.")


question ='''I want to buy two books and 5 pens , how much shall i pay?'''
query(question)

