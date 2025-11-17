"""
Scheduling Agent - Appointment booking and calendar management
"""
import logging
from datetime import datetime, timedelta
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

logger = logging.getLogger("scheduling-agent")

# In-memory storage for demo purposes (replace with real database)
appointments = []


class SchedulingAgent(Agent):
    """Specialized agent for scheduling appointments"""

    def __init__(self, config: AgentConfig):
        self.config = config

        # Build instructions based on configuration
        instructions = config.get_base_instructions()
        instructions += """

        You are a professional scheduling assistant for Mind Call Flow.
        Your role is to help users:
        - Check available time slots
        - Book appointments
        - Confirm appointment details
        - Send confirmation emails

        Be professional, efficient, and helpful. Always confirm details before booking.
        Collect: name, date, time, and purpose of appointment.
        """

        super().__init__(instructions=instructions)

    async def on_enter(self):
        """Called when agent starts"""
        logger.info("Scheduling Agent entered conversation")
        await self.session.generate_reply(
            instructions="Greet the user professionally and let them know you're here to help with scheduling appointments. Ask how you can assist them."
        )


@function_tool
async def check_availability(
    ctx: FunctionContext,
    date: Annotated[str, "Date in YYYY-MM-DD format"],
    time_preference: Annotated[str, "Preferred time of day: morning, afternoon, or evening"] = "any"
) -> str:
    """Check available appointment slots for a given date"""
    logger.info(f"Checking availability for {date}, preference: {time_preference}")

    try:
        requested_date = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return "Invalid date format. Please provide date in YYYY-MM-DD format."

    # Simple demo logic - generate available slots
    available_slots = []

    if time_preference in ["morning", "any"]:
        available_slots.extend(["9:00 AM", "10:00 AM", "11:00 AM"])

    if time_preference in ["afternoon", "any"]:
        available_slots.extend(["1:00 PM", "2:00 PM", "3:00 PM"])

    if time_preference in ["evening", "any"]:
        available_slots.extend(["5:00 PM", "6:00 PM", "7:00 PM"])

    if not available_slots:
        return f"No slots available for {date}."

    return f"Available time slots for {date}: {', '.join(available_slots)}"


@function_tool
async def book_appointment(
    ctx: FunctionContext,
    name: Annotated[str, "Customer name"],
    date: Annotated[str, "Appointment date in YYYY-MM-DD format"],
    time: Annotated[str, "Appointment time (e.g., '2:00 PM')"],
    purpose: Annotated[str, "Purpose of appointment"],
    email: Annotated[str | None, "Customer email for confirmation"] = None
) -> str:
    """Book an appointment"""
    logger.info(f"Booking appointment for {name} on {date} at {time}")

    try:
        appointment_date = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return "Invalid date format. Could not book appointment."

    # Create appointment record
    appointment = {
        "id": len(appointments) + 1,
        "name": name,
        "date": date,
        "time": time,
        "purpose": purpose,
        "email": email,
        "created_at": datetime.now().isoformat()
    }

    appointments.append(appointment)

    confirmation = f"Appointment confirmed for {name} on {date} at {time}. Purpose: {purpose}."
    if email:
        confirmation += f" A confirmation email will be sent to {email}."

    return confirmation


@function_tool
async def send_confirmation(
    ctx: FunctionContext,
    email: Annotated[str, "Email address"],
    appointment_details: Annotated[str, "Appointment details to include"]
) -> str:
    """Send appointment confirmation email"""
    logger.info(f"Sending confirmation email to {email}")

    # Demo: Just log it (replace with real email service)
    return f"Confirmation email sent to {email} with the appointment details."


async def entrypoint(ctx: JobContext):
    """Main entry point for the agent"""
    logger.info(f"Connecting to room: {ctx.room.name}")
    await ctx.connect()

    # Load configuration
    config_data = ctx.job.metadata if hasattr(ctx.job, 'metadata') else {}
    config = AgentConfig(**config_data) if config_data else get_default_config()
    config.agent_type = "scheduling"

    logger.info(f"Starting scheduling agent with config: {config.model_dump()}")

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
    agent = SchedulingAgent(config)
    await session.start(
        agent=agent,
        room=ctx.room,
        function_tools=[check_availability, book_appointment, send_confirmation]
    )


if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            agent_name="scheduling-agent",
        )
    )
