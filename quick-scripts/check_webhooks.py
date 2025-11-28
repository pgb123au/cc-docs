"""
Check if all tool_ids in a RetellAI agent exist in the n8n webhook system
"""
import json
import csv
import sys
import os

def load_agent_tool_ids(agent_file):
    """Extract all tool_ids from agent JSON"""
    with open(agent_file, 'r', encoding='utf-8') as f:
        agent_data = json.load(f)

    conversation_flow = agent_data.get('conversationFlow', {})
    nodes = conversation_flow.get('nodes', [])

    tool_ids = set()
    for node in nodes:
        if node.get('tool_id'):
            tool_ids.add(node['tool_id'])

    return sorted(list(tool_ids))


def load_valid_webhooks(mapping_file):
    """Load valid tool_id mappings from JSON"""
    with open(mapping_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def check_tool_ids(agent_tool_ids, valid_webhooks):
    """Check which tool_ids are valid vs invalid"""
    valid = []
    invalid = []

    for tool_id in agent_tool_ids:
        if tool_id in valid_webhooks:
            valid.append({
                'tool_id': tool_id,
                'webhook_path': valid_webhooks[tool_id]['webhook_path'],
                'endpoint': valid_webhooks[tool_id]['endpoint'],
                'category': valid_webhooks[tool_id]['category']
            })
        else:
            invalid.append(tool_id)

    return valid, invalid


def suggest_fix(invalid_tool_id, valid_webhooks):
    """Suggest possible fixes for invalid tool_ids"""
    # Common mistakes
    suggestions = {
        'tool-log-error': 'Use tool-add-to-followup instead (log-error is deprecated)',
        'tool-faq-search': 'Use Knowledge Base instead (faq tools deprecated)',
        'tool-get-faq-answer': 'Use Knowledge Base instead',
    }

    if invalid_tool_id in suggestions:
        return suggestions[invalid_tool_id]

    # Try to find similar tool_ids
    invalid_part = invalid_tool_id.replace('tool-', '')
    for valid_id in valid_webhooks.keys():
        valid_part = valid_id.replace('tool-', '')
        if invalid_part in valid_part or valid_part in invalid_part:
            return f"Did you mean: {valid_id}?"

    return "No similar tool found - may need to be removed"


def print_report(agent_file, agent_tool_ids, valid_tools, invalid_tools, valid_webhooks):
    """Print comprehensive webhook validation report"""
    agent_name = os.path.basename(agent_file)

    print("\n" + "="*70)
    print("WEBHOOK VALIDATION REPORT")
    print("="*70)
    print(f"\nAgent: {agent_name}")
    print(f"Total tool_ids referenced: {len(agent_tool_ids)}")
    print("-"*70)

    # Valid tools
    if valid_tools:
        print(f"\n[VALID TOOLS] ({len(valid_tools)})")
        for tool in valid_tools:
            print(f"  OK {tool['tool_id']}")
            print(f"     -> Category: {tool['category']}")
            print(f"     -> Webhook: {tool['webhook_path']}")

    # Invalid tools
    if invalid_tools:
        print(f"\n[INVALID TOOLS] ({len(invalid_tools)})")
        for tool_id in invalid_tools:
            print(f"  X {tool_id}")
            suggestion = suggest_fix(tool_id, valid_webhooks)
            print(f"     -> {suggestion}")

    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Valid tools: {len(valid_tools)}/{len(agent_tool_ids)}")
    print(f"Invalid tools: {len(invalid_tools)}/{len(agent_tool_ids)}")

    if invalid_tools:
        print("\nStatus: NEEDS FIXES - Invalid tool_ids found")
        print("Action: Remove or replace invalid tools before import")
    else:
        print("\nStatus: ALL TOOLS VALID - Safe to import")

    print("="*70 + "\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python check_webhooks.py <path_to_agent.json>")
        sys.exit(1)

    agent_file = sys.argv[1]
    mapping_file = os.path.join(os.path.dirname(__file__), 'tool_id_mapping.json')

    # Load data
    agent_tool_ids = load_agent_tool_ids(agent_file)
    valid_webhooks = load_valid_webhooks(mapping_file)

    # Check validity
    valid_tools, invalid_tools = check_tool_ids(agent_tool_ids, valid_webhooks)

    # Print report
    print_report(agent_file, agent_tool_ids, valid_tools, invalid_tools, valid_webhooks)
