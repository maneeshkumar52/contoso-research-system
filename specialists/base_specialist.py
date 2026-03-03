"""Abstract base class for all specialist agents."""
import time
from abc import ABC, abstractmethod
from typing import List
import structlog
from openai import AsyncAzureOpenAI
from shared.config import get_settings
from shared.models import SpecialistOutput, SpecialistType

logger = structlog.get_logger(__name__)


class BaseSpecialist(ABC):
    """Abstract base class providing common LLM calling and timing utilities."""

    specialist_type: SpecialistType = None

    def __init__(self) -> None:
        self.settings = get_settings()
        self.client = AsyncAzureOpenAI(
            azure_endpoint=self.settings.azure_openai_endpoint,
            api_key=self.settings.azure_openai_api_key,
            api_version=self.settings.azure_openai_api_version,
            max_retries=3,
        )
        self._total_tokens = 0

    @abstractmethod
    async def analyse(self, topic: str, context: dict) -> SpecialistOutput:
        """Perform specialist analysis on the given topic."""
        ...

    async def _call_llm(self, system_prompt: str, user_prompt: str, temperature: float = 0.3) -> str:
        """
        Call Azure OpenAI with the given prompts.

        Args:
            system_prompt: System instructions for the LLM.
            user_prompt: User/task prompt.
            temperature: Sampling temperature.

        Returns:
            LLM response text.
        """
        try:
            response = await self.client.chat.completions.create(
                model=self.settings.azure_openai_deployment,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature,
                max_tokens=1500,
            )
            if response.usage:
                self._total_tokens += response.usage.total_tokens
            return response.choices[0].message.content or ""
        except Exception as exc:
            logger.error("llm_call_failed", specialist=str(self.specialist_type), error=str(exc))
            raise

    def _extract_findings(self, response_text: str, max_findings: int = 5) -> List[str]:
        """
        Extract bullet-point key findings from response text.

        Args:
            response_text: LLM response to parse.
            max_findings: Maximum number of findings to return.

        Returns:
            List of finding strings.
        """
        findings = []
        lines = response_text.split("\n")
        for line in lines:
            line = line.strip()
            if line.startswith(("- ", "• ", "* ", "· ")):
                finding = line.lstrip("-•*· ").strip()
                if finding and len(finding) > 10:
                    findings.append(finding)
            elif line and line[0].isdigit() and len(line) > 3 and line[1] in ".):":
                finding = line[2:].strip()
                if finding:
                    findings.append(finding)
            if len(findings) >= max_findings:
                break
        return findings or ["Analysis completed — see detailed report for findings."]
