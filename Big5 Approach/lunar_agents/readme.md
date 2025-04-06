# Lunar Survival Agents

A modular implementation of agents collaborating on NASA's Lunar Survival Challenge, incorporating key principles from Salas et al.'s "Big Five" teamwork model.

## Overview

This project implements a multi-agent system where two AI agents collaborate to solve the NASA Lunar Survival Challenge. The agents are tasked with ranking 15 items in order of importance for survival during a 200-mile trek on the lunar surface.

Key features:
- Implementation of "Team Leadership" and "Closed-loop Communication" from the Big Five teamwork model
- Modular design allowing features to be toggled on/off
- Support for both collaborative and adversarial teamwork modes
- Comprehensive logging and evaluation capabilities

## Project Structure

```
lunar_agents/
├── agents/
│   ├── agent.py             # Base agent class
│   ├── team_leader.py       # Team leader functionality
│   └── team_member.py       # Team member functionality
├── communication/
│   └── closed_loop.py       # Closed-loop communication implementation
├── simulation/
│   └── simulator.py         # Main simulation runner
├── utils/
│   ├── logger.py            # Enhanced logging functionality
│   └── evaluation.py        # Simulation evaluation tools
├── config.py                # Configuration settings
├── main.py                  # Entry point
└── README.md                # Documentation
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/lunar-agents.git
cd lunar-agents
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the project root with the following variables:
```
AZURE_OPENAI_VARE_KEY=your_azure_openai_key
AZURE_ENDPOINT=your_azure_endpoint
```

## Usage

### Basic Usage

Run a simulation with default settings (no special teamwork features):
```bash
python main.py
```

### Feature Options

Enable team leadership:
```bash
python main.py --leadership
```

Enable closed-loop communication:
```bash
python main.py --closedloop
```

Enable both features:
```bash
python main.py --leadership --closedloop
```

Run with an adversarial round after the collaborative round:
```bash
python main.py --adversarial
```

### Run All Combinations

To run simulations with all possible feature combinations and compare results:
```bash
python main.py --all
```

## Understanding the Big Five Implementation

### Team Leadership
The Team Leader agent facilitates collaboration by:
- Establishing clear expectations for the discussion
- Providing structure to the problem-solving approach
- Synthesizing input from team members into a consensus
- Taking responsibility for final decisions

When team leadership is disabled, team decisions are made by averaging individual rankings.

### Closed-loop Communication
Implements the three-step communication protocol:
1. Sender initiates a message
2. Receiver acknowledges receipt and confirms understanding
3. Sender verifies the message was correctly understood

Without closed-loop communication, agents exchange messages directly without verification.

## Evaluation

Simulation results are stored in the `output/` directory as JSON files. Each simulation generates:
- Complete conversation logs
- Final rankings
- Performance scores (compared to NASA's official ranking)

The evaluation system compares different feature combinations to determine the most effective teamwork strategies.

## References

This implementation is based on the teamwork model described in:

Salas, E., Sims, D. E., & Burke, C. S. (2005). Is there a "Big Five" in teamwork? Small Group Research, 36(5), 555-599.
