"""
Outbound Caller Agent - Initiates phone calls and demos capabilities
"""
import logging
from typing import Annotated
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    WorkerOptions,
    cli,
    function_tool,
    FunctionContext,
)
from livekit.plugins import openai, deepgram, cartesia
from config import AgentConfig, get_default_config

logger = logging.getLogger("outbound-caller-agent")

# Call outcomes storage
call_outcomes = []


class OutboundCallerAgent(Agent):
    """Specialized agent for outbound phone calls"""

    def __init__(self, config: AgentConfig):
        self.config = config
        self.user_name = config.user_name or "there"

        # Build instructions based on configuration
        instructions = config.get_base_instructions()
        instructions += f"""

        You are making an outbound call to {self.user_name}.
        This is a demonstration call to showcase Mind Call Flow's voice AI capabilities.

        Your objectives:
        1. Warmly greet {self.user_name} by name
        2. Introduce yourself as an AI assistant from Mind Call Flow
        3. Explain this is a demo of our voice AI technology
        4. Ask if they have a few minutes to see what the platform can do
        5. Demonstrate key capabilities:
           - Natural conversation
           - Understanding context
           - Answering questions
           - Scheduling assistance (if interested)
        6. Ask if they'd like more information or to schedule a full demo
        7. Thank them for their time

        Be warm, professional, and respectful of their time.
        If they seem busy or not interested, politely wrap up the call.
        """

        super().__init__(instructions=instructions)

    async def on_enter(self):
        """Called when agent starts - personalized greeting"""
        logger.info(f"Outbound Caller Agent entered conversation for {self.user_name}")
        await self.session.generate_reply(
            instructions=f"Greet {self.user_name} warmly by name, introduce yourself as an AI assistant from Mind Call Flow, and explain this is a demo call. Ask if they have a moment to see our voice AI capabilities."
        )


@function_tool
async def log_call_outcome(
    ctx: FunctionContext,
    outcome: Annotated[str, "Call outcome: answered, interested, not_interested, callback, or voicemail"],
    notes: Annotated[str | None, "Additional notes about the call"] = None
) -> str:
    """Log the outcome of the outbound call"""
    logger.info(f"Logging call outcome: {outcome}")

    call_record = {
        "outcome": outcome,
        "notes": notes,
        "timestamp": "now"
    }

    call_outcomes.append(call_record)

    return f"Call outcome logged as: {outcome}"


@function_tool
async def schedule_followup(
    ctx: FunctionContext,
    contact_name: Annotated[str, "Name of the contact"],
    preferred_date: Annotated[str, "Preferred date for follow-up"],
    preferred_time: Annotated[str, "Preferred time for follow-up"],
    purpose: Annotated[str, "Purpose of the follow-up"]
) -> str:
    """Schedule a follow-up call or meeting"""
    logger.info(f"Scheduling follow-up for {contact_name} on {preferred_date} at {preferred_time}")

    return f"Follow-up scheduled for {contact_name} on {preferred_date} at {preferred_time}. Purpose: {purpose}. We'll send a calendar invite."


@function_tool
async def send_info_email(
    ctx: FunctionContext,
    email: Annotated[str, "Email address"],
    info_type: Annotated[str, "Type of information to send: pricing, features, case_study, or demo_link"]
) -> str:
    """Send follow-up information via email"""
    logger.info(f"Sending {info_type} information to {email}")

    info_descriptions = {
        "pricing": "pricing information and subscription options",
        "features": "detailed feature list and capabilities",
        "case_study": "customer success stories and case studies",
        "demo_link": "link to schedule a full product demo"
    }

    description = info_descriptions.get(info_type, "information")

    return f"I've sent {description} to {email}. Please check your inbox in the next few minutes."


@function_tool
async def answer_product_question(
    ctx: FunctionContext,
    question_topic: Annotated[str, "Topic of the question: pricing, features, integration, security, or other"]
) -> str:
    """Get detailed information to answer product questions"""
    logger.info(f"Answering product question about: {question_topic}")

    answers = {
        "pricing": "Mind Call Flow offers flexible pricing starting at $99/month for the Starter plan, $299/month for Professional, and custom Enterprise pricing. All plans include unlimited voice minutes and real-time transcription.",

        "features": "Key features include: AI-powered voice agents with customizable personalities, real-time conversation transcription, multi-agent support (scheduling, customer service, general assistant), integration with calendars and CRMs, and detailed analytics.",

        "integration": "We integrate with popular tools including Google Calendar, Salesforce, HubSpot, Slack, and have a REST API for custom integrations. We also support webhooks for real-time event notifications.",

        "security": "Mind Call Flow is SOC 2 compliant with end-to-end encryption for all conversations. We're GDPR and HIPAA compliant, with data residency options available for Enterprise customers.",

        "other": "Mind Call Flow is a next-generation voice AI platform that helps businesses automate customer interactions while maintaining a human touch. Perfect for customer service, scheduling, and outbound campaigns."
    }

    return answers.get(question_topic, answers["other"])


async def entrypoint(ctx: JobContext):
    """Main entry point for the agent"""
    logger.info(f"Connecting to room: {ctx.room.name}")
    await ctx.connect()

    # Load configuration - outbound calls should have user info in metadata
    config_data = ctx.job.metadata if hasattr(ctx.job, 'metadata') else {}
    config = AgentConfig(**config_data) if config_data else get_default_config()
    config.agent_type = "outbound"

    # Log outbound call details
    logger.info(f"Starting outbound call to {config.user_name} ({config.user_phone})")

    # Create agent session
    session = AgentSession(
        stt=deepgram.STT(model="nova-2"),
        llm=openai.LLM(model="gpt-4o-mini"),
        tts=cartesia.TTS(
            voice=config.get_voice_id("cartesia"),
            speed="normal" if config.style.pacing == "normal" else config.style.pacing,
        ),
    )

    # Start the session with function tools
    agent = OutboundCallerAgent(config)
    await session.start(
        agent=agent,
        room=ctx.room,
        function_tools=[log_call_outcome, schedule_followup, send_info_email, answer_product_question]
    )


if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            agent_name="outbound-caller-agent",
        )
    )
