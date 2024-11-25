# loading the API keys
from dotenv import load_dotenv, find_dotenv

from ChatBot import response

load_dotenv(find_dotenv(), override=True)

from langsmith import traceable
from openai import Client

openai = Client()


@traceable
def format_prompt(user_prompt):
    return [
        {
            'role': 'system',
            'content': 'You are a helpful assistant.',
        },
        {
            'role': 'user',
            'content': f'Generate three good names for an online store that sells {user_prompt}?'
        }
    ]


@traceable(run_type='llm')
def invoke_llm(messages):
    return openai.chat.completions.create(
        messages=messages, model='gpt-4o-mini', temperature=0
    )


@traceable
def parse_output(response):
    return response.choices[0].message.content


@traceable
def run_pipeline():
    messages = format_prompt('School supplies')
    response = invoke_llm(messages)
    return parse_output(response)


run_pipeline()

