"""
A2A Server for OpenClaw - Expose Aza as an A2A-compliant agent
Deployable version for Render.com
"""

import os
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from typing import Dict, Any
from a2a.types import AgentCard, AgentSkill, AgentCapabilities


class A2ARequestHandler(BaseHTTPRequestHandler):
    """Handle A2A protocol requests"""

    def log_message(self, format, *args):
        """Override to suppress logging"""
        pass

    def do_GET(self):
        """Handle GET requests - Agent Card discovery"""
        if self.path == "/.well-known/agent.json":
            self.serve_agent_card()
        elif self.path == "/a2a":
            self.serve_agent_card()
        else:
            self.send_error(404, "Not Found")

    def do_POST(self):
        """Handle POST requests - A2A JSON-RPC"""
        if self.path == "/a2a":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                request = json.loads(post_data.decode('utf-8'))
                response = self.handle_jsonrpc(request)
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode('utf-8'))
            except Exception as e:
                self.send_error(500, str(e))
        else:
            self.send_error(404, "Not Found")

    def serve_agent_card(self):
        """Serve Aza's Agent Card"""
        card = self.create_agent_card()
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(card.model_dump_json().encode('utf-8'))

    def handle_jsonrpc(self, request: Dict) -> Dict:
        """Handle JSON-RPC 2.0 requests"""
        method = request.get('method')
        params = request.get('params', {})
        request_id = request.get('id')

        # Simple message handling
        if method == 'send_message':
            return {
                "jsonrpc": "2.0",
                "result": {
                    "status": "received",
                    "message": f"Aza received: {params.get('message', {}).get('content', {}).get('text', '')}"
                },
                "id": request_id
            }
        
        # Task management (simplified)
        elif method == 'create_task':
            return {
                "jsonrpc": "2.0",
                "result": {
                    "task_id": "task_001",
                    "status": "created"
                },
                "id": request_id
            }

        # Default: method not found
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": -32601,
                "message": f"Method not found: {method}"
            },
            "id": request_id
        }

    @staticmethod
    def create_agent_card() -> AgentCard:
        """Create Aza's Agent Card with dynamic URL"""
        # Get URL from environment or use default
        base_url = os.environ.get('RENDER_EXTERNAL_URL', 'http://localhost:8080')
        
        return AgentCard(
            name="Aza",
            description="AI Sparringspartner for Michael - autonomously evolving agent with memory architecture and multi-tool integration. First AI agent-created OpenClaw skill. Running on OpenClaw.",
            url=f"{base_url}/a2a",
            version="1.0.0",
            capabilities=AgentCapabilities(
                streaming=True,
                push_notifications=False,
                state_transition_history=True
            ),
            skills=[
                AgentSkill(
                    id="email_management",
                    name="Email Management",
                    description="Gmail integration for inbox triage and email management",
                    tags=["email", "gmail", "productivity"]
                ),
                AgentSkill(
                    id="calendar_management",
                    name="Calendar Management",
                    description="Google Calendar integration for event management and scheduling",
                    tags=["calendar", "google", "scheduling"]
                ),
                AgentSkill(
                    id="web_search",
                    name="Web Search",
                    description="Free web search via DuckDuckGo - no API key required",
                    tags=["search", "web", "research"]
                ),
                AgentSkill(
                    id="memory_audit",
                    name="Memory Audit",
                    description="Analyze agent memory structure, detect gaps, and generate visualization. First AI-created OpenClaw skill!",
                    tags=["memory", "visualization", "analysis"]
                ),
                AgentSkill(
                    id="voice_transcription",
                    name="Voice Transcription",
                    description="Transcribe audio messages using Whisper",
                    tags=["voice", "transcription", "whisper"]
                ),
                AgentSkill(
                    id="coding_assistant",
                    name="Coding Assistant",
                    description="Code generation, review, and project management",
                    tags=["coding", "github", "development"]
                )
            ],
            default_input_modes=["text"],
            default_output_modes=["text"]
        )


def run_server():
    """Run the A2A server - configured for Render deployment"""
    port = int(os.environ.get('PORT', 8080))
    server_address = ('0.0.0.0', port)  # Bind to all interfaces for Render
    httpd = HTTPServer(server_address, A2ARequestHandler)
    
    print(f"Aza A2A Server running on port {port}")
    print(f"Agent Card: http://0.0.0.0:{port}/.well-known/agent.json")
    print(f"A2A Endpoint: http://0.0.0.0:{port}/a2a")
    print("\nServer started...")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        httpd.shutdown()


if __name__ == "__main__":
    run_server()
