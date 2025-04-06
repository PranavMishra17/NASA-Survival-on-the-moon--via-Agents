"""
Simulation scenarios for lunar survival agents.
"""

from typing import Dict, List, Any, Callable
import logging

from simulation.simulator import LunarSurvivalSimulator
import config

class SimulationScenario:
    """Base class for simulation scenarios."""
    
    def __init__(self, name: str, description: str):
        """
        Initialize a simulation scenario.
        
        Args:
            name: Name of the scenario
            description: Description of the scenario
        """
        self.name = name
        self.description = description
        self.logger = logging.getLogger(f"scenario.{name}")
    
    def setup(self) -> Dict[str, Any]:
        """
        Set up the scenario.
        
        Returns:
            Configuration for the scenario
        """
        return {}
    
    def run(self, simulator: LunarSurvivalSimulator) -> Dict[str, Any]:
        """
        Run the scenario.
        
        Args:
            simulator: Configured simulator
            
        Returns:
            Scenario results
        """
        raise NotImplementedError("Subclasses must implement run")
    
    def evaluate(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate the scenario results.
        
        Args:
            results: Results from running the scenario
            
        Returns:
            Evaluation metrics
        """
        return {
            "name": self.name,
            "description": self.description,
            "score": results.get("score", 0)
        }


class CollaborativeScenario(SimulationScenario):
    """Scenario where agents collaborate to rank items."""
    
    def __init__(self, use_team_leadership: bool = True, use_closed_loop_comm: bool = False):
        """
        Initialize a collaborative scenario.
        
        Args:
            use_team_leadership: Whether to use team leadership
            use_closed_loop_comm: Whether to use closed-loop communication
        """
        features = []
        if use_team_leadership:
            features.append("Team Leadership")
        if use_closed_loop_comm:
            features.append("Closed-loop Communication")
        
        feature_str = " + ".join(features) if features else "Baseline"
        name = f"Collaborative ({feature_str})"
        description = f"Agents collaboratively rank lunar survival items using {feature_str} features"
        
        super().__init__(name, description)
        self.use_team_leadership = use_team_leadership
        self.use_closed_loop_comm = use_closed_loop_comm
    
    def setup(self) -> Dict[str, Any]:
        """Set up the collaborative scenario."""
        self.logger.info(f"Setting up {self.name}")
        return {
            "use_team_leadership": self.use_team_leadership,
            "use_closed_loop_comm": self.use_closed_loop_comm
        }
    
    def run(self, simulator: LunarSurvivalSimulator) -> Dict[str, Any]:
        """Run the collaborative scenario."""
        self.logger.info(f"Running {self.name}")
        results = simulator.run_collaborative_round()
        simulator.save_results()
        return results


class AdversarialScenario(SimulationScenario):
    """Scenario where agents defend their own rankings."""
    
    def __init__(self, use_team_leadership: bool = True, use_closed_loop_comm: bool = False):
        """
        Initialize an adversarial scenario.
        
        Args:
            use_team_leadership: Whether to use team leadership
            use_closed_loop_comm: Whether to use closed-loop communication
        """
        features = []
        if use_team_leadership:
            features.append("Team Leadership")
        if use_closed_loop_comm:
            features.append("Closed-loop Communication")
        
        feature_str = " + ".join(features) if features else "Baseline"
        name = f"Adversarial ({feature_str})"
        description = f"Agents defensively rank lunar survival items using {feature_str} features"
        
        super().__init__(name, description)
        self.use_team_leadership = use_team_leadership
        self.use_closed_loop_comm = use_closed_loop_comm
    
    def setup(self) -> Dict[str, Any]:
        """Set up the adversarial scenario."""
        self.logger.info(f"Setting up {self.name}")
        return {
            "use_team_leadership": self.use_team_leadership,
            "use_closed_loop_comm": self.use_closed_loop_comm
        }
    
    def run(self, simulator: LunarSurvivalSimulator) -> Dict[str, Any]:
        """Run the adversarial scenario."""
        self.logger.info(f"Running {self.name}")
        
        # First run a collaborative round to establish initial rankings
        simulator.run_collaborative_round()
        
        # Then run an adversarial round
        results = simulator.run_adversarial_round()
        simulator.save_results()
        return results


class CompleteScenario(SimulationScenario):
    """Scenario that runs both collaborative and adversarial rounds."""
    
    def __init__(self, use_team_leadership: bool = True, use_closed_loop_comm: bool = False):
        """
        Initialize a complete scenario.
        
        Args:
            use_team_leadership: Whether to use team leadership
            use_closed_loop_comm: Whether to use closed-loop communication
        """
        features = []
        if use_team_leadership:
            features.append("Team Leadership")
        if use_closed_loop_comm:
            features.append("Closed-loop Communication")
        
        feature_str = " + ".join(features) if features else "Baseline"
        name = f"Complete ({feature_str})"
        description = f"Agents complete both collaborative and adversarial rounds using {feature_str} features"
        
        super().__init__(name, description)
        self.use_team_leadership = use_team_leadership
        self.use_closed_loop_comm = use_closed_loop_comm
    
    def setup(self) -> Dict[str, Any]:
        """Set up the complete scenario."""
        self.logger.info(f"Setting up {self.name}")
        return {
            "use_team_leadership": self.use_team_leadership,
            "use_closed_loop_comm": self.use_closed_loop_comm
        }
    
    def run(self, simulator: LunarSurvivalSimulator) -> Dict[str, Any]:
        """Run the complete scenario."""
        self.logger.info(f"Running {self.name}")
        
        # Run collaborative round
        self.logger.info("Running collaborative round")
        collaborative_results = simulator.run_collaborative_round()
        
        # Run adversarial round
        self.logger.info("Running adversarial round")
        adversarial_results = simulator.run_adversarial_round()
        
        # Save final results
        simulator.save_results()
        
        return {
            "collaborative": collaborative_results,
            "adversarial": adversarial_results,
            "final_ranking": simulator.results["final_ranking"],
            "score": simulator.results["score"]
        }


def run_scenario(scenario_class: Callable, **kwargs) -> Dict[str, Any]:
    """
    Run a specific scenario.
    
    Args:
        scenario_class: Scenario class to instantiate
        **kwargs: Arguments to pass to the scenario
        
    Returns:
        Scenario results
    """
    # Create scenario
    scenario = scenario_class(**kwargs)
    
    # Set up the scenario
    config = scenario.setup()
    
    # Create simulator with scenario configuration
    simulator = LunarSurvivalSimulator(
        simulation_id=f"{scenario.name.lower().replace(' ', '_').replace('(', '').replace(')', '')}",
        **config
    )
    
    # Run the scenario
    results = scenario.run(simulator)
    
    # Evaluate the results
    evaluation = scenario.evaluate(results)
    
    return {
        "scenario": scenario.name,
        "description": scenario.description,
        "config": config,
        "results": results,
        "evaluation": evaluation
    }


def run_all_scenarios() -> List[Dict[str, Any]]:
    """
    Run all scenario combinations.
    
    Returns:
        List of scenario results
    """
    scenarios = []
    
    # All combinations of features
    feature_combos = [
        {"leadership": False, "closed_loop": False},
        {"leadership": True, "closed_loop": False},
        {"leadership": False, "closed_loop": True},
        {"leadership": True, "closed_loop": True}
    ]
    
    # Run each scenario with each feature combination
    for combo in feature_combos:
        # Collaborative scenarios
        collaborative_result = run_scenario(
            CollaborativeScenario,
            use_team_leadership=combo["leadership"],
            use_closed_loop_comm=combo["closed_loop"]
        )
        scenarios.append(collaborative_result)
        
        # Adversarial scenarios
        adversarial_result = run_scenario(
            AdversarialScenario,
            use_team_leadership=combo["leadership"],
            use_closed_loop_comm=combo["closed_loop"]
        )
        scenarios.append(adversarial_result)
        
        # Complete scenarios
        complete_result = run_scenario(
            CompleteScenario,
            use_team_leadership=combo["leadership"],
            use_closed_loop_comm=combo["closed_loop"]
        )
        scenarios.append(complete_result)
    
    return scenarios