"""
Closed-loop communication implementation for lunar survival agents.
"""

import logging
from typing import Tuple, Dict, Any, List, Optional

from agents.agent import Agent

class ClosedLoopCommunication:
    """
    Implements closed-loop communication protocol between agents.
    
    Closed-loop communication involves:
    1. Sender initiating a message
    2. Receiver acknowledging and confirming understanding
    3. Sender verifying the message was received correctly
    """
    
    def __init__(self):
        """Initialize the closed-loop communication handler."""
        self.logger = logging.getLogger("communication.closed_loop")
        self.logger.info("Initialized closed-loop communication handler")
    
    def facilitate_exchange(self, 
                           sender: Agent, 
                           receiver: Agent, 
                           initial_message: str) -> Tuple[str, str, str]:
        """
        Facilitate a complete closed-loop communication exchange.
        
        Args:
            sender: The agent sending the initial message
            receiver: The agent receiving the message
            initial_message: The content of the initial message
            
        Returns:
            Tuple containing (initial message, acknowledgment, verification)
        """
        self.logger.info(f"Starting closed-loop exchange: {sender.role} -> {receiver.role}")
        
        # Step 1: Sender initiates message
        sender_message = sender.chat(initial_message)
        self.logger.info(f"Step 1 - Sender message sent: {sender_message[:50]}...")
        
        # Step 2: Receiver acknowledges and confirms understanding
        receiver_prompt = f"""
        You have received the following message from the {sender.role}:
        
        "{sender_message}"
        
        Following closed-loop communication protocol:
        1. Acknowledge that you have received this message
        2. Confirm your understanding by restating the key points in your own words
        3. Then provide your response to the content
        
        Begin your response with an acknowledgment and confirmation.
        """
        
        receiver_message = receiver.chat(receiver_prompt)
        self.logger.info(f"Step 2 - Receiver acknowledgment: {receiver_message[:50]}...")
        
        # Step 3: Sender verifies message was received correctly
        verification_prompt = f"""
        You sent the following message to the {receiver.role}:
        
        "{sender_message}"
        
        They responded with:
        
        "{receiver_message}"
        
        Following closed-loop communication protocol:
        1. Verify whether they understood your message correctly
        2. Clarify any misunderstandings if necessary
        3. Then continue the conversation based on their response
        
        Begin your response with verification of their understanding.
        """
        
        verification_message = sender.chat(verification_prompt)
        self.logger.info(f"Step 3 - Sender verification: {verification_message[:50]}...")
        
        return (sender_message, receiver_message, verification_message)
    
    def extract_content_from_exchange(self, exchange: Tuple[str, str, str]) -> Dict[str, str]:
        """
        Extract the substantive content from a closed-loop exchange.
        
        Args:
            exchange: Tuple of (initial message, acknowledgment, verification)
            
        Returns:
            Dictionary with sender_content and receiver_content keys
        """
        sender_message, receiver_message, verification_message = exchange
        
        # This is a simplified extraction - in practice, you'd want more robust parsing
        # to separate protocol elements from substantive content
        return {
            "sender_content": sender_message,
            "receiver_content": receiver_message.split("\n\n", 1)[1] if "\n\n" in receiver_message else receiver_message,
            "verification_content": verification_message
        }