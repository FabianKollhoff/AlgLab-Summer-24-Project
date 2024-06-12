from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Dict, List


class Student(BaseModel):
    last_name: str = Field(description="The last name of the student", pattern=r"^[a-zA-Z]{2,}(?: [a-zA-Z]+)?$") # might need to allow special characters such as hyphens
    first_name: str = Field(pattern=r"^[A-Z][a-zA-Z]{1,}$")
    matr_number: int = Field(ge=0, le=9999999)
    projects_ratings: Dict[int, int]
    programming_language_ratings: Dict[str, int]
    friends: List[int]

    def __hash__(self) -> int:
        return self.matr_number.__hash__()


    @field_validator("projects_ratings")
    @classmethod
    def check_ratings(cls, v) -> Dict[int, int]:
        for rating in v.values():
            if rating < 1 or rating > 5:
                raise ValueError("Project ratings must be between 1 and 5.")
        return v
    
    @field_validator("friends")
    @classmethod
    def max_number_of_friends(cls, v: List[int]) -> List[int]:
        if len(v) > 2:
            raise ValueError("Only up to two preferred team partners allowed!")
        return v
    

class Project(BaseModel):
    id: int = Field(ge=0)
    name: str
    capacity: int
    min_capacity: int
    veto: List[Student]
    programming_requirements: Dict[str, int]

    def __hash__(self) -> int:
        return self.id.__hash__()

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
    def validate_matr_number(cls, v: List[Student]) -> List[Student]:
        matr_numbers = [student.matr_number for student in v]
        if len(set(matr_numbers)) != len(matr_numbers):
            raise ValueError("There are duplicates of matriculation numbers!")
        return v
    
    @field_validator("students")
    @classmethod
    def check_friends(cls, v: List[Student]) -> List[Student]:
        friend_groups = [student.friends for student in v]
        student_matr_numbers = [student.matr_number for student in v]
        for friends in friend_groups:
            for friend in friends:
                if friend not in student_matr_numbers:
                    raise ValueError(f"Friend with matriculation number {friend} does not exist!")
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

    def get_proj_for_student(self, student: Student):
        for proj in self.projects:
            if student in self.projects[proj]:
                return proj