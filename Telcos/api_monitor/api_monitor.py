#!/usr/bin/env python3
"""
API Change Monitor
Monitors provider API documentation for changes and analyzes impact on n8n/RetellAI systems.
Uses Claude API for intelligent analysis and creates GitHub issues for actionable changes.
"""

import os
import sys
import json
import yaml
import hashlib
import difflib
import requests
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from bs4 import BeautifulSoup
import anthropic

# Script directory
SCRIPT_DIR = Path(__file__).parent
CONFIG_FILE = SCRIPT_DIR / "monitor_config.yaml"
SNAPSHOTS_DIR = SCRIPT_DIR / "page_snapshots"
CONTEXT_FILE = SCRIPT_DIR / "analysis_context.md"
CREDENTIALS_FILE = SCRIPT_DIR.parent / ".credentials"

# Ensure snapshots directory exists
SNAPSHOTS_DIR.mkdir(exist_ok=True)


@dataclass
class PageChange:
    """Represents a detected change in an API page"""
    provider: str
    page_name: str
    url: str
    previous_hash: str
    current_hash: str
    diff_summary: str
    full_diff: str
    detected_at: str
    priority: str = "medium"


@dataclass
class AnalysisResult:
    """Result of Claude's analysis of API changes"""
    provider: str
    summary: str
    impact_level: str  # critical, high, medium, low
    affected_systems: List[str]
    recommendations: List[str]
    action_required: bool
    github_issue_title: Optional[str] = None
    github_issue_body: Optional[str] = None


def load_config() -> dict:
    """Load configuration from YAML file"""
    with open(CONFIG_FILE, 'r') as f:
        return yaml.safe_load(f)


def load_credentials() -> dict:
    """Load API credentials from .credentials file"""
    creds = {}
    if CREDENTIALS_FILE.exists():
        with open(CREDENTIALS_FILE, 'r') as f:
            for line in f:
                line = line.strip()
                if '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    creds[key.strip()] = value.strip()

    # Also check environment variables
    for key in ['ANTHROPIC_API_KEY', 'CLAUDE_API_KEY', 'GITHUB_TOKEN']:
        if key not in creds and os.getenv(key):
            creds[key] = os.getenv(key)

    return creds


def load_context() -> str:
    """Load system context for analysis"""
    if CONTEXT_FILE.exists():
        return CONTEXT_FILE.read_text()
    return ""


