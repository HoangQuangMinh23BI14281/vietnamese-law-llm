from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class LegalChunk:
    text: str
    metadata: dict
    embedding: Optional[List[float]] = field(default=None)