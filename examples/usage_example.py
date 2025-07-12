#!/usr/bin/env python3
"""
Example usage of the Plain.com MCP Server

This script demonstrates how to use the MCP server tools for common support operations.
"""

import asyncio
import json

# from plain_mcp_server.server import PlainMCPServer  # Not needed for this demo


async def demonstrate_support_workflow():
    """Demonstrate a typical AI-powered support workflow"""

    # This is a conceptual example - in practice, you'd use the MCP client
    # to interact with the server through the MCP protocol

    print("🤖 AI Support Assistant Workflow Demo")
    print("=" * 50)

    # Example 1: Fetch open tickets for daily triage
    print("\n1. 📋 Fetching open support tickets...")
    fetch_request = {"status": "TODO", "limit": 5, "include_resolved": False}
    print(f"   Request: {json.dumps(fetch_request, indent=2)}")

    # Example 2: Search for similar issues
    print("\n2. 🔍 Searching for similar issues...")
    search_request = {"query": "login authentication failed", "limit": 10}
    print(f"   Request: {json.dumps(search_request, indent=2)}")

    # Example 3: Get customer context
    print("\n3. 👤 Getting customer context...")
    customer_request = {"customer_id": "cust_example123"}
    print(f"   Request: {json.dumps(customer_request, indent=2)}")

    # Example 4: Add resolution note
    print("\n4. 📝 Adding resolution note...")
    note_request = {
        "thread_id": "th_example123",
        "content": (
            "Issue resolved: Reset user password and provided new login instructions. "
            "Customer confirmed access restored."
        ),
    }
    print(f"   Request: {json.dumps(note_request, indent=2)}")

    # Example 5: Update ticket status
    print("\n5. ✅ Updating ticket status...")
    status_request = {"thread_id": "th_example123", "status": "DONE"}
    print(f"   Request: {json.dumps(status_request, indent=2)}")

    # Example 6: Analyze patterns
    print("\n6. 📊 Analyzing thread patterns...")
    pattern_request = {"thread_id": "th_example123", "days_back": 30}
    print(f"   Request: {json.dumps(pattern_request, indent=2)}")

    print("\n✨ Workflow complete! AI assistant has:")
    print("   • Triaged open tickets")
    print("   • Found similar historical issues")
    print("   • Gathered customer context")
    print("   • Documented resolution")
    print("   • Updated ticket status")
    print("   • Analyzed patterns for insights")


def demonstrate_ai_prompts():
    """Show example AI prompts that would use these tools"""

    print("\n🎯 Example AI Assistant Prompts")
    print("=" * 50)

    prompts = [
        {
            "prompt": "Show me all urgent tickets that need immediate attention",
            "tools": ["fetch_threads"],
            "description": "Filters tickets by priority and status",
        },
        {
            "prompt": "Find tickets similar to th_12345 to understand if this is a recurring issue",
            "tools": ["analyze_thread_patterns", "search_threads"],
            "description": "Pattern analysis for issue identification",
        },
        {
            "prompt": (
                "Get the full context about customer cust_67890 before I respond to their ticket"
            ),
            "tools": ["get_customer_info", "fetch_threads"],
            "description": "Customer context gathering",
        },
        {
            "prompt": "Mark ticket th_98765 as resolved and add a note explaining the solution",
            "tools": ["update_thread_status", "add_thread_note"],
            "description": "Ticket resolution workflow",
        },
        {
            "prompt": "Search for all tickets about API rate limiting in the last 30 days",
            "tools": ["search_threads"],
            "description": "Historical issue analysis",
        },
    ]

    for i, example in enumerate(prompts, 1):
        print(f'\n{i}. 💬 "{example["prompt"]}"')
        print(f"   🔧 Tools used: {', '.join(example['tools'])}")
        print(f"   📝 Purpose: {example['description']}")


if __name__ == "__main__":
    print("Plain.com MCP Server - Usage Examples")
    print("=" * 50)

    # Run the demonstrations
    asyncio.run(demonstrate_support_workflow())
    demonstrate_ai_prompts()

    print("\n" + "=" * 50)
    print("To use these tools with an AI assistant:")
    print("1. Start the MCP server: python -m plain_mcp_server.server")
    print("2. Configure your MCP client with the server")
    print("3. Use natural language prompts like the examples above")
    print("4. The AI will automatically call the appropriate tools")
