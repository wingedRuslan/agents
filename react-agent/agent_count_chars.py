"""ReAct Agent to properly count the number of times a character occurs in a string."""

import os
from dotenv import load_dotenv
from openai import OpenAI

from tools import tool, parse_action_call_tool

load_dotenv()


@tool
def count_char_occurrences(character: str, input_string: str) -> int:
    """Count the number of times a character appears in a string.

    Args:
        character (str): The character to count (should be a single character)
        input_string (str): The string to search in

    Returns:
        int: The number of occurrences of the character in the string
    """
    if len(character) != 1:
        raise ValueError("The 'character' parameter must be a single character")

    # Case-insensitive matching
    lower_character = character.lower()
    lower_input_string = input_string.lower()

    return lower_input_string.count(lower_character)


class ToolCallingAgent:
    """JSON Agent: The Action to take is specified in JSON format."""

    SYSTEM_PROMPT = """
        You are an AI assistant designed to help users efficiently and accurately. Your primary goal is to provide helpful, precise, and clear responses.
        Answer the following questions as best you can. You have access to the following tools:

        {tools_information}
        
        The way you use the tools is by specifying a json blob.
        Specifically, this json should have a `action` key (with the name of the tool to use) and a `action_input` key (with the input to the tool going here).

        ALWAYS use the following format:

        Question: the input question you must answer
        Thought: you should always think about one action to take. Only one action at a time in this format:
        Action:
        ```
        $JSON_BLOB
        ```
        Observation: the result of the action. This Observation is unique, complete, and the source of truth.
        ... (this Thought/Action/Observation can repeat N times, you should take several steps when needed. The $JSON_BLOB must be formatted as markdown and only use a SINGLE action at a time.)

        You must always end your output with the following format:

        Thought: I now know the final answer
        Final Answer: the final answer to the original input question

        Now begin! Reminder to ALWAYS use the exact characters `Final Answer:` when you provide a definitive answer. 
    """

    def __init__(self, model=None, tools=None):
        self.model = model if model else OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.tools = tools if tools else []

        # Build the string representation of all tools
        tools_information = "\n".join(tool.to_string() for tool in self.tools)
        
        self.system_prompt = self.SYSTEM_PROMPT.format(
            tools_information=tools_information
        )

    def run(self, user_query: str, max_turns: int = 5) -> str:
        """
        Run the agent to answer a user query, allowing multiple tool-calling turns.

        Args:
            user_query (str): The user's question or request
            max_turns (int): Maximum number of ReAct iterations

        Returns:
            str: The final agent response
        """
        # Init conversation with system prompt and user query
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_query},
        ]

        while max_turns > 0:
            # Get agent step before 'Observation' (tool calling)
            completion = self.model.chat.completions.create(
                model="gpt-4o-mini", messages=messages, stop=["Observation"]
            )
            agent_step = completion.choices[0].message.content
            print(f"Agent: \n{agent_step}")

            # Check if response contains "Final Answer:"
            if "Final Answer:" in agent_step:
                final_answer = agent_step.split("Final Answer:")[1].strip()
                print(f"Final Answer Found: {final_answer}")
                return final_answer

            # Parse the action and call the appropriate tool
            tool_output = parse_action_call_tool(
                text=agent_step, available_tools=self.tools
            )
            print(f"Observation (Tool Output): {tool_output}")

            # Add the agent's response and tool output to the conversation
            messages.append(
                {
                    "role": "assistant",
                    "content": agent_step + f"\nObservation: {tool_output}",
                }
            )

            max_turns -= 1
            print("\n-------\n")

        return "Please submit another request!"


if __name__ == "__main__":
    print("ReAct Agent to properly count the number of the 'r' in 'strawberry'\n---\n")

    user_query = "how many r's in strawberry?"

    tools = [count_char_occurrences]
    agent = ToolCallingAgent(model=None, tools=[count_char_occurrences])
    result = agent.run(user_query)

    print(f"\n'{user_query:}': {result}")

