from pydantic import BaseModel

class Course(BaseModel):
    department: str
    courseNumber: str
    title: str
    description: str
    school: str
    courseLevel: str