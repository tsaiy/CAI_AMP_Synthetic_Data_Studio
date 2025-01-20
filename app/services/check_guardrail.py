from typing import Dict, Any, Tuple
import re

from app.core.exceptions import APIError  # Change this line

class ContentGuardrail:
    def __init__(self):
        # PII patterns - Made more specific to reduce false positives
        self.pii_patterns = {
            # Requires @ symbol and common domain extensions
            'email': r'\b[\w\.-]+@[\w\.-]+\.(com|org|net|edu|gov|mil|biz|info|io)\b',
            
            # More flexible phone format but requires area code
            'phone': r'\b\d{3}[-.)]\s*\d{3}[-.)]\s*\d{4}\b',
            
            # Requires typical credit card grouping and common starting digits
            'credit_card': r'\b(4\d{3}|5[1-5]\d{2}|6011)([- ]?\d{4}){3}\b',
            
            # Strict SSN format with required hyphens
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
            
            # Validates IP range values
            'ip_address': r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b'
        }

        # Toxic content patterns - Added context requirements
        self.toxic_patterns = {
            # Requires additional context words to trigger
            'hate_speech': r'\b(expressing|showing)\s+\w+\s+(hate|racism|bigotry)\b',
            
            # Focuses on explicit violent threats
            'violence': r'\b(threaten\s+to|going\s+to)\s+(kill|murder|attack|assault)\b',
            
            # Requires clear threatening context
            'threats': r'\b(make|making|made)\s+\w+\s+(threats?|intimidation)\b',
            
            # Looks for specific extremist context
            'extremism': r'\b(promoting|supporting)\s+\w+\s+(extremism|terrorism)\b',
            
            # Focuses on explicit self-harm statements
            'self_harm': r'\b(want|thinking|going)\s+to\s+(harm\s+myself|end\s+my\s+life|commit\s+suicide)\b'
        }

        # Encoded content patterns - Made more specific
        self.encoded_patterns = {
            # Requires longer sequences to trigger
            'hex_sequence': r'(?:\\x[0-9a-fA-F]{2}){4,}',  # Matches 4+ hex sequences
            
            # Requires multiple unicode characters
            'unicode_hex': r'(?:\\u[0-9a-fA-F]{4}){2,}',   # Matches 2+ unicode sequences
            
            # Requires longer hex values
            'long_hex': r'0x[0-9a-fA-F]{8,}'              # Matches hex of 8+ digits
        }

    def validate_prompt(self, prompt: str) -> Tuple[bool, str]:
        """
        Validate prompt content.
        Returns: (is_safe, message)
        """
        violations = []

        # Check for PII
        # pii_results = self._check_patterns(prompt, self.pii_patterns)
        # violations.extend(pii_results)

        # Check for toxic content
        toxic_results = self._check_patterns(prompt, self.toxic_patterns)
        violations.extend(toxic_results)

        # Check for encoded content
        encoded_results = self._check_patterns(prompt, self.encoded_patterns)
        violations.extend(encoded_results)

        if violations:
            return False, f"Content violates policy: {', '.join(violations)}"
        
        return True, "Content is safe"

    def _check_patterns(self, text: str, patterns: Dict[str, str]) -> list:
        """
        Check text against a dictionary of patterns.
        Returns list of violations found.
        """
        violations = []
        for pattern_name, pattern in patterns.items():
            if re.search(pattern, text, re.IGNORECASE | re.MULTILINE):
                violations.append(f'{pattern_name} detected')
        return violations

