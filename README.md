# Mind Call Flow - LiveKit Voice Agents

This directory contains the Python-based LiveKit voice agents for Mind Call Flow.

## Agents

### 1. General Assistant (`general_assistant.py`)
Default conversational AI for general-purpose interactions.

**Capabilities:**
- General Q&A
- Conversation
- Information lookup

### 2. Scheduling Agent (`scheduling_agent.py`)
Specialized agent for appointment booking and calendar management.

**Function Tools:**
- `check_availability` - Check available time slots
- `book_appointment` - Book an appointment
- `send_confirmation` - Send email confirmations

### 3. Customer Service Agent (`customer_service.py`)
Support and FAQ handling with knowledge base.

**Function Tools:**
- `search_knowledge_base` - Search FAQs
- `create_ticket` - Create support tickets
- `escalate_to_human` - Escalate to human agent
- `check_service_status` - Check service status

### 4. Outbound Caller (`outbound_caller.py`)
Initiates outbound phone calls with personalized greetings.

**Function Tools:**
- `log_call_outcome` - Log call results
- `schedule_followup` - Schedule follow-up calls
- `send_info_email` - Send information via email
- `answer_product_question` - Answer product questions

## Setup

### 1. Create Virtual Environment

```bash
cd agent
python -m venv venv

# On Windows
venv\Scripts\activate

# On Mac/Linux
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your API keys:

```bash
cp .env.example .env
```

Required variables:
- `LIVEKIT_API_KEY` - From LiveKit Cloud
- `LIVEKIT_API_SECRET` - From LiveKit Cloud
- `LIVEKIT_URL` - Your LiveKit server URL
- `OPENAI_API_KEY` - OpenAI API key
- `DEEPGRAM_API_KEY` - Deepgram API key
- `CARTESIA_API_KEY` - Cartesia API key (optional)
- `TWILIO_ACCOUNT_SID` - Twilio account SID (for outbound calls)
- `TWILIO_AUTH_TOKEN` - Twilio auth token (for outbound calls)
- `TWILIO_PHONE_NUMBER` - Twilio phone number (for outbound calls)

## Running Agents

### Console Mode (for testing)

Test agents in your terminal:

```bash
# General Assistant
python general_assistant.py console

# Scheduling Agent
python scheduling_agent.py console

# Customer Service
python customer_service.py console

# Outbound Caller
python outbound_caller.py console
```

### Development Mode (with playground)

Run agent and test in browser:

```bash
# General Assistant
python general_assistant.py dev

# Scheduling Agent
python scheduling_agent.py dev
```

Then visit https://agents-playground.livekit.io/ to test

### Production Mode

Start agent worker to handle rooms:

```bash
# General Assistant
python general_assistant.py start

# Scheduling Agent
python scheduling_agent.py start

# Customer Service
python customer_service.py start

# Outbound Caller
python outbound_caller.py start
```

## Configuration

Agents can be configured via job metadata when starting a room. See `config.py` for available options:

```python
{
    "agent_type": "general",  # general, scheduling, customer_service, outbound
    "voice_gender": "female",  # male, female
    "style": {
        "tone": "friendly",  # formal, casual, friendly, empathetic
        "verbosity": "balanced",  # concise, balanced, detailed
        "pacing": "normal"  # slow, normal, fast
    },
    "user_name": "John",  # For outbound calls
    "user_phone": "+1234567890",  # For outbound calls
    "user_email": "john@example.com"  # For outbound calls
}
```

## Testing

Test individual agents in console mode:

```bash
python general_assistant.py console
```

Type messages and the agent will respond with voice (played in terminal).

## Deployment

For production deployment:

1. **Railway/Render:**
   - Create new service
   - Connect to GitHub repo
   - Set environment variables
   - Deploy `/agent` directory

2. **LiveKit Cloud Agents:**
   - Upload agent code to LiveKit Cloud
   - Configure auto-scaling
   - Monitor via dashboard

## Troubleshooting

### No audio output
- Check that your speakers are working
- Verify `CARTESIA_API_KEY` or `ELEVENLABS_API_KEY` is set

### Agent not responding
- Check LiveKit connection in logs
- Verify `LIVEKIT_URL` is correct
- Ensure `OPENAI_API_KEY` is valid

### Function tools not working
- Check function tool logs
- Verify tool parameters match expected types
- Test tools individually in console mode

## Development

To add new function tools:

1. Define the tool with `@function_tool` decorator
2. Add type annotations using `Annotated`
3. Add tool to `session.start()` function_tools list
4. Update agent instructions to mention the new capability

Example:

```python
@function_tool
async def my_new_tool(
    ctx: FunctionContext,
    param: Annotated[str, "Description of parameter"]
) -> str:
    """What this tool does"""
    # Implementation
    return "Result"
```

## License

MIT
