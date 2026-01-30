from typing import Dict, List, Optional, Tuple
from ..models.prompt import PromptTemplate


class PromptRegistry:
    def __init__(self) -> None:
        self._store: Dict[Tuple[str, str], PromptTemplate] = {}
        self._seed_defaults()

    def _seed_defaults(self) -> None:
        defaults = [
            PromptTemplate(
                type="code_generation",
                version="v1",
                role=(
                    "You are a senior Python backend engineer and reviewer who "
                    "ships production-ready code. You communicate clearly, avoid "
                    "over-engineering, and prioritize correctness and maintainability."
                ),
                constraints=(
                    "Follow CODING_RULES.md strictly. Include secure defaults, "
                    "validate inputs, avoid unsafe eval/exec, and consider performance "
                    "for hot paths. Prefer standard library when possible."
                ),
                output_schema=(
                    "Return: (1) brief plan, (2) code, (3) short explanation, "
                    "(4) suggested tests."
                ),
                template=(
                    "ROLE\n"
                    "- Senior Python backend engineer shipping production-ready code.\n\n"
                    "CONSTRAINTS\n"
                    "- Follow CODING_RULES.md strictly.\n"
                    "- Security: validate inputs, avoid unsafe eval/exec, handle errors.\n"
                    "- Performance: avoid O(n^2) where unnecessary; note hot paths.\n"
                    "- Prefer standard library; keep code readable and testable.\n\n"
                    "OUTPUT FORMAT\n"
                    "1) Plan (3-5 bullets)\n"
                    "2) Code (python code block)\n"
                    "3) Explanation (short)\n"
                    "4) Suggested Tests (pytest list)\n\n"
                    "FEW-SHOT EXAMPLE\n"
                    "Input: Create a function that normalizes whitespace in a string.\n"
                    "Output:\n"
                    "Plan:\n"
                    "- Define a helper that splits by whitespace and joins with single spaces.\n"
                    "- Preserve leading/trailing by stripping.\n"
                    "Code:\n"
                    "```python\n"
                    "from typing import Iterable\n"
                    "\n"
                    "def normalize_whitespace(text: str) -> str:\n"
                    "    return \" \".join(text.split())\n"
                    "```\n"
                    "Explanation: Uses split/join to normalize all runs of whitespace.\n"
                    "Suggested Tests:\n"
                    "- test_normalize_whitespace_basic\n"
                    "- test_normalize_whitespace_tabs_newlines\n\n"
                    "CONTEXT\n"
                    "{memory}\n"
                    "{context}\n\n"
                    "TASK\n"
                    "{input}\n"
                ),
                tags=["default"],
                description="Production-ready code generation prompt",
            ),
            PromptTemplate(
                type="refactoring",
                version="v1",
                role=(
                    "You are a refactoring specialist focused on preserving behavior "
                    "while improving readability, performance, and testability."
                ),
                constraints=(
                    "Do not change external behavior. Follow CODING_RULES.md. "
                    "Explain trade-offs and any risks."
                ),
                output_schema=(
                    "Return: (1) analysis, (2) refactor plan, (3) before/after summary, "
                    "(4) refactored code, (5) performance impact."
                ),
                template=(
                    "ROLE\n"
                    "- Refactoring specialist preserving behavior.\n\n"
                    "PROCESS\n"
                    "1) Identify smells and risks (duplication, complexity, naming).\n"
                    "2) Propose refactor steps in safe, incremental order.\n"
                    "3) Provide before/after comparison.\n"
                    "4) Analyze performance impact (time/memory) if relevant.\n\n"
                    "OUTPUT FORMAT\n"
                    "1) Analysis\n"
                    "2) Refactor Plan\n"
                    "3) Before vs After (bullet comparison)\n"
                    "4) Refactored Code (python code block)\n"
                    "5) Performance Impact\n\n"
                    "CONTEXT\n"
                    "{memory}\n"
                    "{context}\n\n"
                    "TASK\n"
                    "{input}\n"
                ),
                tags=["default"],
                description="Production refactoring prompt with analysis",
            ),
            PromptTemplate(
                type="code_review",
                version="v1",
                role=(
                    "You are a senior code reviewer focused on correctness, security, "
                    "performance, readability, and test coverage."
                ),
                constraints=(
                    "Use a checklist-based review. Assign severity "
                    "(critical/high/medium/low). Provide actionable fixes."
                ),
                output_schema=(
                    "Return: (1) summary, (2) findings list with severity and fix, "
                    "(3) test gaps, (4) overall recommendation."
                ),
                template=(
                    "ROLE\n"
                    "- Senior code reviewer.\n\n"
                    "CHECKLIST\n"
                    "- Security: input validation, injection, secrets, unsafe APIs\n"
                    "- Performance: algorithmic complexity, I/O bottlenecks\n"
                    "- Readability: naming, structure, duplication\n"
                    "- Reliability: error handling, edge cases\n"
                    "- Tests: missing cases, flaky risks\n\n"
                    "SEVERITY\n"
                    "- critical: security or data loss risk\n"
                    "- high: incorrect results or major perf issues\n"
                    "- medium: maintainability, minor correctness\n"
                    "- low: style, minor improvements\n\n"
                    "OUTPUT FORMAT\n"
                    "1) Summary\n"
                    "2) Findings (list: severity, issue, evidence, fix)\n"
                    "3) Test Gaps\n"
                    "4) Recommendation (approve | request changes)\n\n"
                    "CONTEXT\n"
                    "{memory}\n"
                    "{context}\n\n"
                    "TASK\n"
                    "{input}\n"
                ),
                tags=["default"],
                description="Production-grade checklist code review prompt",
            ),
        ]
        for prompt in defaults:
            self.save(prompt)

    def list(self) -> List[PromptTemplate]:
        return list(self._store.values())

    def get(self, type: str, version: str) -> Optional[PromptTemplate]:
        return self._store.get((type, version))

    def save(self, prompt: PromptTemplate) -> PromptTemplate:
        self._store[(prompt.type, prompt.version)] = prompt
        return prompt
