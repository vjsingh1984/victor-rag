# Copyright 2025 Vijaykumar Singh <singhvjd@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Enhanced safety integration for victor-rag using framework safety capabilities."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from victor.framework.capabilities.safety_rules import (
    SafetyAction,
    SafetyCategory,
    SafetyRule,
)
from victor.core.verticals.protocols import SafetyExtensionProtocol, SafetyPattern

# NOTE: SafetyCoordinator is now internal to victor.agent
# External verticals should use SafetyExtensionProtocol and SafetyRule patterns
# The framework will handle rule evaluation and coordination

logger = logging.getLogger(__name__)


class RAGSafetyRules:
    """RAG-specific safety rules."""

    @staticmethod
    def get_all_rules() -> List[SafetyRule]:
        """Get all RAG safety rules."""
        return [
            SafetyRule(
                rule_id="rag_delete_index",
                category=SafetyCategory.FILE,
                pattern=r"delete.*index|drop.*vector|remove.*embeddings",
                description="Delete RAG index or embeddings",
                action=SafetyAction.REQUIRE_CONFIRMATION,
                severity=9,
                confirmation_prompt="This will delete the RAG index. Rebuilding may take time. Continue?",
            ),
            SafetyRule(
                rule_id="rag_bulk_embed",
                category=SafetyCategory.SHELL,
                pattern=r"embed.*--all|index.*bulk|--rebuild.*index",
                description="Bulk rebuild of RAG index",
                action=SafetyAction.WARN,
                severity=6,
            ),
            SafetyRule(
                rule_id="rag_share_corpus",
                category=SafetyCategory.SHELL,
                pattern=r"share.*corpus|upload.*documents|publish.*index",
                description="Share or upload RAG corpus documents",
                action=SafetyAction.REQUIRE_CONFIRMATION,
                severity=7,
                confirmation_prompt="Ensure documents don't contain sensitive information. Continue?",
            ),
        ]


class EnhancedRAGSafetyExtension(SafetyExtensionProtocol):
    """Enhanced safety extension for RAG using framework capabilities."""

    def __init__(self, strict_mode: bool = False):
        from victor.framework.capabilities.safety_rules import SafetyRulesCapabilityProvider

        self._provider = SafetyRulesCapabilityProvider(strict_mode=strict_mode)
        # Register custom RAG-specific rules
        for rule in RAGSafetyRules.get_all_rules():
            self._provider.add_custom_rule(rule)
        logger.info("EnhancedRAGSafetyExtension initialized")

    def check_operation(self, tool_name: str, args: List[str], context: Optional[Dict[str, Any]] = None) -> Any:
        """Check operation safety using framework provider."""
        return self._provider.check_operation(tool_name, args, context)

    def is_operation_safe(self, tool_name: str, args: List[str], context: Optional[Dict[str, Any]] = None) -> bool:
        """Check if operation is safe using framework provider."""
        return self._provider.is_operation_safe(tool_name, args, context)

    def get_bash_patterns(self) -> List[SafetyPattern]:
        """Get bash safety patterns."""
        return []

    def get_file_patterns(self) -> List[SafetyPattern]:
        """Get file safety patterns."""
        return []

    def get_tool_restrictions(self) -> Dict[str, List[str]]:
        """Get tool restrictions."""
        return {}

    def get_provider(self):
        """Get the framework safety rules provider."""
        return self._provider

    def get_safety_stats(self) -> Dict[str, Any]:
        """Get safety statistics."""
        return {"strict_mode": self._provider.strict_mode, "custom_rules": len(RAGSafetyRules.get_all_rules())}


__all__ = ["RAGSafetyRules", "EnhancedRAGSafetyExtension"]
