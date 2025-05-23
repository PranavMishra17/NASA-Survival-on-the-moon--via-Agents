"""
Modified simulator for running lunar survival agent collaborations.
Key improvements:
1. Reversed order of rounds - adversarial first, then collaborative
2. Enhanced knowledge sharing between agents
3. Improved adversarial round to focus on resolving differences, not defending positions
4. Better position adjustment algorithm for consensus building
"""

import os
import logging
import json
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
from utils.logger import SimulationLogger
from agents.team_member import ModularAgent, create_agent_team
from communication.closed_loop import ClosedLoopCommunication
import config

# Add these imports at the top of simulator.py
from teamwork.mutual_monitoring import MutualMonitoring
from teamwork.shared_mental_model import SharedMentalModel

# At the top of simulator.py (outside the class)
def initialize_agents(use_team_leadership, use_closed_loop_comm, simulation_id):
    """Initialize agents with compatibility for both old and new agent structures."""
    try:
        # Try to import the modular agent
        from agents.modular_agent import ModularAgent
        logging.info(f"Using modular agent architecture for {simulation_id}")
        
        # Create science agent
        science_agent = ModularAgent(
            role_type="Science", 
            use_closed_loop_comm=use_closed_loop_comm,
            can_lead=use_team_leadership
        )
        
        # Create resource agent
        resource_agent = ModularAgent(
            role_type="Resource", 
            use_closed_loop_comm=use_closed_loop_comm,
            can_lead=False
        )
        
        # Set up compatibility references
        leader = science_agent if use_team_leadership else None
        team_leader = leader if leader else science_agent
        team_member = resource_agent
        
        # Share knowledge
        science_agent.share_knowledge(resource_agent)
        resource_agent.share_knowledge(science_agent)
        
        return team_leader, team_member, leader, science_agent, resource_agent
        
    except (ImportError, ModuleNotFoundError):
        # Fall back to original approach
        logging.info(f"Using original agent architecture for {simulation_id}")
        from agents.team_leader import TeamLeader
        from agents.team_member import TeamMember
        
        team_leader = TeamLeader(use_closed_loop_comm=use_closed_loop_comm)
        team_member = TeamMember(use_closed_loop_comm=use_closed_loop_comm)
        
        # For new code pattern, duplicated references
        leader = team_leader
        science_agent = team_member
        resource_agent = team_member
        
        return team_leader, team_member, leader, science_agent, resource_agent


