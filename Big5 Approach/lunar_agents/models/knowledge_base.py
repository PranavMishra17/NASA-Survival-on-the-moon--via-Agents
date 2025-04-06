"""
Knowledge base management for lunar survival agents.
"""

from typing import Dict, Any, List, Optional

class KnowledgeBase:
    """
    Knowledge base for storing and retrieving agent knowledge.
    
    This class provides a structured way to store domain knowledge,
    experiential knowledge, and reasoning processes.
    """
    
    def __init__(self, agent_role: str):
        """
        Initialize a knowledge base for an agent.
        
        Args:
            agent_role: Role of the agent
        """
        self.agent_role = agent_role
        self.domain_knowledge = {}
        self.experiential_knowledge = {}
        self.reasoning_processes = {}
        self.teamwork_knowledge = {}
    
    def add_domain_knowledge(self, category: str, knowledge: Dict[str, Any]) -> None:
        """
        Add domain-specific knowledge.
        
        Args:
            category: Category of knowledge (e.g., "lunar_environment")
            knowledge: Dictionary of knowledge items
        """
        if category not in self.domain_knowledge:
            self.domain_knowledge[category] = {}
        
        self.domain_knowledge[category].update(knowledge)
    
    def add_experiential_knowledge(self, experience_type: str, knowledge: Dict[str, Any]) -> None:
        """
        Add experiential knowledge based on interactions.
        
        Args:
            experience_type: Type of experience (e.g., "team_interactions")
            knowledge: Dictionary of knowledge items
        """
        if experience_type not in self.experiential_knowledge:
            self.experiential_knowledge[experience_type] = {}
        
        self.experiential_knowledge[experience_type].update(knowledge)
    
    def add_reasoning_process(self, process_name: str, steps: List[str]) -> None:
        """
        Add a reasoning process.
        
        Args:
            process_name: Name of the reasoning process
            steps: List of steps in the reasoning process
        """
        self.reasoning_processes[process_name] = steps
    
    def add_teamwork_knowledge(self, component: str, knowledge: Dict[str, Any]) -> None:
        """
        Add knowledge about teamwork components.
        
        Args:
            component: Teamwork component (e.g., "leadership", "communication")
            knowledge: Dictionary of knowledge items
        """
        if component not in self.teamwork_knowledge:
            self.teamwork_knowledge[component] = {}
        
        self.teamwork_knowledge[component].update(knowledge)
    
    def get_domain_knowledge(self, category: Optional[str] = None) -> Dict[str, Any]:
        """
        Retrieve domain knowledge.
        
        Args:
            category: Optional category to filter by
            
        Returns:
            Dictionary of domain knowledge
        """
        if category:
            return self.domain_knowledge.get(category, {})
        return self.domain_knowledge
    
    def get_experiential_knowledge(self, experience_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Retrieve experiential knowledge.
        
        Args:
            experience_type: Optional type to filter by
            
        Returns:
            Dictionary of experiential knowledge
        """
        if experience_type:
            return self.experiential_knowledge.get(experience_type, {})
        return self.experiential_knowledge
    
    def get_reasoning_process(self, process_name: str) -> List[str]:
        """
        Retrieve a reasoning process.
        
        Args:
            process_name: Name of the reasoning process
            
        Returns:
            List of steps in the reasoning process
        """
        return self.reasoning_processes.get(process_name, [])
    
    def get_teamwork_knowledge(self, component: Optional[str] = None) -> Dict[str, Any]:
        """
        Retrieve teamwork knowledge.
        
        Args:
            component: Optional component to filter by
            
        Returns:
            Dictionary of teamwork knowledge
        """
        if component:
            return self.teamwork_knowledge.get(component, {})
        return self.teamwork_knowledge
    
    def update_from_interaction(self, interaction_data: Dict[str, Any]) -> None:
        """
        Update knowledge base from an interaction.
        
        Args:
            interaction_data: Data from an interaction
        """
        # Extract relevant information from the interaction
        if "new_knowledge" in interaction_data:
            for category, knowledge in interaction_data["new_knowledge"].items():
                self.add_domain_knowledge(category, knowledge)
        
        # Update experiential knowledge
        if "interaction_type" in interaction_data:
            experience_type = interaction_data["interaction_type"]
            experience_data = {
                "timestamp": interaction_data.get("timestamp"),
                "outcome": interaction_data.get("outcome"),
                "counterpart": interaction_data.get("counterpart"),
                "notes": interaction_data.get("notes")
            }
            
            self.add_experiential_knowledge(
                experience_type, 
                {interaction_data.get("id", "unknown"): experience_data}
            )
    
    def serialize(self) -> Dict[str, Any]:
        """
        Serialize the knowledge base to a dictionary.
        
        Returns:
            Dictionary representation of the knowledge base
        """
        return {
            "agent_role": self.agent_role,
            "domain_knowledge": self.domain_knowledge,
            "experiential_knowledge": self.experiential_knowledge,
            "reasoning_processes": self.reasoning_processes,
            "teamwork_knowledge": self.teamwork_knowledge
        }
    
    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> 'KnowledgeBase':
        """
        Deserialize a dictionary into a knowledge base.
        
        Args:
            data: Dictionary representation of a knowledge base
            
        Returns:
            KnowledgeBase instance
        """
        kb = cls(data["agent_role"])
        kb.domain_knowledge = data.get("domain_knowledge", {})
        kb.experiential_knowledge = data.get("experiential_knowledge", {})
        kb.reasoning_processes = data.get("reasoning_processes", {})
        kb.teamwork_knowledge = data.get("teamwork_knowledge", {})
        
        return kb
    
    def initialize_leadership_knowledge(self) -> None:
        """Initialize knowledge related to team leadership."""
        self.add_teamwork_knowledge("leadership", {
            "definition": "Ability to direct and coordinate the activities of other team members, assess team performance, assign tasks, develop knowledge, motivate members, and establish a positive atmosphere",
            "behaviors": [
                "Facilitate team problem solving",
                "Provide performance expectations and acceptable interaction patterns",
                "Synchronize and combine individual team member contributions",
                "Seek and evaluate information that affects team functioning",
                "Clarify team member roles",
                "Engage in preparatory meetings and feedback sessions"
            ],
            "importance": "Team leadership facilitates team effectiveness by guiding cognitive processes, coordination, and collective motivation rather than by providing direct solutions"
        })
    
    def initialize_communication_knowledge(self) -> None:
        """Initialize knowledge related to closed-loop communication."""
        self.add_teamwork_knowledge("closed_loop_communication", {
            "definition": "The exchange of information between a sender and a receiver with verification of understanding",
            "steps": [
                "Sender initiates message",
                "Receiver acknowledges receipt and confirms understanding",
                "Sender follows up to verify message was received correctly"
            ],
            "importance": "Closed-loop communication ensures critical information is properly exchanged, especially in complex or stressful environments",
            "examples": [
                "Sender: 'The oxygen tanks should be our top priority.'",
                "Receiver: 'I understand that you're saying oxygen tanks are most important for survival. That makes sense because there's no oxygen on the moon.'",
                "Sender: 'That's correct. I'm glad we're aligned on the importance of oxygen for survival.'"
            ]
        })
    
    def initialize_lunar_environment_knowledge(self) -> None:
        """Initialize knowledge about the lunar environment."""
        self.add_domain_knowledge("lunar_environment", {
            "atmosphere": "Virtually none; vacuum conditions",
            "temperature": "Extreme variations from -280°F in shade to +260°F in sunlight",
            "gravity": "1/6 of Earth's gravity",
            "radiation": "No atmospheric protection from solar and cosmic radiation",
            "day_night_cycle": "14 Earth days of daylight followed by 14 Earth days of darkness",
            "terrain": "Covered with powdery dust, craters, and rocky surfaces",
            "resources": "No readily available water or oxygen",
            "communication": "No atmosphere to carry sound waves; requires radio or physical contact"
        })
    
    def initialize_survival_priorities_knowledge(self) -> None:
        """Initialize knowledge about survival priorities."""
        self.add_domain_knowledge("survival_priorities", {
            "oxygen": "Critical for respiration; no survival without it",
            "water": "Essential for maintaining hydration and body functions",
            "temperature_regulation": "Protection from extreme temperature variations",
            "navigation": "Ability to locate the rendezvous point",
            "communication": "Ability to signal location and status",
            "physical_needs": "Energy, shelter, and first aid"
        })