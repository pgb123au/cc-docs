"""
Validate RetellAI Agent JSON File
"""
import json
import os
import sys
from collections import Counter

def validate_agent(file_path):
    """Comprehensive agent validation"""

    results = {
        'filename': os.path.basename(file_path),
        'issues': [],
        'warnings': [],
        'valid_checks': []
    }

    # Check 1: File exists
    if not os.path.exists(file_path):
        results['issues'].append(f"File not found: {file_path}")
        return results

    # Check 2: Valid JSON
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            agent_data = json.load(f)
        results['valid_checks'].append("Valid JSON structure")
    except json.JSONDecodeError as e:
        results['issues'].append(f"Invalid JSON: {str(e)}")
        return results

    # Check 3: agent_name matches filename
    base_filename = os.path.splitext(os.path.basename(file_path))[0]
    agent_name = agent_data.get('agent_name', '')

    if agent_name == base_filename:
        results['valid_checks'].append(f"agent_name matches filename: {agent_name}")
    else:
        results['issues'].append(f"agent_name mismatch:\n  Filename: {base_filename}\n  agent_name field: {agent_name}")

    # Check 4: _CC suffix present
    if base_filename.endswith('_CC'):
        results['valid_checks'].append("_CC suffix present in filename")
    else:
        results['warnings'].append("Missing _CC suffix in filename")

    if agent_name.endswith('_CC'):
        results['valid_checks'].append("_CC suffix present in agent_name")
    else:
        results['warnings'].append("Missing _CC suffix in agent_name field")

    # Check 5: Version format
    version = agent_data.get('version', '')
    if version.startswith('v') and '.' in version:
        results['valid_checks'].append(f"Version format valid: {version}")
    else:
        results['issues'].append(f"Invalid version format: {version} (should be vX.XXX)")

    # Check 6: Version sync
    if version in agent_name:
        results['valid_checks'].append(f"Version synced in agent_name: {version}")
    else:
        results['issues'].append(f"Version mismatch:\n  version field: {version}\n  agent_name: {agent_name}")

    # Check 7: Duplicate node IDs
    conversation_flow = agent_data.get('conversationFlow', {})
    nodes = conversation_flow.get('nodes', [])

    node_ids = [node.get('id') for node in nodes if node.get('id')]
    node_id_counts = Counter(node_ids)
    duplicates = {nid: count for nid, count in node_id_counts.items() if count > 1}

    if duplicates:
        results['issues'].append(f"Duplicate node IDs found: {list(duplicates.keys())}")
    else:
        results['valid_checks'].append(f"No duplicate node IDs ({len(node_ids)} unique nodes)")

    # Check 8: Extract all tool_ids
    tool_ids = set()
    for node in nodes:
        if node.get('tool_id'):
            tool_ids.add(node['tool_id'])

    results['tool_ids'] = sorted(list(tool_ids))
    results['valid_checks'].append(f"Found {len(tool_ids)} unique tool_ids")

    # Check 9: Orphaned edges
    node_id_set = set(node_ids)
    orphaned_edges = []

    for node in nodes:
        edges = node.get('edges', [])
        for edge in edges:
            dest_id = edge.get('destination_node_id')
            if dest_id and dest_id not in node_id_set:
                orphaned_edges.append({
                    'from_node': node.get('id', 'unknown'),
                    'edge_id': edge.get('id', 'unknown'),
                    'to_node': dest_id
                })

    if orphaned_edges:
        results['issues'].append(f"Orphaned edges found: {len(orphaned_edges)} edges point to non-existent nodes")
        results['orphaned_details'] = orphaned_edges
    else:
        results['valid_checks'].append("No orphaned edges")

    return results


def print_results(results):
    """Print validation results"""
    print("\n" + "="*70)
    print("RETELLAI AGENT VALIDATION REPORT")
    print("="*70)
    print(f"\nFile: {results['filename']}")
    print("-"*70)

    # Valid checks
    if results['valid_checks']:
        print("\n[PASSED CHECKS]")
        for check in results['valid_checks']:
            print(f"  OK {check}")

    # Warnings
    if results['warnings']:
        print("\n[WARNINGS]")
        for warning in results['warnings']:
            print(f"  ! {warning}")

    # Issues
    if results['issues']:
        print("\n[CRITICAL ISSUES]")
        for issue in results['issues']:
            print(f"  X {issue}")

    # Tool IDs
    if results.get('tool_ids'):
        print(f"\n[TOOL IDs FOUND] ({len(results['tool_ids'])} unique)")
        for tool_id in results['tool_ids']:
            print(f"  - {tool_id}")

    # Orphaned edges detail
    if results.get('orphaned_details'):
        print("\n[ORPHANED EDGE DETAILS]")
        for orphan in results['orphaned_details'][:10]:  # Show first 10
            print(f"  Edge {orphan['edge_id']}: {orphan['from_node']} -> {orphan['to_node']} (missing)")

    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Passed checks: {len(results['valid_checks'])}")
    print(f"Warnings: {len(results['warnings'])}")
    print(f"Critical issues: {len(results['issues'])}")

    if results['issues']:
        print("\nStatus: NEEDS FIXES - Not ready for import")
    elif results['warnings']:
        print("\nStatus: READY WITH WARNINGS - Safe to import")
    else:
        print("\nStatus: READY FOR IMPORT - All checks passed!")

    print("="*70 + "\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate_agent.py <path_to_agent.json>")
        sys.exit(1)

    file_path = sys.argv[1]
    results = validate_agent(file_path)
    print_results(results)
