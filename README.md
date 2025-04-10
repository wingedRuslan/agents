# Agents

## ReAct Character Counter Agent

ReAct Agent from scratch capable of counting the number of 'r's in 'strawberry' :grin:. 

Tool-calling ReAct Agent is [here](./react-agent/agent_count_chars.py).
* ReAct (Reasoning + Acting) architecture with specialized tool(s).
* Enable the LLM to reason about when to use external tools vs. when to answer directly (via iterative reasoning).
* JSON-Based Tool Calling: Clean interface for tool selection and invocation.
* Built on the OpenAI Python SDK with no external requirements


## Duo-Writing Agents

A collaborative writing system using two specialized agents (Writer and Critique) that work together to produce high-quality text that meets specific (user-defined) requirements. 

1.  :memo: **Writer Agent:** Generates initial content based on the provided writing task (equipped with Google Search Tool). 
2.  :mag: **Critique Agent:** Evaluates the generated content against a defined set of requirements.
3.  :arrows_counterclockwise: **Iteration:** The system cycles through until all requirements are met.

