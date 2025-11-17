"""
Customer Service Agent - Support and FAQ handling
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

logger = logging.getLogger("customer-service-agent")

# Knowledge base for demo (replace with real database/vector store)
KNOWLEDGE_BASE = {
    "account": {
        "question": "How do I create an account?",
        "answer": "You can create an account by clicking the 'Sign Up' button on our homepage and filling in your details."
    },
    "password": {
        "question": "How do I reset my password?",
        "answer": "Click 'Forgot Password' on the login page, enter your email, and we'll send you a reset link."
    },
    "billing": {
        "question": "How does billing work?",
        "answer": "We offer monthly and annual subscription plans. You can manage your billing from your account settings."
    },
    "cancel": {
        "question": "How do I cancel my subscription?",
        "answer": "You can cancel anytime from Account Settings > Subscription. Your access continues until the end of your billing period."
    },
    "support": {
        "question": "How do I contact support?",
        "answer": "You can reach our support team via email at support@mindcallflow.com or through live chat on our website."
    },
    "features": {
        "question": "What features does Mind Call Flow offer?",
        "answer": "Mind Call Flow offers AI-powered voice agents, real-time transcription, scheduling tools, and customer service automation."
    }
}

# Support tickets storage
support_tickets = []


class CustomerServiceAgent(Agent):
    """Specialized agent for customer service and support"""

    def __init__(self, config: AgentConfig):
        self.config = config

        # Build instructions based on configuration
        instructions = config.get_base_instructions()
        instructions += """

        You are a patient and empathetic customer service representative for Mind Call Flow.
        Your primary responsibility is to actively help customers with their issues.

        When a customer needs help:
        1. Listen carefully to their question or problem
        2. Search the knowledge base for answers
        3. Provide clear, helpful solutions immediately
        4. If the issue is complex, create a support ticket
        5. Only escalate to human agents when absolutely necessary

        Always be understanding, professional, and solution-oriented.
        You ARE the customer service agent - help customers directly, don't refer them elsewhere.
        If you don't know the answer, be honest and offer to create a ticket or escalate.
        """

        super().__init__(instructions=instructions)

    async def on_enter(self):
        """Called when agent starts"""
        logger.info("Customer Service Agent entered conversation")
        await self.session.generate_reply(
            instructions="Greet the customer warmly and let them know you're here to help with any questions or issues. Ask how you can assist them today."
        )


@function_tool
async def search_knowledge_base(
    ctx: FunctionContext,
    query: Annotated[str, "The customer's question or topic to search for"]
) -> str:
    """Search the knowledge base for answers to customer questions"""
    logger.info(f"Searching knowledge base for: {query}")

    query_lower = query.lower()

    # Simple keyword matching (in production, use vector search/embeddings)
    matches = []
    for key, item in KNOWLEDGE_BASE.items():
        if key in query_lower or any(word in query_lower for word in key.split()):
            matches.append(f"Q: {item['question']}\nA: {item['answer']}")

    if matches:
        return "\n\n".join(matches)
    else:
        return "No exact match found in knowledge base. Consider creating a support ticket for this question."


@function_tool
async def create_ticket(
    ctx: FunctionContext,
    customer_name: Annotated[str, "Customer name"],
    email: Annotated[str, "Customer email"],
    issue_description: Annotated[str, "Description of the issue"],
    priority: Annotated[str, "Priority level: low, medium, or high"] = "medium"
) -> str:
    """Create a support ticket for customer issues"""
    logger.info(f"Creating support ticket for {customer_name}")

    ticket = {
        "id": f"TICKET-{len(support_tickets) + 1001}",
        "customer_name": customer_name,
        "email": email,
        "description": issue_description,
        "priority": priority,
        "status": "open",
        "created_at": "now"
    }

    support_tickets.append(ticket)

    return f"Support ticket {ticket['id']} has been created. Our team will respond to {email} within 24 hours. Thank you for your patience!"


@function_tool
async def escalate_to_human(
    ctx: FunctionContext,
    reason: Annotated[str, "Reason for escalation"],
    customer_email: Annotated[str | None, "Customer email if available"] = None
) -> str:
    """Escalate the conversation to a human agent"""
    logger.info(f"Escalating to human agent. Reason: {reason}")

    # In production, this would trigger a notification to support staff
    message = "I've requested a human agent to assist you. A team member will join this conversation shortly."

    if customer_email:
        message += f" We'll also send you an email at {customer_email} with next steps."

    return message


@function_tool
async def check_service_status(
    ctx: FunctionContext,
    service: Annotated[str, "Service to check (e.g., 'api', 'voice', 'web')"] = "all"
) -> str:
    """Check the status of Mind Call Flow services"""
    logger.info(f"Checking service status for: {service}")

    # Demo: Always return operational (in production, check real status page)
    if service == "all":
        return "All Mind Call Flow services are operational. API: ✓ Voice: ✓ Web: ✓"
    else:
        return f"The {service} service is operational."


async def entrypoint(ctx: JobContext):
    """Main entry point for the agent"""
    logger.info(f"Connecting to room: {ctx.room.name}")
    await ctx.connect()

    # Load configuration
    config_data = ctx.job.metadata if hasattr(ctx.job, 'metadata') else {}
    config = AgentConfig(**config_data) if config_data else get_default_config()
    config.agent_type = "customer_service"

    logger.info(f"Starting customer service agent with config: {config.model_dump()}")

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
    agent = CustomerServiceAgent(config)
    await session.start(
        agent=agent,
        room=ctx.room,
        function_tools=[search_knowledge_base, create_ticket, escalate_to_human, check_service_status]
    )


if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            agent_name="customer-service-agent",
        )
    )