def fetch_page_content(url: str, selector: str = "main") -> Tuple[str, str]:
    """
    Fetch a page and extract relevant content.
    Returns (content_text, content_hash)
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    }

    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Remove script and style elements
        for element in soup(['script', 'style', 'nav', 'footer', 'header']):
            element.decompose()

        # Try to find content using selector
        content = None
        for sel in selector.split(','):
            sel = sel.strip()
            if sel.startswith('.'):
                content = soup.find(class_=sel[1:])
            elif sel.startswith('#'):
                content = soup.find(id=sel[1:])
            else:
                content = soup.find(sel)
            if content:
                break

        # Fallback to body if no content found
        if not content:
            content = soup.find('body') or soup

        # Extract text and normalize
        text = content.get_text(separator='\n', strip=True)

        # Normalize whitespace
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        normalized_text = '\n'.join(lines)

        # Calculate hash
        content_hash = hashlib.sha256(normalized_text.encode()).hexdigest()[:16]

        return normalized_text, content_hash

    except Exception as e:
        print(f"  Error fetching {url}: {e}")
        return "", ""


def get_snapshot_path(provider: str, page_name: str) -> Path:
    """Get the path for a page snapshot file"""
    safe_name = page_name.replace(' ', '_').lower()
    return SNAPSHOTS_DIR / f"{provider}_{safe_name}.json"


def load_snapshot(provider: str, page_name: str) -> Optional[dict]:
    """Load previous snapshot for a page"""
    path = get_snapshot_path(provider, page_name)
    if path.exists():
        with open(path, 'r') as f:
            return json.load(f)
    return None


def save_snapshot(provider: str, page_name: str, content: str, content_hash: str, url: str):
    """Save current page snapshot"""
    path = get_snapshot_path(provider, page_name)
    snapshot = {
        'provider': provider,
        'page_name': page_name,
        'url': url,
        'content': content,
        'hash': content_hash,
        'captured_at': datetime.now().isoformat()
    }
    with open(path, 'w') as f:
        json.dump(snapshot, f, indent=2)


def generate_diff(old_content: str, new_content: str) -> Tuple[str, str]:
    """
    Generate diff between old and new content.
    Returns (summary, full_diff)
    """
    old_lines = old_content.split('\n')
    new_lines = new_content.split('\n')

    diff = list(difflib.unified_diff(old_lines, new_lines, lineterm='', n=3))

    if not diff:
        return "", ""

    full_diff = '\n'.join(diff)

    # Generate summary
    additions = sum(1 for line in diff if line.startswith('+') and not line.startswith('+++'))
    deletions = sum(1 for line in diff if line.startswith('-') and not line.startswith('---'))

    summary = f"{additions} lines added, {deletions} lines removed"

    return summary, full_diff


def check_for_changes(config: dict) -> List[PageChange]:
    """Check all configured pages for changes"""
    changes = []

    for provider_key, provider_config in config.get('providers', {}).items():
        provider_name = provider_config.get('name', provider_key)
        print(f"\nChecking {provider_name}...")

        for page in provider_config.get('pages', []):
            page_name = page.get('name', 'Unknown')
            url = page.get('url')
            selector = page.get('selector', 'main')
            priority = page.get('priority', 'medium')

            print(f"  - {page_name}...", end=' ')

            # Fetch current content
            current_content, current_hash = fetch_page_content(url, selector)

            if not current_content:
                print("FAILED")
                continue

            # Load previous snapshot
            snapshot = load_snapshot(provider_key, page_name)

            if snapshot:
                previous_hash = snapshot.get('hash', '')
                previous_content = snapshot.get('content', '')

                if current_hash != previous_hash:
                    print("CHANGED!")
                    diff_summary, full_diff = generate_diff(previous_content, current_content)

                    changes.append(PageChange(
                        provider=provider_name,
                        page_name=page_name,
                        url=url,
                        previous_hash=previous_hash,
                        current_hash=current_hash,
                        diff_summary=diff_summary,
                        full_diff=full_diff,
                        detected_at=datetime.now().isoformat(),
                        priority=priority
                    ))
                else:
                    print("unchanged")
            else:
                print("NEW (first snapshot)")

            # Save current snapshot
            save_snapshot(provider_key, page_name, current_content, current_hash, url)

    return changes


def analyze_changes_with_claude(changes: List[PageChange], config: dict, credentials: dict) -> List[AnalysisResult]:
    """Use Claude to analyze the detected changes"""
    results = []

    api_key = credentials.get('ANTHROPIC_API_KEY') or credentials.get('CLAUDE_API_KEY')
    if not api_key:
        print("\nWarning: No Claude API key found. Skipping AI analysis.")
        # Return basic results without AI analysis
        for change in changes:
            results.append(AnalysisResult(
                provider=change.provider,
                summary=f"Changes detected in {change.page_name}: {change.diff_summary}",
                impact_level="unknown",
                affected_systems=["Requires manual review"],
                recommendations=["Review changes manually"],
                action_required=True,
                github_issue_title=f"[API Change] {change.provider}: {change.page_name}",
                github_issue_body=f"Changes detected:\n\n{change.diff_summary}\n\nURL: {change.url}"
            ))
        return results

    # Load system context
    context = load_context()

    # Initialize Claude client
    client = anthropic.Anthropic(api_key=api_key)

    # Group changes by provider for batch analysis
    provider_changes = {}
    for change in changes:
        if change.provider not in provider_changes:
            provider_changes[change.provider] = []
        provider_changes[change.provider].append(change)

    for provider, provider_change_list in provider_changes.items():
        # Build prompt for analysis
        changes_text = ""
        for change in provider_change_list:
            changes_text += f"\n### {change.page_name}\n"
            changes_text += f"URL: {change.url}\n"
            changes_text += f"Priority: {change.priority}\n"
            changes_text += f"Summary: {change.diff_summary}\n"
            changes_text += f"Diff:\n```\n{change.full_diff[:3000]}\n```\n"  # Limit diff size

        prompt = f"""Analyze these API documentation changes for {provider} and assess their impact on our system.

## System Context
{context}

## Detected Changes
{changes_text}

