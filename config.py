"""
Agent configuration module for voice and conversational style settings.
"""
import os
from typing import Literal
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

# Voice gender to TTS voice ID mapping
# Cartesia Sonic voices
CARTESIA_VOICES = {
    "male": "a0e99841-438c-4a64-b679-ae501e7d6091",  # Helpful male voice
    "female": "79a125e8-cd45-4c13-8a67-188112f4dd22",  # Friendly female voice
}

# ElevenLabs voices (if using ElevenLabs instead)
ELEVENLABS_VOICES = {
    "male": "pNInz6obpgDQGcFmaJgB",  # Adam voice
    "female": "EXAVITQu4vr4xnSDxMaL",  # Bella voice
}

class ConversationalStyle(BaseModel):
    """Conversational style configuration"""
    tone: Literal["formal", "casual", "friendly", "empathetic"] = "friendly"
    verbosity: Literal["concise", "balanced", "detailed"] = "balanced"
    pacing: Literal["slow", "normal", "fast"] = "normal"

    def get_instruction_modifiers(self) -> str:
        """Generate instruction text based on style settings"""
        modifiers = []

        # Tone modifiers
        if self.tone == "formal":
            modifiers.append("Maintain a professional and formal tone.")
        elif self.tone == "casual":
            modifiers.append("Use a casual, conversational tone.")
        elif self.tone == "friendly":
            modifiers.append("Be warm, friendly, and approachable.")
        elif self.tone == "empathetic":
            modifiers.append("Show empathy and understanding. Be supportive.")

        # Verbosity modifiers
        if self.verbosity == "concise":
            modifiers.append("Keep responses brief and to the point (1-2 sentences).")
        elif self.verbosity == "balanced":
            modifiers.append("Provide clear but concise responses (2-3 sentences).")
        elif self.verbosity == "detailed":
            modifiers.append("Give thorough, detailed explanations.")

        # Pacing modifiers
        if self.pacing == "slow":
            modifiers.append("Speak slowly and clearly. Pause between thoughts.")
        elif self.pacing == "normal":
            modifiers.append("Speak at a natural, conversational pace.")
        elif self.pacing == "fast":
            modifiers.append("Speak energetically and efficiently.")

        return " ".join(modifiers)

class AgentConfig(BaseModel):
    """Complete agent configuration"""
    agent_type: Literal["general", "scheduling", "customer_service", "outbound"] = "general"
    voice_gender: Literal["male", "female"] = "female"
    style: ConversationalStyle = ConversationalStyle()
    user_name: str | None = None  # For personalized outbound calls
    user_phone: str | None = None
    user_email: str | None = None

    def get_voice_id(self, tts_provider: str = "cartesia") -> str:
        """Get the voice ID for the configured gender and TTS provider"""
        if tts_provider == "cartesia":
            return CARTESIA_VOICES[self.voice_gender]
        elif tts_provider == "elevenlabs":
            return ELEVENLABS_VOICES[self.voice_gender]
        else:
            return CARTESIA_VOICES[self.voice_gender]

    def get_stt_model(self) -> str:
        """Get the speech-to-text model"""
        return "deepgram/nova-2"

    def get_llm_model(self) -> str:
        """Get the language model"""
        return "openai/gpt-4o-mini"

    def get_base_instructions(self) -> str:
        """Get base instructions that apply to all agent types"""
        base = "You are a helpful AI voice assistant. "
        base += self.style.get_instruction_modifiers()
        return base

# Default configuration
def get_default_config() -> AgentConfig:
    """Get default agent configuration from environment variables"""
    return AgentConfig(
        agent_type=os.getenv("DEFAULT_AGENT_TYPE", "general"),
        voice_gender=os.getenv("DEFAULT_VOICE_GENDER", "female"),
        style=ConversationalStyle(
            tone=os.getenv("DEFAULT_TONE", "friendly"),
            verbosity=os.getenv("DEFAULT_VERBOSITY", "balanced"),
            pacing=os.getenv("DEFAULT_PACING", "normal"),
        )
    )
