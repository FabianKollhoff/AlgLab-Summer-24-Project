from pydantic import BaseModel
from typing import Dict, List

import json

import random

class Project(BaseModel):
    name : str
    #student_rating: Dict[Student, int]

class Student(BaseModel):
    last_name: str
    first_name: str
    matr_number: int
    projects_ratings: Dict[str, int]


class Instance(BaseModel):
    students: List[Student]
    projects: Dict[str, Project]

class Generator():

    def generateProjects(self, number_projects):
        return {str(i) : Project(name = str(i)) for i in range(number_projects)}

    def generateProjectsRatings(self):
        return {project : random.randint(1, 5) for project in self.projects}

    def generateStudents(self, number_students):
        students = []
        for i in range(number_students):
            student = Student(last_name="Doe", first_name="Joe", matr_number=i, projects_ratings=self.generateProjectsRatings())
            students.append(student)
        return students

    def __init__(self):
        self.projects = self.generateProjects(number_projects=10)
        self.students = self.generateStudents(number_students=100)
        self.instance = Instance(
                students=self.students,
                projects=self.projects
            )

g = Generator()

data = g.instance.model_dump_json()
with open('instances/data_s100_g10.json', 'w') as f:
    f.write(data)

with open('instances/data_s100_g10.json') as f:
    test = f.read()
    instance: Instance = Instance.model_validate_json(test)

print(instance)