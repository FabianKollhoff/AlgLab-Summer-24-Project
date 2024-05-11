from pydantic import BaseModel
from typing import Dict, List

class Project(BaseModel):
    name : str
    capacity : int
    #student_rating: Dict[Student, int]

class Student(BaseModel):
    last_name: str
    first_name: str
    matr_number: int
    projects_ratings: Dict[str, int]


class Instance(BaseModel):
    students: List[Student]
    projects: Dict[str, Project]


class Solution(BaseModel):
    projects: Dict[str, List[Student]]