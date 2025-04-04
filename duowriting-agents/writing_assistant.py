import os
from typing import Dict, Any, Optional
from autogen import ConversableAgent, register_function

from prompts import WRITER_SYSTEM_PROMPT, CRITIQUE_SYSTEM_MESSAGE
from tools import google_search


class WritingAssistant:
    """A collaborative writing system with Writer and Critique agents."""
    
    def __init__(
        self,
        llm_config: Dict[str, Any],
        writer_system_message: Optional[str] = None,
        critique_system_message: Optional[str] = None,
        max_iterations: int = 5,
    ):
        """
        Initialize the Writer and Critique agents.
        
        Args:
            llm_config: Configuration for the language model.
            writer_system_message: Custom system message for the Writer agent.
            critique_system_message: Custom system message for the Critique agent.
            max_iterations: Maximum number of revision iterations.
        """
        writer_system_message = writer_system_message or WRITER_SYSTEM_PROMPT
        critique_system_message = critique_system_message or CRITIQUE_SYSTEM_MESSAGE
        self.max_iterations = max_iterations
        
        self.writer = ConversableAgent(
            name="Writer",
            description="Creates written content based on requirements",
            system_message=writer_system_message,
            llm_config=llm_config,
            human_input_mode="NEVER",
            max_consecutive_auto_reply=2
        )
        self.critique = ConversableAgent(
            name="Critique",
            description="Reviews content and provides feedback until requirements are met",
            system_message=critique_system_message,
            llm_config=llm_config,
            human_input_mode="NEVER",
            max_consecutive_auto_reply=1,
            is_termination_msg=lambda msg: "approved" in str(msg.get("content", "")).lower()
        )
        
        # Register the Google search tool with agents
        register_function(
            google_search,
            caller=self.writer,      # The writer can suggest calls to the google search
            executor=self.critique,  # The critique can execute the google search calls.
            name="google_search",
            description="Search for information on Google to get up-to-date facts and data",
        )
    
    def generate(self, writing_task: str, requirements: str) -> str:
        """
        Generate content based on the task and requirements.
        
        Args:
            writing_task: Description of what needs to be written.
            requirements: Specific criteria the writing should meet.
            
        Returns:
            str: The final approved content.
        """
        initial_message = (
            f"Writing Task: {writing_task}\n"
            f"Standards for Evaluation: {requirements}\n"
            "Please write content that addresses this task. Your writing will be evaluated based on the standards provided."
        )
        
        # Start the chat between Writer and Critique agents
        chat_result = self.critique.initiate_chat(
            self.writer,
            message=initial_message,
            max_turns=self.max_iterations, 
            summary_method="last_msg",
        )

        self.chat_history = chat_result.chat_history

        # Extract the final content (last message from the Writer)
        for msg in reversed(self.chat_history):
            if msg["name"] == "Writer":
                return msg["content"]
        
        return "No content was generated."


if __name__ == "__main__":

    llm_config = {
        "config_list": [
            {
                "model": "gpt-4o-mini", 
                "api_key": os.environ.get("OPENAI_API_KEY")
            }
        ]
    }
    
    # task = "Write an official email to a manager asking for the presentation deck discussed in the meeting."
    # requirements = "The email should be short, clear, and straight to the point."

    task = "Write a brief update on the latest developments in AI"
    requirements = "The content should be factual, mention recent advancements within the last 6 months, and be understandable to a general audience."

    assistant = WritingAssistant(llm_config)
    final_content = assistant.generate(task, requirements)
    
    print("\nFINAL APPROVED CONTENT:\n")
    print(final_content)

