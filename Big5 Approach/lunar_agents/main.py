"""
Main entry point for lunar survival simulation with enhanced teamwork features.
"""

import argparse
import logging
import os
import json
from typing import Dict, Any, List
from datetime import datetime

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

def run_simulation(
    use_team_leadership: bool = False, 
    use_closed_loop_comm: bool = False,
    use_mutual_monitoring: bool = False,
    use_shared_mental_model: bool = False,
    iterations: int = 3
) -> Dict[str, Any]:
    """
    Run a lunar survival simulation with selected teamwork features.
    
    Args:
        use_team_leadership: Whether to use team leadership behaviors
        use_closed_loop_comm: Whether to use closed-loop communication
        use_mutual_monitoring: Whether to use mutual performance monitoring
        use_shared_mental_model: Whether to use shared mental models
        iterations: Number of refinement iterations
        
    Returns:
        Simulation results
    """
    # Create configuration
    sim_config = {
        "use_team_leadership": use_team_leadership,
        "use_closed_loop_comm": use_closed_loop_comm,
        "use_mutual_monitoring": use_mutual_monitoring,
        "use_shared_mental_model": use_shared_mental_model
    }
    
    # Set up simulation ID with features in name
    features = []
    if use_team_leadership:
        features.append("leadership")
    if use_closed_loop_comm:
        features.append("closed_loop")
    if use_mutual_monitoring:
        features.append("mutual_monitoring")
    if use_shared_mental_model:
        features.append("shared_mental_model")
    
    feature_str = "_".join(features) if features else "baseline"
    simulation_id = f"sim_{feature_str}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Create simulator
    simulator = LunarSurvivalSimulator(
        simulation_id=simulation_id,
        use_team_leadership=use_team_leadership,
        use_closed_loop_comm=use_closed_loop_comm,
        use_mutual_monitoring=use_mutual_monitoring,
        use_shared_mental_model=use_shared_mental_model
    )
    
    # Run sequential refinement
    simulator.run_sequential_refinement(iterations=iterations)
    
    # Save and return results
    simulator.save_results()
    return simulator.results

def run_all_configurations(runs=1, iterations=3):
    """
    Run simulations with individual and all feature combinations.
    
    Args:
        runs: Number of runs per configuration
        iterations: Number of iterations per run
        
    Returns:
        Dictionary with results for each configuration
    """
    # Define configurations to test
    configurations = [
        # Baseline (no features)
        {
            "name": "Baseline", 
            "leadership": False, 
            "closed_loop": False,
            "mutual_monitoring": False,
            "shared_mental_model": False
        },
        # Single features
        {
            "name": "Leadership", 
            "leadership": True, 
            "closed_loop": False,
            "mutual_monitoring": False,
            "shared_mental_model": False
        },
        {
            "name": "Closed-loop", 
            "leadership": False, 
            "closed_loop": True,
            "mutual_monitoring": False,
            "shared_mental_model": False
        },
        {
            "name": "Mutual Monitoring", 
            "leadership": False, 
            "closed_loop": False,
            "mutual_monitoring": True,
            "shared_mental_model": False
        },
        {
            "name": "Shared Mental Model", 
            "leadership": False, 
            "closed_loop": False,
            "mutual_monitoring": False,
            "shared_mental_model": True
        },
        # All features
        {
            "name": "All Features", 
            "leadership": True, 
            "closed_loop": True,
            "mutual_monitoring": True,
            "shared_mental_model": True
        }
    ]
    
    # Track scores across all runs
    score_data = {config["name"]: [] for config in configurations}
    
    # For each run
    for run in range(1, runs + 1):
        print(f"\n=== Run {run}/{runs} ===")
        
        # For each configuration
        for config in configurations:
            print(f"Running {config['name']}...")
            
            # Create simulator ID
            sim_id = f"sim_{config['name'].lower().replace(' ', '_')}_{run}"
            
            # Run simulation with this configuration
            result = run_simulation(
                use_team_leadership=config["leadership"],
                use_closed_loop_comm=config["closed_loop"],
                use_mutual_monitoring=config["mutual_monitoring"],
                use_shared_mental_model=config["shared_mental_model"],
                iterations=iterations
            )
            
            # Store score
            score = result["score"]
            score_data[config["name"]].append(score)
            
            # Print this run's result
            print(f"{config['name'].ljust(25)} Score: {score}")
    
    # Calculate and display average scores
    print("\n=== Average Scores ===")
    avg_scores = {}
    for name, scores in score_data.items():
        avg = sum(scores) / len(scores)
        avg_scores[name] = avg
        print(f"{name.ljust(25)} Score: {avg:.1f}")
    
    # Save aggregate results
    output_path = os.path.join("output", f"teamwork_features_results.json")
    with open(output_path, 'w') as f:
        json.dump({
            "runs": runs,
            "iterations": iterations,
            "individual_scores": score_data,
            "average_scores": avg_scores
        }, f, indent=2)
    
    print(f"\nDetailed results saved to: {output_path}")
    return avg_scores

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Run lunar survival agent simulations with teamwork features')
    parser.add_argument('--leadership', action='store_true', help='Use team leadership')
    parser.add_argument('--closedloop', action='store_true', help='Use closed-loop communication')
    parser.add_argument('--mutual', action='store_true', help='Use mutual performance monitoring')
    parser.add_argument('--mental', action='store_true', help='Use shared mental model')
    parser.add_argument('--all', action='store_true', help='Run all feature combinations')
    parser.add_argument('--runs', type=int, default=1, help='Number of runs for each configuration')
    parser.add_argument('--iterations', type=int, default=3, help='Number of refinement iterations')
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
        output_path = os.path.join("output", "results_visualization.png")
        evaluator.visualize_results(results, output_path)
        print(f"\nVisualization saved to: {output_path}")
    
    elif args.all:
        logging.info(f"Running all individual feature configurations with {args.runs} runs, {args.iterations} iterations")
        run_all_configurations(runs=args.runs, iterations=args.iterations)
        
    else:
        logging.info("Running single simulation")
        result = run_simulation(
            use_team_leadership=args.leadership,
            use_closed_loop_comm=args.closedloop,
            use_mutual_monitoring=args.mutual,
            use_shared_mental_model=args.mental,
            iterations=args.iterations
        )
        
        # Determine which features were used
        features = []
        if args.leadership:
            features.append("Team Leadership")
        if args.closedloop:
            features.append("Closed-loop Communication")
        if args.mutual:
            features.append("Mutual Performance Monitoring")
        if args.mental:
            features.append("Shared Mental Model")
        
        features_str = ", ".join(features) if features else "None"
        
        print(f"\nResults Summary:")
        print(f"Teamwork Features: {features_str}")
        print(f"Iterations: {args.iterations}")
        print(f"Score: {result['score']} (lower is better)")
        print(f"Final Ranking:")
        for i, item in enumerate(result["final_ranking"]):
            print(f"{i+1}. {item}")
        
        # Show where to find logs
        sim_id = result["simulation_id"]
        feature_dir = "_".join(features).lower().replace(" ", "_") if features else "baseline"
        
        print(f"\nDetailed logs available at: logs/ {os.path.join(feature_dir, sim_id)}")

if __name__ == "__main__":
    main()