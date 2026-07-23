from dataclasses import dataclass, field

@dataclass(slots=True)
class Primitive:
    id:str
    name:str
    geometry:str
    category:str=""
    research_questions:list[str]=field(default_factory=list)
