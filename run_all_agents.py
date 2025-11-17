"""
Multi-Agent Runner
Runs the general assistant agent in production mode
"""
import sys
import logging
from general_assistant import entrypoint as general_entrypoint
from livekit.agents import cli, WorkerOptions

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("multi-agent-runner")

if __name__ == "__main__":
    logger.info("Starting LiveKit general assistant agent...")
    
    # Add 'start' command to sys.argv so cli.run_app works
    sys.argv = ["run_all_agents.py", "start"]
    
    # Run the general assistant
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=general_entrypoint,
        )
    )
