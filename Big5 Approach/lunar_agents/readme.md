# Lunar Survival Agents with Big Five Teamwork Model

A comprehensive implementation of NASA's Lunar Survival Challenge using intelligent agents and the complete "Big Five" teamwork model by Salas et al.

## Overview

This project implements a multi-agent system that collaborates to solve the NASA Lunar Survival Challenge. Agents are tasked with ranking 15 items in order of importance for survival during a 200-mile trek on the lunar surface using a sequential refinement process.

The project integrates all five components of the Salas et al. Big Five teamwork model:
1. Team Leadership
2. Mutual Performance Monitoring
3. Backup Behavior (via specialized agents)
4. Adaptability (via sequential refinement)
5. Team Orientation (via shared mental models)

## Key Features

- **Sequential Refinement**: Agents iteratively refine a single ranking until consensus emerges
- **Modular Teamwork Components**: All Big Five elements can be toggled independently
- **Specialized Agents**: Science Analyst and Resource Manager with distinct expertise
- **Comprehensive Evaluation**: Detailed performance metrics for each teamwork configuration
- **Extensive Logging**: Structured logs for analysis of teamwork dynamics

## Agent Specializations

The system consists of two specialized agents:

1. **Science Analyst**: Provides expertise on lunar environment conditions, survival principles, and scientific reasoning.

2. **Resource Manager**: Specializes in resource utilization, prioritization strategies, and multi-use potential of items.

Either agent can take on leadership responsibilities, creating a flexible team structure.

## Teamwork Components

### Team Leadership

When enabled, one agent assumes leadership responsibilities:
- Defining the overall approach and task structure
- Synthesizing team perspectives
- Making final decisions when consensus is difficult
- Providing performance expectations
- Clarifying team member roles

### Mutual Performance Monitoring

When enabled, agents monitor each other's work:
- Detecting issues like missing or duplicate items
- Identifying questionable rankings based on domain knowledge
- Providing constructive feedback
- Tracking issue resolution rates

### Shared Mental Models

When enabled, agents develop common understanding of:
- Task environment (lunar conditions, survival priorities)
- Team member roles and expertise
- Task procedures and coordination strategies
- Expected interaction patterns

This shared understanding helps agents anticipate each other's needs and converge more efficiently.

### Closed-Loop Communication

When enabled, all communications follow a three-step verification protocol:
1. **Sender Phase**: Agent sends initial message
2. **Receiver Phase**: Recipient acknowledges and confirms understanding
3. **Verification Phase**: Original sender verifies the message was correctly understood

## Sequential Refinement Process

The simulation uses a streamlined sequential refinement approach:

1. **Initial Ranking**: A randomly selected agent creates an initial ranking with justifications
2. **Iterative Refinement**: Agents take turns refining the ranking, explaining all changes
3. **Monitoring & Feedback**: When enabled, agents provide feedback on potential issues
4. **Convergence**: Process continues until rankings converge (difference score < threshold)

## Usage

### Basic Usage
```bash
python main.py
```

### Feature Options
```bash
python main.py --leadership     # Enable team leadership
python main.py --closedloop     # Enable closed-loop communication
python main.py --mutual         # Enable mutual performance monitoring
python main.py --mental         # Enable shared mental models
python main.py --iterations 5   # Set number of refinement iterations
```

### Run All Combinations
```bash
python main.py --all --runs 5   # Run 5 simulations of each configuration
```

### Analyze Previous Results
```bash
python main.py --analyze
```

## Log Files and Output Structure

Each simulation run creates a structured directory of logs for analysis:

```
logs/
├── baseline/
│   └── sim_20250415_123456/
│       ├── sim_20250415_123456.log                 # Main log file
│       ├── sim_20250415_123456_main_loop.jsonl      # Agent exchanges
│       ├── sim_20250415_123456_events.jsonl         # General events
├── leadership/
├── closed_loop/
├── mutual_monitoring/
├── shared_mental_model/
└── leadership_closed_loop_mutual_monitoring_shared_mental_model/
    └── sim_20250415_456789/
        ├── sim_20250415_456789.log
        ├── sim_20250415_456789_main_loop.jsonl
        ├── sim_20250415_456789_leader.jsonl
        ├── sim_20250415_456789_closed_loop.jsonl
        ├── sim_20250415_456789_monitoring.jsonl
        ├── sim_20250415_456789_mental_model.jsonl
        ├── sim_20250415_456789_events.jsonl
```

Aggregated results are stored in `output/teamwork_features_results.json` for analysis.

## Evaluation

The system automatically scores each simulation by comparing the final ranking against NASA's official ranking. Lower scores indicate better performance. The evaluation system analyzes:

- NASA Score: Comparison between the final ranking and NASA's official ranking
- Convergence Rate: How quickly agents reach consensus
- Teamwork Metrics:
    1. Leadership effectiveness (when enabled)
    2. Monitoring effectiveness and issue resolution rate (when enabled)
    3. Mental model convergence (when enabled)
    4. Communication efficiency (when closed-loop enabled)

## Project Structure

```
lunar_agents/
├── agents/
│   ├── agent.py             # Base agent class
│   ├── team_leader.py       # Team leader functionality
│   ├── team_member.py       # Team member functionality
│   └── modular_agent.py     # For Sequential Refinement  
├── communication/
│   └── closed_loop.py       # Closed-loop communication implementation
├── models/
│   └── knowledge_base.py    # Knowledge base management
├── teamwork/
│   ├── mutual_monitoring.py            #  Modular implementation of Mutual Monitoring functionality
│   └── shared_mental_model.py.py        # Modular implementation of Shared Mental Model functionality
├── simulation/
│   ├── simulator.py         # Main simulation runner
│   └── scenarios.py         # Different simulation scenarios
├── utils/
│   ├── logger.py            # Enhanced logging functionality
│   └── evaluation.py        # Simulation evaluation tools
├── config.py                # Configuration settings
├── main.py                  # Entry point
└── README.md                # Documentation
```

## References

This implementation is based on the teamwork model described in:

Salas, E., Sims, D. E., & Burke, C. S. (2005). Is there a "Big Five" in teamwork? Small Group Research, 36(5), 555-599.