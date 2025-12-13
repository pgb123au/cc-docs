# -*- coding: utf-8 -*-
"""Telemarketing Analysis Library for Telco Warehouse

Adapted from telemarketing_analysis_library.py for database integration.
Includes regex patterns aligned with Master Telemarketing Classification Taxonomy.

Usage:
    from telemarketing_taxonomy import TelemarketingTaxonomy

    flags = TelemarketingTaxonomy.analyze_transcript(transcript_text)
    # Returns: {'DNC_REQUEST': True, 'RETIRED': True, ...}

    classification = TelemarketingTaxonomy.get_crm_classification(flags)
    # Returns: {'is_dnc': True, 'dnc_reason': 'explicit_request', 'contact_status': 'active', ...}
"""

import re
from typing import Dict, List, Optional, Any


class TelemarketingTaxonomy:
    """
    Comprehensive taxonomy for classifying telemarketing call transcripts.
    Aligned with Master Telemarketing Classification Taxonomy for CRM actions.
    """

    # ==========================================
    # 1. COMPLIANCE & LEGAL RISK (CRITICAL)
    # ==========================================
    # Priority 1 - These flags require immediate action

    COMPLIANCE_FLAGS = {
        "DNC_REQUEST": {
            "description": "Explicit request to stop calling or remove from list.",
            "crm_action": "Add to internal suppression list. Stop calling immediately.",
            "priority": 1,
            "patterns": [
                r"\b(take|remove|delete)\s+(me|my\s+number)\s+(off|from)\s+(your|the)\s+(list|database)",
                r"\b(stop|quit)\s+calling\s+(me|us)",
                r"\bdo\s+not\s+call\s+(me|us|this\s+number)\s+again",
                r"\bput\s+me\s+on\s+(your|the)\s+do\s+not\s+call",
                r"\bdnc\b",
                r"\bnever\s+call\s+(me\s+)?back",
                r"\bdon'?t\s+call\s+(me\s+)?again",
                r"\bstop\s+ringing\s+me",
            ]
        },
        "DNC_REGISTRY_MENTION": {
            "description": "Mention of national or state registries (TPS, ACMA, FTC).",
            "crm_action": "Flag for compliance audit. Check why they were dialed.",
            "priority": 1,
            "patterns": [
                r"\bnational\s+do\s+not\s+call",
                r"\bregistered\s+number",
                r"\bTPS\b",  # Telephone Preference Service (UK)
                r"\bACMA\b",  # Australian Communications and Media Authority
                r"\bFTC\b",   # Federal Trade Commission (US)
                r"\breport\s+(you|this)\s+to",
                r"\bunsolicited\s+call",
            ]
        },
        "LEGAL_THREAT": {
            "description": "Threats of lawsuits, lawyers, or police.",
            "crm_action": "Escalate to Legal/Compliance officer.",
            "priority": 1,
            "patterns": [
                r"\bi\s+(will|am\s+going\s+to)\s+sue",
                r"\bcontact\s+my\s+lawyer",
                r"\billegal\s+call",
                r"\breporting\s+you",
                r"\bharassment",
                r"\bpress\s+charges",
                r"\bcall\s+the\s+police",
                r"\blawyer",
                r"\bsolicitor",
            ]
        },
        "VULNERABLE_CUSTOMER": {
            "description": "Indication of incapacity, age-related confusion, or distress.",
            "crm_action": "Void any sale. Flag as 'Do Not Contact - Vulnerable'.",
            "priority": 1,
            "patterns": [
                r"\bi\s+don'?t\s+understand\s+what\s+this\s+is",
                r"\bmy\s+(son|daughter|carer)\s+handles\s+my",
                r"\bi\s+am\s+(very|too)\s+old",
                r"\bdementia",
                r"\balzheimer",
                r"\bin\s+hospital",
                r"\bcan'?t\s+hear\s+you",
                r"\bconfused",
                r"\bnursing\s+home",
            ]
        },
        "PROFANITY_ABUSE": {
            "description": "Hostile language directed at the agent.",
            "crm_action": "Allow agent cool-down. Block number if habitual.",
            "priority": 2,
            "patterns": [
                r"\bfuck\s*(off|you)?",
                r"\bfucking\b",
                r"\bshit\b",
                r"\bbitch\b",
                r"\basshole\b",
                r"\bpiss\s+off",
                r"\bstop\s+wasting\s+my\s+time",
                r"\bscammer",
                r"\bfraud",
                r"\bgo\s+to\s+hell",
            ]
        }
    }

    # ==========================================
    # 2. LIST HYGIENE (DISQUALIFIERS)
    # ==========================================
    # Priority 2 - Reasons to permanently remove from campaign

    DISQUALIFICATION_FLAGS = {
        "RETIRED": {
            "description": "Contact is no longer in the workforce (B2B).",
            "crm_action": "Remove contact but keep Company active to find replacement.",
            "priority": 2,
            "patterns": [
                r"\bi\s+(am|have)\s+retired",
                r"\bno\s+longer\s+working",
                r"\bpensioner",
                r"\bout\s+of\s+the\s+business",
                r"\bdon'?t\s+work\s+there\s+anymore",
                r"\bdon'?t\s+work\s+anymore",
                r"\bno\s+longer\s+practicing",
                r"\bfinished\s+working",
                r"\bstopped\s+working",
            ]
        },
        "DECEASED": {
            "description": "The intended contact has passed away.",
            "crm_action": "Permanent suppression. Respectful removal.",
            "priority": 1,
            "patterns": [
                r"\bhe\s+passed\s+away",
                r"\bshe\s+passed\s+away",
                r"\bpassed\s+away",
                r"\bno\s+longer\s+with\s+us",
                r"\bdied",
                r"\bdeceased",
                r"\bpassing",
            ]
        },
        "OUT_OF_BUSINESS": {
            "description": "The company being called is closed (B2B).",
            "crm_action": "Mark Account as Inactive/Closed.",
            "priority": 2,
            "patterns": [
                r"\bcompany\s+closed",
                r"\bwent\s+under",
                r"\bno\s+longer\s+trading",
                r"\bout\s+of\s+business",
                r"\bbankrupt",
                r"\bclosed\s+down",
                r"\bclosed\s+permanently",
                r"\bshut\s+down",
                r"\bliquidat",
                r"\bwinding\s+up",
            ]
        },
        "WRONG_NUMBER": {
            "description": "The person reached is not the person on the list.",
            "crm_action": "Mark number as Invalid for that Contact.",
            "priority": 2,
            "patterns": [
                r"\bwrong\s+number",
                r"\bno\s+one\s+by\s+that\s+name",
                r"\bthere\s+is\s+no\s+\w+\s+here",
                r"\bwho\s+are\s+you\s+looking\s+for",
                r"\byou\s+have\s+the\s+wrong",
                r"\bnever\s+heard\s+of",
                r"\bwho\s+is\s+that",
                r"\bdon'?t\s+know\s+(who|that)",
            ]
        },
        "MINOR_UNDERAGE": {
            "description": "Contact is a child.",
            "crm_action": "Do Not Sell. Terminate call politely.",
            "priority": 1,
            "patterns": [
                r"\bi'?m\s+only\s+\d+",
                r"\bi\s+am\s+a\s+child",
                r"\bi\s+am\s+a\s+minor",
                r"\bparents?\s+aren'?t\s+home",
                r"\bmom\s+is\s+out",
                r"\bdad\s+is\s+out",
                r"\bunder\s+18",
                r"\bmy\s+mum\b",
                r"\bmy\s+dad\b",
            ]
        },
        "COMPETITOR": {
            "description": "The person called works for a competitor.",
            "crm_action": "Mark as 'Competitor'. Stop calling.",
            "priority": 2,
            "patterns": [
                r"\bi\s+work\s+for\s+\w+\s+too",
                r"\bwe\s+are\s+a\s+competitor",
                r"\bwe\s+do\s+the\s+same\s+thing",
                r"\bindustry\s+peer",
                r"\bsame\s+business",
            ]
        },
        "NO_LONGER_AT_COMPANY": {
            "description": "Target contact has moved jobs (B2B).",
            "crm_action": "Mark contact as 'Left Company'. Research new role.",
            "priority": 3,
            "patterns": [
                r"\bleft\s+the\s+company",
                r"\bno\s+longer\s+works\s+here",
                r"\bdoesn'?t\s+work\s+here",
                r"\bmoved\s+on",
                r"\bchanged\s+jobs",
            ]
        }
    }

    # ==========================================
    # 3. TECHNICAL & OPERATIONAL
    # ==========================================
    # Machine detections and non-human interactions

    TECHNICAL_FLAGS = {
        "VOICEMAIL_GENERIC": {
            "description": "Standard carrier voicemail message.",
            "crm_action": "Retry later or leave message.",
            "priority": 3,
            "patterns": [
                r"\bplease\s+leave\s+a\s+message",
                r"\brecord\s+your\s+message",
                r"\bperson\s+you\s+have\s+called",
                r"\bunable\s+to\s+take\s+your\s+call",
                r"\bafter\s+the\s+(tone|beep)",
                r"\bcan'?t\s+take\s+your\s+call",
                r"\bleave\s+your\s+name\s+and\s+number",
            ]
        },
        "VOICEMAIL_FULL": {
            "description": "Cannot leave voicemail - mailbox full.",
            "crm_action": "Mark for alternate contact method.",
            "priority": 2,
            "patterns": [
                r"\bmailbox\s+is\s+full",
                r"\bmessage\s+bank\s+is\s+full",
                r"\bvoicemail\s+(is\s+)?full",
                r"\bcannot\s+leave\s+a\s+message",
                r"\bno\s+message\s+could\s+be\s+left",
            ]
        },
        "DISCONNECTED": {
            "description": "Number not in service.",
            "crm_action": "Mark as Invalid. Remove from dialer.",
            "priority": 2,
            "patterns": [
                r"\bnumber\s+you\s+have\s+dial",
                r"\bnot\s+in\s+service",
                r"\bcheck\s+the\s+number",
                r"\bdisconnected",
                r"\bnot\s+valid",
                r"\bnot\s+connected",
            ]
        },
        "GATEKEEPER": {
            "description": "Receptionist or assistant screening the call.",
            "crm_action": "Retry at different time or with different approach.",
            "priority": 3,
            "patterns": [
                r"\bmay\s+i\s+ask\s+what\s+this\s+is\s+regarding",
                r"\bis\s+he\s+expecting\s+your\s+call",
                r"\bshe\s+is\s+in\s+a\s+meeting",
                r"\btake\s+a\s+message",
                r"\btransfer\s+you",
                r"\bwho\s+is\s+calling",
                r"\bwhat\s+company\s+are\s+you\s+from",
            ]
        },
        "LANGUAGE_BARRIER": {
            "description": "Contact does not speak the agent's language.",
            "crm_action": "Mark for specific language team or remove.",
            "priority": 2,
            "patterns": [
                r"\bno\s+english",
                r"\bi\s+don'?t\s+speak",
                r"\bonly\s+speak\s+\w+",
                r"\btranslate",
                r"\bdon'?t\s+understand\s+english",
            ]
        }
    }

    # ==========================================
    # 4. SALES OUTCOMES & INTEREST
    # ==========================================

    OUTCOME_FLAGS = {
        "SALE_CLOSED": {
            "description": "Successful conversion.",
            "crm_action": "Closed Won.",
            "priority": 1,
            "patterns": [
                r"\blet'?s\s+do\s+it",
                r"\bsign\s+me\s+up",
                r"\bwhere\s+do\s+i\s+sign",
                r"\btake\s+my\s+card\s+details",
                r"\bsend\s+the\s+contract",
                r"\bproceed",
                r"\bi'?ll\s+take\s+it",
                r"\byes\s+please",
                r"\bbook\s+(me\s+)?in",
            ]
        },
        "APPOINTMENT_SET": {
            "description": "Specific date and time agreed for follow-up.",
            "crm_action": "Meeting Booked.",
            "priority": 1,
            "patterns": [
                r"\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\s+(works|is\s+good)",
                r"\bnext\s+week\s+(works|is\s+good)",
                r"\bbook\s+a\s+(time|meeting|call)",
                r"\bschedule\s+a",
                r"\bput\s+me\s+in\s+the\s+diary",
            ]
        },
        "HARD_OBJECTION": {
            "description": "Definitive no.",
            "crm_action": "Closed Lost (Reason: Not Interested).",
            "priority": 2,
            "patterns": [
                r"\bnot\s+interested",
                r"\bdon'?t\s+want\s+it",
                r"\bno\s+thank\s+you",
                r"\bno\s+thanks",
                r"\balready\s+have\s+(one|that)",
                r"\bhappy\s+with\s+current",
                r"\bnot\s+for\s+me",
                r"\bwaste\s+of\s+money",
            ]
        },
        "SOFT_OBJECTION_CALLBACK": {
            "description": "Not now, but maybe later.",
            "crm_action": "Nurture / Recycle (3-6 months).",
            "priority": 3,
            "patterns": [
                r"\bcall\s+me\s+back",
                r"\bcall\s+(me\s+)?later",
                r"\bbusy\s+right\s+now",
                r"\bcan\s+you\s+email\s+me",
                r"\bsend\s+some\s+info",
                r"\btalk\s+next\s+week",
                r"\btry\s+again\s+later",
                r"\bnot\s+a\s+good\s+time",
                r"\bcall\s+tomorrow",
                r"\bcall\s+next\s+week",
                r"\bafter\s+\d+\s*(pm|am)",
            ]
        },
        "PRICE_OBJECTION": {
            "description": "Price is the main barrier.",
            "crm_action": "Flag for discount offer or nurture.",
            "priority": 3,
            "patterns": [
                r"\btoo\s+expensive",
                r"\bcan'?t\s+afford",
                r"\bno\s+budget",
                r"\bbudget\s+(is\s+)?tight",
                r"\bcheaper",
                r"\bcost\s+too\s+much",
                r"\bprice\s+is\s+(too\s+)?high",
            ]
        },
        "AUTHORITY_OBJECTION": {
            "description": "Need to speak to someone else.",
            "crm_action": "Schedule callback or get referral.",
            "priority": 3,
            "patterns": [
                r"\bask\s+my\s+(wife|husband|partner|boss)",
                r"\btalk\s+to\s+the\s+boss",
                r"\brun\s+it\s+by",
                r"\bdecision\s+maker",
                r"\bneed\s+to\s+discuss",
                r"\bcheck\s+with\s+my",
            ]
        },
        "REFERRAL": {
            "description": "Contact provides details for a better person to speak with.",
            "crm_action": "Create new lead from referral.",
            "priority": 2,
            "patterns": [
                r"\bspeak\s+to\s+\w+\s+instead",
                r"\btry\s+calling\s+\w+",
                r"\byou\s+should\s+talk\s+to",
                r"\blet\s+me\s+give\s+you\s+(\w+('?s)?|their|his|her)\s+number",
                r"\bhere'?s\s+their\s+number",
            ]
        }
    }

    # ==========================================
    # 5. QA & SCRIPT COMPLIANCE
    # ==========================================

    QA_FLAGS = {
        "RECORDING_DISCLOSURE": {
            "description": "Agent mentioned the call is recorded.",
            "crm_action": "QA compliance check passed.",
            "priority": 4,
            "patterns": [
                r"\bcall\s+(is|may\s+be)\s+recorded",
                r"\bquality\s+and\s+training",
                r"\bmonitor\s+this\s+call",
                r"\brecorded\s+line",
            ]
        },
        "VERIFICATION_KYC": {
            "description": "Identity verification steps performed.",
            "crm_action": "KYC compliance check passed.",
            "priority": 4,
            "patterns": [
                r"\bverify\s+your\s+address",
                r"\bdate\s+of\s+birth",
                r"\bconfirm\s+your\s+name",
                r"\bsecurity\s+(check|question)",
            ]
        }
    }

    # ==========================================
    # 6. SENTIMENT & EMOTION
    # ==========================================

    SENTIMENT_FLAGS = {
        "SENTIMENT_ANGRY": {
            "description": "Indicators of frustration or anger.",
            "crm_action": "Note for agent welfare. Consider cooling off period.",
            "priority": 3,
            "patterns": [
                r"\bridiculous",
                r"\bwast(e|ing)\s+(of\s+)?time",
                r"\bmanager",  # Often escalation
                r"\bhow\s+dare\s+you",
                r"\bfed\s+up",
                r"\bangry",
                r"\bfurious",
                r"\bunbelievable",
                r"\boutrageous",
            ]
        },
        "SENTIMENT_POSITIVE": {
            "description": "Indicators of happiness or agreement.",
            "crm_action": "Hot lead - prioritize follow-up.",
            "priority": 2,
            "patterns": [
                r"\bthat\s+sounds\s+great",
                r"\bperfect",
                r"\bthank\s+you\s+so\s+much",
                r"\bappreciate\s+it",
                r"\bexcellent",
                r"\bwonderful",
                r"\bbrilliant",
                r"\bfantastic",
                r"\binterested",
                r"\btell\s+me\s+more",
            ]
        },
        "SENTIMENT_CONFUSED": {
            "description": "Indicators of lack of understanding.",
            "crm_action": "Consider simpler follow-up approach.",
            "priority": 3,
            "patterns": [
                r"\bi\s+don'?t\s+understand",
                r"\bwhat\s+do\s+you\s+mean",
                r"\bcan\s+you\s+repeat",
                r"\bnot\s+sure\s+i\s+follow",
                r"\bsorry\s*,?\s*what",
                r"\bconfus",
            ]
        },
        "SENTIMENT_URGENT": {
            "description": "Customer has an immediate problem.",
            "crm_action": "Prioritize for immediate callback.",
            "priority": 2,
            "patterns": [
                r"\bemergency",
                r"\bright\s+now",
                r"\bimmediate",
                r"\burgent",
                r"\basap\b",
                r"\bstraight\s+away",
            ]
        }
    }

    # ==========================================
    # ANALYSIS METHODS
    # ==========================================

    @classmethod
    def get_all_categories(cls) -> Dict[str, Dict]:
        """Return all flag categories combined."""
        return {
            **cls.COMPLIANCE_FLAGS,
            **cls.DISQUALIFICATION_FLAGS,
            **cls.TECHNICAL_FLAGS,
            **cls.OUTCOME_FLAGS,
            **cls.QA_FLAGS,
            **cls.SENTIMENT_FLAGS
        }

    @classmethod
    def analyze_transcript(cls, text: str) -> Dict[str, bool]:
        """
        Run text against all flags.
        Returns a dict of detected flags (only those that matched).
        """
        if not text:
            return {}

        results = {}
        all_categories = cls.get_all_categories()

        for flag, data in all_categories.items():
            for pattern in data['patterns']:
                if re.search(pattern, text, re.IGNORECASE):
                    results[flag] = True
                    break  # Stop checking this flag if found

        return results

    @classmethod
    def analyze_transcript_detailed(cls, text: str) -> Dict[str, Any]:
        """
        Run text against all flags with detailed output.
        Returns flag names, descriptions, and matched patterns.
        """
        if not text:
            return {"flags": [], "details": {}}

        results = {"flags": [], "details": {}}
        all_categories = cls.get_all_categories()

        for flag, data in all_categories.items():
            for pattern in data['patterns']:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    results["flags"].append(flag)
                    results["details"][flag] = {
                        "description": data["description"],
                        "crm_action": data["crm_action"],
                        "priority": data["priority"],
                        "matched_text": match.group(0)
                    }
                    break

        return results

    @classmethod
    def get_crm_classification(cls, flags: Dict[str, bool]) -> Dict[str, Any]:
        """
        Convert raw flags into CRM-ready classification.

        Returns:
            {
                'is_dnc': bool,
                'dnc_reason': str or None,
                'contact_status': str,  # 'active', 'retired', 'closed', 'deceased', 'invalid', 'vulnerable'
                'lead_status': str,     # 'hot', 'warm', 'cold', 'lost', 'dnc'
                'lead_score': int,      # 1-100
                'callback_requested': bool,
                'hostile': bool,
                'voicemail_full': bool,
                'requires_escalation': bool,
                'flags_detected': list
            }
        """
        result = {
            'is_dnc': False,
            'dnc_reason': None,
            'contact_status': 'active',
            'lead_status': 'cold',
            'lead_score': 50,
            'callback_requested': False,
            'hostile': False,
            'voicemail_full': False,
            'requires_escalation': False,
            'flags_detected': list(flags.keys())
        }

        # DNC determination (Priority 1)
        if flags.get('DNC_REQUEST') or flags.get('DNC_REGISTRY_MENTION'):
            result['is_dnc'] = True
            result['dnc_reason'] = 'explicit_request'
            result['lead_status'] = 'dnc'
            result['lead_score'] = 0
        elif flags.get('DECEASED'):
            result['is_dnc'] = True
            result['dnc_reason'] = 'deceased'
            result['contact_status'] = 'deceased'
            result['lead_status'] = 'dnc'
            result['lead_score'] = 0
        elif flags.get('PROFANITY_ABUSE'):
            result['is_dnc'] = True
            result['dnc_reason'] = 'hostile'
            result['hostile'] = True
            result['lead_status'] = 'dnc'
            result['lead_score'] = 0
        elif flags.get('LEGAL_THREAT'):
            result['is_dnc'] = True
            result['dnc_reason'] = 'legal_threat'
            result['requires_escalation'] = True
            result['lead_status'] = 'dnc'
            result['lead_score'] = 0
        elif flags.get('VULNERABLE_CUSTOMER'):
            result['is_dnc'] = True
            result['dnc_reason'] = 'vulnerable'
            result['contact_status'] = 'vulnerable'
            result['lead_status'] = 'dnc'
            result['lead_score'] = 0

        # Contact status determination
        if flags.get('RETIRED'):
            result['contact_status'] = 'retired'
            result['lead_score'] = max(0, result['lead_score'] - 40)
        elif flags.get('OUT_OF_BUSINESS'):
            result['contact_status'] = 'closed'
            result['lead_score'] = 0
        elif flags.get('WRONG_NUMBER') or flags.get('DISCONNECTED'):
            result['contact_status'] = 'invalid'
            result['lead_score'] = 0
        elif flags.get('NO_LONGER_AT_COMPANY'):
            result['contact_status'] = 'left_company'
            result['lead_score'] = max(0, result['lead_score'] - 30)

        # Lead status determination (if not already DNC)
        if result['lead_status'] != 'dnc':
            if flags.get('SALE_CLOSED') or flags.get('APPOINTMENT_SET'):
                result['lead_status'] = 'hot'
                result['lead_score'] = 100
            elif flags.get('SENTIMENT_POSITIVE'):
                result['lead_status'] = 'warm'
                result['lead_score'] = min(100, result['lead_score'] + 30)
            elif flags.get('HARD_OBJECTION'):
                result['lead_status'] = 'lost'
                result['lead_score'] = max(0, result['lead_score'] - 30)
            elif flags.get('SOFT_OBJECTION_CALLBACK'):
                result['callback_requested'] = True
                result['lead_status'] = 'warm'
                result['lead_score'] = min(100, result['lead_score'] + 10)

        # Technical flags
        if flags.get('VOICEMAIL_FULL'):
            result['voicemail_full'] = True

        # Sentiment modifiers
        if flags.get('SENTIMENT_ANGRY') and not result['is_dnc']:
            result['lead_score'] = max(0, result['lead_score'] - 20)
        if flags.get('SENTIMENT_URGENT'):
            result['lead_score'] = min(100, result['lead_score'] + 20)

        return result


