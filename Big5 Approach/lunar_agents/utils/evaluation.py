"""
Evaluation tools for lunar survival agent simulations with Big Five teamwork features.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter

import config

class SimulationEvaluator:
    """
    Tools for evaluating and visualizing simulation results.
    """
    
    def __init__(self, output_dir: str = None):
        """
        Initialize the evaluator.
        
        Args:
            output_dir: Directory with simulation results
        """
        self.output_dir = output_dir or config.OUTPUT_DIR
        self.logger = logging.getLogger("evaluation")
    
    def load_results(self, simulation_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Load results for a specific simulation or all simulations.
        
        Args:
            simulation_id: Optional specific simulation ID to load
            
        Returns:
            Dictionary of results or list of results
        """
        if simulation_id:
            result_path = os.path.join(self.output_dir, f"{simulation_id}_results.json")
            with open(result_path, 'r') as f:
                return json.load(f)
        else:
            # Try loading different results file formats
            possible_files = [
                "all_simulations.json",
                "multiple_runs_summary.json",
                "teamwork_features_results.json",
                "sequential_runs_summary.json"
            ]
            
            for filename in possible_files:
                file_path = os.path.join(self.output_dir, filename)
                if os.path.exists(file_path):
                    with open(file_path, 'r') as f:
                        return json.load(f)
            
            # If combined files don't exist, load individual files
            results = []
            for filename in os.listdir(self.output_dir):
                if filename.endswith("_results.json"):
                    with open(os.path.join(self.output_dir, filename), 'r') as f:
                        results.append(json.load(f))
            return results
    
    def evaluate_performance(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Evaluate the performance of different simulation configurations.
        
        Args:
            results: List of simulation results
            
        Returns:
            Dictionary with evaluation metrics
        """
        # Handle different result formats
        if isinstance(results, dict) and "individual_scores" in results:
            # Format from multiple runs
            return self._evaluate_multiple_runs(results)
        
        # Group results by configuration
        config_groups = {}
        for result in results:
            # Build configuration key considering all features
            config_key = (
                result['config'].get('use_team_leadership', False),
                result['config'].get('use_closed_loop_comm', False),
                result['config'].get('use_mutual_monitoring', False),
                result['config'].get('use_shared_mental_model', False)
            )
            
            if config_key not in config_groups:
                config_groups[config_key] = []
            
            config_groups[config_key].append(result)
        
        # Calculate average scores for each configuration
        avg_scores = {}
        for config_key, group_results in config_groups.items():
            leadership, closed_loop, mutual_monitoring, shared_mental = config_key
            scores = [r['score'] for r in group_results]
            avg_score = sum(scores) / len(scores)
            
            config_str = []
            if leadership:
                config_str.append("Leadership")
            if closed_loop:
                config_str.append("Closed-loop")
            if mutual_monitoring:
                config_str.append("Mutual Monitoring")
            if shared_mental:
                config_str.append("Shared Mental Model")
            
            config_name = " + ".join(config_str) if config_str else "Baseline"
            avg_scores[config_name] = avg_score
        
        # Compare to NASA ranking
        nasa_ranking = config.LUNAR_ITEMS
        
        # Calculate rank correlations
        rank_correlations = {}
        for result in results:
            config_key = []
            if result['config'].get('use_team_leadership'):
                config_key.append("Leadership")
            if result['config'].get('use_closed_loop_comm'):
                config_key.append("Closed-loop")
            if result['config'].get('use_mutual_monitoring'):
                config_key.append("Mutual Monitoring")
            if result['config'].get('use_shared_mental_model'):
                config_key.append("Shared Mental Model")
            
            config_name = " + ".join(config_key) if config_key else "Baseline"
            
            correlation = self._calculate_rank_correlation(
                result.get('final_ranking', []),
                nasa_ranking
            )
            
            if config_name not in rank_correlations:
                rank_correlations[config_name] = []
            
            rank_correlations[config_name].append(correlation)
        
        # Average correlations
        avg_correlations = {
            config: sum(corrs) / len(corrs)
            for config, corrs in rank_correlations.items()
        }
        
        # Analyze teamwork metrics if available
        teamwork_metrics = self._analyze_teamwork_metrics(results)
        
        # Analyze sequential refinement metrics if available
        iteration_metrics = self._analyze_iteration_metrics(results)
        
        return {
            "average_scores": avg_scores,
            "rank_correlations": avg_correlations,
            "teamwork_metrics": teamwork_metrics,
            "iteration_metrics": iteration_metrics
        }
    
    def _evaluate_multiple_runs(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate results from multiple runs format.
        
        Args:
            results: Dictionary with multiple runs data
            
        Returns:
            Dictionary with evaluation metrics
        """
        # Extract relevant data
        individual_scores = results.get("individual_scores", {})
        
        # Calculate average scores and correlations
        avg_scores = results.get("average_scores", {})
        
        # Calculate rank correlations
        nasa_ranking = config.LUNAR_ITEMS
        rank_correlations = {}
        
        # Return combined metrics
        return {
            "average_scores": avg_scores,
            "rank_correlations": rank_correlations
        }
    
    def _analyze_teamwork_metrics(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze teamwork component effectiveness.
        
        Args:
            results: List of simulation results
            
        Returns:
            Dictionary with teamwork metrics
        """
        metrics = {
            "mutual_monitoring": {},
            "shared_mental_model": {}
        }
        
        # Extract metrics from results
        for result in results:
            teamwork_metrics = result.get("teamwork_metrics", {})
            
            # Process mutual monitoring metrics
            if "mutual_monitoring" in teamwork_metrics:
                mm_metrics = teamwork_metrics["mutual_monitoring"]
                effectiveness = mm_metrics.get("team_monitoring_effectiveness")
                
                if effectiveness not in metrics["mutual_monitoring"]:
                    metrics["mutual_monitoring"][effectiveness] = 0
                metrics["mutual_monitoring"][effectiveness] += 1
            
            # Process shared mental model metrics
            if "shared_mental_model" in teamwork_metrics:
                smm_metrics = teamwork_metrics["shared_mental_model"]
                effectiveness = smm_metrics.get("effectiveness_rating")
                
                if effectiveness not in metrics["shared_mental_model"]:
                    metrics["shared_mental_model"][effectiveness] = 0
                metrics["shared_mental_model"][effectiveness] += 1
        
        return metrics
    
    def _analyze_iteration_metrics(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze metrics from the sequential refinement iterations.
        
        Args:
            results: List of simulation results
            
        Returns:
            Dictionary with iteration metrics
        """
        metrics = {
            "avg_iterations_to_consensus": 0,
            "score_progression": {},
            "convergence_rate": {}
        }
        
        total_iterations = 0
        num_results = 0
        
        # Extract iteration data from sequential refinement
        for result in results:
            exchanges = result.get("exchanges", [])
            for exchange in exchanges:
                if exchange.get("type") == "sequential_refinement":
                    iterations = exchange.get("iterations", [])
                    
                    # Count iterations until consensus
                    consensus_iteration = len(iterations)
                    total_iterations += consensus_iteration
                    num_results += 1
                    
                    # Track score progression
                    config_name = self._get_config_name(result["config"])
                    if config_name not in metrics["score_progression"]:
                        metrics["score_progression"][config_name] = []
                    
                    # Extract scores by iteration
                    iteration_scores = []
                    for iteration in iterations:
                        if "nasa_score" in iteration:
                            iteration_scores.append(iteration["nasa_score"])
                    
                    if iteration_scores:
                        metrics["score_progression"][config_name].append(iteration_scores)
                    
                    # Calculate convergence rate
                    if config_name not in metrics["convergence_rate"]:
                        metrics["convergence_rate"][config_name] = []
                    
                    # Extract difference scores by iteration
                    difference_scores = []
                    for iteration in iterations:
                        if "difference_score" in iteration:
                            difference_scores.append(iteration["difference_score"])
                    
                    if difference_scores and len(difference_scores) > 1:
                        # Calculate rate of convergence
                        initial_diff = difference_scores[0] if len(difference_scores) > 1 else 0
                        final_diff = difference_scores[-1]
                        convergence_rate = (initial_diff - final_diff) / max(1, len(difference_scores) - 1)
                        metrics["convergence_rate"][config_name].append(convergence_rate)
        
        # Calculate average iterations to consensus
        if num_results > 0:
            metrics["avg_iterations_to_consensus"] = total_iterations / num_results
        
        # Average the score progressions and convergence rates
        for config_name, progressions in metrics["score_progression"].items():
            if progressions:
                # Normalize to the same length
                max_length = max(len(prog) for prog in progressions)
                normalized_progs = []
                for prog in progressions:
                    if len(prog) < max_length:
                        # Pad with last score
                        normalized_progs.append(prog + [prog[-1]] * (max_length - len(prog)))
                    else:
                        normalized_progs.append(prog)
                
                # Average across runs
                avg_progression = []
                for i in range(max_length):
                    values = [prog[i] for prog in normalized_progs if i < len(prog)]
                    avg_progression.append(sum(values) / len(values))
                
                metrics["score_progression"][config_name] = avg_progression
        
        # Average convergence rates
        for config_name, rates in metrics["convergence_rate"].items():
            if rates:
                metrics["convergence_rate"][config_name] = sum(rates) / len(rates)
        
        return metrics
    
    def _get_config_name(self, config: Dict[str, bool]) -> str:
        """Generate a consistent configuration name from config dict."""
        config_str = []
        if config.get("use_team_leadership"):
            config_str.append("Leadership")
        if config.get("use_closed_loop_comm"):
            config_str.append("Closed-loop")
        if config.get("use_mutual_monitoring"):
            config_str.append("Mutual Monitoring")
        if config.get("use_shared_mental_model"):
            config_str.append("Shared Mental Model")
        
        return " + ".join(config_str) if config_str else "Baseline"
    
    def visualize_results(self, results: List[Dict[str, Any]], output_path: Optional[str] = None) -> None:
        """
        Create visualizations of simulation results.
        
        Args:
            results: List of simulation results
            output_path: Optional path to save visualizations
        """
        eval_metrics = self.evaluate_performance(results)
        
        # Create figure with updated size for more plots
        plt.figure(figsize=(16, 12))
        
        # Plot 1: Average scores by configuration
        plt.subplot(2, 3, 1)
        configs = list(eval_metrics["average_scores"].keys())
        scores = list(eval_metrics["average_scores"].values())
        
        # Sort by score (lower is better)
        sorted_indices = np.argsort(scores)
        configs = [configs[i] for i in sorted_indices]
        scores = [scores[i] for i in sorted_indices]
        
        y_pos = np.arange(len(configs))
        
        plt.barh(y_pos, scores)
        plt.yticks(y_pos, configs, fontsize=8)
        plt.xlabel('Average Score (lower is better)')
        plt.title('Performance by Configuration')
        
        # Plot 2: Rank correlation with NASA
        plt.subplot(2, 3, 2)
        configs = list(eval_metrics["rank_correlations"].keys())
        correlations = list(eval_metrics["rank_correlations"].values())
        
        # Sort by correlation (higher is better)
        sorted_indices = np.argsort(correlations)[::-1]
        configs = [configs[i] for i in sorted_indices]
        correlations = [correlations[i] for i in sorted_indices]
        
        y_pos = np.arange(len(configs))
        
        plt.barh(y_pos, correlations)
        plt.yticks(y_pos, configs, fontsize=8)
        plt.xlabel('Rank Correlation (higher is better)')
        plt.title('Correlation with NASA Ranking')
        
        # Plot 3: Item frequency in top 5
        plt.subplot(2, 3, 3)
        top_items = self._analyze_top_items(results)
        items = list(top_items.keys())
        counts = list(top_items.values())
        
        # Sort by frequency
        sorted_indices = np.argsort(counts)[::-1]
        items = [items[i] for i in sorted_indices]
        counts = [counts[i] for i in sorted_indices]
        
        # Only show top 10 items
        items = items[:10]
        counts = counts[:10]
        
        y_pos = np.arange(len(items))
        
        plt.barh(y_pos, counts)
        plt.yticks(y_pos, items, fontsize=8)
        plt.xlabel('Frequency in Top 5')
        plt.title('Most Common Items in Top 5 Rankings')
        
        # Plot 4: Score Progression by Configuration
        plt.subplot(2, 3, 4)
        
        if "iteration_metrics" in eval_metrics and "score_progression" in eval_metrics["iteration_metrics"]:
            score_progressions = eval_metrics["iteration_metrics"]["score_progression"]
            
            for config_name, progression in score_progressions.items():
                plt.plot(range(len(progression)), progression, marker='o', label=config_name)
            
            plt.xlabel('Iteration')
            plt.ylabel('NASA Score (lower is better)')
            plt.title('Score Progression During Refinement')
            plt.legend(fontsize=8, loc='upper right')
        else:
            plt.text(0.5, 0.5, 'No iteration data available', ha='center', va='center')
        
        # Plot 5: Mutual Monitoring Effectiveness
        plt.subplot(2, 3, 5)
        
        if "teamwork_metrics" in eval_metrics and "mutual_monitoring" in eval_metrics["teamwork_metrics"]:
            mm_metrics = eval_metrics["teamwork_metrics"]["mutual_monitoring"]
            
            if mm_metrics:
                effectiveness = list(mm_metrics.keys())
                counts = list(mm_metrics.values())
                
                plt.bar(effectiveness, counts)
                plt.xlabel('Effectiveness Rating')
                plt.ylabel('Count')
                plt.title('Mutual Monitoring Effectiveness')
            else:
                plt.text(0.5, 0.5, 'No mutual monitoring data available', ha='center', va='center')
        else:
            plt.text(0.5, 0.5, 'No mutual monitoring data available', ha='center', va='center')
        
        # Plot 6: Shared Mental Model Effectiveness
        plt.subplot(2, 3, 6)
        
        if "teamwork_metrics" in eval_metrics and "shared_mental_model" in eval_metrics["teamwork_metrics"]:
            smm_metrics = eval_metrics["teamwork_metrics"]["shared_mental_model"]
            
            if smm_metrics:
                effectiveness = list(smm_metrics.keys())
                counts = list(smm_metrics.values())
                
                plt.bar(effectiveness, counts)
                plt.xlabel('Effectiveness Rating')
                plt.ylabel('Count')
                plt.title('Shared Mental Model Effectiveness')
            else:
                plt.text(0.5, 0.5, 'No shared mental model data available', ha='center', va='center')
        else:
            plt.text(0.5, 0.5, 'No shared mental model data available', ha='center', va='center')
        
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path)
            self.logger.info(f"Visualization saved to {output_path}")
        else:
            plt.show()
    
    def _analyze_top_items(self, results: List[Dict[str, Any]], top_n: int = 5) -> Dict[str, int]:
        """
        Analyze which items appear most frequently in the top N of rankings.
        
        Args:
            results: List of simulation results
            top_n: Number of top items to consider
            
        Returns:
            Dictionary with items and their frequency in top N
        """
        item_counter = Counter()
        
        for result in results:
            ranking = result.get('final_ranking', [])
            for i, item in enumerate(ranking[:top_n]):
                item_counter[item] += 1
        
        return dict(item_counter)
    
    def _calculate_rank_correlation(self, ranking1: List[str], ranking2: List[str]) -> float:
        """
        Calculate Spearman's rank correlation between two rankings.
        
        Args:
            ranking1: First ranking list
            ranking2: Second ranking list
            
        Returns:
            Correlation coefficient (-1 to 1)
        """
        # Convert to position dictionaries
        pos1 = {item: i for i, item in enumerate(ranking1)}
        pos2 = {item: i for i, item in enumerate(ranking2)}
        
        # Get common items
        common_items = set(ranking1) & set(ranking2)
        
        if not common_items:
            return 0.0
        
        # Calculate differences
        d_squared_sum = sum((pos1[item] - pos2[item])**2 for item in common_items)
        n = len(common_items)
        
        # Spearman's formula
        correlation = 1 - (6 * d_squared_sum) / (n * (n**2 - 1))
        
        return correlation
    
    def visualize_iteration_progression(self, results: Dict[str, Any], output_path: Optional[str] = None) -> None:
        """
        Create visualizations specifically for iteration progress.
        
        Args:
            results: Results dictionary from a single run
            output_path: Optional path to save visualizations
        """
        # Extract iteration data
        iteration_data = None
        for exchange in results.get("exchanges", []):
            if exchange.get("type") == "sequential_refinement":
                iteration_data = exchange.get("iterations", [])
                break
        
        if not iteration_data:
            self.logger.warning("No iteration data found for visualization")
            return
        
        # Create figure
        plt.figure(figsize=(15, 10))
        
        # Plot 1: NASA Score Progression
        plt.subplot(2, 2, 1)
        
        iterations = []
        scores = []
        agents = []
        
        for iteration in iteration_data:
            iter_num = iteration.get("iteration", 0)
            score = iteration.get("nasa_score", 0)
            agent = iteration.get("current_agent", "")
            
            iterations.append(iter_num)
            scores.append(score)
            agents.append(agent)
        
        # Plot points by agent
        for agent_type in set(agents):
            agent_iterations = [i for i, a in zip(iterations, agents) if a == agent_type]
            agent_scores = [s for s, a in zip(scores, agents) if a == agent_type]
            plt.plot(agent_iterations, agent_scores, marker='o', linestyle='-', label=f"{agent_type} Agent")
        
        plt.xlabel('Iteration')
        plt.ylabel('NASA Score (lower is better)')
        plt.title('Score Progression by Iteration')
        plt.legend()
        plt.grid(True)
        
        # Plot 2: Difference Score Progression
        plt.subplot(2, 2, 2)
        
        diff_scores = []
        
        for iteration in iteration_data:
            if "difference_score" in iteration:
                diff_scores.append(iteration["difference_score"])
        
        if diff_scores:
            plt.plot(range(1, len(diff_scores) + 1), diff_scores, marker='o', linestyle='-')
            plt.xlabel('Iteration')
            plt.ylabel('Difference Score')
            plt.title('Convergence of Rankings')
            plt.grid(True)
        else:
            plt.text(0.5, 0.5, 'No difference score data available', ha='center', va='center')
        
        # Plot 3: Item Position Changes
        plt.subplot(2, 2, 3)
        
        # Select key items to track
        key_items = ["Oxygen tanks", "Water", "Stellar map", "Magnetic compass", "Box of matches"]
        
        for item in key_items:
            positions = []
            for iteration in iteration_data:
                ranking = iteration.get("current_ranking", [])
                try:
                    position = ranking.index(item) + 1  # 1-indexed position
                    positions.append(position)
                except (ValueError, IndexError):
                    positions.append(None)
            
            plt.plot(range(len(positions)), positions, marker='o', linestyle='-', label=item)
        
        plt.xlabel('Iteration')
        plt.ylabel('Position in Ranking')
        plt.title('Item Position Changes')
        plt.legend()
        plt.grid(True)
        
        # Plot 4: Agent Performance Comparison
        plt.subplot(2, 2, 4)
        
        agent_scores = {}
        for i, iteration in enumerate(iteration_data):
            if i == 0:  # Skip initial ranking
                continue
                
            agent = iteration.get("current_agent", "unknown")
            score = iteration.get("nasa_score", 0)
            
            if agent not in agent_scores:
                agent_scores[agent] = []
            
            agent_scores[agent].append(score)
        
        # Calculate average score for each agent
        avg_scores = {}
        for agent, scores_list in agent_scores.items():
            if scores_list:
                avg_scores[agent] = sum(scores_list) / len(scores_list)
        
        if avg_scores:
            agents = list(avg_scores.keys())
            scores = [avg_scores[agent] for agent in agents]
            
            plt.bar(agents, scores)
            plt.xlabel('Agent')
            plt.ylabel('Average NASA Score')
            plt.title('Average Performance by Agent')
            
            # Add improvement percentage
            if len(iteration_data) > 1:
                initial_score = iteration_data[0].get("nasa_score", 0)
                final_score = iteration_data[-1].get("nasa_score", 0)
                improvement = ((initial_score - final_score) / initial_score) * 100 if initial_score > 0 else 0
                
                plt.text(0.5, 0.9, f"Overall Improvement: {improvement:.1f}%", 
                        ha='center', transform=plt.gca().transAxes)
        else:
            plt.text(0.5, 0.5, 'No agent performance data available', ha='center', va='center')
        
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path)
            self.logger.info(f"Iteration visualization saved to {output_path}")
        else:
            plt.show()