"""
Modular agent implementation for lunar survival challenge.
"""

from typing import List, Dict, Any, Optional
import random
import logging

from agents.agent import Agent
import config

class ModularAgent(Agent):
    """
    Modular agent with specialization capabilities for the lunar survival challenge.
    This agent can specialize in different areas and optionally take leadership roles.
    """
    
    def __init__(self, role_type="Science", use_closed_loop_comm: bool = False, can_lead: bool = False):
        """
        Initialize a team member with specific role expertise.
        
        Args:
            role_type: The specific role type ("Science" or "Resource")
            use_closed_loop_comm: Whether to use closed-loop communication
            can_lead: Whether this agent can take leadership responsibilities
        """
        # Set role and expertise based on role type
        if role_type == "Science":
            role = "Science Analyst"
            expertise = config.AGENT_ROLES["Science Analyst"]
            self.specialization = "science"
        elif role_type == "Resource":
            role = "Resource Manager"
            expertise = config.AGENT_ROLES["Resource Manager"]
            self.specialization = "resource"
        else:
            role = "Team Member"
            expertise = "General team member with balanced knowledge"
            self.specialization = "general"
        
        # Initialize the base agent
        super().__init__(
            role=role,
            expertise_description=expertise,
            use_team_leadership=can_lead,  # Now any agent can potentially have leadership abilities
            use_closed_loop_comm=use_closed_loop_comm
        )
        
        # Track whether this agent has leadership capabilities
        self.can_lead = can_lead
        
        # Initialize specialized knowledge based on role
        self._initialize_specialized_knowledge()
        
        # Create shared knowledge repository that can be accessed by other agents
        self.shared_knowledge = {}
    
    def _initialize_specialized_knowledge(self):
        """Initialize knowledge specific to the agent's specialization."""
        if self.specialization == "science":
            self._initialize_scientific_knowledge()
        elif self.specialization == "resource":
            self._initialize_resource_knowledge()
        else:
            # General knowledge for non-specialized agents
            self._initialize_general_knowledge()
            
        # Add NASA rationale to all agents regardless of specialization
        self.add_to_knowledge_base("nasa_rationale", config.NASA_RATIONALE)
    
    def _initialize_scientific_knowledge(self):
        """Initialize scientific knowledge about the lunar environment."""
        # Detailed lunar environment knowledge
        self.add_to_knowledge_base("lunar_environment", {
            "atmosphere": "No atmosphere, complete vacuum conditions which affects heat distribution, sound transmission, and protection from radiation",
            "temperature": "Extreme variations (+250°F in direct sunlight, -250°F in shadow) with rapid shifts due to lack of atmospheric insulation",
            "gravity": "1/6 of Earth's gravity (0.166g), requiring less energy for movement but also less stability",
            "radiation": "No atmospheric or magnetic field protection from solar radiation, cosmic rays, and solar flares",
            "day_length": "14 Earth days of daylight followed by 14 Earth days of darkness due to lunar rotation",
            "terrain": "Uneven surfaces, craters, regolith (fine dust) that clings electrostatically to equipment and can damage seals",
            "visibility": "High contrast between light and shadow areas, causing visual perception difficulties"
        })
        
        # Detailed survival principles
        self.add_to_knowledge_base("survival_principles", {
            "oxygen": "Absolutely critical; no natural oxygen on lunar surface; survival impossible beyond minutes without it",
            "water": "Critical for hydration, cooling, and preventing rapid body fluid loss in vacuum environment",
            "temperature_regulation": "Essential to manage temperature extremes from solar radiation and vacuum conditions",
            "navigation": "Stellar navigation most reliable; no magnetic field for compass; landmarks and maps crucial",
            "communication": "No atmosphere to carry sound; radio or visual signals required for distance communication",
            "radiation_protection": "Necessary to prevent acute radiation syndrome and long-term cell damage",
            "movement_efficiency": "Important to minimize oxygen consumption and avoid exhaustion in spacesuits"
        })
        
        # Add scientific reasoning methods
        self.add_to_knowledge_base("scientific_reasoning", {
            "empirical_analysis": "Evaluating items based on known physical properties and lunar conditions",
            "survival_hierarchy": "Prioritizing items based on Maslow's hierarchy applied to lunar survival",
            "resource_criticality": "Assessing which resources cannot be substituted or lived without",
            "functional_analysis": "Evaluating multiple uses and adaptability of items in emergency situations",
            "risk_assessment": "Calculating probability and impact of various failure scenarios"
        })
    
    def _initialize_resource_knowledge(self):
        """Initialize knowledge about resource management for lunar survival."""
        # Resource management principles
        self.add_to_knowledge_base("resource_management", {
            "prioritization": "Allocating limited resources to highest survival value tasks",
            "conservation": "Techniques to minimize consumption of non-renewable resources",
            "repurposing": "Using equipment for alternative purposes when needed",
            "redundancy": "Ensuring critical functions have backups",
            "synergy": "Combining resources to increase overall effectiveness"
        })
        
        # Item utility assessment
        self.add_to_knowledge_base("item_utility", {
            "primary_function": "Original intended use of each item",
            "secondary_functions": "Alternative creative uses in emergency situations",
            "complementary_items": "How items can work together for greater effect",
            "weight_to_utility_ratio": "Value considering transport effort required",
            "durability": "Expected lifespan in harsh lunar conditions"
        })
        
        # Basic lunar environment knowledge (less detailed than science specialist)
        self.add_to_knowledge_base("lunar_environment", {
            "atmosphere": "No atmosphere, vacuum conditions",
            "temperature": "Extreme variations between sunlight and shadow",
            "gravity": "1/6 of Earth's gravity",
            "radiation": "High radiation exposure risk",
            "terrain": "Dusty, cratered surface challenging for movement"
        })
    
    def _initialize_general_knowledge(self):
        """Initialize general knowledge for non-specialized agents."""
        # Basic lunar environment knowledge
        self.add_to_knowledge_base("lunar_environment", {
            "atmosphere": "No atmosphere, vacuum conditions",
            "temperature": "Extreme temperature variations",
            "gravity": "Low gravity environment",
            "radiation": "Exposure to solar radiation",
            "terrain": "Dusty, uneven surfaces"
        })
        
        # Basic survival principles
        self.add_to_knowledge_base("survival_principles", {
            "priorities": "Oxygen, water, shelter/temperature, food",
            "navigation": "Finding way to rendezvous point",
            "conservation": "Conserving limited resources"
        })
    
    def share_knowledge(self, other_agent):
        """
        Share specialized knowledge with another agent.
        
        Args:
            other_agent: Another agent to share knowledge with
        """
        # Copy shared knowledge to other agent
        for key, value in self.shared_knowledge.items():
            other_agent.add_to_knowledge_base(key, value)
        
        # Add specialized knowledge to shared repository
        if self.specialization == "science":
            if "lunar_environment" in self.knowledge_base:
                self.shared_knowledge["science_lunar_environment"] = self.knowledge_base["lunar_environment"]
            if "survival_principles" in self.knowledge_base:
                self.shared_knowledge["science_survival_principles"] = self.knowledge_base["survival_principles"]
        
        elif self.specialization == "resource":
            if "resource_management" in self.knowledge_base:
                self.shared_knowledge["resource_management"] = self.knowledge_base["resource_management"]
            if "item_utility" in self.knowledge_base:
                self.shared_knowledge["item_utility"] = self.knowledge_base["item_utility"]
        
        self.logger.info(f"Agent {self.role} shared knowledge with {other_agent.role}")
        return self.shared_knowledge
    
    def analyze_items(self) -> str:
        """
        Provide specialized analysis of the lunar survival items.
        
        Returns:
            The agent's analysis
        """
        prompt = f"""
        As a {self.role} with expertise in {self.specialization}, analyze the importance of the following items 
        for survival during a 200-mile trek on the lunar surface:

        {', '.join(config.LUNAR_ITEMS)}
        
        Based on your specialized knowledge, consider:
        1. Each item's utility in the lunar environment
        2. Its importance for addressing survival needs
        3. Its relative priority compared to other items
        4. Any creative uses or applications beyond its primary function
        
        Provide a detailed analysis and then rank the items from 1 (most important) to 15 (least important).
        Present your ranking as a numbered list with a brief justification for each item's placement.
        """
        
        return self.chat(prompt)
    
    def respond_to_agent(self, agent_message: str) -> str:
        """
        Respond to another agent's message from your specialized perspective.
        
        Args:
            agent_message: Message from another agent
            
        Returns:
            This agent's specialized response
        """
        prompt = f"""
        Another team member has provided the following input:
        
        "{agent_message}"
        
        As a {self.role} with expertise in {self.specialization}, respond to this message.
        Apply your specialized knowledge to this discussion about lunar survival items.
        If you notice any misconceptions or have additional information to add from your
        area of expertise, share that information.
        
        If you are using closed-loop communication, acknowledge the message and confirm your
        understanding before providing your response.
        """
        
        return self.chat(prompt)
        
    def leadership_action(self, action_type: str, context: str = None) -> str:
        """
        Perform a leadership action if this agent has leadership capabilities.
        
        Args:
            action_type: Type of leadership action
            context: Optional context information
            
        Returns:
            Result of the leadership action, or explanation if not a leader
        """
        if not self.can_lead:
            return f"As a {self.role} without leadership designation, I cannot perform leadership actions."
        
        action_prompts = {
            "define_task": f"""
                As the designated leader for this task, define the overall approach for ranking lunar survival items.
                
                Break this down into clear subtasks, specifying:
                1. The objective of each subtask
                2. The sequence in which they should be completed
                3. How to evaluate successful completion
                
                Provide clear, specific instructions that will guide the team through this process.
                
                Additional context: {context or ''}
            """,
            
            "synthesize": f"""
                As the designated leader, synthesize the team's perspectives into a consensus ranking.
                
                Context information: {context or ''}
                
                Create a final ranking that:
                1. Incorporates the scientific principles critical for lunar survival
                2. Balances different perspectives from team members
                3. Provides clear reasoning for each item's position
                
                Present your final ranking as a numbered list from 1 to 15 with brief justifications.
                Ensure all items from the lunar items list are included exactly once.
            """,
            
            "facilitate": f"""
                As the designated leader, facilitate progress on our current discussion.
                
                Current context: {context or ''}
                
                Please:
                1. Identify areas of agreement and disagreement
                2. Propose next steps to move the discussion forward
                3. Ask specific questions to gather needed information
                4. Summarize key insights so far
                
                Your goal is to help the team make progress rather than advocate for a specific position.
            """
        }
        
        if action_type in action_prompts:
            return self.chat(action_prompts[action_type])
        else:
            return f"Unknown leadership action: {action_type}"


