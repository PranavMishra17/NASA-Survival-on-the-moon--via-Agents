"""
Configuration settings for the lunar agents simulation.
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Azure OpenAI settings
AZURE_API_KEY = os.environ.get('AZURE_OPENAI_VARE_KEY')
AZURE_ENDPOINT = os.environ.get('AZURE_ENDPOINT')
AZURE_DEPLOYMENT = "VARELab-GPT4o"
AZURE_API_VERSION = "2024-08-01-preview"

# Model settings
TEMPERATURE = 0.5
MAX_TOKENS = 1500

# Simulation settings
LOG_DIR = "logs"
OUTPUT_DIR = "output"
SIMULATION_ROUNDS = 5

# Create required directories
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Lunar survival items (NASA's ranking from most to least important)
LUNAR_ITEMS = [
    "Oxygen tanks",
    "Water",
    "Stellar map",
    "Food concentrate",
    "Solar-powered FM receiver-transmitter",
    "50 feet of nylon rope",
    "First aid kit",
    "Parachute silk",
    "Life raft",
    "Signal flares",
    "Two .45 caliber pistols",
    "One case of dehydrated milk",
    "Portable heating unit",
    "Magnetic compass",
    "Box of matches"
]

# NASA's official ranking explanation
NASA_RATIONALE = {
    "Oxygen tanks": "Most pressing survival need on the moon",
    "Water": "Replacement for tremendous liquid loss on the light side",
    "Stellar map": "Primary means of navigation - stars are visible",
    "Food concentrate": "Efficient, high-energy food supply",
    "Solar-powered FM receiver-transmitter": "For communication with mother ship; also possible to use as emergency distress signal",
    "50 feet of nylon rope": "Useful for scaling cliffs, tying injured together",
    "First aid kit": "Valuable for injuries, medications",
    "Parachute silk": "Protection from the sun's rays",
    "Life raft": "CO2 bottles for propulsion across chasms, possible shelter",
    "Signal flares": "Distress call when mother ship is visible",
    "Two .45 caliber pistols": "Possible propulsion devices",
    "One case of dehydrated milk": "Food, mixed with water for drinking",
    "Portable heating unit": "Not needed unless on the dark side",
    "Magnetic compass": "The magnetic field on the moon is not polarized, worthless for navigation",
    "Box of matches": "Virtually worthless - no oxygen to sustain flame"
}

# Team configuration
TEAM_NAME = "Lunar Survival Team"
TEAM_GOAL = "Rank the lunar survival items in order of importance for the 200-mile trek to the rendezvous point"

# Agent roles and expertise
AGENT_ROLES = {
    "Team Leader": "Coordinate team efforts, facilitate decision-making, and ensure team follows effective problem-solving process",
    "Science Analyst": "Provide scientific analysis of the lunar environment and survival requirements based on technical knowledge",
    "Resource Manager": "Analyze resource efficiency, prioritize items based on utility vs weight, and manage limited supplies for optimal survival"
}