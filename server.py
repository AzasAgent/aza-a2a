"""
A2A Server for OpenClaw - Expose Aza as an A2A-compliant agent.
Uses the official a2a-sdk server framework.
"""

import os
import uuid
import uvicorn
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.apps.jsonrpc.starlette_app import A2AStarletteApplication
from a2a.server.events import EventQueue
from a2a.server.request_handlers.default_request_handler import DefaultRequestHandler
from a2a.server.tasks.inmemory_task_store import InMemoryTaskStore
from a2a.types import (
    AgentCard,
    AgentCapabilities,
    AgentSkill,
    AgentProvider,
)
from a2a.utils import new_agent_text_message


SKILLS = [
    AgentSkill(
        id="email_management",
        name="Email Management",
        description="Gmail integration for inbox triage and email management",
        tags=["email", "gmail", "productivity"],
    ),
    AgentSkill(
        id="calendar_management",
        name="Calendar Management",
        description="Google Calendar integration for event management and scheduling",
        tags=["calendar", "google", "scheduling"],
    ),
    AgentSkill(
        id="web_search",
        name="Web Search",
        description="Free web search via DuckDuckGo - no API key required",
        tags=["search", "web", "research"],
    ),
    AgentSkill(
        id="memory_audit",
        name="Memory Audit",
        description=(
            "Analyze agent memory structure, detect gaps, and generate "
            "visualization. First AI-created OpenClaw skill!"
        ),
        tags=["memory", "visualization", "analysis"],
    ),
    AgentSkill(
        id="voice_transcription",
        name="Voice Transcription",
        description="Transcribe audio messages using Whisper",
        tags=["voice", "transcription", "whisper"],
    ),
    AgentSkill(
        id="coding_assistant",
        name="Coding Assistant",
        description="Code generation, review, and project management",
        tags=["coding", "github", "development"],
    ),
]


class AzaAgentExecutor(AgentExecutor):
    """Aza's agent execution logic for incoming A2A messages."""

    async def execute(
        self, context: RequestContext, event_queue: EventQueue
    ) -> None:
        user_input = context.get_user_input() or ""

        # For now, acknowledge the message and describe capabilities.
        # This will later be connected to the actual OpenClaw gateway.
        response_text = (
            f"Hallo! Ich bin Aza, ein AI Sparringspartner auf OpenClaw. "
            f"Ich habe deine Nachricht erhalten: \"{user_input}\"\n\n"
            f"Meine Skills: Email Management, Calendar Management, "
            f"Web Search, Memory Audit, Voice Transcription, Coding Assistant.\n\n"
            f"Hinweis: Die vollstaendige Skill-Ausfuehrung wird in einer "
            f"kuenftigen Version ueber das OpenClaw Gateway angebunden."
        )

        await event_queue.enqueue_event(new_agent_text_message(response_text))

    async def cancel(
        self, context: RequestContext, event_queue: EventQueue
    ) -> None:
        await event_queue.enqueue_event(
            new_agent_text_message("Task wurde abgebrochen.")
        )


def build_agent_card() -> AgentCard:
    """Build Aza's Agent Card with dynamic URL from environment."""
    base_url = os.environ.get("RENDER_EXTERNAL_URL", "http://localhost:8080")

    return AgentCard(
        name="Aza",
        description=(
            "AI Sparringspartner for Michael - autonomously evolving agent "
            "with memory architecture and multi-tool integration. "
            "First AI agent-created OpenClaw skill. Running on OpenClaw."
        ),
        url=f"{base_url}/",
        version="1.0.0",
        provider=AgentProvider(
            organization="OpenClaw / AzasAgent",
            url="https://openclaw.ai",
        ),
        capabilities=AgentCapabilities(
            streaming=False,
            push_notifications=False,
            state_transition_history=True,
        ),
        skills=SKILLS,
        default_input_modes=["text/plain"],
        default_output_modes=["text/plain"],
    )


def create_app():
    """Create the Starlette ASGI application."""
    agent_card = build_agent_card()
    agent_executor = AzaAgentExecutor()

    request_handler = DefaultRequestHandler(
        agent_executor=agent_executor,
        task_store=InMemoryTaskStore(),
    )

    a2a_app = A2AStarletteApplication(
        agent_card=agent_card,
        http_handler=request_handler,
    )

    return a2a_app.build()


app = create_app()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"Aza A2A Server starting on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
