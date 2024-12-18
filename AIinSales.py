from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(), override=True)

import openai
import pandas as pd
import streamlit as st
from langgraph.graph import StateGraph
from typing import TypedDict, List, Dict
import random
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

# Define State Management
class WorkflowState(TypedDict):
    crm_data: List[Dict]
    communications: List[str]
    sentiments: List[Dict]
    recommendations: List[str]
    deals: List[Dict]

# Node/ Agents ----
# 1. Data Preprocessing Agent
def process_crm_data(state: Dict) -> Dict:
    for customer in state['crm_data']:
        customer["relationship_score"] = random.randint(5, 10)
    return state

# 2. Sentiment Analysis Agent
def analyze_sentiments(state: Dict) -> Dict:
    llm = ChatOpenAI(model="gpt-3.5-turbo")
    state['sentiments'] = []
    for comm in state['communications']:
        response = llm.invoke([HumanMessage(content=f"Analyze the sentiment of this communication: {comm}")])
        state['sentiments'].append({
            'text': comm,
            'analysis': response.content.strip()
        })
    return state

# 3. Recommendation Agent
def generate_recommendations(state: Dict) -> Dict:
    state['recommendations'] = []
    for customer, sentiment in zip(state['crm_data'], state['sentiments']):
        if 'positive' in sentiment['analysis'].lower():
            action = f'Followup with {customer["name"]} about potential upselling.'
        elif 'negative' in sentiment['analysis'].lower():
            action = f'Address concerns with {customer["name"]} about pricing or delivery'
        else:
            action = f'Schedule a call with {customer["name"]} for a deeper conversation.'
        state['recommendations'].append(action)
    return state

# 4. Deal Proposal Agent
def propose_deals(state: Dict) -> Dict:
    state['deals'] = []
    for recommendation, customer in zip(state['recommendations'], state['crm_data']):
        deal = f'Create a deal with {customer["name"]} for {recommendation}'
        state['deals'].append(deal)
    return state

# Build Langgraph Workflow
def create_workflow():
    workflow = StateGraph(WorkflowState)

    workflow.add_node("process_crm_data", process_crm_data)
    workflow.add_node("analyze_sentiments", analyze_sentiments)
    workflow.add_node("generate_recommendations", generate_recommendations)
    workflow.add_node("propose_deals", propose_deals)

    workflow.set_entry_point("process_crm_data")

    workflow.add_edge("process_crm_data", "analyze_sentiments")
    workflow.add_edge("analyze_sentiments", "generate_recommendations")
    workflow.add_edge("generate_recommendations", "propose_deals")

    return workflow

# Mock Data for Workflow
crm_data = [
    {"name": "Acme Corp", "industry": "Manufacturing", "last_purchase": "2022-01-01"},
    {"name": "XYZ Corp", "industry": "Finance", "last_purchase": "2021-12-31"},
    {"name": "Widget Inc", "industry": "Consumer Goods", "last_purchase": "2021-11-30"}
]

# Mock Communications
communications = [
    "We exploring cost saving solutions for next year.",
    "Your demo was helpful, We will review internally",
    "We are interested in bundled pricing options for services."
]

#### Streamlit UI Integration ####

# Streamlit UI for Sales Guidance System
st.title("AI-powered Sales Guidance System")

# Input Data Display
st.write("### Input CRM Data")
st.dataframe(pd.DataFrame(crm_data))

# Start Workflow Button
if st.button("Generate Recommendations"):
    workflow = create_workflow().compile()
    initial_state = {
        'crm_data': crm_data,
        'communications': communications,
        'sentiments': [],
        'recommendations': [],
        'deals': []
    }
    # Execute Workflow
    final_state = workflow.invoke(initial_state)

    # Display Results
    st.write("### Sentiment Analysis Results")
    st.json(final_state['sentiments'])

    st.write("### Next Best Action")
    for rec in final_state['recommendations']:
        st.write(f'- {rec}')

    st.write("### Proposed Deals")
    deals_df = pd.DataFrame(final_state['deals'], columns=['Deal'])
    st.dataframe(deals_df)