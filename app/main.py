"""Main entry point for the FA³AI multi-agent system."""
import os
import logging
from typing import Optional
from app.agents.financial_advisor_agent.agent import KnowledgeOrchestratorSystem
from app.config import settings

# Configure logging directly since utils is empty
logging.basicConfig(level=settings.log_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def main():
    """Main function to run the multi-agent system."""
    print("=" * 60)
    print("FA³AI - Financial Advisor Agentic Assistant")
    print("Multi-Agent System powered by Google ADK")
    print("=" * 60)
    print()
    
    # Load API Key from environment (handled by settings or .env)
    api_key = settings.google_api_key or os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        print(f"🔑 Authentication Error: Please make sure to add GOOGLE_API_KEY to .env")
        return
    
    print("✅ Gemini API key setup complete.")
    
    # Initialize orchestrator system
    print("🚀 Initializing multi-agent system...")
    print("   - Knowledge Orchestrator Agent")
    print("   - Knowledge Planner Agent")
    print("   - Knowledge Retriever Agent (RAG with ChromaDB)")
    print("   - Content Reviewer Agent (Compliance)")
    orchestrator = KnowledgeOrchestratorSystem(api_key=api_key)
    print("✅ System ready!")
    print()
    
    # Interactive loop
    print("Enter your queries (type 'exit' to quit, 'clear' to reset session):")
    print("-" * 60)
    
    while True:
        try:
            query = input("\n💬 You: ").strip()
            
            if not query:
                continue
            
            if query.lower() == "exit":
                print("\n👋 Goodbye!")
                break
            
            if query.lower() == "clear":
                orchestrator.clear_session()
                print("✅ Session cleared")
                continue
            
            # Process query (uses async internally)
            print("\n🤖 Processing with LLM Orchestrator Pattern...")
            print("   (Orchestrator will call sub-agents as tools)")
            result = orchestrator.process_query(query)
            
            if result["success"]:
                print(f"\n📝 Response:\n{result['response']}")
                
                # Show metadata
                metadata = result.get("metadata", {})
                print(f"\n📊 Session ID: {metadata.get('session_id', 'N/A')}")
            else:
                print(f"\n❌ Error: {result.get('error', 'Unknown error')}")
                print(f"Response: {result.get('response', '')}")
        
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            print(f"\n❌ Unexpected error: {e}")


if __name__ == "__main__":
    main()
