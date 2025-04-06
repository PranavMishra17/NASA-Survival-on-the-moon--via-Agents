"""
Simulator for running lunar survival agent collaborations.
"""

import os
import logging
import json
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
from utils.logger import SimulationLogger
from agents.team_leader import TeamLeader
from agents.team_member import TeamMember
from communication.closed_loop import ClosedLoopCommunication
import config

class LunarSurvivalSimulator:
    """
    Simulator for running lunar survival agent collaborations.
    """
    
    def __init__(self, 
                simulation_id: str = None,
                use_team_leadership: bool = True,
                use_closed_loop_comm: bool = False):
        """
        Initialize the simulator.
        
        Args:
            simulation_id: Optional ID for the simulation, defaults to timestamp
            use_team_leadership: Whether to use team leadership behaviors
            use_closed_loop_comm: Whether to use closed-loop communication
        """
        # Set simulation ID and configuration
        self.simulation_id = simulation_id or f"sim_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.use_team_leadership = use_team_leadership
        self.use_closed_loop_comm = use_closed_loop_comm
        
        # Setup logging with enhanced structure
        self.config = {
            "use_team_leadership": use_team_leadership,
            "use_closed_loop_comm": use_closed_loop_comm,
        }
        self.logger = SimulationLogger(
            simulation_id=self.simulation_id,
            log_dir=config.LOG_DIR,
            config=self.config
        ).logger
        
        # Initialize agents
        self.team_leader = TeamLeader(use_closed_loop_comm=use_closed_loop_comm)
        self.team_member = TeamMember(use_closed_loop_comm=use_closed_loop_comm)
        
        # Initialize communication handler if needed
        self.comm_handler = ClosedLoopCommunication() if use_closed_loop_comm else None
        
        # Store results
        self.results = {
            "simulation_id": self.simulation_id,
            "config": self.config,
            "exchanges": [],
            "final_ranking": [],
            "nasa_ranking": config.LUNAR_ITEMS,
            "score": 0
        }
        
        self.logger.info(f"Initialized simulation {self.simulation_id}")
        self.logger.info(f"  Team Leadership: {use_team_leadership}")
        self.logger.info(f"  Closed-loop Communication: {use_closed_loop_comm}")
        
    def _setup_logging(self):
        """Set up logging for this simulation."""
        # Create a logger
        self.logger = logging.getLogger(f"simulation.{self.simulation_id}")
        self.logger.setLevel(logging.INFO)
        
        # Create a file handler
        log_path = os.path.join(config.LOG_DIR, f"{self.simulation_id}.log")
        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(logging.INFO)
        
        # Create a formatter and add it to the handler
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        # Add the handler to the logger
        self.logger.addHandler(file_handler)
    
    def run_collaborative_round(self):
        """Run a collaborative round where agents work together on ranking."""
        self.logger.info("Starting collaborative round")
        
        logger = SimulationLogger(
            self.simulation_id,
            config.LOG_DIR,
            self.config
        )
        
        round_results = {
            "type": "collaborative",
            "exchanges": []
        }
        
        # Step 1: Team leader defines the task if leadership is enabled
        if self.use_team_leadership:
            task_definition = self.team_leader.define_task(
                "Rank the lunar survival items for our 200-mile trek to the rendezvous point"
            )
            
            logger.log_leader_action(
                "task_definition",
                task_definition
            )
            
            logger.log_main_loop(
                "collaborative",
                "setup",
                "leader",
                task_definition
            )
        
        # Step 2: Team member performs initial analysis
        member_analysis = self.team_member.analyze_items()
        member_ranking = self.team_member.get_item_ranking(member_analysis)
        
        logger.log_main_loop(
            "collaborative",
            "initial_analysis",
            "member",
            member_analysis
        )
        
        # Step 3: Team leader initiates discussion
        if self.use_closed_loop_comm:
            # Use closed-loop communication protocol
            leader_prompt = """
            As Team Leader, initiate discussion about ranking the lunar survival items. 
            Review the list and provide your initial thoughts on how they should be ranked.
            """
            
            exchange = self.comm_handler.facilitate_exchange(
                self.team_leader, 
                self.team_member,
                leader_prompt
            )
            
            logger.log_closed_loop(
                "leader",
                exchange[0],
                exchange[1],
                exchange[2]
            )
            
            round_results["exchanges"].append({
                "type": "closed_loop",
                "sender": "leader",
                "initial_message": exchange[0],
                "acknowledgment": exchange[1],
                "verification": exchange[2]
            })
            
            # Extract leader's ranking from their message
            leader_ranking = self.team_leader.get_item_ranking(exchange[0])
        else:
            # Standard communication
            leader_discussion = self.team_leader.lead_discussion(
                "Ranking the lunar survival items for our 200-mile trek to the rendezvous point."
            )
            
            logger.log_main_loop(
                "collaborative",
                "leader_discussion",
                "leader",
                leader_discussion
            )
            
            round_results["exchanges"].append({
                "type": "standard",
                "role": "leader",
                "message": leader_discussion
            })
            
            # Team member responds to leader
            member_response = self.team_member.respond_to_leader(leader_discussion)
            
            logger.log_main_loop(
                "collaborative",
                "member_response",
                "member",
                member_response
            )
            
            round_results["exchanges"].append({
                "type": "standard",
                "role": "member",
                "message": member_response
            })
            
            # Extract rankings
            leader_ranking = self.team_leader.get_item_ranking(leader_discussion)
            member_ranking = self.team_member.get_item_ranking(member_response)
        
        # Step 4: Facilitate back-and-forth discussion (multiple exchanges)
        # Allow up to 3 rounds of discussion
        if not self.use_closed_loop_comm:
            for i in range(3):
                # Leader responds to member's last message
                last_member_message = round_results["exchanges"][-1]["message"]
                
                leader_prompt = f"""
                Continue our discussion about ranking the lunar survival items.
                Respond to the Science Analyst's points: "{last_member_message[:200]}..."
                Focus on areas where we might disagree and work toward consensus.
                """
                
                leader_response = self.team_leader.chat(leader_prompt)
                
                logger.log_main_loop(
                    "collaborative",
                    f"discussion_round_{i+1}",
                    "leader",
                    leader_response
                )
                
                round_results["exchanges"].append({
                    "type": "standard",
                    "role": "leader",
                    "message": leader_response
                })
                
                # Member responds to leader
                member_prompt = f"""
                Continue our discussion about ranking the lunar survival items.
                Respond to the Team Leader's points: "{leader_response[:200]}..."
                Focus on scientific facts about the lunar environment and work toward consensus.
                """
                
                member_response = self.team_member.chat(member_prompt)
                
                logger.log_main_loop(
                    "collaborative",
                    f"discussion_round_{i+1}",
                    "member",
                    member_response
                )
                
                round_results["exchanges"].append({
                    "type": "standard",
                    "role": "member",
                    "message": member_response
                })
        
        # Step 5: Synthesize rankings
        if self.use_team_leadership:
            # Team leader synthesizes the rankings
            final_synthesis = self.team_leader.synthesize_rankings(
                member_ranking, leader_ranking
            )
            
            logger.log_leader_action(
                "final_synthesis",
                final_synthesis,
                {"final_ranking": self.team_leader.get_item_ranking(final_synthesis)}
            )
            
            logger.log_main_loop(
                "collaborative",
                "final_synthesis",
                "leader",
                final_synthesis
            )
            
            round_results["exchanges"].append({
                "type": "standard",
                "role": "leader",
                "message": final_synthesis
            })
            
            # Extract the final ranking
            final_ranking = self.team_leader.get_item_ranking(final_synthesis)
        else:
            # Without team leadership, take the average ranking
            self.logger.info("No team leadership - using average of individual rankings")
            final_ranking = self._average_rankings([leader_ranking, member_ranking])
            
            round_results["exchanges"].append({
                "type": "system",
                "message": "Final ranking determined by averaging individual rankings"
            })
        
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
            
    def run_adversarial_round(self):
        """Run an adversarial round where agents debate their rankings."""
        self.logger.info("Starting adversarial round")
        
        logger = SimulationLogger(
            self.simulation_id,
            config.LOG_DIR,
            self.config
        )
        
        round_results = {
            "type": "adversarial",
            "exchanges": []
        }
        
        # Step 1: Both agents create initial rankings
        leader_ranking = self._get_leader_initial_ranking()
        member_ranking = self._get_member_initial_ranking()
        
        # Step 2: Team leader documents the initial rankings if leadership is enabled
        if self.use_team_leadership:
            documentation = self.team_leader.document_agent_capabilities(
                f"Team Leader ranking: {leader_ranking}\nScience Analyst ranking: {member_ranking}"
            )
            
            logger.log_leader_action(
                "document_rankings",
                documentation
            )
        
        # Step 3: Identify key disagreements
        disagreements = self._identify_ranking_disagreements(leader_ranking, member_ranking)
        
        # Step 4: Debate each disagreement
        for item, positions in disagreements.items():
            self.logger.info(f"Debating item: {item}")
            
            if self.use_closed_loop_comm:
                # Closed-loop communication for debate
                challenge_prompt = f"""
                As Team Leader, debate the ranking of '{item}'. 
                You ranked it at position #{positions['leader']}, while the Science Analyst ranked it at #{positions['member']}.
                Explain why your ranking is more appropriate, using clear reasoning.
                """
                
                exchange = self.comm_handler.facilitate_exchange(
                    self.team_leader,
                    self.team_member,
                    challenge_prompt
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
                
                # Member counter-challenges
                counter_challenge_prompt = f"""
                As Science Analyst, debate the ranking of '{item}'. 
                You ranked it at position #{positions['member']}, while the Team Leader ranked it at #{positions['leader']}.
                Defend your position with scientific facts about the lunar environment.
                """
                
                exchange = self.comm_handler.facilitate_exchange(
                    self.team_member,
                    self.team_leader,
                    counter_challenge_prompt
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
            else:
                # Standard debate
                # Leader challenges member's ranking
                challenge_prompt = f"""
                As Team Leader, debate the ranking of '{item}'. 
                You ranked it at position #{positions['leader']}, while the Science Analyst ranked it at #{positions['member']}.
                Explain why your ranking is more appropriate, using clear reasoning.
                """
                
                leader_challenge = self.team_leader.chat(challenge_prompt)
                
                logger.log_main_loop(
                    "adversarial",
                    f"debate_{item}_challenge",
                    "leader",
                    leader_challenge
                )
                
                round_results["exchanges"].append({
                    "type": "standard",
                    "item": item,
                    "role": "leader",
                    "message": leader_challenge
                })
                
                # Member defends position
                defense_prompt = f"""
                The Team Leader has challenged your ranking of '{item}':
                
                "{leader_challenge}"
                
                Defend your position with scientific facts about the lunar environment.
                Explain why you ranked it at position #{positions['member']} instead of #{positions['leader']}.
                """
                
                member_defense = self.team_member.chat(defense_prompt)
                
                logger.log_main_loop(
                    "adversarial",
                    f"debate_{item}_defense",
                    "member",
                    member_defense
                )
                
                round_results["exchanges"].append({
                    "type": "standard",
                    "item": item,
                    "role": "member",
                    "message": member_defense
                })
                
                # Leader responds to defense
                response_prompt = f"""
                The Science Analyst has defended their ranking of '{item}':
                
                "{member_defense}"
                
                Respond to their defense and suggest a compromise position for this item.
                Be specific about where this item should be ranked in the final list.
                """
                
                leader_response = self.team_leader.chat(response_prompt)
                
                logger.log_main_loop(
                    "adversarial",
                    f"debate_{item}_response",
                    "leader",
                    leader_response
                )
                
                round_results["exchanges"].append({
                    "type": "standard",
                    "item": item,
                    "role": "leader",
                    "message": leader_response
                })
        
        # Step 5: Create final consensus ranking
        if self.use_team_leadership:
            final_prompt = f"""
            As Team Leader, after our debates about specific items, create a final consensus ranking
            that incorporates valid points from both perspectives.
            
            IMPORTANT: 
            1. Your final list must include ALL 15 items exactly ONCE
            2. The items must be from this list: {', '.join(config.LUNAR_ITEMS)}
            3. Double-check for any duplicates or missing items
            
            Present your final numbered ranking from 1 to 15 with brief justifications.
            """
            
            final_decision = self.team_leader.chat(final_prompt)
            
            logger.log_leader_action(
                "adversarial_final_decision",
                final_decision,
                {"final_ranking": self.team_leader.get_item_ranking(final_decision)}
            )
            
            logger.log_main_loop(
                "adversarial",
                "final_decision",
                "leader",
                final_decision
            )
            
            round_results["exchanges"].append({
                "type": "standard",
                "role": "leader",
                "message": final_decision
            })
            
            final_ranking = self.team_leader.get_item_ranking(final_decision)
        else:
            # Without leadership, average rankings with adjustments from debates
            self.logger.info("No team leadership - averaging rankings with debate adjustments")
            
            # Apply debate adjustments
            adjusted_leader_ranking = leader_ranking.copy()
            adjusted_member_ranking = member_ranking.copy()
            
            # Simple adjustment based on debates
            for exchange in round_results["exchanges"]:
                if "item" in exchange:
                    item = exchange["item"]
                    # Move the rankings slightly closer together
                    try:
                        leader_idx = adjusted_leader_ranking.index(item)
                        member_idx = adjusted_member_ranking.index(item)
                        
                        if abs(leader_idx - member_idx) > 3:
                            # Move rankings closer by 1 position
                            if leader_idx < member_idx:
                                adjusted_leader_ranking.remove(item)
                                adjusted_leader_ranking.insert(leader_idx + 1, item)
                                adjusted_member_ranking.remove(item)
                                adjusted_member_ranking.insert(member_idx - 1, item)
                            else:
                                adjusted_leader_ranking.remove(item)
                                adjusted_leader_ranking.insert(leader_idx - 1, item)
                                adjusted_member_ranking.remove(item)
                                adjusted_member_ranking.insert(member_idx + 1, item)
                    except ValueError:
                        pass
            
            final_ranking = self._average_rankings([adjusted_leader_ranking, adjusted_member_ranking])
            
            round_results["exchanges"].append({
                "type": "system",
                "message": "Final ranking determined by averaging individual rankings with debate adjustments"
            })
        
        # Store final ranking
        round_results["final_ranking"] = final_ranking
        
        # Calculate score
        score = self._calculate_score(final_ranking)
        round_results["score"] = score
        
        self.logger.info(f"Adversarial round completed with score: {score}")
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
    
    def _average_rankings(self, rankings: List[List[str]]) -> List[str]:
        """
        Average multiple rankings.
        
        Args:
            rankings: List of ranking lists
            
        Returns:
            Averaged ranking
        """
        # Create a dictionary to store the total position value for each item
        total_positions = {item: 0 for item in config.LUNAR_ITEMS}
        
        # Sum up positions for each item
        for ranking in rankings:
            for i, item in enumerate(ranking):
                if item in total_positions:
                    total_positions[item] += i + 1  # Add 1 because indices are 0-based
        
        # Calculate average position by dividing by number of rankings
        avg_positions = {item: pos / len(rankings) for item, pos in total_positions.items()}
        
        # Sort items by average position (lower is better)
        sorted_items = sorted(avg_positions.keys(), key=lambda item: avg_positions[item])
        
        return sorted_items
    
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
    
    def _format_ranking(self, ranking: List[str]) -> str:
        """Format a ranking list for inclusion in a prompt."""
        if not ranking:
            return "No ranking provided"
        
        formatted = []
        for i, item in enumerate(ranking):
            formatted.append(f"{i+1}. {item}")
        
        return "\n".join(formatted)
    
    def _get_leader_initial_ranking(self):
        """Get the team leader's initial ranking of items."""
        prompt = """
        As Team Leader, create a ranking of the lunar survival items based on your knowledge and expertise.
        Provide a ranked list from 1 (most important) to 15 (least important) with brief justifications.
        Be sure to include all items exactly once in your ranking.
        """
        
        leader_analysis = self.team_leader.chat(prompt)
        self.logger.info("Team Leader created initial ranking")
        return self.team_leader.get_item_ranking(leader_analysis)

    def _get_member_initial_ranking(self):
        """Get the team member's initial ranking of items."""
        prompt = """
        As Science Analyst, create a ranking of the lunar survival items based on your scientific knowledge.
        Provide a ranked list from 1 (most important) to 15 (least important) with brief justifications.
        Be sure to include all items exactly once in your ranking.
        """
        
        member_analysis = self.team_member.chat(prompt)
        self.logger.info("Science Analyst created initial ranking")
        return self.team_member.get_item_ranking(member_analysis)

    def _identify_ranking_disagreements(self, leader_ranking, member_ranking):
        """Identify disagreements between leader and member rankings."""
        disagreements = {}
        
        # Find items with significant ranking differences (position differs by >2)
        for item in config.LUNAR_ITEMS:
            try:
                leader_pos = leader_ranking.index(item) + 1 if item in leader_ranking else -1
                member_pos = member_ranking.index(item) + 1 if item in member_ranking else -1
                
                if leader_pos > 0 and member_pos > 0 and abs(leader_pos - member_pos) > 2:
                    disagreements[item] = {
                        "leader": leader_pos,
                        "member": member_pos
                    }
            except ValueError:
                self.logger.warning(f"Item {item} not found in one of the rankings")
        
        # Limit to 3 most significant disagreements to focus the debate
        sorted_disagreements = sorted(
            disagreements.items(), 
            key=lambda x: abs(x[1]["leader"] - x[1]["member"]),
            reverse=True
        )
        
        return dict(sorted_disagreements[:3])


    def _debate_item_ranking(self, item: str, leader_position: int, member_position: int) -> Dict[str, str]:
        """Facilitate a debate about a specific item's ranking."""
        debate_results = {}
        
        # Leader challenges member's ranking
        leader_challenge_prompt = f"""
        As Team Leader, you ranked '{item}' at position #{leader_position}, while the Science Analyst ranked it at #{member_position}.
        
        Explain why you believe your ranking is more appropriate, using clear logical reasoning.
        Support your position with specific facts about the lunar environment and survival priorities.
        Focus ONLY on this specific item - do not discuss other items.
        """
        
        leader_challenge = self.team_leader.chat(leader_challenge_prompt)
        debate_results["leader_challenge"] = leader_challenge
        self.logger.info(f"Leader challenge for {item}: {leader_challenge}")
        
        # Member defends their position
        member_defense_prompt = f"""
        The Team Leader has challenged your ranking of '{item}'. 
        
        The Team Leader ranked '{item}' at position #{leader_position}, while you ranked it at #{member_position}.
        
        The Team Leader argued: "{leader_challenge}"
        
        Defend your position with scientific facts about the lunar environment and survival priorities.
        Focus ONLY on this specific item - do not discuss other items.
        """
        
        member_defense = self.team_member.chat(member_defense_prompt)
        debate_results["member_defense"] = member_defense
        self.logger.info(f"Member defense for {item}: {member_defense}")
        
        # Leader responds to defense
        leader_response_prompt = f"""
        The Science Analyst has defended their ranking of '{item}' at position #{member_position} as follows:
        
        "{member_defense}"
        
        Respond to their defense and suggest a compromise position for this item,
        taking into account both perspectives. Be specific about where this item should
        be ranked in the final list.
        """
        
        leader_response = self.team_leader.chat(leader_response_prompt)
        debate_results["leader_response"] = leader_response
        self.logger.info(f"Leader response for {item}: {leader_response}")
        
        return debate_results

    def _resolve_item_debate(self, item: str, debate_result: Dict[str, str]) -> Dict[str, Any]:
        """Resolve the debate about a specific item."""
        # Extract the leader's final position from their response
        leader_response = debate_result["leader_response"]
        
        # Use regex to find suggested position
        import re
        position_match = re.search(r'position #?(\d+)', leader_response, re.IGNORECASE)
        if position_match:
            suggested_position = int(position_match.group(1))
        else:
            # Try to find any number that might represent a position
            numbers = re.findall(r'#?(\d+)', leader_response)
            suggested_position = int(numbers[0]) if numbers else -1
        
        if suggested_position < 1 or suggested_position > 15:
            self.logger.warning(f"Could not extract valid position for {item}, using average")
            # Use the average position from the original disagreement
            leader_pos = int(re.search(r'position #?(\d+)', debate_result["leader_challenge"], re.IGNORECASE).group(1))
            member_pos = int(re.search(r'position #?(\d+)', debate_result["member_defense"], re.IGNORECASE).group(1))
            suggested_position = (leader_pos + member_pos) // 2
        
        return {
            "item": item,
            "final_position": suggested_position,
            "reasoning": leader_response
        }

    def _resolve_all_debates(self, debate_exchanges: List[Dict[str, Any]]) -> List[str]:
        """Create a final ranking based on all debate resolutions."""
        # Create a dictionary of items and their resolved positions
        resolved_positions = {}
        
        for exchange in debate_exchanges:
            item = exchange["item"]
            resolution = exchange["resolution"]
            position = resolution["final_position"]
            resolved_positions[item] = position
        
        # For items not explicitly debated, average the leader and member rankings
        all_items = set(config.LUNAR_ITEMS)
        debated_items = set(resolved_positions.keys())
        undebated_items = all_items - debated_items
        
        leader_ranking = self._get_leader_initial_ranking()
        member_ranking = self._get_member_initial_ranking()
        
        for item in undebated_items:
            if item in leader_ranking and item in member_ranking:
                leader_pos = leader_ranking.index(item) + 1
                member_pos = member_ranking.index(item) + 1
                resolved_positions[item] = (leader_pos + member_pos) // 2
            elif item in leader_ranking:
                resolved_positions[item] = leader_ranking.index(item) + 1
            elif item in member_ranking:
                resolved_positions[item] = member_ranking.index(item) + 1
            else:
                # Fallback position if item isn't in either ranking
                resolved_positions[item] = 15
        
        # Sort items by their resolved positions
        sorted_items = sorted(resolved_positions.items(), key=lambda x: x[1])
        
        # Create final ranking list
        final_ranking = [item for item, _ in sorted_items]
        
        # Ensure all items are included exactly once
        missing_items = all_items - set(final_ranking)
        for item in missing_items:
            final_ranking.append(item)
        
        return final_ranking[:15]  # Ensure only 15 items