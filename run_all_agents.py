"""
Multi-Agent Runner
Runs the general assistant agent only (simplified for deployment)
"""
import logging
from general_assistant import entrypoint as general_entrypoint
from livekit.agents import cli, WorkerOptions

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("multi-agent-runner")

if __name__ == "__main__":
    logger.info("Starting LiveKit general assistant agent...")

    # Run only the general assistant for now
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=general_entrypoint,
        )
    )
