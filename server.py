"""
A2A Server for OpenClaw - Expose Aza as an A2A-compliant agent.
Uses the official a2a-sdk server framework.
"""

import os
import json
import uvicorn
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse
from starlette.routing import Route
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


async def landing_page(request: Request) -> HTMLResponse:
    """Serve a human-friendly landing page for browser visitors."""
    base_url = os.environ.get("RENDER_EXTERNAL_URL", "http://localhost:8080")
    html = f"""\
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Aza - A2A Agent</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0a0a0f;
            color: #e0e0e0;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .container {{
            max-width: 640px;
            width: 100%;
            padding: 2rem;
        }}
        .status-dot {{
            display: inline-block;
            width: 10px;
            height: 10px;
            background: #22c55e;
            border-radius: 50%;
            margin-right: 8px;
            animation: pulse 2s ease-in-out infinite;
        }}
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.4; }}
        }}
        .header {{
            display: flex;
            align-items: center;
            gap: 1rem;
            margin-bottom: 0.5rem;
        }}
        .header h1 {{
            font-size: 2rem;
            font-weight: 700;
            background: linear-gradient(135deg, #60a5fa, #a78bfa);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .status-line {{
            display: flex;
            align-items: center;
            font-size: 0.9rem;
            color: #22c55e;
            margin-bottom: 2rem;
        }}
        .desc {{
            color: #9ca3af;
            line-height: 1.6;
            margin-bottom: 2rem;
        }}
        .card {{
            background: #14141f;
            border: 1px solid #2a2a3a;
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        }}
        .card h2 {{
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #6b7280;
            margin-bottom: 1rem;
        }}
        .skills-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 0.75rem;
        }}
        .skill {{
            background: #1a1a2a;
            border-radius: 8px;
            padding: 0.75rem;
        }}
        .skill-name {{
            font-weight: 600;
            font-size: 0.9rem;
            margin-bottom: 0.25rem;
        }}
        .skill-desc {{
            font-size: 0.75rem;
            color: #6b7280;
        }}
        .endpoints {{
            font-family: 'SF Mono', 'Fira Code', monospace;
            font-size: 0.8rem;
        }}
        .endpoint {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.5rem 0;
            border-bottom: 1px solid #1f1f2f;
        }}
        .endpoint:last-child {{ border-bottom: none; }}
        .method {{
            display: inline-block;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.7rem;
            font-weight: 700;
        }}
        .method-get {{ background: #164e3a; color: #34d399; }}
        .method-post {{ background: #3b2f1a; color: #fbbf24; }}
        .endpoint-path {{ color: #93c5fd; }}
        .meta {{
            display: flex;
            gap: 2rem;
            margin-bottom: 2rem;
        }}
        .meta-item {{
            font-size: 0.8rem;
        }}
        .meta-label {{ color: #6b7280; }}
        .meta-value {{ color: #d1d5db; font-weight: 600; }}
        .footer {{
            text-align: center;
            margin-top: 2rem;
            font-size: 0.8rem;
            color: #4b5563;
        }}
        .footer a {{ color: #60a5fa; text-decoration: none; }}
        .footer a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Aza</h1>
        </div>
        <div class="status-line">
            <span class="status-dot"></span> Online &mdash; A2A Protocol v0.3.0
        </div>
        <p class="desc">
            AI Sparringspartner auf OpenClaw. Autonom evolvierender Agent mit
            Memory-Architektur und Multi-Tool-Integration.
        </p>

        <div class="meta">
            <div class="meta-item">
                <span class="meta-label">Version</span><br>
                <span class="meta-value">1.0.0</span>
            </div>
            <div class="meta-item">
                <span class="meta-label">Provider</span><br>
                <span class="meta-value">OpenClaw / AzasAgent</span>
            </div>
            <div class="meta-item">
                <span class="meta-label">Transport</span><br>
                <span class="meta-value">JSON-RPC 2.0</span>
            </div>
        </div>

        <div class="card">
            <h2>Skills</h2>
            <div class="skills-grid">
                <div class="skill">
                    <div class="skill-name">Email Management</div>
                    <div class="skill-desc">Gmail Inbox-Triage</div>
                </div>
                <div class="skill">
                    <div class="skill-name">Calendar</div>
                    <div class="skill-desc">Google Calendar Events</div>
                </div>
                <div class="skill">
                    <div class="skill-name">Web Search</div>
                    <div class="skill-desc">DuckDuckGo (free)</div>
                </div>
                <div class="skill">
                    <div class="skill-name">Memory Audit</div>
                    <div class="skill-desc">Agent-Memory-Analyse</div>
                </div>
                <div class="skill">
                    <div class="skill-name">Voice Transcription</div>
                    <div class="skill-desc">Whisper STT</div>
                </div>
                <div class="skill">
                    <div class="skill-name">Coding Assistant</div>
                    <div class="skill-desc">Code & GitHub</div>
                </div>
            </div>
        </div>

        <div class="card">
            <h2>API Endpoints</h2>
            <div class="endpoints">
                <div class="endpoint">
                    <span><span class="method method-get">GET</span>
                    <span class="endpoint-path">/.well-known/agent-card.json</span></span>
                </div>
                <div class="endpoint">
                    <span><span class="method method-post">POST</span>
                    <span class="endpoint-path">/</span>
                    <span style="color:#6b7280"> &mdash; message/send, tasks/get, tasks/cancel</span></span>
                </div>
                <div class="endpoint">
                    <span><span class="method method-get">GET</span>
                    <span class="endpoint-path">/health</span></span>
                </div>
            </div>
        </div>

        <div class="footer">
            Powered by <a href="https://openclaw.ai">OpenClaw</a>
            &middot; <a href="https://github.com/AzasAgent/aza-a2a">GitHub</a>
            &middot; <a href="{base_url}/.well-known/agent-card.json">Agent Card</a>
        </div>
    </div>
</body>
</html>"""
    return HTMLResponse(html)


async def health_check(request: Request) -> JSONResponse:
    """Health check endpoint for Render and monitoring."""
    return JSONResponse({
        "status": "online",
        "agent": "Aza",
        "version": "1.0.0",
        "protocol": "A2A v0.3.0",
    })


async def agent_card_endpoint(request: Request) -> JSONResponse:
    """Serve the Agent Card at the new canonical endpoint."""
    agent_card = build_agent_card()
    return JSONResponse(agent_card.model_dump(exclude_none=True))


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

    app = a2a_app.build()

    # Add human-friendly GET routes alongside the A2A POST routes
    app.routes.insert(0, Route("/", landing_page, methods=["GET"]))
    app.routes.insert(1, Route("/health", health_check, methods=["GET"]))
    app.routes.insert(2, Route("/.well-known/agent-card.json", agent_card_endpoint, methods=["GET"]))

    return app


app = create_app()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"Aza A2A Server starting on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
