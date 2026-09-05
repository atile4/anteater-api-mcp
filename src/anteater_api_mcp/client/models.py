from pydantic import BaseModel

class Course(BaseModel):
    department: str
    courseNumber: str
    title: str
    description: str
    school: str
    courseLevel: str

class Major(BaseModel):
    id: str
    name: str
    type: str
    division: str
    catalogYear: str | None = None
    specialization: list[str] | None = None