# ==========================================
# DATABASE INTEGRATION HELPERS
# ==========================================

def analyze_for_database(transcript: str, call_summary: str = None) -> Dict[str, Any]:
    """
    Analyze transcript and return database-ready values.

    Args:
        transcript: The call transcript text
        call_summary: Optional Retell call summary

    Returns:
        Dict ready to INSERT into telco.call_analysis
    """
    # Combine transcript and summary for analysis
    text_to_analyze = transcript or ""
    if call_summary:
        text_to_analyze += " " + call_summary

    # Get raw flags
    flags = TelemarketingTaxonomy.analyze_transcript(text_to_analyze)

    # Get CRM classification
    classification = TelemarketingTaxonomy.get_crm_classification(flags)

    # Return database-ready dict
    return {
        'is_dnc': classification['is_dnc'],
        'dnc_reason': classification['dnc_reason'],
        'contact_status': classification['contact_status'],
        'lead_status': classification['lead_status'],
        'lead_score': classification['lead_score'],
        'callback_requested': classification['callback_requested'],
        'hostile': classification['hostile'],
        'voicemail_full': classification['voicemail_full'],
        'requires_escalation': classification['requires_escalation'],
        'flags_detected': classification['flags_detected'],
        'analysis_method': 'taxonomy_regex'
    }


# Example usage
if __name__ == "__main__":
    # Test transcripts
    test_cases = [
        "I don't understand why you are calling me. It is a waste of time. Remove me from your list.",
        "I'm retired now, I don't work anymore. Please don't call again.",
        "That sounds great! Let's do it. Sign me up.",
        "I'm busy right now, can you call me back next week?",
        "Wrong number mate, there's no Bob here.",
        "He passed away last month, please remove this number.",
    ]

    print("=" * 60)
    print("TELEMARKETING TAXONOMY TEST")
    print("=" * 60)

    for text in test_cases:
        print(f"\nTranscript: {text[:60]}...")
        result = analyze_for_database(text)
        print(f"  DNC: {result['is_dnc']} ({result['dnc_reason']})")
        print(f"  Status: {result['contact_status']}")
        print(f"  Lead: {result['lead_status']} (score: {result['lead_score']})")
        print(f"  Flags: {result['flags_detected']}")
