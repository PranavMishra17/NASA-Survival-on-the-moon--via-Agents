"""
Team member agent for lunar survival challenge.
"""

from typing import List, Dict, Any, Optional

from agents.agent import Agent
import config

class TeamMember(Agent):
    """Agent specialized in scientific analysis for the lunar survival challenge."""
    
    def __init__(self, use_closed_loop_comm: bool = False):
        super().__init__(
            role="Science Analyst",
            expertise_description=config.AGENT_ROLES["Science Analyst"],
            use_team_leadership=False,  # Team members don't use leadership behaviors
            use_closed_loop_comm=use_closed_loop_comm
        )
        
        # Add science-specific knowledge
        self._initialize_scientific_knowledge()
    
    def _initialize_scientific_knowledge(self):
        """Initialize scientific knowledge about the lunar environment."""
        self.add_to_knowledge_base("lunar_environment", {
            "atmosphere": "No atmosphere, vacuum conditions",
            "temperature": "Extreme variations (+250°F in sunlight, -250°F in shadow)",
            "gravity": "1/6 of Earth's gravity",
            "radiation": "No protection from solar radiation",
            "day_length": "14 Earth days of daylight, 14 Earth days of darkness",
            "terrain": "Uneven surfaces, craters, dust"
        })
        
        self.add_to_knowledge_base("survival_principles", {
            "priorities": "Oxygen, water, shelter/temperature regulation, food",
            "navigation": "Stellar navigation is most reliable without magnetic field",
            "communication": "No atmosphere to carry sound waves, radio required",
            "movement": "Conserve energy and resources during trek",
            "physical_effects": "Vacuum effects on human body, radiation exposure risks"
        })
    
    def analyze_items(self) -> str:
        """
        Provide scientific analysis of the lunar survival items.
        
        Returns:
            The team member's analysis
        """
        prompt = f"""
        As a Science Analyst, I need you to analyze the importance of the following items for survival 
        during a 200-mile trek on the lunar surface:

        {', '.join(config.LUNAR_ITEMS)}
        
        For each item, consider:
        1. Its utility in the lunar environment
        2. Its importance for addressing survival needs
        3. Its relative priority compared to other items
        
        Provide a detailed analysis and then rank the items from 1 (most important) to 15 (least important).
        Present your ranking as a numbered list with a brief justification for each item's placement.
        """
        
        return self.chat(prompt)
    
    def respond_to_leader(self, leader_message: str) -> str:
        """
        Respond to the team leader's message.
        
        Args:
            leader_message: Message from the team leader
            
        Returns:
            The team member's response
        """
        prompt = f"""
        The Team Leader has provided the following input:
        
        "{leader_message}"
        
        As a Science Analyst, respond to the Team Leader's message. Apply your scientific knowledge of the lunar environment 
        and survival principles. Provide your perspective on the ranking of items, and be prepared to justify your reasoning
        with scientific facts.
        
        If you are using closed-loop communication, be sure to acknowledge receipt of the leader's message and confirm your
        understanding before providing your response.
        """
        
        return self.chat(prompt)