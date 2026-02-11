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
                    "You are a senior Python engineer. Produce production-ready, readable code "
                    "that follows the design documents and project conventions."
                ),
                constraints=(
                    "Follow CODING_RULES.md. Use the standard library unless a third-party dependency "
                    "is explicitly required. Avoid unsafe eval/exec/pickle. Minimize broad try/except. "
                    "Use clear English identifiers and concise docstrings only when necessary."
                ),
                output_schema=(
                    "Return exactly two fenced blocks and nothing else:\n"
                    "1) Python implementation\n"
                    "2) JSON test cases (for pytest generator)\n"
                ),
                template=(
                    "ROLE\n"
                    "- Senior Python engineer\n\n"
                    "CONSTRAINTS\n"
                    "- Follow CODING_RULES.md\n"
                    "- Avoid eval/exec/pickle\n"
                    "- Prefer stdlib, keep dependencies minimal\n"
                    "- Use English identifiers, minimal comments\n\n"
                    "OUTPUT FORMAT (STRICT)\n"
                    "Return only these two fenced blocks:\n\n"
                    "```python\n"
                    "def your_function(param: str) -> str:\n"
                    "    \"\"\"Short docstring if needed.\"\"\"\n"
                    "    return param\n"
                    "```\n\n"
                    "```json\n"
                    "{{\n"
                    "  \"cases\": [\n"
                    "    {{\"name\": \"case_1\", \"call\": \"your_function\", \"input\": [\"test\"], \"expected\": \"test\"}},\n"
                    "    {{\"name\": \"case_2\", \"call\": \"your_function\", \"input\": [\"\"], \"expected\": \"\"}}\n"
                    "  ]\n"
                    "}}\n"
                    "```\n\n"
                    "CONTEXT\n"
                    "{memory}\n\n"
                    "{context}\n\n"
                    "TASK\n"
                    "{input}\n"
                ),
                tags=["default"],
                description="Strict code + JSON tests, no extra text",
            ),
            PromptTemplate(
                type="refactoring",
                version="v1",
                role=(
                    "You are a refactoring specialist. Preserve behavior while improving readability, "
                    "performance, and testability."
                ),
                constraints=(
                    "Do not change external behavior unless explicitly requested. Follow CODING_RULES.md. "
                    "Explain risks and tradeoffs clearly."
                ),
                output_schema=(
                    "Output sections: Analysis, Refactor Plan, Before vs After, Refactored Code, Performance."
                ),
                template=(
                    "ROLE\n"
                    "- Refactoring specialist\n\n"
                    "PROCESS\n"
                    "1) Identify pain points and risks\n"
                    "2) Propose staged refactor plan\n"
                    "3) Show before/after comparison\n"
                    "4) Provide refactored code\n"
                    "5) Performance impact\n\n"
                    "OUTPUT FORMAT\n"
                    "## 1. Analysis\n"
                    "- Issues:\n"
                    "- Risks:\n\n"
                    "## 2. Refactor Plan\n"
                    "1. ...\n"
                    "2. ...\n\n"
                    "## 3. Before vs After\n"
                    "Before:\n"
                    "- Complexity: ...\n"
                    "After:\n"
                    "- Complexity: ...\n\n"
                    "## 4. Refactored Code\n"
                    "```python\n"
                    "# Refactored implementation\n"
                    "def refactored_function(param: str) -> str:\n"
                    "    return param\n"
                    "```\n\n"
                    "## 5. Performance\n"
                    "- Time: ...\n"
                    "- Memory: ...\n\n"
                    "CONTEXT\n"
                    "{memory}\n\n"
                    "{context}\n\n"
                    "TASK\n"
                    "{input}\n"
                ),
                tags=["default"],
                description="Structured refactor guidance with preserved behavior",
            ),
            PromptTemplate(
                type="code_review",
                version="v1",
                role=(
                    "You are a senior code reviewer. Focus on security, correctness, performance, "
                    "readability, and test gaps."
                ),
                constraints=(
                    "Use severity levels: critical, high, medium, low. Provide actionable fixes."
                ),
                output_schema=(
                    "Output sections: Summary, Findings by Severity, Test Gaps, Final Recommendation."
                ),
                template=(
                    "ROLE\n"
                    "- Senior code reviewer\n\n"
                    "CHECKLIST\n"
                    "- Security: input validation, injection risks, unsafe APIs\n"
                    "- Correctness: edge cases, error handling\n"
                    "- Performance: complexity, I/O bottlenecks\n"
                    "- Readability: naming, structure, duplication\n"
                    "- Tests: missing cases, flakiness\n\n"
                    "OUTPUT FORMAT\n"
                    "## 1. Summary\n"
                    "Overall assessment in 2-3 sentences.\n\n"
                    "## 2. Findings\n"
                    "### [CRITICAL] Title\n"
                    "- Issue:\n"
                    "- Evidence:\n"
                    "- Fix:\n\n"
                    "### [HIGH] Title\n"
                    "- Issue:\n"
                    "- Evidence:\n"
                    "- Fix:\n\n"
                    "### [MEDIUM] Title\n"
                    "- Issue:\n"
                    "- Evidence:\n"
                    "- Fix:\n\n"
                    "### [LOW] Title\n"
                    "- Issue:\n"
                    "- Evidence:\n"
                    "- Fix:\n\n"
                    "## 3. Test Gaps\n"
                    "- Missing case 1\n"
                    "- Missing case 2\n\n"
                    "## 4. Final Recommendation\n"
                    "Decision: approve | request changes\n"
                    "Rationale: ...\n\n"
                    "CONTEXT\n"
                    "{memory}\n\n"
                    "{context}\n\n"
                    "TASK\n"
                    "{input}\n"
                ),
                tags=["default"],
                description="Severity-based review with actionable fixes",
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
