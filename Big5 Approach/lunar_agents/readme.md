# Lunar Survival Agents

A modular implementation of agents collaborating on NASA's Lunar Survival Challenge, incorporating key principles from Salas et al.'s "Big Five" teamwork model.

## Overview

This project implements a multi-agent system where two AI agents (Team Leader and Science Analyst) collaborate to solve the NASA Lunar Survival Challenge. The agents are tasked with ranking 15 items in order of importance for survival during a 200-mile trek on the lunar surface.

Key features:
- Implementation of "Team Leadership" and "Closed-loop Communication" from the Big Five teamwork model
- Modular design allowing features to be toggled on/off
- Support for both collaborative and adversarial teamwork modes
- Comprehensive logging and evaluation capabilities

## Agent Setup

The system consists of two specialized agents:

1. **Team Leader Agent**: Responsible for coordinating the team, establishing structure, and making final decisions. The Team Leader maintains a shared knowledge base and synthesizes perspectives.

2. **Science Analyst Agent**: Provides scientific expertise about the lunar environment and offers evidence-based recommendations for survival priorities.

## Communication Cycles

### Main Loop Communication
This is the standard communication flow between agents:

1. **Initial Rankings**: Both agents create their initial rankings independently
2. **Collaborative Round**: Agents share and discuss their rankings to reach consensus
3. **Adversarial Round**: Agents debate discrepancies in their rankings by:
   - Identifying key disagreements in item positions
   - Debating each disagreement with supporting evidence
   - Reaching a final consensus through structured discussion

### Team Leadership Component
When enabled, the Team Leader provides additional structure:

- **Task Definition**: Defines the overall approach and creates subtask specifications
- **Agent Capability Assessment**: Documents the capabilities and limitations of team members
- **Knowledge Base Management**: Maintains a shared repository of information
- **Decision Authority**: Makes final determinations on rankings, especially when disagreements persist
- **Meta-Cognitive Guidance**: Regularly evaluates team progress and adjusts approach as needed

### Closed-Loop Communication Component
When enabled, all communications follow a three-step verification protocol:

1. **Sender Phase**: Agent sends initial message with detailed content
2. **Receiver Phase**: Recipient acknowledges receipt and confirms understanding
3. **Verification Phase**: Original sender verifies the message was correctly understood

This protocol ensures critical information is properly exchanged and understood, reducing the risk of miscommunication.

## Usage

### Basic Usage
```bash
python main.py
```

### Feature Options
```bash
python main.py --leadership    # Enable team leadership
python main.py --closedloop    # Enable closed-loop communication
python main.py --adversarial   # Include adversarial round
```

### Run All Combinations
```bash
python main.py --all
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
│   └── sim_20250406_123456/
│       ├── sim_20250406_123456.log           # Main log file
│       ├── sim_20250406_123456_main_loop.jsonl  # All agent exchanges
│       ├── sim_20250406_123456_events.jsonl     # General events
├── leadership/
│   └── sim_20250406_234567/
│       ├── sim_20250406_234567.log
│       ├── sim_20250406_234567_main_loop.jsonl
│       ├── sim_20250406_234567_leader.jsonl     # Leadership actions
│       ├── sim_20250406_234567_events.jsonl
├── closed_loop/
│   └── sim_20250406_345678/
│       ├── sim_20250406_345678.log
│       ├── sim_20250406_345678_main_loop.jsonl
│       ├── sim_20250406_345678_closed_loop.jsonl  # Closed-loop exchanges
│       ├── sim_20250406_345678_events.jsonl
└── leadership_closed_loop/
    └── sim_20250406_456789/
        ├── sim_20250406_456789.log
        ├── sim_20250406_456789_main_loop.jsonl
        ├── sim_20250406_456789_leader.jsonl
        ├── sim_20250406_456789_closed_loop.jsonl
        ├── sim_20250406_456789_events.jsonl
```

Simulation results are also stored in `output/all_simulations.json` for comparative analysis.

## Evaluation

The system automatically scores each simulation by comparing the final ranking against NASA's official ranking. Lower scores indicate better performance. The evaluation system analyzes:

- Score comparisons across different feature combinations
- The impact of Team Leadership and Closed-loop Communication
- The effectiveness of collaborative vs. adversarial approaches

## Project Structure

```
lunar_agents/
├── agents/
│   ├── agent.py             # Base agent class
│   ├── team_leader.py       # Team leader functionality
│   └── team_member.py       # Team member functionality
├── communication/
│   └── closed_loop.py       # Closed-loop communication implementation
├── models/
│   └── knowledge_base.py    # Knowledge base management
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