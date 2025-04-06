"""
Main entry point for the lunar survival simulation.
"""

import argparse
import logging
import os
import json
from typing import Dict, Any, List

from simulation.simulator import LunarSurvivalSimulator
from utils.logger import SimulationLogger
import config

def setup_logging():
    """Set up logging for the application."""
    # Create logs directory if it doesn't exist
    os.makedirs(config.LOG_DIR, exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        handlers=[
            logging.FileHandler(os.path.join(config.LOG_DIR, "lunar_agents.log")),
            logging.StreamHandler()
        ]
    )

def run_simulation(use_team_leadership: bool, use_closed_loop_comm: bool, run_adversarial: bool = False) -> Dict[str, Any]:
    """
    Run a lunar survival simulation.
    
    Args:
        use_team_leadership: Whether to use team leadership behaviors
        use_closed_loop_comm: Whether to use closed-loop communication
        run_adversarial: Whether to run adversarial round after collaborative round
        
    Returns:
        Simulation results
    """
    # Create configuration
    sim_config = {
        "use_team_leadership": use_team_leadership,
        "use_closed_loop_comm": use_closed_loop_comm,
    }
    
    # Set up simulation ID with features in name
    features = []
    if use_team_leadership:
        features.append("leadership")
    if use_closed_loop_comm:
        features.append("closed_loop")
    
    feature_str = "_".join(features) if features else "baseline"
    simulation_id = f"sim_{feature_str}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Create simulator
    simulator = LunarSurvivalSimulator(
        simulation_id=simulation_id,
        use_team_leadership=use_team_leadership,
        use_closed_loop_comm=use_closed_loop_comm
    )
    
    # Run collaborative round
    simulator.run_collaborative_round()
    
    # Run adversarial round if requested
    if run_adversarial:
        simulator.run_adversarial_round()
    
    # Save and return results
    simulator.save_results()
    return simulator.results

def run_all_combinations() -> List[Dict[str, Any]]:
    """
    Run simulations with all combinations of features.
    
    Returns:
        List of all simulation results
    """
    combinations = [
        {"leadership": False, "closed_loop": False},
        {"leadership": True, "closed_loop": False},
        {"leadership": False, "closed_loop": True},
        {"leadership": True, "closed_loop": True}
    ]
    
    results = []
    
    for combo in combinations:
        logging.info(f"Running simulation with: {combo}")
        result = run_simulation(
            use_team_leadership=combo["leadership"],
            use_closed_loop_comm=combo["closed_loop"],
            run_adversarial=True
        )
        results.append(result)
        
        # Print interim results
        feature_str = []
        if combo["leadership"]:
            feature_str.append("Leadership")
        if combo["closed_loop"]:
            feature_str.append("Closed-loop")
        
        feature_name = " + ".join(feature_str) if feature_str else "Baseline"
        print(f"Completed: {feature_name.ljust(25)} Score: {result['score']}")
    
    # Save the combined results
    with open(os.path.join(config.OUTPUT_DIR, "all_simulations.json"), 'w') as f:
        json.dump(results, f, indent=2)
    
    return results

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Run lunar survival agent simulations')
    parser.add_argument('--leadership', action='store_true', help='Use team leadership')
    parser.add_argument('--closedloop', action='store_true', help='Use closed-loop communication')
    parser.add_argument('--adversarial', action='store_true', help='Run adversarial round')
    parser.add_argument('--all', action='store_true', help='Run all feature combinations')
    parser.add_argument('--analyze', action='store_true', help='Analyze previous results')
    
    args = parser.parse_args()
    
    # Set up logging
    setup_logging()
    
    if args.analyze:
        # Analyze previous results
        from utils.evaluation import SimulationEvaluator
        evaluator = SimulationEvaluator()
        results = evaluator.load_results()
        metrics = evaluator.evaluate_performance(results)
        
        print("\nAnalysis Results:")
        print("\nAverage Scores:")
        for config, score in metrics["average_scores"].items():
            print(f"{config.ljust(25)} Score: {score}")
        
        print("\nRank Correlations with NASA's List:")
        for config, corr in metrics["rank_correlations"].items():
            print(f"{config.ljust(25)} Correlation: {corr:.4f}")
        
        # Generate visualization
        output_path = os.path.join(config.OUTPUT_DIR, "results_visualization.png")
        evaluator.visualize_results(results, output_path)
        print(f"\nVisualization saved to: {output_path}")
    
    elif args.all:
        logging.info("Running all feature combinations")
        results = run_all_combinations()
        
        # Print a summary
        print("\nFinal Results Summary:")
        for result in results:
            config = result["config"]
            features = []
            if config["use_team_leadership"]:
                features.append("Leadership")
            if config["use_closed_loop_comm"]:
                features.append("Closed-loop")
            
            feature_str = " + ".join(features) if features else "Baseline"
            print(f"{feature_str.ljust(25)} Score: {result['score']}")
    else:
        logging.info("Running single simulation")
        result = run_simulation(
            use_team_leadership=args.leadership,
            use_closed_loop_comm=args.closedloop,
            run_adversarial=args.adversarial
        )
        
        print(f"\nResults Summary:")
        print(f"Team Leadership: {args.leadership}")
        print(f"Closed-loop Communication: {args.closedloop}")
        print(f"Score: {result['score']} (lower is better)")
        print(f"Final Ranking:")
        for i, item in enumerate(result["final_ranking"]):
            print(f"{i+1}. {item}")
        
        # Show where to find logs
        sim_id = result["simulation_id"]
        features = []
        if args.leadership:
            features.append("leadership")
        if args.closedloop:
            features.append("closed_loop")
        feature_dir = "_".join(features) if features else "baseline"
        
        print(f"\nDetailed logs available at: {os.path.join(config.LOG_DIR, feature_dir, sim_id)}")

if __name__ == "__main__":
    from datetime import datetime
    main()