## Your Task
1. Summarize what changed in plain English
2. Assess the impact level (critical/high/medium/low) based on:
   - Does this affect features we currently use?
   - Does this enable new capabilities we need?
   - Is there a deprecation or breaking change?
3. List which systems are affected (n8n webhooks, RetellAI agents, telco sync, etc.)
4. Provide specific recommendations for action
5. If action is required, suggest a GitHub issue title and body

Respond in JSON format:
{{
    "summary": "Plain English summary of what changed",
    "impact_level": "critical|high|medium|low",
    "affected_systems": ["system1", "system2"],
    "recommendations": ["recommendation 1", "recommendation 2"],
    "action_required": true|false,
    "github_issue_title": "Title if action required, null otherwise",
    "github_issue_body": "Issue body if action required, null otherwise"
}}"""

        try:
            response = client.messages.create(
                model=config.get('claude', {}).get('model', 'claude-sonnet-4-20250514'),
                max_tokens=config.get('claude', {}).get('max_tokens', 4000),
                messages=[{"role": "user", "content": prompt}]
            )

            # Parse response
            response_text = response.content[0].text

            # Extract JSON from response
            import re
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                analysis = json.loads(json_match.group())
                results.append(AnalysisResult(
                    provider=provider,
                    summary=analysis.get('summary', 'Analysis complete'),
                    impact_level=analysis.get('impact_level', 'medium'),
                    affected_systems=analysis.get('affected_systems', []),
                    recommendations=analysis.get('recommendations', []),
                    action_required=analysis.get('action_required', False),
                    github_issue_title=analysis.get('github_issue_title'),
                    github_issue_body=analysis.get('github_issue_body')
                ))
            else:
                print(f"  Warning: Could not parse Claude response for {provider}")

        except Exception as e:
            print(f"  Error analyzing {provider} changes: {e}")
            results.append(AnalysisResult(
                provider=provider,
                summary=f"Error during analysis: {e}",
                impact_level="unknown",
                affected_systems=[],
                recommendations=["Manual review required"],
                action_required=True
            ))

    return results


def create_github_issue(title: str, body: str, credentials: dict, config: dict) -> Optional[str]:
    """Create a GitHub issue for actionable changes"""
    token = credentials.get('GITHUB_TOKEN')
    if not token:
        print("  Warning: No GitHub token found. Skipping issue creation.")
        return None

    repo = config.get('settings', {}).get('github_repo', '')
    if not repo:
        print("  Warning: No GitHub repo configured. Skipping issue creation.")
        return None

    try:
        url = f"https://api.github.com/repos/{repo}/issues"
        headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        data = {
            'title': title,
            'body': body,
            'labels': ['api-change', 'automated']
        }

        response = requests.post(url, headers=headers, json=data, timeout=30)

        if response.status_code == 201:
            issue_url = response.json().get('html_url')
            print(f"  Created GitHub issue: {issue_url}")
            return issue_url
        else:
            print(f"  Failed to create GitHub issue: {response.status_code}")
            return None

    except Exception as e:
        print(f"  Error creating GitHub issue: {e}")
        return None


def send_email_notification(changes: List[PageChange], analyses: List[AnalysisResult],
                           config: dict, github_issues: List[str]):
    """Send email notification about changes via n8n webhook"""
    webhook_url = config.get('settings', {}).get('webhook_url')
    email = config.get('settings', {}).get('email_recipient')

    if not webhook_url:
        print("\nNo webhook URL configured for email notifications.")
        return

    # Build email content
    subject = f"API Changes Detected - {datetime.now().strftime('%Y-%m-%d')}"

    body_html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
            h2 {{ color: #2980b9; margin-top: 30px; }}
            h3 {{ color: #27ae60; }}
            .critical {{ color: #e74c3c; font-weight: bold; }}
            .high {{ color: #e67e22; font-weight: bold; }}
            .medium {{ color: #f39c12; }}
            .low {{ color: #95a5a6; }}
            .change-box {{ background: #f8f9fa; border-left: 4px solid #3498db; padding: 15px; margin: 15px 0; }}
            .recommendation {{ background: #e8f6e8; padding: 10px; margin: 5px 0; border-radius: 4px; }}
            .action-required {{ background: #ffeaa7; padding: 15px; border-radius: 4px; margin: 20px 0; }}
            code {{ background: #f4f4f4; padding: 2px 6px; border-radius: 3px; }}
            a {{ color: #3498db; }}
        </style>
    </head>
    <body>
        <h1>API Documentation Changes Detected</h1>
        <p>The following changes were detected in provider API documentation that may affect your n8n and RetellAI systems.</p>
    """

    # Add analysis results
    for analysis in analyses:
        impact_class = analysis.impact_level.lower()
        body_html += f"""
        <h2>{analysis.provider}</h2>
        <p><strong>Impact Level:</strong> <span class="{impact_class}">{analysis.impact_level.upper()}</span></p>

        <div class="change-box">
            <h3>Summary</h3>
            <p>{analysis.summary}</p>
        </div>

        <h3>Affected Systems</h3>
        <ul>
        """
        for system in analysis.affected_systems:
            body_html += f"<li>{system}</li>"
        body_html += "</ul>"

        if analysis.recommendations:
            body_html += "<h3>Recommendations</h3>"
            for rec in analysis.recommendations:
                body_html += f'<div class="recommendation">{rec}</div>'

        if analysis.action_required:
            body_html += f"""
            <div class="action-required">
                <strong>Action Required!</strong> This change needs attention.
            </div>
            """

    # Add GitHub issues created
    if github_issues:
        body_html += "<h2>GitHub Issues Created</h2><ul>"
        for issue_url in github_issues:
            if issue_url:
                body_html += f'<li><a href="{issue_url}">{issue_url}</a></li>'
        body_html += "</ul>"

    # Add raw changes section
    body_html += "<h2>Raw Changes</h2>"
    for change in changes:
        body_html += f"""
        <div class="change-box">
            <strong>{change.provider} - {change.page_name}</strong><br>
            URL: <a href="{change.url}">{change.url}</a><br>
            Changes: {change.diff_summary}
        </div>
        """

    body_html += f"""
        <hr>
        <p style="color: #666; font-size: 12px;">
            Generated by API Change Monitor at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>
            This is an automated email from the Telco monitoring system.
        </p>
    </body>
    </html>
    """

    # Send via webhook
    try:
        payload = {
            'to': email,
            'subject': subject,
            'body_html': body_html,
            'source': 'api_monitor',
            'timestamp': datetime.now().isoformat(),
            'change_count': len(changes),
            'action_required': any(a.action_required for a in analyses)
        }

        response = requests.post(webhook_url, json=payload, timeout=30)

        if response.status_code == 200:
            print(f"\nEmail notification sent to {email}")
        else:
            print(f"\nFailed to send email: {response.status_code}")

    except Exception as e:
        print(f"\nError sending email notification: {e}")