class LunarSurvivalSimulator:
    """
    Simulator for running lunar survival agent collaborations.
    """
    
    def __init__(self, 
                simulation_id: str = None,
                use_team_leadership: bool = True,
                use_closed_loop_comm: bool = False,
                use_mutual_monitoring: bool = False,
                use_shared_mental_model: bool = False):
        """
        Initialize the simulator.
        
        Args:
            simulation_id: Optional ID for the simulation, defaults to timestamp
            use_team_leadership: Whether to use team leadership behaviors
            use_closed_loop_comm: Whether to use closed-loop communication
            use_mutual_monitoring: Whether to use mutual performance monitoring
            use_shared_mental_model: Whether to use shared mental model
        """
        # Set simulation ID and configuration
        self.simulation_id = simulation_id or f"sim_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.use_team_leadership = use_team_leadership
        self.use_closed_loop_comm = use_closed_loop_comm
        self.use_mutual_monitoring = use_mutual_monitoring
        self.use_shared_mental_model = use_shared_mental_model
        
        # Setup logging with enhanced structure
        self.config = {
            "use_team_leadership": use_team_leadership,
            "use_closed_loop_comm": use_closed_loop_comm,
            "use_mutual_monitoring": use_mutual_monitoring,
            "use_shared_mental_model": use_shared_mental_model
        }
        self.logger = SimulationLogger(
            simulation_id=self.simulation_id,
            log_dir=config.LOG_DIR,
            config=self.config
        ).logger
        
        # Initialize agents
        self.team_leader, self.team_member, self.leader, self.science_agent, self.resource_agent = initialize_agents(
            use_team_leadership=use_team_leadership,
            use_closed_loop_comm=use_closed_loop_comm,
            simulation_id=self.simulation_id
        )
        
        # Initialize teamwork components
        self.mutual_monitor = MutualMonitoring() if use_mutual_monitoring else None
        self.mental_model = SharedMentalModel() if use_shared_mental_model else None
        
        # Initialize shared knowledge if using shared mental model
        if self.mental_model:
            self.mental_model.initialize_lunar_task_model()
            self.mental_model.initialize_team_model([
                self.science_agent.role, 
                self.resource_agent.role
            ])
        
        # Create a shared knowledge repository available to both agents
        self.shared_knowledge = {}
        
        # Initialize communication handler if needed
        self.comm_handler = ClosedLoopCommunication() if use_closed_loop_comm else None
        
        # Store results
        self.results = {
            "simulation_id": self.simulation_id,
            "config": self.config,
            "exchanges": [],
            "final_ranking": [],
            "nasa_ranking": config.LUNAR_ITEMS,
            "score": 0,
            "teamwork_metrics": {}
        }
        
        self.logger.info(f"Initialized simulation {self.simulation_id}")
        self.logger.info(f"  Team Leadership: {use_team_leadership}")
        self.logger.info(f"  Closed-loop Communication: {use_closed_loop_comm}")
        self.logger.info(f"  Mutual Performance Monitoring: {use_mutual_monitoring}")
        self.logger.info(f"  Shared Mental Model: {use_shared_mental_model}")
        
        # Initialize shared knowledge between agents
        self._initialize_shared_knowledge()

    def initialize_agents(use_team_leadership, use_closed_loop_comm, simulation_id):
        """
        Initialize agents using the appropriate approach based on what's available.
        
        This function tries to use the modular agent approach first, and falls back
        to the original approach if ModularAgent is not available.
        
        Args:
            use_team_leadership: Whether to use team leadership
            use_closed_loop_comm: Whether to use closed-loop communication
            simulation_id: Simulation ID for logging
            
        Returns:
            Tuple of (team_leader, team_member, leader, science_agent, resource_agent)
        """
        try:
            # Try to import the modular agent
            from agents.team_member import ModularAgent, create_agent_team
            logging.info(f"Using modular agent architecture for {simulation_id}")
            
            # Create agent team
            agents = create_agent_team(
                use_team_leadership=use_team_leadership,
                use_closed_loop_comm=use_closed_loop_comm,
                random_leader=False  # Use deterministic leadership for now
            )
            
            # Extract agents
            science_agent = agents["science"]
            resource_agent = agents["resource"]
            leader = agents["leader"]
            
            # Create backwards compatibility mapping
            team_leader = leader if leader else science_agent
            team_member = resource_agent if leader == science_agent else science_agent
            
            return team_leader, team_member, leader, science_agent, resource_agent
            
        except (ImportError, ModuleNotFoundError):
            # Fall back to original approach
            logging.info(f"Using original agent architecture for {simulation_id}")
            from agents.team_leader import TeamLeader
            from agents.team_member import TeamMember
            
            team_leader = TeamLeader(use_closed_loop_comm=use_closed_loop_comm)
            team_member = TeamMember(use_closed_loop_comm=use_closed_loop_comm)
            
            # For new code pattern, duplicated references
            leader = team_leader
            science_agent = team_member
            resource_agent = team_member
            
            return team_leader, team_member, leader, science_agent, resource_agent
    
    def _initialize_shared_knowledge(self):
        """Initialize shared knowledge that both agents can access."""
        # Add lunar environment knowledge
        self.shared_knowledge["lunar_environment"] = {
            #"atmosphere": "No atmosphere, vacuum conditions",
            #"temperature": "Extreme variations (+250°F in sunlight, -250°F in shadow)",
            #"gravity": "1/6 of Earth's gravity",
            #"radiation": "No protection from solar radiation",
            #"day_length": "14 Earth days of daylight, 14 Earth days of darkness",
            #"terrain": "Uneven surfaces, craters, dust"
        }
        
        # Add survival principles
        self.shared_knowledge["survival_principles"] = {
            #"priorities": "Oxygen, water, shelter/temperature regulation, food",
            #"navigation": "Stellar navigation is most reliable without magnetic field",
            #"communication": "No atmosphere to carry sound waves, radio required",
            #"movement": "Conserve energy and resources during trek",
            #"physical_effects": "Vacuum effects on human body, radiation exposure risks"
        }
        
        # Share knowledge with both agents
        for key, value in self.shared_knowledge.items():
            self.science_agent.add_to_knowledge_base(key, value)
            self.resource_agent.add_to_knowledge_base(key, value)
        
        # Add NASA rationale to both knowledge bases to improve reasoning
        self.science_agent.add_to_knowledge_base("nasa_rationale", config.NASA_RATIONALE)
        self.resource_agent.add_to_knowledge_base("nasa_rationale", config.NASA_RATIONALE)
        
    def run_simulation(self):
        """Run the full simulation with adversarial round first, then collaborative."""
        # Run adversarial round first to identify and resolve differences
        self.logger.info("Starting with adversarial round to identify differences")
        adversarial_results = self.run_adversarial_round()
        
        # Run collaborative round to build consensus
        self.logger.info("Following with collaborative round to build on resolutions")
        collaborative_results = self.run_collaborative_round()
        
        # Save results
        self.save_results()
        
        return {
            "adversarial": adversarial_results,
            "collaborative": collaborative_results,
            "final_ranking": self.results["final_ranking"],
            "score": self.results["score"]
        }
    
    def run_adversarial_round(self):
        """
        Run an adversarial round where agents discuss differences to understand perspectives.
        This is now the first round, focused on exploring different viewpoints rather than defending positions.
        """
        self.logger.info("Starting adversarial round for perspective sharing")
        
        logger = SimulationLogger(
            self.simulation_id,
            config.LOG_DIR,
            self.config
        )
        
        round_results = {
            "type": "adversarial",
            "exchanges": []
        }
        
        # Step 1: Both agents create initial independent rankings
        leader_ranking = self._get_leader_initial_ranking()
        member_ranking = self._get_member_initial_ranking()
        
        # Share these initial rankings in the shared knowledge
        self.shared_knowledge["initial_rankings"] = {
            "leader": leader_ranking,
            "member": member_ranking
        }
        
        # Step 2: Identify key differences in perspectives
        disagreements = self._identify_ranking_disagreements(leader_ranking, member_ranking)
        
        # Step 3: Discuss each difference with focus on understanding perspectives
        for item, positions in disagreements.items():
            self.logger.info(f"Exploring different perspectives on item: {item}")
            
            if self.use_closed_loop_comm:
                # Using closed-loop communication for structured discussion
                # Modified prompts to focus on understanding, not defending
                perspective_prompt = f"""
                Let's discuss why we have different perspectives on '{item}'. 
                You ranked it at position #{positions['leader']}, while the Science Analyst ranked it at #{positions['member']}.
                
                Instead of defending your position, explain your reasoning and ask the Science Analyst 
                about their scientific rationale. The goal is to understand each other's perspective
                and find the most accurate ranking together.
                """
                
                exchange = self.comm_handler.facilitate_exchange(
                    self.team_leader,
                    self.team_member,
                    perspective_prompt
                )
                
                logger.log_closed_loop(
                    "leader",
                    exchange[0],
                    exchange[1],
                    exchange[2]
                )
                
                round_results["exchanges"].append({
                    "type": "closed_loop",
                    "item": item,
                    "sender": "leader",
                    "initial_message": exchange[0],
                    "acknowledgment": exchange[1],
                    "verification": exchange[2]
                })
                
                # Have member explain their perspective
                member_perspective_prompt = f"""
                Let's continue our discussion about '{item}'. 
                You ranked it at position #{positions['member']}, while the Team Leader ranked it at #{positions['leader']}.
                
                Please explain the scientific principles that led to your ranking. What lunar environmental 
                factors influenced your decision? What survival principles apply here?
                
                The goal is to share knowledge and find the most accurate ranking together.
                """
                
                exchange = self.comm_handler.facilitate_exchange(
                    self.team_member,
                    self.team_leader,
                    member_perspective_prompt
                )
                
                logger.log_closed_loop(
                    "member",
                    exchange[0],
                    exchange[1],
                    exchange[2]
                )
                
                round_results["exchanges"].append({
                    "type": "closed_loop",
                    "item": item,
                    "sender": "member",
                    "initial_message": exchange[0],
                    "acknowledgment": exchange[1],
                    "verification": exchange[2]
                })
                
                # Add resolution discussion - new addition
                resolution_prompt = f"""
                Based on our discussion about '{item}', let's work toward a consensus.
                
                You initially ranked it at position #{positions['leader']}, and the Science Analyst at #{positions['member']}.
                After hearing the scientific perspective, where do you think this item should be ranked?
                
                Explicitly state what position you now think '{item}' should have in our final ranking,
                and explain your reasoning based on our discussion.
                """
                
                exchange = self.comm_handler.facilitate_exchange(
                    self.team_leader,
                    self.team_member,
                    resolution_prompt
                )
                
                logger.log_closed_loop(
                    "leader",
                    exchange[0],
                    exchange[1],
                    exchange[2]
                )
                
                round_results["exchanges"].append({
                    "type": "closed_loop",
                    "item": item,
                    "sender": "leader",
                    "purpose": "resolution",
                    "initial_message": exchange[0],
                    "acknowledgment": exchange[1],
                    "verification": exchange[2]
                })
                
            else:
                # Standard communication with improved prompts
                perspective_prompt = f"""
                Let's discuss why we have different perspectives on '{item}'. 
                You ranked it at position #{positions['leader']}, while the Science Analyst ranked it at #{positions['member']}.
                
                Instead of defending your position, explain your reasoning and ask the Science Analyst 
                about their scientific rationale. The goal is to understand each other's perspective.
                """
                
                leader_perspective = self.team_leader.chat(perspective_prompt)
                
                logger.log_main_loop(
                    "adversarial",
                    f"discuss_{item}_perspective",
                    "leader",
                    leader_perspective
                )
                
                round_results["exchanges"].append({
                    "type": "standard",
                    "item": item,
                    "role": "leader",
                    "purpose": "perspective",
                    "message": leader_perspective
                })
                
                # Member shares scientific perspective
                member_prompt = f"""
                The Team Leader has shared their perspective on '{item}':
                
                "{leader_perspective}"
                
                Please explain the scientific principles that led to your ranking of #{positions['member']}.
                What lunar environmental factors influenced your decision? What survival principles apply here?
                
                Focus on sharing knowledge rather than defending your position.
                """
                
                member_perspective = self.team_member.chat(member_prompt)
                
                logger.log_main_loop(
                    "adversarial",
                    f"discuss_{item}_science",
                    "member",
                    member_perspective
                )
                
                round_results["exchanges"].append({
                    "type": "standard",
                    "item": item,
                    "role": "member",
                    "purpose": "science",
                    "message": member_perspective
                })
                
                # Leader proposes resolution based on scientific input
                resolution_prompt = f"""
                The Science Analyst has shared their scientific perspective on '{item}':
                
                "{member_perspective}"
                
                Based on this scientific information and your leadership expertise, propose a consensus position
                for this item. Where should '{item}' be ranked, and why?
                
                Be explicit about the exact position number you propose and explain your reasoning.
                """
                
                leader_resolution = self.team_leader.chat(resolution_prompt)
                
                logger.log_main_loop(
                    "adversarial",
                    f"discuss_{item}_resolution",
                    "leader",
                    leader_resolution
                )
                
                round_results["exchanges"].append({
                    "type": "standard",
                    "item": item,
                    "role": "leader",
                    "purpose": "resolution",
                    "message": leader_resolution
                })
                
                # Capture the proposed resolution in shared knowledge
                import re
                position_match = re.search(r'position #?(\d+)', leader_resolution, re.IGNORECASE)
                if position_match:
                    proposed_position = int(position_match.group(1))
                    if 1 <= proposed_position <= 15:
                        if "item_resolutions" not in self.shared_knowledge:
                            self.shared_knowledge["item_resolutions"] = {}
                        self.shared_knowledge["item_resolutions"][item] = proposed_position
                        
                        # Share this knowledge with both agents
                        self.team_leader.add_to_knowledge_base("item_resolutions", {item: proposed_position})
                        self.team_member.add_to_knowledge_base("item_resolutions", {item: proposed_position})
        
        # Create preliminary ranking based on discussed resolutions
        preliminary_ranking = self._create_preliminary_ranking(leader_ranking, member_ranking)
        
        # Store in shared knowledge for use in collaborative round
        self.shared_knowledge["preliminary_ranking"] = preliminary_ranking
        self.team_leader.add_to_knowledge_base("preliminary_ranking", preliminary_ranking)
        self.team_member.add_to_knowledge_base("preliminary_ranking", preliminary_ranking)
        
        # Store results of the adversarial round
        round_results["preliminary_ranking"] = preliminary_ranking
        
        # Calculate score for this preliminary ranking
        score = self._calculate_score(preliminary_ranking)
        round_results["score"] = score
        
        self.logger.info(f"Adversarial round completed with score: {score}")
        self.results["exchanges"].append(round_results)
        
        return round_results
    
    """
    Sequential refinement method for the lunar survival simulator.
    This replaces the collaborative and adversarial rounds with an iterative refinement process.
    """
    def run_sequential_refinement(self, iterations=4):
        """
        Run a sequential refinement process where agents iteratively improve rankings.
        
        Args:
            iterations: Number of refinement iterations to perform
            
        Returns:
            Dictionary with results of the refinement process
        """
        self.logger.info("Starting sequential refinement process")
        
        logger = SimulationLogger(
            self.simulation_id,
            config.LOG_DIR,
            self.config
        )
        
        round_results = {
            "type": "sequential_refinement",
            "exchanges": [],
            "iterations": []
        }
        
        # Ensure teamwork metrics exist in results
        if "teamwork_metrics" not in self.results:
            self.results["teamwork_metrics"] = {}
        
        # Step 1: First agent creates an initial ranking with justifications
        import random
        start_with_science = random.choice([True, False])
        
        self.logger.info(f"Starting with {'Science' if start_with_science else 'Resource'} agent")
        
        if start_with_science:
            first_agent = self.science_agent
            second_agent = self.resource_agent
            first_role = "science"
            second_role = "resource"
        else:
            first_agent = self.resource_agent
            second_agent = self.science_agent  
            first_role = "resource"
            second_role = "science"
        
        # Initial ranking from first agent
        first_prompt = f"""
        As a {first_agent.role} with expertise in your domain, create an initial ranking 
        of the lunar survival items for a 200-mile trek to the rendezvous point.
        
        Consider the specific conditions on the lunar surface and the survival priorities.
        
        Rank all 15 items from most important (1) to least important (15), with clear
        justifications for each item's placement. Present your ranking as a numbered list.
        
        Items to rank: {', '.join(config.LUNAR_ITEMS)}
        """
        
        # Apply shared mental model to initial prompt if enabled
        if self.use_shared_mental_model:
            first_prompt = self.mental_model.enhance_agent_prompt(first_role, first_prompt)
        
        first_message = first_agent.chat(first_prompt)
        current_ranking = first_agent.get_item_ranking(first_message)
        
        logger.log_main_loop(
            "sequential",
            "initial_ranking",
            first_role,
            first_message
        )
        
        round_results["exchanges"].append({
            "type": "initial_ranking",
            "role": first_role,
            "message": first_message,
            "ranking": current_ranking
        })
        
        # Apply mutual monitoring to initial ranking if enabled
        if self.use_mutual_monitoring:
            monitoring_result = self.mutual_monitor.monitor_ranking(
                agent_role=first_role,
                ranking=current_ranking,
                rationale=first_message
            )
            
            # Generate feedback from the second agent if issues detected
            if monitoring_result["issues_detected"]:
                feedback = self.mutual_monitor.generate_feedback(
                    monitoring_result=monitoring_result,
                    feedback_agent_role=second_role
                )
                
                logger.log_main_loop(
                    "sequential",
                    "initial_monitoring_feedback",
                    second_role,
                    feedback
                )
                
                round_results["exchanges"].append({
                    "type": "monitoring_feedback",
                    "iteration": 0,
                    "role": second_role,
                    "message": feedback
                })
                
                # Let the first agent respond to feedback
                response_prompt = f"""
                You've received this feedback from your teammate:
                
                "{feedback}"
                
                Consider this feedback and respond to it. If you agree with any points raised,
                explain how you'll address them in your ranking. If you disagree with any points,
                explain your reasoning.
                
                Then provide your updated ranking that takes this feedback into account.
                """
                
                feedback_response = first_agent.chat(response_prompt)
                updated_ranking = first_agent.get_item_ranking(feedback_response)
                
                logger.log_main_loop(
                    "sequential",
                    "initial_feedback_response",
                    first_role,
                    feedback_response
                )
                
                round_results["exchanges"].append({
                    "type": "feedback_response",
                    "iteration": 0,
                    "role": first_role,
                    "message": feedback_response,
                    "ranking": updated_ranking
                })
                
                # Update current ranking with the feedback-adjusted ranking
                current_ranking = updated_ranking
                current_message = feedback_response
            else:
                current_message = first_message
        else:
            current_message = first_message
        
        # Update shared mental model with initial understanding if enabled
        if self.use_shared_mental_model:
            understanding = self.mental_model.extract_understanding_from_message(current_message)
            self.mental_model.update_shared_understanding(first_role, understanding)
        
        # Store initial ranking for comparison
        round_results["iterations"].append({
            "iteration": 0,
            "current_ranking": current_ranking,
            "current_message": current_message,
            "current_agent": first_role
        })
        
        # Step 2: Iterative refinement process
        refining_agent = second_agent
        refining_role = second_role
        
        for i in range(1, iterations + 1):
            self.logger.info(f"Iteration {i}: {refining_role} agent refining ranking")
            
            refine_prompt = f"""
            Review the current ranking of lunar survival items:
            
            {current_message}
            
            Based on your expertise as a {refining_agent.role}, refine this ranking.
            
            For each item where you suggest a change in ranking, explain:
            1. Why you believe the item should be ranked differently
            2. How your specialized knowledge informs this decision
            3. The specific reasons for the new position
            
            If you agree with the current ranking of an item, briefly acknowledge this.
            
            Provide your complete refined ranking as a numbered list from 1-15 with brief justifications.
            Ensure all items from this list are included exactly once: {', '.join(config.LUNAR_ITEMS)}
            """
            
            # Enhance prompt with shared mental model if enabled
            if self.use_shared_mental_model:
                refine_prompt = self.mental_model.enhance_agent_prompt(refining_role, refine_prompt)
            
            refined_message = refining_agent.chat(refine_prompt)
            refined_ranking = refining_agent.get_item_ranking(refined_message)
            
            logger.log_main_loop(
                "sequential",
                f"{refining_role}_refinement_{i}",
                refining_role,
                refined_message
            )
            
            round_results["exchanges"].append({
                "type": "refinement",
                "iteration": i,
                "role": refining_role,
                "message": refined_message,
                "ranking": refined_ranking
            })
            
            # Apply mutual monitoring if enabled
            if self.use_mutual_monitoring:
                # Monitor the ranking for issues
                monitoring_result = self.mutual_monitor.monitor_ranking(
                    agent_role=refining_role,
                    ranking=refined_ranking,
                    rationale=refined_message
                )
                
                # Generate feedback from the other agent if issues detected
                if monitoring_result["issues_detected"]:
                    feedback_role = "science" if refining_role == "resource" else "resource"
                    feedback_agent = self.science_agent if feedback_role == "science" else self.resource_agent
                    
                    feedback = self.mutual_monitor.generate_feedback(
                        monitoring_result=monitoring_result,
                        feedback_agent_role=feedback_role
                    )
                    
                    # Log the feedback
                    logger.log_main_loop(
                        "sequential",
                        f"monitoring_feedback_{i}",
                        feedback_role,
                        feedback
                    )
                    
                    round_results["exchanges"].append({
                        "type": "monitoring_feedback",
                        "iteration": i,
                        "role": feedback_role,
                        "message": feedback
                    })
                    
                    # Let the agent respond to the feedback
                    response_prompt = f"""
                    You've received this feedback from your teammate:
                    
                    "{feedback}"
                    
                    Consider this feedback and respond to it. If you agree with any points raised,
                    explain how you'll address them in your ranking. If you disagree with any points,
                    explain your reasoning.
                    
                    Then provide your updated ranking that takes this feedback into account.
                    """
                    
                    feedback_response = refining_agent.chat(response_prompt)
                    updated_ranking = refining_agent.get_item_ranking(feedback_response)
                    
                    logger.log_main_loop(
                        "sequential",
                        f"feedback_response_{i}",
                        refining_role,
                        feedback_response
                    )
                    
                    round_results["exchanges"].append({
                        "type": "feedback_response",
                        "iteration": i,
                        "role": refining_role,
                        "message": feedback_response,
                        "ranking": updated_ranking
                    })
                    
                    # Update current ranking with the feedback-adjusted ranking
                    refined_ranking = updated_ranking
                    refined_message = feedback_response
            
            # Update shared mental model if enabled
            if self.use_shared_mental_model:
                # Extract the agent's understanding from their message
                understanding = self.mental_model.extract_understanding_from_message(refined_message)
                
                # Update the shared mental model
                self.mental_model.update_shared_understanding(refining_role, understanding)
            
            # Store iteration results
            difference_score = self._calculate_ranking_difference(current_ranking, refined_ranking)
            
            round_results["iterations"].append({
                "iteration": i,
                "current_ranking": refined_ranking,
                "current_message": refined_message,
                "current_agent": refining_role,
                "difference_score": difference_score
            })
            
            # Update for next iteration
            current_ranking = refined_ranking
            current_message = refined_message
            
            # Swap agents for next iteration
            if refining_role == "science":
                refining_agent = self.resource_agent
                refining_role = "resource"
            else:
                refining_agent = self.science_agent  
                refining_role = "science"
            
            # Check if consensus is reached (difference score below threshold)
            if difference_score <= 10:
                self.logger.info(f"Consensus reached at iteration {i} with difference score {difference_score}")
                break
        
        # Use the final refined ranking
        final_ranking = current_ranking
        final_message = current_message
        
        # Calculate score against NASA ranking
        score = self._calculate_score(final_ranking)
        
        # Store results
        round_results["final_ranking"] = final_ranking
        round_results["final_message"] = final_message
        round_results["score"] = score
        
        # Add teamwork metrics to the results
        if self.use_mutual_monitoring:
            teamwork_metrics = self.mutual_monitor.analyze_team_performance()
            self.results["teamwork_metrics"]["mutual_monitoring"] = teamwork_metrics
            self.logger.info(f"Mutual monitoring effectiveness: {teamwork_metrics['team_monitoring_effectiveness']}")
        
        if self.use_shared_mental_model:
            teamwork_metrics = self.mental_model.analyze_mental_model_effectiveness()
            self.results["teamwork_metrics"]["shared_mental_model"] = teamwork_metrics
            self.logger.info(f"Shared mental model effectiveness: {teamwork_metrics['effectiveness_rating']}")
        
        self.logger.info(f"Sequential refinement completed with score: {score}")
        self.results["exchanges"].append(round_results)
        self.results["final_ranking"] = final_ranking
        self.results["score"] = score
        
        return round_results


    def _calculate_ranking_difference(self, ranking1, ranking2):
        """
        Calculate the sum of absolute differences between two rankings.
        This measures how different the two rankings are.
        
        Args:
            ranking1: First ranking list
            ranking2: Second ranking list
            
        Returns:
            Sum of absolute position differences
        """
        difference = 0
        
        # Create position dictionaries
        pos1 = {item: i for i, item in enumerate(ranking1)}
        pos2 = {item: i for i, item in enumerate(ranking2)}
        
        # Calculate position differences for each item
        for item in config.LUNAR_ITEMS:
            if item in pos1 and item in pos2:
                difference += abs(pos1[item] - pos2[item])
        
        return difference

    def _format_ranking(self, ranking):
        """Format a ranking list for inclusion in a prompt."""
        if not ranking:
            return "No ranking provided"
        
        formatted = []
        for i, item in enumerate(ranking):
            formatted.append(f"{i+1}. {item}")
        
        return "\n".join(formatted)
    
    def _create_preliminary_ranking(self, leader_ranking, member_ranking):
        """
        Create a preliminary ranking based on discussed resolutions.
        This uses a weighted approach that better considers scientific input.
        """
        # Start with all items and their positions in both rankings
        item_positions = {}
        
        for item in config.LUNAR_ITEMS:
            leader_pos = leader_ranking.index(item) + 1 if item in leader_ranking else 15
            member_pos = member_ranking.index(item) + 1 if item in member_ranking else 15
            
            # Use resolved positions from discussions if available
            if "item_resolutions" in self.shared_knowledge and item in self.shared_knowledge["item_resolutions"]:
                resolved_pos = self.shared_knowledge["item_resolutions"][item]
                # Give higher weight to resolved positions
                item_positions[item] = (resolved_pos * 0.6) + (leader_pos * 0.2) + (member_pos * 0.2)
            else:
                # For items not explicitly discussed:
                # Give the science analyst's ranking more weight for technical items
                # Give the leader's ranking more weight for team-oriented items
                technical_items = ["Oxygen tanks", "Water", "Stellar map", "Solar-powered FM receiver-transmitter", 
                                 "First aid kit", "Portable heating unit", "Magnetic compass"]
                
                if item in technical_items:
                    # Give more weight to scientific opinion for technical items
                    item_positions[item] = (leader_pos * 0.4) + (member_pos * 0.6)
                else:
                    # Give more weight to leadership for other items
                    item_positions[item] = (leader_pos * 0.6) + (member_pos * 0.4)
        
        # Sort items by their weighted positions
        preliminary_ranking = sorted(item_positions.keys(), key=lambda item: item_positions[item])
        
        return preliminary_ranking
    
    def run_collaborative_round(self):
        """
        Run a collaborative round where agents build on their shared understanding.
        Now this is the second round, building on the insights from the adversarial round.
        """
        self.logger.info("Starting collaborative round to build consensus")
        
        logger = SimulationLogger(
            self.simulation_id,
            config.LOG_DIR,
            self.config
        )
        
        round_results = {
            "type": "collaborative",
            "exchanges": []
        }
        
        # Step 1: Begin with a review of what was learned in the adversarial round
        if self.use_team_leadership:
            review_prompt = """
            As Team Leader, let's review what we learned from our discussions about the lunar survival items.
            
            Summarize the key insights from our previous discussions, particularly the scientific principles
            that should guide our final ranking. Reference specific items where scientific considerations 
            led to a change in understanding.
            
            Then outline how we'll approach creating our final consensus ranking.
            """
            
            review_message = self.team_leader.chat(review_prompt)
            
            logger.log_leader_action(
                "collaborative_review",
                review_message
            )
            
            logger.log_main_loop(
                "collaborative",
                "review_insights",
                "leader",
                review_message
            )
            
            round_results["exchanges"].append({
                "type": "standard",
                "role": "leader",
                "purpose": "review",
                "message": review_message
            })
            
            # Have science analyst add additional insights
            science_review_prompt = f"""
            The Team Leader has provided this review of our discussions:
            
            "{review_message}"
            
            As the Science Analyst, please add any important scientific considerations that may have been
            overlooked. Focus on the lunar environment factors that are most critical for survival and
            how they affect our ranking of items.
            """
            
            science_review = self.team_member.chat(science_review_prompt)
            
            logger.log_main_loop(
                "collaborative",
                "science_review",
                "member",
                science_review
            )
            
            round_results["exchanges"].append({
                "type": "standard",
                "role": "member",
                "purpose": "science_review",
                "message": science_review
            })
        
        # Step 2: Create a systematic approach to ranking all items
        system_prompt = """
        Let's create a systematic framework for ranking all items based on survival priorities.
        
        Propose a clear methodology that:
        1. Categorizes items by their function (oxygen, navigation, communication, etc.)
        2. Prioritizes these categories based on survival needs
        3. Ranks items within each category
        
        This will help us create a consistent and scientifically sound ranking.
        """
        
        # Decide which agent should lead the systematic approach
        if self.use_team_leadership:
            system_message = self.team_leader.chat(system_prompt)
            agent_role = "leader"
        else:
            system_message = self.team_member.chat(system_prompt)
            agent_role = "member"
        
        logger.log_main_loop(
            "collaborative",
            "systematic_approach",
            agent_role,
            system_message
        )
        
        round_results["exchanges"].append({
            "type": "standard",
            "role": agent_role,
            "purpose": "system",
            "message": system_message
        })
        
        # Step 3: Apply the systematic approach to all items
        apply_prompt = f"""
        Let's apply our systematic approach to all 15 items:
        
        {', '.join(config.LUNAR_ITEMS)}
        
        Based on our previous discussions and the framework we've established, create a complete
        ranking from 1 (most important) to 15 (least important).
        
        For each item, provide a brief but clear justification based on:
        1. Its role in addressing survival needs
        2. The scientific principles involving the lunar environment
        3. Insights from our previous discussions
        
        Present your ranking as a numbered list with justifications.
        """
        
        if self.use_closed_loop_comm:
            # Use closed-loop for final ranking synthesis
            exchange = self.comm_handler.facilitate_exchange(
                self.team_leader if self.use_team_leadership else self.team_member,
                self.team_member if self.use_team_leadership else self.team_leader,
                apply_prompt
            )
            
            logger.log_closed_loop(
                "leader" if self.use_team_leadership else "member",
                exchange[0],
                exchange[1],
                exchange[2]
            )
            
            round_results["exchanges"].append({
                "type": "closed_loop",
                "sender": "leader" if self.use_team_leadership else "member",
                "purpose": "final_ranking",
                "initial_message": exchange[0],
                "acknowledgment": exchange[1],
                "verification": exchange[2]
            })
            
            # Extract the final ranking
            if self.use_team_leadership:
                final_ranking = self.team_leader.get_item_ranking(exchange[0])
            else:
                final_ranking = self.team_member.get_item_ranking(exchange[0])
                
        else:
            # Standard approach for final ranking
            ranking_message = self.team_leader.chat(apply_prompt) if self.use_team_leadership else self.team_member.chat(apply_prompt)
            
            agent_role = "leader" if self.use_team_leadership else "member"
            logger.log_main_loop(
                "collaborative",
                "final_ranking",
                agent_role,
                ranking_message
            )
            
            round_results["exchanges"].append({
                "type": "standard",
                "role": agent_role,
                "purpose": "final_ranking",
                "message": ranking_message
            })
            
            # Get feedback from the other agent
            feedback_prompt = f"""
            Review this proposed final ranking:
            
            "{ranking_message}"
            
            Do you agree with this ranking? Are there any specific items that you believe should be
            ranked differently? If so, explain your reasoning with specific references to survival
            needs and the lunar environment.
            
            If you agree with the ranking, state that explicitly.
            """
            
            feedback_agent = self.team_member if self.use_team_leadership else self.team_leader
            feedback_role = "member" if self.use_team_leadership else "leader"
            
            feedback_message = feedback_agent.chat(feedback_prompt)
            
            logger.log_main_loop(
                "collaborative",
                "ranking_feedback",
                feedback_role,
                feedback_message
            )
            
            round_results["exchanges"].append({
                "type": "standard",
                "role": feedback_role,
                "purpose": "feedback",
                "message": feedback_message
            })
            
            # Process the feedback and create truly final ranking
            resolve_prompt = f"""
            Consider this feedback on our ranking:
            
            "{feedback_message}"
            
            Based on this feedback and all our previous discussions, create the absolute final ranking
            of all 15 lunar survival items. This will be our team's official submission.
            
            Present the ranking as a simple numbered list from 1 to 15, with a brief justification for each item.
            Ensure all items from this list are included exactly once: {', '.join(config.LUNAR_ITEMS)}
            """
            
            final_resolve = self.team_leader.chat(resolve_prompt) if self.use_team_leadership else self.team_member.chat(resolve_prompt)
            
            logger.log_main_loop(
                "collaborative",
                "final_resolve",
                agent_role,
                final_resolve
            )
            
            round_results["exchanges"].append({
                "type": "standard",
                "role": agent_role,
                "purpose": "final_resolve",
                "message": final_resolve
            })
            
            # Extract the final ranking
            if self.use_team_leadership:
                final_ranking = self.team_leader.get_item_ranking(final_resolve)
            else:
                final_ranking = self.team_member.get_item_ranking(final_resolve)
        
        # Store final ranking
        round_results["final_ranking"] = final_ranking
        
        # Calculate score
        score = self._calculate_score(final_ranking)
        round_results["score"] = score
        
        self.logger.info(f"Collaborative round completed with score: {score}")
        self.results["exchanges"].append(round_results)
        self.results["final_ranking"] = final_ranking
        self.results["score"] = score
        
        return round_results
    
    def save_results(self) -> str:
        """
        Save simulation results to file.
        
        Returns:
            Path to the saved results file
        """
        output_path = os.path.join(config.OUTPUT_DIR, f"{self.simulation_id}_results.json")
        
        with open(output_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        self.logger.info(f"Results saved to {output_path}")
        return output_path
    
    def _calculate_score(self, ranking: List[str]) -> int:
        """
        Calculate score by comparing with NASA's ranking.
        
        Lower score is better (0 would be perfect match with NASA).
        
        Args:
            ranking: List of items in ranked order
            
        Returns:
            Score (sum of absolute differences in position)
        """
        score = 0
        nasa_positions = {item: i for i, item in enumerate(config.LUNAR_ITEMS)}
        
        for i, item in enumerate(ranking):
            if item in nasa_positions:
                # Calculate absolute difference in position
                score += abs(i - nasa_positions[item])
        
        return score
    
    def _get_leader_initial_ranking(self):
        """Get the team leader's initial ranking of items."""
        prompt = """
        As Team Leader, create an initial ranking of the lunar survival items based on your knowledge and expertise.
        Provide a ranked list from 1 (most important) to 15 (least important).
        
        Consider these questions in your ranking:
        1. What are the immediate survival needs on the lunar surface?
        2. What items would be most useful for the 200-mile trek?
        3. How do the unique properties of the lunar environment affect each item's utility?
        
        Present your ranking as a numbered list from 1 to 15.
        Be sure to include all items exactly once in your ranking.
        """
        
        leader_analysis = self.team_leader.chat(prompt)
        self.logger.info("Team Leader created initial ranking")
        return self.team_leader.get_item_ranking(leader_analysis)

    def _get_member_initial_ranking(self):
        """Get the team member's initial ranking of items."""
        prompt = """
        As Science Analyst, create an initial ranking of the lunar survival items 
        based on your scientific knowledge of the lunar environment.
        
        Consider these factors in your ranking:
        1. The absence of atmosphere and its implications
        2. Temperature extremes and radiation exposure
        3. Reduced gravity and its effects on movement and energy expenditure
        4. Navigation challenges without a magnetic field
        
        Provide a ranked list from 1 (most important) to 15 (least important).
        Present your ranking as a numbered list from 1 to 15.
        Be sure to include all items exactly once in your ranking.
        """
        
        member_analysis = self.team_member.chat(prompt)
        self.logger.info("Science Analyst created initial ranking")
        return self.team_member.get_item_ranking(member_analysis)

    def _identify_ranking_disagreements(self, leader_ranking, member_ranking):
        """
        Identify disagreements between leader and member rankings.
        Modified to focus on the most significant disagreements for productive discussion.
        """
        disagreements = {}
        
        # Find items with significant ranking differences (position differs by >2)
        for item in config.LUNAR_ITEMS:
            try:
                leader_pos = leader_ranking.index(item) + 1 if item in leader_ranking else -1
                member_pos = member_ranking.index(item) + 1 if item in member_ranking else -1
                
                if leader_pos > 0 and member_pos > 0 and abs(leader_pos - member_pos) > 2:
                    # Add information about why this item might be significant
                    nasa_rationale = config.NASA_RATIONALE.get(item, "")
                    
                    disagreements[item] = {
                        "leader": leader_pos,
                        "member": member_pos,
                        "difference": abs(leader_pos - member_pos),
                        "nasa_rationale": nasa_rationale,
                        "high_priority": leader_pos <= 5 or member_pos <= 5
                    }
            except ValueError:
                self.logger.warning(f"Item {item} not found in one of the rankings")
        
        # Prioritize disagreements that involve high-priority items (top 5)
        # and have the largest differences
        
        # First include all high-priority disagreements
        high_priority_items = [item for item, data in disagreements.items() if data["high_priority"]]
        
        # Then add remaining items with largest differences
        remaining_items = [item for item, data in disagreements.items() if not data["high_priority"]]
        remaining_items = sorted(remaining_items, key=lambda x: disagreements[x]["difference"], reverse=True)
        
        # Combine to get most important disagreements to discuss
        # Limit to 5 items to allow for more in-depth discussion
        prioritized_items = high_priority_items + remaining_items
        prioritized_items = prioritized_items[:5]
        
        return {item: disagreements[item] for item in prioritized_items}