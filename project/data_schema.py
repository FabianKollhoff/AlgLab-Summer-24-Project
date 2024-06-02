from pydantic import BaseModel, field_validator, model_validator, Field
from typing import Dict, List

#class Programming_Languages(BaseModel):
#    programming_languages = Dict[str]


class Student(BaseModel):
    last_name: str = Field(description="The last name of the student", pattern=r"^[a-zA-Z]{2,}(?: [a-zA-Z]+)?$") # might need to allow special characters such as hyphens
    first_name: str = Field(pattern=r"^[A-Z][a-zA-Z]{1,}$")
    matr_number: int = Field
    projects_ratings: Dict[int, int]
    programming_language_ratings: Dict[str, int]
    #friends: List[Student] TODO: check length with a validator

    def __hash__(self) -> int:
        return self.matr_number.__hash__()

    @field_validator("matr_number")
    @classmethod
    def matr_number_is_non_negative(cls, v: int) -> int:
        if v < 0:
            raise ValueError("The matriculation number must be non-negative.")
        if v > 9999999:
            raise ValueError("The matriculation number has at most 7 digits.")
        return v

    @field_validator("projects_ratings")
    @classmethod
    def check_ratings(cls, v) -> Dict[int, int]:
        for rating in v.values():
            if rating < 1 or rating > 5:
                raise ValueError("Project ratings must be between 1 and 5.")
        return v
    

class Project(BaseModel):
    id: int
    name: str
    capacity: int
    min_capacity: int
    veto: List[Student]
    programming_requirements: Dict[str, int]

    def __hash__(self) -> int:
        return self.id.__hash__()

    @field_validator("id")
    @classmethod
    def id_is_non_negative(cls, v: int) -> int:
        if v < 0:
            raise ValueError("Project ID should be non-negative.")
        return v

    @field_validator("capacity")
    @classmethod
    def check_max_capacity(cls, v: int) -> int:
        if v < 5:
            raise ValueError("Maximum project capacity is too small.")
        return v
    
    @field_validator("min_capacity")
    @classmethod
    def check_min_capacity(cls, v: int) -> int:
        if v < 5:
            raise ValueError("Minimum project capacity is too small.")
        return v
    
    #@field_validator("programming_requirements")
    #@classmethod
    #def check_max(cls, v: List[str, int]):
    #    for programing_language in v:

    @model_validator(mode="after")
    def check_capacities(self):
        if self.min_capacity > self.capacity:
            raise ValueError(f"The minimum capacity {self.min_capacity} is bigger than the maximum capacity {self.capacity}.")
        return self
    

class Instance(BaseModel):
    students: List[Student]
    projects: Dict[int, Project]

    @field_validator("students")
    @classmethod
    def validate_matr_number(cls, v) -> List[Student]:
        matr_numbers = [student.matr_number for student in v]
        if len(set(matr_numbers)) != len(matr_numbers):
            raise ValueError("There are duplicates of matriculation numbers!")
        return v
    
    @model_validator(mode="after")
    def validate_project_ratings(self):
        for student in self.students:
            for project_id in student.projects_ratings:
                if project_id not in self.projects:
                    raise ValueError(f"Invalid project ID {project_id} in student's project ratings.")
        return self
    
    @model_validator(mode="after")
    def check_number_of_students(self):
        number_of_students = len(self.students)
        sum_capacity = sum(project.capacity for project in self.projects.values())
        if number_of_students > sum(project.capacity for project in self.projects.values()):
            raise ValueError(f"The number of students {number_of_students} exceeds the sum of all project capacities {sum_capacity}!")
        return self
    
    @model_validator(mode="after")
    def check_vetos(self):
        for project in self.projects.values():
            for prohibited_student in project.veto:
                if prohibited_student not in self.students:
                    raise ValueError(f"Student with matriculation number {prohibited_student.matr_number} does not exist.")
        return self
    
        
class Solution(BaseModel):
    projects: Dict[int, List[Student]]