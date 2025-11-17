"""
General Assistant Agent - Default conversational AI
"""
import logging
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    WorkerOptions,
    cli,
)
from livekit.plugins import openai, deepgram, cartesia
from config import AgentConfig, get_default_config

logger = logging.getLogger("general-assistant")


class GeneralAssistant(Agent):
    """General purpose conversational AI assistant"""

    def __init__(self, config: AgentConfig):
        self.config = config

        # Build instructions based on configuration
        instructions = config.get_base_instructions()
        instructions += """

        You are a helpful AI assistant for Mind Call Flow, a platform for AI-powered conversations.
        You can help with:
        - General questions and conversations
        - Information lookup
        - Basic problem-solving
        - Scheduling appointments and managing calendars
        - Customer service and support inquiries
        - Providing guidance and suggestions

        You are capable of handling all types of requests. When users ask about scheduling,
        help them book appointments directly. When they need support, assist them immediately.

        Always be helpful, clear, and conversational.
        """

        super().__init__(instructions=instructions)

    async def on_enter(self):
        """Called when agent starts - generate greeting"""
        logger.info("General Assistant entered conversation")
        await self.session.generate_reply(
            instructions="Greet the user warmly and introduce yourself as their AI assistant. Ask how you can help them today."
        )


async def entrypoint(ctx: JobContext):
    """Main entry point for the agent"""
    logger.info(f"Connecting to room: {ctx.room.name}")
    await ctx.connect()

    # Load configuration from job metadata if provided, otherwise use defaults
    config_data = ctx.job.metadata if hasattr(ctx.job, 'metadata') else {}
    config = AgentConfig(**config_data) if config_data else get_default_config()

    logger.info(f"Starting agent with config: {config.model_dump()}")

    # Create agent session with configured STT/LLM/TTS
    session = AgentSession(
        stt=deepgram.STT(model="nova-2"),
        llm=openai.LLM(model="gpt-4o-mini"),
        tts=cartesia.TTS(
            voice=config.get_voice_id("cartesia"),
            speed="normal" if config.style.pacing == "normal" else config.style.pacing,
        ),
    )

    # Start the session
    agent = GeneralAssistant(config)
    await session.start(agent=agent, room=ctx.room)


if __name__ == "__main__":
    # Run the agent
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            agent_name="general-assistant",
        )
    )
