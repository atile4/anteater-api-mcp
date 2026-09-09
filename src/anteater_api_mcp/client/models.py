from pydantic import BaseModel, Field

class Course(BaseModel):
    id: str | None = None
    department: str
    courseNumber: str
    courseNumeric: int | None = None
    school: str
    title: str
    courseLevel: str
    minUnits: float | None = None
    maxUnits: float | None = None
    description: str
    departmentName: str | None = None
    
    # TODO: Implement Instructor model for elements in this list
    instructors: list[dict] | None = None
    
    # TODO: Implement PrerequisiteTree model for structure matching AND/OR logic
    prerequisiteTree: dict | None = None
    
    prerequisiteText: str | None = None
    
    # TODO: Implement PrerequisiteRef model for elements in this list
    prerequisites: list[dict] | None = None
    
    dependencies: list[str] | None = None
    repeatability: str | None = None
    repeatabilityTimes: int | None = None
    repeatabilityType: str | None = None
    gradingOption: str | None = None
    concurrent: str | None = None
    sameAs: str | None = None
    restriction: str | None = None
    overlap: str | None = None
    corequisites: str | None = None
    geList: list[str] | None = None
    geText: str | None = None
    terms: list[str] | None = None


class CourseSearchResult(BaseModel):
    data: list[Course]
    warnings: list[str] = []

class Major(BaseModel):
    id: str
    name: str
    type: str
    division: str
    catalogYear: str | None = None
    specialization: list[str] | None = None

class APExam(BaseModel):
    fullName: str
    rewards: list[dict]
