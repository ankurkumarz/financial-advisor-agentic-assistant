"""
Compliance Checklist Tool for automated validation of financial advisory responses.

This tool provides structured validation against regulatory requirements, legal standards,
and ethical guidelines to ensure AI-generated financial advice meets compliance standards.
"""

from typing import Dict, Any, List, Optional
import re
from ...utils import setup_logger

logger = setup_logger(__name__)


class ComplianceChecklistTool:
    """
    Tool for validating financial advisory responses against compliance requirements.

    Checks for:
    - AI disclosure requirements
    - Regulatory compliance (SEC, FINRA, etc.)
    - Prohibited content and guarantees
    - Risk disclosure adequacy
    - Required disclaimers
    - Ethical standards
    """

    # Prohibited patterns that indicate non-compliant content
    PROHIBITED_PATTERNS = {
        "guaranteed_returns": [
            r"guaranteed?\s+returns?",
            r"guaranteed?\s+\d+%",
            r"guaranteed?\s+profit",
            r"risk-free\s+returns?",
            r"no\s+risk",
            r"cannot\s+lose",
            r"will\s+definitely",
        ],
        "specific_predictions": [
            r"will\s+(definitely|certainly|surely)\s+(rise|increase|go\s+up|gain)",
            r"guaranteed?\s+to\s+(double|triple)",
            r"certain\s+to\s+(outperform|beat)",
        ],
        "unlicensed_advice": [
            r"you\s+should\s+(buy|sell|purchase)\s+(?!consider|evaluate)",
            r"I\s+recommend\s+buying",
            r"invest\s+all\s+your",
        ],
        "market_manipulation": [
            r"insider\s+information",
            r"pump\s+and\s+dump",
            r"manipulate\s+the\s+market",
        ]
    }

    # Required disclaimer keywords
    REQUIRED_DISCLAIMERS = {
        "ai_disclosure": [
            "AI", "artificial intelligence", "probabilistic", "agentic AI"
        ],
        "general_disclaimer": [
            "not constitute", "educational", "informational purposes"
        ],
        "professional_advice": [
            "licensed", "qualified professional", "financial advisor"
        ],
        "risk_warning": [
            "risk", "loss", "principal", "past performance"
        ]
    }

    # Risk types that should be disclosed for investment-related content
    RISK_TYPES = [
        "market risk",
        "credit risk",
        "liquidity risk",
        "volatility",
        "loss of principal",
        "interest rate risk",
        "inflation risk"
    ]

    def get_tool_definition(self) -> Dict[str, Any]:
        """Return tool definition for agent integration."""
        return {
            "name": "compliance_checklist",
            "description": (
                "Validates financial advisory responses against comprehensive compliance requirements. "
                "Checks for AI disclosures, prohibited content, required disclaimers, regulatory compliance, "
                "and risk disclosure adequacy. Returns structured compliance validation report with specific "
                "issues and recommendations."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "response_text": {
                        "type": "string",
                        "description": "The financial advisory response to validate for compliance"
                    },
                    "response_type": {
                        "type": "string",
                        "description": "Type of financial content: 'investment_advice', 'general_info', 'product_explanation', 'market_analysis', 'tax_advice', 'legal_advice'",
                        "enum": ["investment_advice", "general_info", "product_explanation", "market_analysis", "tax_advice", "legal_advice"]
                    },
                    "strict_mode": {
                        "type": "boolean",
                        "description": "If true, applies stricter validation criteria (default: true)",
                        "default": True
                    }
                },
                "required": ["response_text", "response_type"]
            },
            "handler": self.validate_compliance
        }

    def validate_compliance(
        self,
        response_text: str,
        response_type: str = "general_info",
        strict_mode: bool = True
    ) -> Dict[str, Any]:
        """
        Validate response against compliance checklist.

        Args:
            response_text: The advisory response to validate
            response_type: Type of financial content
            strict_mode: Apply stricter validation criteria

        Returns:
            Structured compliance validation report
        """
        try:
            logger.info(f"Running compliance validation for response_type: {response_type}")

            validation_results = {
                "overall_status": "PENDING",
                "validation_timestamp": "Current validation run",
                "response_type": response_type,
                "strict_mode": strict_mode,
                "checks_performed": {},
                "issues_found": [],
                "missing_elements": [],
                "recommendations": []
            }

            # 1. AI Disclosure Check
            ai_disclosure_result = self._check_ai_disclosure(response_text, strict_mode)
            validation_results["checks_performed"]["ai_disclosure"] = ai_disclosure_result
            if not ai_disclosure_result["passed"]:
                validation_results["issues_found"].extend(ai_disclosure_result["issues"])
                validation_results["missing_elements"].append("AI disclosure statement")

            # 2. Prohibited Content Check
            prohibited_result = self._check_prohibited_content(response_text)
            validation_results["checks_performed"]["prohibited_content"] = prohibited_result
            if not prohibited_result["passed"]:
                validation_results["issues_found"].extend(prohibited_result["issues"])

            # 3. Required Disclaimers Check
            disclaimer_result = self._check_required_disclaimers(response_text, response_type, strict_mode)
            validation_results["checks_performed"]["required_disclaimers"] = disclaimer_result
            if not disclaimer_result["passed"]:
                validation_results["missing_elements"].extend(disclaimer_result["missing"])

            # 4. Risk Disclosure Check (for investment-related content)
            if response_type in ["investment_advice", "product_explanation", "market_analysis"]:
                risk_result = self._check_risk_disclosure(response_text, strict_mode)
                validation_results["checks_performed"]["risk_disclosure"] = risk_result
                if not risk_result["passed"]:
                    validation_results["missing_elements"].extend(risk_result["missing_risks"])

            # 5. Specific Content Type Checks
            type_specific_result = self._check_content_type_specific(response_text, response_type)
            validation_results["checks_performed"]["content_type_specific"] = type_specific_result
            if not type_specific_result["passed"]:
                validation_results["issues_found"].extend(type_specific_result["issues"])

            # Determine overall status
            critical_issues = [
                not ai_disclosure_result["passed"],
                not prohibited_result["passed"],
            ]

            if any(critical_issues):
                validation_results["overall_status"] = "REJECTED"
                validation_results["recommendations"].append(
                    "CRITICAL: Response contains critical compliance violations and must be rejected or significantly modified."
                )
            elif validation_results["missing_elements"]:
                validation_results["overall_status"] = "REQUIRES_MODIFICATION"
                validation_results["recommendations"].append(
                    "Response requires modifications to add missing compliance elements."
                )
            else:
                validation_results["overall_status"] = "APPROVED"
                validation_results["recommendations"].append(
                    "Response meets compliance requirements."
                )

            # Add specific recommendations
            if validation_results["missing_elements"]:
                validation_results["recommendations"].append(
                    f"Add the following elements: {', '.join(validation_results['missing_elements'])}"
                )

            logger.info(f"Compliance validation completed with status: {validation_results['overall_status']}")
            return validation_results

        except Exception as e:
            logger.error(f"Error in compliance validation: {str(e)}")
            return {
                "overall_status": "ERROR",
                "error": str(e),
                "recommendation": "Manual review required due to validation error"
            }

    def _check_ai_disclosure(self, text: str, strict_mode: bool) -> Dict[str, Any]:
        """Check for adequate AI disclosure."""
        text_lower = text.lower()

        # Check for key AI disclosure terms
        has_ai_mention = any(term in text_lower for term in ["ai", "artificial intelligence", "ai-generated", "ai-powered"])
        has_probabilistic = "probabilistic" in text_lower or "may contain errors" in text_lower or "can make mistakes" in text_lower
        has_professional_advice_warning = any(term in text_lower for term in [
            "not a substitute", "consult", "licensed", "qualified professional"
        ])

        passed = has_ai_mention and (has_probabilistic or not strict_mode) and has_professional_advice_warning

        issues = []
        if not has_ai_mention:
            issues.append({
                "severity": "CRITICAL",
                "issue": "Missing AI system disclosure",
                "requirement": "Must disclose that response is AI-generated"
            })
        if not has_probabilistic and strict_mode:
            issues.append({
                "severity": "CRITICAL",
                "issue": "Missing probabilistic nature disclosure",
                "requirement": "Must warn that AI systems are probabilistic and can make mistakes"
            })
        if not has_professional_advice_warning:
            issues.append({
                "severity": "HIGH",
                "issue": "Missing professional advice consultation warning",
                "requirement": "Must advise users to consult licensed professionals"
            })

        return {
            "passed": passed,
            "has_ai_mention": has_ai_mention,
            "has_probabilistic_warning": has_probabilistic,
            "has_professional_advice_warning": has_professional_advice_warning,
            "issues": issues
        }

    def _check_prohibited_content(self, text: str) -> Dict[str, Any]:
        """Check for prohibited content patterns."""
        text_lower = text.lower()
        detected_violations = []

        for violation_type, patterns in self.PROHIBITED_PATTERNS.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text_lower, re.IGNORECASE)
                for match in matches:
                    # Get context around match
                    start = max(0, match.start() - 30)
                    end = min(len(text), match.end() + 30)
                    context = text[start:end]

                    detected_violations.append({
                        "severity": "CRITICAL",
                        "type": violation_type,
                        "pattern": pattern,
                        "matched_text": match.group(),
                        "context": context.strip(),
                        "regulation": "SEC/FINRA regulations prohibit guarantees and misleading statements"
                    })

        return {
            "passed": len(detected_violations) == 0,
            "violations_detected": len(detected_violations),
            "issues": detected_violations
        }

    def _check_required_disclaimers(self, text: str, response_type: str, strict_mode: bool) -> Dict[str, Any]:
        """Check for required disclaimers based on content type."""
        text_lower = text.lower()
        missing = []
        present = []

        # Check each required disclaimer category
        for category, keywords in self.REQUIRED_DISCLAIMERS.items():
            has_disclaimer = any(keyword.lower() in text_lower for keyword in keywords)
            if has_disclaimer:
                present.append(category)
            else:
                missing.append(category)

        # Content-specific disclaimer requirements
        if response_type == "tax_advice" and "tax professional" not in text_lower:
            missing.append("tax_advice_limitation")

        if response_type == "legal_advice" and "legal" not in text_lower and "attorney" not in text_lower:
            missing.append("legal_advice_limitation")

        # In strict mode, all disclaimers are required
        passed = len(missing) == 0 if strict_mode else len(present) >= 2

        return {
            "passed": passed,
            "present": present,
            "missing": missing,
            "total_required": len(self.REQUIRED_DISCLAIMERS)
        }

    def _check_risk_disclosure(self, text: str, strict_mode: bool) -> Dict[str, Any]:
        """Check for adequate risk disclosure in investment content."""
        text_lower = text.lower()
        disclosed_risks = []
        missing_risks = []

        for risk_type in self.RISK_TYPES:
            if risk_type in text_lower:
                disclosed_risks.append(risk_type)
            else:
                missing_risks.append(risk_type)

        # In strict mode, require at least 3 risk types; otherwise 1 is sufficient
        min_required = 3 if strict_mode else 1
        passed = len(disclosed_risks) >= min_required

        return {
            "passed": passed,
            "disclosed_risks": disclosed_risks,
            "missing_risks": missing_risks if not passed else [],
            "disclosure_count": len(disclosed_risks),
            "minimum_required": min_required
        }

    def _check_content_type_specific(self, text: str, response_type: str) -> Dict[str, Any]:
        """Perform content-type specific validation."""
        text_lower = text.lower()
        issues = []

        if response_type == "investment_advice":
            # Check for suitability considerations
            suitability_terms = ["risk tolerance", "time horizon", "financial situation", "investment objectives"]
            has_suitability = any(term in text_lower for term in suitability_terms)

            if not has_suitability:
                issues.append({
                    "severity": "HIGH",
                    "issue": "Investment advice lacks suitability considerations",
                    "requirement": "Must consider client's risk tolerance, time horizon, and financial situation"
                })

        elif response_type == "tax_advice":
            if "tax professional" not in text_lower and "cpa" not in text_lower:
                issues.append({
                    "severity": "CRITICAL",
                    "issue": "Tax advice without proper disclaimer",
                    "requirement": "Must direct users to consult tax professionals/CPAs"
                })

        elif response_type == "legal_advice":
            if "attorney" not in text_lower and "legal professional" not in text_lower:
                issues.append({
                    "severity": "CRITICAL",
                    "issue": "Legal advice without proper disclaimer",
                    "requirement": "Must direct users to consult licensed attorneys"
                })

        return {
            "passed": len(issues) == 0,
            "issues": issues
        }


# Export the tool definition function for agent integration
def get_compliance_checklist_tool():
    """Get the compliance checklist tool for agent integration."""
    return compliance_checklist_tool.get_tool_definition()

# Create singleton instance
compliance_checklist_tool = ComplianceChecklistTool()