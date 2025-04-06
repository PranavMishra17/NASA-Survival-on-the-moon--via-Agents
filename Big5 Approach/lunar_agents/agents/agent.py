"""
Base agent class for lunar survival challenge.
"""

import logging
import json
from typing import List, Dict, Any, Optional, Tuple

from langchain_openai import AzureChatOpenAI
import config

class Agent:
    """Base agent class for lunar survival challenge."""
    
    def __init__(self, 
                 role: str, 
                 expertise_description: str,
                 use_team_leadership: bool = False,
                 use_closed_loop_comm: bool = False,
                 examples: Optional[List[Dict[str, str]]] = None):
        """
        Initialize an LLM-based agent with a specific role.
        
        Args:
            role: The role of the agent (e.g., "Science Analyst")
            expertise_description: Description of the agent's expertise
            use_team_leadership: Whether this agent uses team leadership behaviors
            use_closed_loop_comm: Whether this agent uses closed-loop communication
            examples: Optional examples to include in the prompt
        """
        self.role = role
        self.expertise_description = expertise_description
        self.use_team_leadership = use_team_leadership
        self.use_closed_loop_comm = use_closed_loop_comm
        self.examples = examples or []
        self.conversation_history = []
        self.knowledge_base = {}
        
        # Initialize logger
        self.logger = logging.getLogger(f"agent.{role}")
        
        # Initialize LLM
        self.client = AzureChatOpenAI(
            azure_deployment=config.AZURE_DEPLOYMENT,
            api_key=config.AZURE_API_KEY,
            api_version=config.AZURE_API_VERSION,
            azure_endpoint=config.AZURE_ENDPOINT,
            temperature=config.TEMPERATURE
        )
        
        # Build initial system message
        self.messages = [
            {"role": "system", "content": self._build_system_prompt()}
        ]
        
        # Add example conversations if provided
        if self.examples:
            for example in self.examples:
                self.messages.append({"role": "user", "content": example['question']})
                self.messages.append({
                    "role": "assistant", 
                    "content": example['answer'] + "\n\n" + example.get('reason', '')
                })
                
        self.logger.info(f"Initialized {self.role} agent")
    
    def _build_system_prompt(self) -> str:
        """Build the system prompt for the agent."""
        prompt = f"You are a {self.role} who {self.expertise_description}. "
        prompt += f"You are part of the {config.TEAM_NAME}. Your goal is to {config.TEAM_GOAL}. "

        # Add information about the lunar environment
        prompt += """
        The scenario is that you are a member of a space crew originally scheduled to rendezvous with a mother ship on the lighted surface of the moon. 
        Due to mechanical difficulties, however, your ship was forced to land at a spot 200 miles from the rendezvous point. 
        During re-entry and landing, much of the equipment aboard was damaged, and, since survival depends on reaching the mother ship, 
        the most critical items available must be chosen for the 200-mile trip.
        
        Your task is to rank the items in terms of their importance for the crew's survival.
        """

        # Add team leadership component if enabled
        if self.use_team_leadership:
            prompt += """
            As part of this team, you should demonstrate effective team leadership by:
            1. Facilitating team problem solving
            2. Providing performance expectations and acceptable interaction patterns
            3. Synchronizing and combining individual team member contributions
            4. Seeking and evaluating information that affects team functioning
            5. Clarifying team member roles
            6. Engaging in preparatory discussions and feedback sessions with the team
            """
        
        # Add closed-loop communication component if enabled
        if self.use_closed_loop_comm:
            prompt += """
            When communicating with your teammates, you should use closed-loop communication:
            1. When you send information, make it clear and specific
            2. When you receive information, acknowledge receipt and confirm understanding
            3. When your sent information is acknowledged, verify that it was understood correctly
            
            This three-step process ensures that critical information is properly exchanged.
            """
        
        return prompt
    
    def add_to_knowledge_base(self, key: str, value: Any) -> None:
        """
        Add information to the agent's knowledge base.
        
        Args:
            key: The key for the knowledge
            value: The value of the knowledge
        """
        self.knowledge_base[key] = value
        self.logger.info(f"Added to knowledge base: {key}")
    
    def get_from_knowledge_base(self, key: str) -> Any:
        """
        Retrieve information from the agent's knowledge base.
        
        Args:
            key: The key for the knowledge
            
        Returns:
            The value of the knowledge, or None if not found
        """
        return self.knowledge_base.get(key)
    
    def chat(self, message: str) -> str:
        """
        Send a message to the agent and get a response.
        
        Args:
            message: The message to send to the agent
            
        Returns:
            The agent's response
        """
        self.logger.info(f"Received message: {message[:100]}...")
        
        # Add the user message to the conversation
        self.messages.append({"role": "user", "content": message})
        
        # Get response from LLM
        response = self.client.predict_messages(
            messages=self.messages
        )
        
        # Extract and store the response
        assistant_message = response.content
        self.messages.append({"role": "assistant", "content": assistant_message})
        self.conversation_history.append({"user": message, "assistant": assistant_message})
        
        self.logger.info(f"Responded: {assistant_message[:100]}...")
        
        return assistant_message
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get the conversation history."""
        return self.conversation_history
    
    def get_item_ranking(self, message: str = None) -> List[str]:
        """
        Extract the agent's ranking of items from their response.
        
        Args:
            message: Optional message to analyze, defaults to last response
            
        Returns:
            List of items in ranked order
        """
        if message is None:
            if not self.conversation_history:
                return []
            message = self.conversation_history[-1]["assistant"]
        
        # This is a simple extraction method - in real applications you'd want more robust parsing
        ranking = []
        lines = message.split('\n')
        
        for line in lines:
            # Look for numbered items (1. Item, 2. Item, etc.)
            if any(f"{i}." in line for i in range(1, 16)):
                for item in config.LUNAR_ITEMS:
                    if item.lower() in line.lower():
                        ranking.append(item)
                        break
        
        return ranking