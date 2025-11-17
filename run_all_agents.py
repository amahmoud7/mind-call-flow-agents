"""
Multi-Agent Runner
Runs all 4 LiveKit agents simultaneously in dev mode
"""
import multiprocessing
import sys
import logging
from general_assistant import entrypoint as general_entrypoint
from scheduling_agent import entrypoint as scheduling_entrypoint
from customer_service import entrypoint as customer_service_entrypoint
from outbound_caller import entrypoint as outbound_entrypoint
from livekit.agents import cli, WorkerOptions

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("multi-agent-runner")


def run_agent(agent_name: str, entrypoint_func):
    """Run a single agent"""
    logger.info(f"Starting {agent_name}...")
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint_func,
            agent_name=agent_name,
        )
    )


if __name__ == "__main__":
    logger.info("Starting all LiveKit agents...")

    # Create process for each agent
    processes = [
        multiprocessing.Process(
            target=run_agent,
            args=("general-assistant", general_entrypoint),
            name="general-assistant"
        ),
        multiprocessing.Process(
            target=run_agent,
            args=("scheduling-agent", scheduling_entrypoint),
            name="scheduling-agent"
        ),
        multiprocessing.Process(
            target=run_agent,
            args=("customer-service-agent", customer_service_entrypoint),
            name="customer-service-agent"
        ),
        multiprocessing.Process(
            target=run_agent,
            args=("outbound-caller-agent", outbound_entrypoint),
            name="outbound-caller-agent"
        ),
    ]

    # Start all processes
    for process in processes:
        process.start()
        logger.info(f"Started process: {process.name}")

    # Wait for all processes
    try:
        for process in processes:
            process.join()
    except KeyboardInterrupt:
        logger.info("Shutting down all agents...")
        for process in processes:
            process.terminate()
        for process in processes:
            process.join()
        logger.info("All agents stopped")
        sys.exit(0)
