"""
Evaluation tools for lunar survival agent simulations.
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
            # Load all simulation results
            all_results_path = os.path.join(self.output_dir, "all_simulations.json")
            if os.path.exists(all_results_path):
                with open(all_results_path, 'r') as f:
                    return json.load(f)
            
            # If combined file doesn't exist, load individual files
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
        # Group results by configuration
        config_groups = {}
        for result in results:
            config_key = (
                result['config'].get('use_team_leadership', False),
                result['config'].get('use_closed_loop_comm', False)
            )
            
            if config_key not in config_groups:
                config_groups[config_key] = []
            
            config_groups[config_key].append(result)
        
        # Calculate average scores for each configuration
        avg_scores = {}
        for config_key, group_results in config_groups.items():
            leadership, closed_loop = config_key
            scores = [r['score'] for r in group_results]
            avg_score = sum(scores) / len(scores)
            
            config_str = []
            if leadership:
                config_str.append("Leadership")
            if closed_loop:
                config_str.append("Closed-loop")
            
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
        
        return {
            "average_scores": avg_scores,
            "rank_correlations": avg_correlations
        }
    
    def visualize_results(self, results: List[Dict[str, Any]], output_path: Optional[str] = None) -> None:
        """
        Create visualizations of simulation results.
        
        Args:
            results: List of simulation results
            output_path: Optional path to save visualizations
        """
        eval_metrics = self.evaluate_performance(results)
        
        # Set up figure
        plt.figure(figsize=(12, 8))
        
        # Plot 1: Average scores by configuration
        plt.subplot(2, 2, 1)
        configs = list(eval_metrics["average_scores"].keys())
        scores = list(eval_metrics["average_scores"].values())
        
        y_pos = np.arange(len(configs))
        
        plt.barh(y_pos, scores)
        plt.yticks(y_pos, configs)
        plt.xlabel('Average Score (lower is better)')
        plt.title('Performance by Configuration')
        
        # Plot 2: Rank correlation with NASA
        plt.subplot(2, 2, 2)
        configs = list(eval_metrics["rank_correlations"].keys())
        correlations = list(eval_metrics["rank_correlations"].values())
        
        y_pos = np.arange(len(configs))
        
        plt.barh(y_pos, correlations)
        plt.yticks(y_pos, configs)
        plt.xlabel('Rank Correlation (higher is better)')
        plt.title('Correlation with NASA Ranking')
        
        # Plot 3: Item frequency in top 5
        plt.subplot(2, 1, 2)
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
        plt.yticks(y_pos, items)
        plt.xlabel('Frequency in Top 5')
        plt.title('Most Common Items in Top 5 Rankings')
        
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