def main():
    """Main entry point"""
    print("=" * 60)
    print("API CHANGE MONITOR")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # Load configuration
    print("\nLoading configuration...")
    config = load_config()
    credentials = load_credentials()

    # Check for changes
    print("\nChecking API documentation pages...")
    changes = check_for_changes(config)

    if not changes:
        print("\n" + "=" * 60)
        print("No changes detected. All pages unchanged.")
        print("=" * 60)
        return 0

    print(f"\n{len(changes)} change(s) detected!")

    # Analyze changes with Claude
    print("\nAnalyzing changes with Claude...")
    analyses = analyze_changes_with_claude(changes, config, credentials)

    # Create GitHub issues for actionable changes
    print("\nProcessing GitHub issues...")
    github_issues = []
    for analysis in analyses:
        if analysis.action_required and analysis.github_issue_title:
            issue_url = create_github_issue(
                analysis.github_issue_title,
                analysis.github_issue_body or "",
                credentials,
                config
            )
            if issue_url:
                github_issues.append(issue_url)

    # Send email notification
    print("\nSending email notification...")
    send_email_notification(changes, analyses, config, github_issues)

    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Pages checked: {sum(len(p.get('pages', [])) for p in config.get('providers', {}).values())}")
    print(f"Changes detected: {len(changes)}")
    print(f"Analyses completed: {len(analyses)}")
    print(f"GitHub issues created: {len([i for i in github_issues if i])}")

    action_required = any(a.action_required for a in analyses)
    if action_required:
        print("\n⚠️  ACTION REQUIRED - Review the changes and GitHub issues")
    else:
        print("\n✓ No immediate action required")

    return 1 if action_required else 0


if __name__ == "__main__":
    sys.exit(main())
