"""
Market Size Validator Agent

Specialized agent for validating startup TAM/SAM/SOM claims against authoritative market research sources.
Compares startup market size claims with data from reputable sources like Gartner, Forrester, and industry reports.
"""

from .agent import market_size_validator_agent

__all__ = ["market_size_validator_agent"]