# Factory function to create agents with random or specified leadership
def create_agent_team(use_team_leadership=True, use_closed_loop_comm=False, random_leader=False):
    """
    Create a team of agents with different specializations.
    
    Args:
        use_team_leadership: Whether to use team leadership
        use_closed_loop_comm: Whether to use closed-loop communication
        random_leader: Whether to randomly assign leadership (if True, ignores use_team_leadership)
        
    Returns:
        Dictionary of created agents
    """
    # Determine leadership assignment
    science_leads = False
    resource_leads = False
    
    if random_leader:
        # Randomly choose one agent to be the leader
        if random.random() < 0.5:
            science_leads = True
        else:
            resource_leads = True
    elif use_team_leadership:
        # Default leadership assignment if not random
        science_leads = True
    
    # Create the agents
    science_agent = ModularAgent(
        role_type="Science", 
        use_closed_loop_comm=use_closed_loop_comm,
        can_lead=science_leads
    )
    
    resource_agent = ModularAgent(
        role_type="Resource", 
        use_closed_loop_comm=use_closed_loop_comm,
        can_lead=resource_leads
    )
    
    # Log the team configuration
    logging.info(f"Created agent team with leadership configuration:")
    logging.info(f"  Science Agent leads: {science_leads}")
    logging.info(f"  Resource Agent leads: {resource_leads}")
    logging.info(f"  Closed-loop communication: {use_closed_loop_comm}")
    
    # Share knowledge between agents
    science_agent.share_knowledge(resource_agent)
    resource_agent.share_knowledge(science_agent)
    
    return {
        "science": science_agent,
        "resource": resource_agent,
        "leader": science_agent if science_leads else (resource_agent if resource_leads else None)
    }