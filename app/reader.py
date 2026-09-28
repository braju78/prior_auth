from typing import Protocol
from pydantic import BaseModel, ConfigDict, Field
class ClinicalFacts(BaseModel):
    model_config = ConfigDict(extra="forbid")
    pain_weeks: float | None = Field(default=None)
    physio_weeks: float | None = Field(default=None)
class Reader(Protocol):
    async def extract(self, clinical_note: str) -> ClinicalFacts: ...
class LLMReader:
    def __init__(self):
        import os
        from langchain_openai import ChatOpenAI
        self.llm = ChatOpenAI(model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"), temperature=0).with_structured_output(ClinicalFacts)
    async def extract(self, clinical_note: str) -> ClinicalFacts:
        system = """Extract only two facts from this synthetic clinical note. Return pain_weeks and physio_weeks as numbers or null. Do not infer a duration that is not explicitly established. 'No physiotherapy was tried' means 0 weeks. A treatment other than physiotherapy does not count. If physiotherapy is not mentioned or has no duration, return null."""
        return ClinicalFacts.model_validate(await self.llm.ainvoke([("system", system), ("human", clinical_note)]))
class FixtureReader:
    def __init__(self, fixtures: dict[str, ClinicalFacts]): self.fixtures = fixtures
    async def extract(self, clinical_note: str) -> ClinicalFacts: return self.fixtures[clinical_note.strip()]
