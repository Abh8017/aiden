import streamlit as st
import openai
from crewai import Agent, Task, Crew, Process
from graphviz import Digraph
import os
from dotenv import load_dotenv, find_dotenv

# Load environment variables
load_dotenv(find_dotenv())
openai_api_key = os.getenv('OPENAI_API_KEY')
openai_api_base = os.getenv('OPENAI_API_BASE', 'http://localhost:1234/v1')

if not openai_api_key:
    st.error("OPENAI_API_KEY environment variable not set.")
else:
    openai.api_key = openai_api_key
    openai.api_base = openai_api_base

# Display logo
st.image("logo.png", use_column_width=True)

# Display sidebar logo
st.sidebar.image("logo2.png",width=150)

# Initialize state
if 'agents' not in st.session_state:
    st.session_state.agents = []
if 'tasks' not in st.session_state:
    st.session_state.tasks = []
if 'hierarchy' not in st.session_state:
    st.session_state.hierarchy = []

# Sidebar for creating agents
st.sidebar.title("Create Agents")
agent_name = st.sidebar.text_input("Agent Name")
agent_role = st.sidebar.text_input("Agent Role")
agent_goal = st.sidebar.text_area("Agent Goal", height=100)
agent_backstory = st.sidebar.text_area("Agent Backstory", height=100)

if st.sidebar.button("Add Agent"):
    if agent_name and agent_role and agent_goal and agent_backstory:
        new_agent = Agent(
            role=agent_role,
            goal=agent_goal,
            backstory=agent_backstory,
            verbose=True,
            allow_delegation=False
        )
        st.session_state.agents.append({'name': agent_name, 'agent': new_agent})
        st.sidebar.success(f"Agent {agent_name} added successfully!")
    else:
        st.sidebar.error("Please fill in all agent details.")

# Sidebar for creating tasks
st.sidebar.title("Create Tasks")
task_description = st.sidebar.text_area("Task Description", height=100)
assigned_agent = st.sidebar.selectbox("Assign to Agent", [agent['name'] for agent in st.session_state.agents])

if st.sidebar.button("Add Task"):
    if task_description and assigned_agent:
        agent = next(agent['agent'] for agent in st.session_state.agents if agent['name'] == assigned_agent)
        new_task = Task(
            description=task_description,
            agent=agent
        )
        st.session_state.tasks.append({'description': task_description, 'task': new_task, 'agent': assigned_agent})
        st.sidebar.success(f"Task added successfully to {assigned_agent}!")
    else:
        st.sidebar.error("Please provide a task description and assign it to an agent.")

# Main interface
st.title("Get things done with GenAI")

# Display agents and their details
st.subheader("Agents")
for agent in st.session_state.agents:
    st.write(f"**Name:** {agent['name']}")
    st.write(f"**Role:** {agent['agent'].role}")
    st.write(f"**Goal:** {agent['agent'].goal}")
    st.write(f"**Backstory:** {agent['agent'].backstory}")

# Display tasks
st.subheader("Tasks")
for task in st.session_state.tasks:
    st.write(f"**Description:** {task['description']}")
    st.write(f"**Assigned Agent:** {task['agent']}")

# Hierarchy visualization
st.subheader("Hierarchy")
if st.session_state.hierarchy:
    dot = Digraph()
    for relation in st.session_state.hierarchy:
        dot.edge(relation['from'], relation['to'])
    st.graphviz_chart(dot)

# Add hierarchy details
agent_from = st.selectbox("From Agent", [agent['name'] for agent in st.session_state.agents])
agent_to = st.selectbox("To Agent", [agent['name'] for agent in st.session_state.agents])

if st.button("Add Hierarchy Relation"):
    if agent_from and agent_to and agent_from != agent_to:
        st.session_state.hierarchy.append({'from': agent_from, 'to': agent_to})
        st.success("Hierarchy relation added successfully!")
    else:
        st.error("Please select two different agents.")

# Workflow execution
if st.button("Execute Workflow"):
    if st.session_state.agents and st.session_state.tasks:
        crew_agents = [agent['agent'] for agent in st.session_state.agents]
        crew_tasks = [task['task'] for task in st.session_state.tasks]
        crew = Crew(
            agents=crew_agents,
            tasks=crew_tasks,
            verbose=True,
            process=Process.sequential
        )
        result = crew.kickoff()
        st.subheader("Workflow Results")
        st.write(result)
    else:
        st.error("Please add agents and tasks before executing the workflow.")

# Satisfaction rating
st.sidebar.title("Satisfaction Rating")
satisfaction_rating = st.sidebar.slider("Rate the performance of each agent", 1, 5, 3)
st.sidebar.write(f"Your rating: {satisfaction_rating}")
