"""
Enhanced logging functionality for lunar agents simulation.
"""

from logging import config
import os
import logging
from typing import Optional, Dict, Any
import json
from datetime import datetime

class SimulationLogger:
    """Enhanced logger for tracking simulation progress and results."""
    
    def __init__(self, 
                 simulation_id: str, 
                 log_dir: str,
                 config: Dict[str, bool] = None):
        """
        Initialize the simulation logger.
        
        Args:
            simulation_id: ID for the simulation
            log_dir: Directory to store logs
            config: Configuration options (leadership, closed_loop)
        """
        self.simulation_id = simulation_id
        self.log_dir = log_dir
        self.config = config or {}
        
        # Create configuration string for the folder name
        config_str = []
        if self.config.get("use_team_leadership"):
            config_str.append("leadership")
        if self.config.get("use_closed_loop_comm"):
            config_str.append("closed_loop")
        self.config_name = "_".join(config_str) if config_str else "baseline"
        
        # Create folder structure: logs/[config_name]/[simulation_id]/
        self.run_dir = os.path.join(self.log_dir, self.config_name, self.simulation_id)
        os.makedirs(self.run_dir, exist_ok=True)
        
        # Setup file paths
        self.log_file = os.path.join(self.run_dir, f"{simulation_id}.log")
        self.events_file = os.path.join(self.run_dir, f"{simulation_id}_events.jsonl")
        
        # Initialize the logger
        self.logger = self._setup_logger()
        
        # Log initial configuration
        self.log_event("simulation_started", {
            "simulation_id": simulation_id,
            "timestamp": datetime.now().isoformat(),
            "config": self.config,
            "config_name": self.config_name
        })
        
        self.logger.info(f"SimulationLogger initialized for {simulation_id} with configuration: {self.config_name}")

        # Create additional log files for different types of communication
        self.main_loop_file = os.path.join(self.run_dir, f"{simulation_id}_main_loop.jsonl")
        self.closed_loop_file = os.path.join(self.run_dir, f"{simulation_id}_closed_loop.jsonl")
        self.leader_file = os.path.join(self.run_dir, f"{simulation_id}_leader.jsonl")
    
    def _setup_logger(self) -> logging.Logger:
        """Set up the file and console loggers."""
        logger = logging.getLogger(f"simulation.{self.simulation_id}")
        logger.setLevel(logging.INFO)
        
        # Remove existing handlers if any
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        # File handler
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        logger.addHandler(file_handler)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        ))
        logger.addHandler(console_handler)
        
        return logger
    
    def log_agent_message(self, agent_role: str, message_type: str, content: str) -> None:
        """
        Log a complete agent message.
        
        Args:
            agent_role: Role of the agent (leader/member)
            message_type: Type of message (send, receive, etc.)
            content: Complete message text
        """
        # Log to standard logger with full message
        self.logger.info(f"Agent {agent_role} {message_type}:")
        self.logger.info(f"{content}")
        
        # Also log as structured event
        self.log_event("agent_message", {
            "agent_role": agent_role,
            "message_type": message_type,
            "content": content
        })
    
    def log_round_result(self, 
                        round_type: str, 
                        score: int, 
                        ranking: list, 
                        metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Log the result of a simulation round.
        
        Args:
            round_type: Type of round (collaborative, adversarial)
            score: Score achieved
            ranking: Final ranking
            metadata: Optional additional metadata
        """
        self.log_event("round_result", {
            "round_type": round_type,
            "score": score,
            "ranking": ranking,
            "metadata": metadata or {}
        })
        
        self.logger.info(f"Round {round_type} completed with score: {score}")
    
    def log_simulation_complete(self, results: Dict[str, Any]) -> None:
        """
        Log the completion of the simulation.
        
        Args:
            results: Final simulation results
        """
        self.log_event("simulation_completed", {
            "simulation_id": self.simulation_id,
            "final_score": results.get("score"),
            "final_ranking": results.get("final_ranking"),
            "summary": results
        })
        
        self.logger.info(f"Simulation {self.simulation_id} completed with score: {results.get('score')}")

    def setup_logging(simulation_id: str, configuration: Dict[str, bool]) -> logging.Logger:
        """
        Set up logging for a simulation run.
        
        Args:
            simulation_id: ID of the simulation
            configuration: Configuration options (leadership, closed_loop)
        
        Returns:
            Configured logger
        """
        # Create configuration string
        config_str = []
        if configuration.get("leadership"):
            config_str.append("leadership")
        if configuration.get("closed_loop"):
            config_str.append("closed_loop")
        config_name = "_".join(config_str) if config_str else "baseline"
        
        # Create folder structure
        run_dir = os.path.join(config.LOG_DIR, config_name, simulation_id)
        os.makedirs(run_dir, exist_ok=True)
        
        # Configure logger
        logger = logging.getLogger(f"simulation.{simulation_id}")
        logger.setLevel(logging.INFO)
        
        # File handler with full path
        log_path = os.path.join(run_dir, f"{simulation_id}.log")
        file_handler = logging.FileHandler(log_path)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        ))
        
        # Add handlers and return
        logger.addHandler(file_handler)
        logger.addHandler(logging.StreamHandler())
        
        logger.info(f"Initialized logging for {simulation_id} with configuration: {config_name}")
        return logger

    def log_agent_message(logger: logging.Logger, agent_role: str, message: str):
        """
        Log a complete agent message.
        
        Args:
            logger: Logger instance
            agent_role: Role of the agent (leader/member)
            message: Complete message text
        """
        logger.info(f"Agent {agent_role} message:")
        # Log full message, not just first 100 chars
        logger.info(f"{message}")

    def log_event(self, event_type, data):
        """Log a structured event to the events file."""
        event = {
            "event_type": event_type,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        
        with open(self.events_file, 'a') as f:
            f.write(json.dumps(event) + '\n')
        
        self.logger.info(f"Event logged: {event_type}")
    
    def log_main_loop(self, round_type, step, agent_role, message):
        """Log main conversation flow between agents."""
        event = {
            "round_type": round_type,
            "step": step,
            "agent_role": agent_role,
            "timestamp": datetime.now().isoformat(),
            "message": message
        }
        
        with open(self.main_loop_file, 'a') as f:
            f.write(json.dumps(event) + '\n')
        
        self.logger.info(f"Main loop: {round_type} - {step} - {agent_role}")
    
    def log_closed_loop(self, sender, initial_message, acknowledgment, verification):
        """Log closed-loop communication events."""
        event = {
            "sender": sender,
            "timestamp": datetime.now().isoformat(),
            "initial_message": initial_message,
            "acknowledgment": acknowledgment,
            "verification": verification
        }
        
        with open(self.closed_loop_file, 'a') as f:
            f.write(json.dumps(event) + '\n')
        
        self.logger.info(f"Closed-loop communication from {sender} completed")
    
    def log_leader_action(self, action_type, content, updates=None):
        """Log leader-specific actions and knowledge base updates."""
        event = {
            "action_type": action_type,
            "timestamp": datetime.now().isoformat(),
            "content": content,
            "knowledge_updates": updates or {}
        }
        
        with open(self.leader_file, 'a') as f:
            f.write(json.dumps(event) + '\n')
        
        self.logger.info(f"Leader action: {action_type}")
