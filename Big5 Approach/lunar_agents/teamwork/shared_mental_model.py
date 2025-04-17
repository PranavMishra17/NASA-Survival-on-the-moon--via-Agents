"""
Shared Mental Model implementation for lunar survival agents.

Shared Mental Model: An organizing knowledge structure of the relationships
among the task the team is engaged in and how the team members will interact.
This enables team members to anticipate and predict each other's needs through
common understandings of the environment and expectations of performance.
"""

import logging
import json
from typing import Dict, List, Any

class SharedMentalModel:
    """
    Implements shared mental model capabilities for agents.
    
    A shared mental model enables agents to have common understanding of:
    1. Task-related knowledge (task procedures, strategies, environment constraints)
    2. Team-related knowledge (roles, responsibilities, interaction patterns)
    
    This shared understanding helps with coordination and anticipation of needs.
    """
    
    def __init__(self):
        """Initialize the shared mental model handler."""
        self.logger = logging.getLogger("teamwork.shared_mental_model")
        
        # Initialize knowledge repositories
        self.task_knowledge = {}
        self.team_knowledge = {}
        self.shared_understanding = {}
        self.convergence_metrics = []
        
        self.logger.info("Initialized shared mental model handler")
    
    def initialize_lunar_task_model(self) -> Dict[str, Any]:
        """
        Initialize the shared task-related mental model for lunar survival.
        
        Returns:
            Dictionary with task model elements
        """
        # Create task-related mental model
        task_model = {
            "objective": "Rank 15 items in order of importance for a 200-mile trek on the lunar surface",
            "environment": {
                "atmosphere": "None (vacuum)",
                "temperature": "Extreme variations (+250°F in sunlight, -250°F in shadow)",
                "gravity": "1/6 of Earth's gravity",
                "terrain": "Dusty, cratered, uneven surfaces",
                "radiation": "High with no atmospheric protection",
                "day_length": "14 Earth days of light, 14 days of darkness"
            },
            "survival_priorities": [
                "Oxygen supply",
                "Water/fluid replacement",
                "Navigation to rendezvous point",
                "Temperature regulation",
                "Food/energy",
                "Communication",
                "First aid/medical"
            ],
            "evaluation_criteria": {
                "scientific_validity": "Does the ranking align with scientific facts about the lunar environment?",
                "resource_efficiency": "Does the ranking optimize the use of limited resources?",
                "completeness": "Are all 15 items included in the ranking?",
                "justification": "Is each item's placement supported by clear reasoning?"
            },
            "task_procedure": [
                "Individual assessment of items based on specialized knowledge",
                "Sharing of perspectives and justifications",
                "Identification of areas of agreement and disagreement",
                "Resolution of disagreements through evidence-based discussion",
                "Creation of consensus ranking"
            ]
        }
        
        # Store in task knowledge repository
        self.task_knowledge["lunar_survival"] = task_model
        
        self.logger.info("Initialized lunar survival task mental model")
        return task_model
    
    def initialize_team_model(self, roles: List[str]) -> Dict[str, Any]:
        """
        Initialize the shared team-related mental model.
        
        Args:
            roles: List of agent roles in the team
            
        Returns:
            Dictionary with team model elements
        """
        # Create team-related mental model
        team_model = {
            "roles": {},
            "interaction_patterns": {
                "sequential_refinement": "Each agent takes turns refining a single ranking",
                "knowledge_sharing": "Agents share specialized knowledge to support decisions",
                "disagreement_resolution": "Evidence-based approach to resolving different perspectives",
                "performance_monitoring": "Agents monitor each other's work for completeness and accuracy"
            },
            "coordination_mechanisms": {
                "explicit_communication": "Clear expression of reasoning and justifications",
                "knowledge_integration": "Combining specialized knowledge for better decisions",
                "turn-taking": "Alternating refinement of rankings",
                "convergence_tracking": "Monitoring how rankings converge over iterations"
            }
        }
        
        # Add role-specific information
        for role in roles:
            if "Science" in role:
                team_model["roles"][role] = {
                    "expertise": "Scientific knowledge of lunar environment and survival requirements",
                    "responsibilities": [
                        "Provide accurate scientific assessment of lunar conditions",
                        "Evaluate items based on scientific principles",
                        "Identify scientifically invalid assumptions in rankings"
                    ],
                    "information_needs": [
                        "Resource management considerations",
                        "Multiple-use potential of items"
                    ]
                }
            elif "Resource" in role:
                team_model["roles"][role] = {
                    "expertise": "Resource management and optimization of supplies",
                    "responsibilities": [
                        "Assess efficiency and utility of items",
                        "Identify multiple-use potential of items",
                        "Optimize ranking for resource constraints"
                    ],
                    "information_needs": [
                        "Scientific facts about lunar environment",
                        "Physical principles affecting item utility"
                    ]
                }
            else:
                team_model["roles"][role] = {
                    "expertise": "General lunar survival knowledge",
                    "responsibilities": [
                        "Provide balanced assessment of items",
                        "Integrate different perspectives",
                        "Ensure complete and consistent ranking"
                    ],
                    "information_needs": [
                        "Specialized scientific and resource knowledge",
                        "NASA's historical ranking rationale"
                    ]
                }
        
        # Store in team knowledge repository
        self.team_knowledge["lunar_team"] = team_model
        
        self.logger.info(f"Initialized team mental model with {len(roles)} roles")
        return team_model
    
    def update_shared_understanding(self, agent_role: str, understanding: Dict[str, Any]) -> None:
        """
        Update an agent's understanding in the shared mental model.
        
        Args:
            agent_role: Role of the agent sharing understanding
            understanding: Dictionary of the agent's current understanding
        """
        self.shared_understanding[agent_role] = understanding
        self.logger.info(f"Updated shared understanding from {agent_role}")
        
        # Calculate convergence metrics if multiple agents have shared
        if len(self.shared_understanding) > 1:
            convergence = self._calculate_understanding_convergence()
            self.convergence_metrics.append(convergence)
            self.logger.info(f"Current understanding convergence: {convergence['overall_convergence']:.2f}")
    
    def _calculate_understanding_convergence(self) -> Dict[str, Any]:
        """
        Calculate how well team members' mental models have converged.
        
        Returns:
            Dictionary with convergence metrics
        """
        # This is a simplified calculation - in a real implementation, 
        # this would use more sophisticated comparison algorithms
        convergence = {
            "timestamp": "current_time",
            "elements": {},
            "overall_convergence": 0.0
        }
        
        # Extract all agents
        agents = list(self.shared_understanding.keys())
        
        # Compare each pair of agents
        total_comparisons = 0
        total_similarity = 0.0
        
        for i in range(len(agents)):
            for j in range(i+1, len(agents)):
                agent1 = agents[i]
                agent2 = agents[j]
                
                # Compare understandings
                understanding1 = self.shared_understanding[agent1]
                understanding2 = self.shared_understanding[agent2]
                
                # Check if both have priority lists to compare
                if "priorities" in understanding1 and "priorities" in understanding2:
                    priorities1 = understanding1["priorities"]
                    priorities2 = understanding2["priorities"]
                    
                    similarity = self._calculate_list_similarity(priorities1, priorities2)
                    convergence["elements"][f"priorities_{agent1}_{agent2}"] = similarity
                    
                    total_similarity += similarity
                    total_comparisons += 1
                
                # Check if both have environment understanding
                if "environment" in understanding1 and "environment" in understanding2:
                    env1 = understanding1["environment"]
                    env2 = understanding2["environment"]
                    
                    similarity = self._calculate_dict_similarity(env1, env2)
                    convergence["elements"][f"environment_{agent1}_{agent2}"] = similarity
                    
                    total_similarity += similarity
                    total_comparisons += 1
        
        # Calculate overall convergence
        if total_comparisons > 0:
            convergence["overall_convergence"] = total_similarity / total_comparisons
        
        return convergence
    
    def _calculate_list_similarity(self, list1: List, list2: List) -> float:
        """Calculate similarity between two lists."""
        if not list1 or not list2:
            return 0.0
        
        # Check overlap
        set1 = set(list1)
        set2 = set(list2)
        
        intersection = set1.intersection(set2)
        union = set1.union(set2)
        
        # Jaccard similarity
        similarity = len(intersection) / max(1, len(union))
        
        # For ordered lists, we could also consider position similarity
        # This is a simplified version
        return similarity
    
    def _calculate_dict_similarity(self, dict1: Dict, dict2: Dict) -> float:
        """Calculate similarity between two dictionaries."""
        if not dict1 or not dict2:
            return 0.0
        
        # Check key overlap
        keys1 = set(dict1.keys())
        keys2 = set(dict2.keys())
        
        intersection = keys1.intersection(keys2)
        union = keys1.union(keys2)
        
        # Base similarity on key overlap
        key_similarity = len(intersection) / max(1, len(union))
        
        # Check value similarity for common keys
        value_similarity = 0.0
        for key in intersection:
            if dict1[key] == dict2[key]:
                value_similarity += 1.0
        
        value_similarity = value_similarity / max(1, len(intersection))
        
        # Combine key and value similarity
        return (key_similarity + value_similarity) / 2.0
    
    def enhance_agent_prompt(self, agent_role: str, base_prompt: str) -> str:
        """
        Enhance an agent's prompt with shared mental model elements.
        
        Args:
            agent_role: Role of the agent
            base_prompt: The original prompt for the agent
            
        Returns:
            Enhanced prompt with shared mental model elements
        """
        enhanced_prompt = base_prompt
        
        # Add shared task model
        if "lunar_survival" in self.task_knowledge:
            task_model = self.task_knowledge["lunar_survival"]
            
            # Add shared understanding of the lunar environment
            environment_info = "\n\nOur team's shared understanding of the lunar environment:\n"
            for aspect, description in task_model["environment"].items():
                environment_info += f"- {aspect.capitalize()}: {description}\n"
            
            # Add shared understanding of survival priorities
            priorities_info = "\nOur team's shared understanding of survival priorities:\n"
            for i, priority in enumerate(task_model["survival_priorities"]):
                priorities_info += f"{i+1}. {priority}\n"
            
            # Add shared understanding of the task procedure
            procedure_info = "\nOur team's agreed approach to this task:\n"
            for i, step in enumerate(task_model["task_procedure"]):
                procedure_info += f"{i+1}. {step}\n"
            
            # Combine shared mental model elements
            shared_model_info = f"{environment_info}\n{priorities_info}\n{procedure_info}"
            
            # Add role-specific guidance
            if "lunar_team" in self.team_knowledge and agent_role in self.team_knowledge["lunar_team"]["roles"]:
                role_info = self.team_knowledge["lunar_team"]["roles"][agent_role]
                
                role_guidance = f"\nAs the {agent_role}, your specific expertise is in {role_info['expertise']}.\n"
                role_guidance += "Your key responsibilities include:\n"
                for resp in role_info["responsibilities"]:
                    role_guidance += f"- {resp}\n"
                
                role_guidance += "\nYou should seek from your teammates:\n"
                for need in role_info["information_needs"]:
                    role_guidance += f"- {need}\n"
                
                shared_model_info += f"\n{role_guidance}"
            
            # Add convergence information if available
            if self.convergence_metrics:
                latest_convergence = self.convergence_metrics[-1]
                convergence_info = f"\nOur team's mental models have converged to a level of {latest_convergence['overall_convergence']:.2f} out of 1.0."
                shared_model_info += convergence_info
            
            # Add the shared mental model information to the prompt
            enhanced_prompt += f"\n\n=== SHARED TEAM UNDERSTANDING ===\n{shared_model_info}"
        
        return enhanced_prompt
    
    def extract_understanding_from_message(self, message: str) -> Dict[str, Any]:
        """
        Extract an agent's understanding from their message.
        
        Args:
            message: The agent's message
            
        Returns:
            Dictionary representing the agent's mental model
        """
        # This would ideally use NLP techniques to extract understanding
        # This is a simplified implementation
        understanding = {
            "priorities": [],
            "environment": {},
            "justifications": {}
        }
        
        # Extract priorities (ranking)
        lines = message.split("\n")
        for line in lines:
            # Look for numbered lines that likely contain the ranking
            if any(f"{i}." in line for i in range(1, 16)):
                # Split to get just the item name
                parts = line.split(".", 1)
                if len(parts) > 1:
                    item_part = parts[1].strip()
                    # Further split to separate item from justification
                    item_parts = item_part.split("-", 1)
                    item = item_parts[0].strip()
                    understanding["priorities"].append(item)
                    
                    # If there's a justification, capture it
                    if len(item_parts) > 1:
                        justification = item_parts[1].strip()
                        understanding["justifications"][item] = justification
        
        # Extract environment understanding
        environment_aspects = ["atmosphere", "temperature", "gravity", "radiation"]
        for aspect in environment_aspects:
            # Look for mentions of environmental factors
            for line in lines:
                if aspect.lower() in line.lower():
                    understanding["environment"][aspect] = line.strip()
                    break
        
        return understanding
    
    def analyze_mental_model_effectiveness(self) -> Dict[str, Any]:
        """
        Analyze the effectiveness of the shared mental model.
        
        Returns:
            Dictionary with effectiveness metrics
        """
        # Analyze convergence trend
        convergence_trend = "unknown"
        if len(self.convergence_metrics) > 1:
            initial = self.convergence_metrics[0]["overall_convergence"]
            final = self.convergence_metrics[-1]["overall_convergence"]
            
            if final > initial + 0.2:
                convergence_trend = "strong_improvement"
            elif final > initial + 0.1:
                convergence_trend = "moderate_improvement"
            elif final > initial:
                convergence_trend = "slight_improvement"
            elif final < initial - 0.1:
                convergence_trend = "divergence"
            else:
                convergence_trend = "stable"
        
        # Analyze understanding completeness
        completeness_scores = {}
        for role, understanding in self.shared_understanding.items():
            # Calculate completeness based on how many elements are present
            environment_completeness = len(understanding.get("environment", {})) / 4.0  # Based on 4 key aspects
            priorities_completeness = min(1.0, len(understanding.get("priorities", [])) / 15.0)  # Based on 15 items
            justification_completeness = len(understanding.get("justifications", {})) / max(1, len(understanding.get("priorities", [])))
            
            avg_completeness = (environment_completeness + priorities_completeness + justification_completeness) / 3.0
            completeness_scores[role] = avg_completeness
        
        # Overall metrics
        analysis = {
            "convergence_trend": convergence_trend,
            "final_convergence": self.convergence_metrics[-1]["overall_convergence"] if self.convergence_metrics else 0.0,
            "understanding_completeness": completeness_scores,
            "avg_completeness": sum(completeness_scores.values()) / max(1, len(completeness_scores)),
            "effectiveness_rating": "high" if (self.convergence_metrics and self.convergence_metrics[-1]["overall_convergence"] > 0.7) else "medium" if (self.convergence_metrics and self.convergence_metrics[-1]["overall_convergence"] > 0.4) else "low"
        }
        
        self.logger.info(f"Mental model effectiveness analysis: {analysis['effectiveness_rating']} effectiveness")
        return analysis