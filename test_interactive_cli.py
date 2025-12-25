#!/usr/bin/env python3
"""
Interactive CLI Testing Tool for RAG Chatbot
Allows manual testing and debugging of queries, retrieval, and responses
Run: python test_interactive_cli.py
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import time

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.chat.rag_chain import RAGChain
from src.vectorstore.retriever import DocumentRetriever
from src.chat.llm_manager import LLMManager
from src.core.config import settings

# Color codes
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
CYAN = '\033[96m'
MAGENTA = '\033[95m'
RESET = '\033[0m'
BOLD = '\033[1m'
DIM = '\033[2m'

class InteractiveRAGTester:
    """Interactive CLI tool for RAG chatbot testing"""

    def __init__(self):
        self.rag_chain = RAGChain()
        self.retriever = DocumentRetriever()
        self.llm_manager = LLMManager()
        self.conversation_id = None
        self.current_user_role = "C-Level"
        self.current_user_id = 1
        self.debug_mode = False
        self.history = []

    def print_banner(self):
        """Print welcome banner"""
        print(f"\n{BOLD}{CYAN}")
        print("╔" + "═" * 68 + "╗")
        print("║" + " " * 68 + "║")
        print("║" + "  🚀 RAG CHATBOT INTERACTIVE TESTING TOOL".center(68) + "║")
        print("║" + "  Test queries, retrieve documents, and validate responses".center(68) + "║")
        print("║" + " " * 68 + "║")
        print("╚" + "═" * 68 + "╝")
        print(f"{RESET}\n")

        self.print_help()

    def print_help(self):
        """Print help menu"""
        print(f"{BOLD}{BLUE}Available Commands:{RESET}\n")
        print(f"  {CYAN}/ask <query>{RESET}                 Ask a question to the RAG system")
        print(f"  {CYAN}/retrieve <query>{RESET}            Retrieve documents for a query (no LLM)")
        print(f"  {CYAN}/debug-on{RESET}                    Turn on debug output")
        print(f"  {CYAN}/debug-off{RESET}                   Turn off debug output")
        print(f"  {CYAN}/role <role>{RESET}                 Set user role (C-Level, Finance, Employee, etc)")
        print(f"  {CYAN}/new-conversation{RESET}           Start a new conversation")
        print(f"  {CYAN}/history{RESET}                    Show conversation history")
        print(f"  {CYAN}/clear{RESET}                      Clear screen")
        print(f"  {CYAN}/help{RESET}                       Show this help menu")
        print(f"  {CYAN}/exit{RESET}                       Exit the tool\n")

    def prompt_user(self) -> str:
        """Get user input with custom prompt"""
        prompt = f"\n{BOLD}{GREEN}You:{RESET} "
        try:
            return input(prompt).strip()
        except EOFError:
            return "/exit"
        except KeyboardInterrupt:
            return "/exit"

    def print_section_header(self, title: str):
        """Print section header"""
        print(f"\n{BOLD}{CYAN}▼ {title}{RESET}")
        print(f"{CYAN}{'-' * 70}{RESET}\n")

    def print_success(self, text: str):
        """Print success"""
        print(f"{GREEN}✓{RESET} {text}")

    def print_error(self, text: str):
        """Print error"""
        print(f"{RED}✗{RESET} {text}")

    def print_warning(self, text: str):
        """Print warning"""
        print(f"{YELLOW}⚠{RESET} {text}")

    def print_info(self, text: str):
        """Print info"""
        print(f"{BLUE}ℹ{RESET} {text}")

    def print_debug(self, text: str):
        """Print debug info"""
        if self.debug_mode:
            print(f"{DIM}{MAGENTA}[DEBUG] {text}{RESET}")

    # ======================== COMMAND HANDLERS ========================

    def handle_ask(self, query: str):
        """Handle /ask command"""
        if not query:
            self.print_error("Please provide a query. Usage: /ask <query>")
            return

        self.print_section_header(f"Processing Query: {query}")

        try:
            # Show start time
            start_time = time.time()

            # Process query
            self.print_info("Retrieving documents...")
            response_data = self.rag_chain.process_query(
                question=query,
                user_id=self.current_user_id,
                user_role=self.current_user_role,
                conversation_id=self.conversation_id
            )

            elapsed = time.time() - start_time

            # Update conversation ID
            if self.conversation_id is None and "conversation_id" in response_data:
                self.conversation_id = response_data["conversation_id"]
                self.print_info(f"New conversation started (ID: {self.conversation_id})")

            # Extract response data
            answer = response_data.get("answer", "")
            sources = response_data.get("sources_used", [])
            confidence = response_data.get("confidence_score", 0)
            tokens_used = response_data.get("tokens_used", 0)
            context_messages = response_data.get("context_messages_used", 0)

            # Print response
            print(f"\n{BOLD}{CYAN}Assistant:{RESET}")
            print(f"\n{answer}\n")

            # Print metadata
            self.print_section_header("Response Metadata")
            self.print_info(f"Processing time: {elapsed:.2f}s")
            self.print_info(f"Confidence score: {confidence:.2%}")
            self.print_info(f"Tokens used: {tokens_used}")
            self.print_info(f"Context messages: {context_messages}")
            self.print_info(f"Sources retrieved: {len(sources)}")

            # Print sources
            if sources:
                self.print_section_header(f"Sources ({len(sources)})")
                for i, source in enumerate(sources[:5], 1):  # Show first 5
                    doc_name = source.get("document_id", "Unknown")
                    relevance = source.get("relevance_score", 0)
                    content = source.get("content", "")[:80]
                    print(f"  {i}. {doc_name} (relevance: {relevance:.2%})")
                    print(f"     {content}...\n")

                if len(sources) > 5:
                    self.print_info(f"... and {len(sources) - 5} more sources")
            else:
                self.print_warning("No sources found for this response (possible hallucination)")

            # Store in history
            self.history.append({
                "timestamp": datetime.now().isoformat(),
                "query": query,
                "answer": answer,
                "confidence": confidence,
                "sources": len(sources),
                "role": self.current_user_role
            })

            # Debug: Show augmented queries if debug mode
            if self.debug_mode and "augmented_queries" in response_data:
                self.print_section_header("Debug: Query Augmentation")
                for i, aug_query in enumerate(response_data.get("augmented_queries", []), 1):
                    print(f"  {i}. {aug_query}")

        except Exception as e:
            self.print_error(f"Failed to process query: {str(e)}")
            import traceback
            traceback.print_exc()

    def handle_retrieve(self, query: str):
        """Handle /retrieve command"""
        if not query:
            self.print_error("Please provide a query. Usage: /retrieve <query>")
            return

        self.print_section_header(f"Retrieving Documents for: {query}")

        try:
            # Create mock user
            mock_user = type('obj', (object,), {
                'id': self.current_user_id,
                'role': self.current_user_role
            })()

            # Retrieve documents
            results = self.retriever.retrieve_for_user(query, mock_user, top_k=8)

            if not results:
                self.print_warning("No documents retrieved for this query")
                return

            self.print_success(f"Retrieved {len(results)} documents")

            # Show each document
            for i, (doc, distance) in enumerate(results, 1):
                similarity = 1 - distance  # Convert distance to similarity
                content = doc.page_content
                metadata = doc.metadata

                print(f"\n{BOLD}Document {i}:{RESET}")
                print(f"  Similarity: {similarity:.3f} ({similarity:.2%})")
                print(f"  Metadata: {json.dumps(metadata, indent=2)}")
                print(f"  Content preview:")
                print(f"  {DIM}{content[:150]}...{RESET}")

        except Exception as e:
            self.print_error(f"Retrieval failed: {str(e)}")

    def handle_debug_toggle(self, on: bool):
        """Handle debug mode toggle"""
        self.debug_mode = on
        status = "enabled" if on else "disabled"
        self.print_info(f"Debug mode {status}")

    def handle_role_change(self, role: str):
        """Handle role change"""
        valid_roles = ["C-Level", "Finance", "Marketing", "HR", "Engineering", "Employee"]

        if role not in valid_roles:
            self.print_error(f"Invalid role. Valid roles: {', '.join(valid_roles)}")
            return

        self.current_user_role = role
        self.print_success(f"User role changed to: {role}")

    def handle_new_conversation(self):
        """Start a new conversation"""
        self.conversation_id = None
        self.print_success("New conversation started")

    def handle_history(self):
        """Show conversation history"""
        if not self.history:
            self.print_warning("No history yet")
            return

        self.print_section_header("Conversation History")

        for i, entry in enumerate(self.history, 1):
            timestamp = entry["timestamp"].split("T")[1][:8]  # HH:MM:SS
            query = entry["query"][:50]
            confidence = entry["confidence"]
            sources = entry["sources"]

            print(f"{i}. [{timestamp}] (Role: {entry['role']})")
            print(f"   Q: {query}...")
            print(f"   Confidence: {confidence:.2%} | Sources: {sources}\n")

    def handle_clear(self):
        """Clear screen"""
        os.system("cls" if os.name == "nt" else "clear")
        self.print_banner()

    # ======================== MAIN LOOP ========================

    def run(self):
        """Run interactive CLI"""
        self.print_banner()

        print(f"{BOLD}Settings:{RESET}")
        print(f"  User Role: {self.current_user_role}")
        print(f"  User ID: {self.current_user_id}")
        print(f"  Debug Mode: {self.debug_mode}\n")

        while True:
            try:
                user_input = self.prompt_user()

                if not user_input:
                    continue

                # Parse command
                if user_input.lower() == "/exit":
                    print(f"\n{BOLD}{GREEN}Thank you for testing! Goodbye.{RESET}\n")
                    break

                elif user_input.lower() == "/help":
                    self.print_help()

                elif user_input.lower() == "/clear":
                    self.handle_clear()

                elif user_input.lower() == "/debug-on":
                    self.handle_debug_toggle(True)

                elif user_input.lower() == "/debug-off":
                    self.handle_debug_toggle(False)

                elif user_input.lower() == "/new-conversation":
                    self.handle_new_conversation()

                elif user_input.lower() == "/history":
                    self.handle_history()

                elif user_input.startswith("/ask "):
                    query = user_input[5:].strip()
                    self.handle_ask(query)

                elif user_input.startswith("/retrieve "):
                    query = user_input[10:].strip()
                    self.handle_retrieve(query)

                elif user_input.startswith("/role "):
                    role = user_input[6:].strip()
                    self.handle_role_change(role)

                else:
                    # Treat as direct question (without /ask prefix)
                    self.handle_ask(user_input)

            except KeyboardInterrupt:
                print(f"\n{YELLOW}Interrupted. Type '/exit' to quit.{RESET}")
            except Exception as e:
                self.print_error(f"Unexpected error: {str(e)}")


def main():
    """Entry point"""
    try:
        tester = InteractiveRAGTester()
        tester.run()
    except Exception as e:
        print(f"\n{RED}Fatal error: {str(e)}{RESET}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
