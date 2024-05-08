from pydantic import BaseModel
from typing import Dict, List

from data_schema import Project, Student, Instance
import json

import random



class Generator():

    def generateProjects(self, number_projects):
        return {str(i) : Project(name = str(i), capacity = random.randint(8, 16)) for i in range(number_projects)}

    def generateProjectsRatings(self):
        return {project : random.randint(1, 5) for project in self.projects}

    def generateStudents(self, number_students):
        students = []
        for i in range(number_students):
            student = Student(last_name="Doe", first_name="Joe", matr_number=i, projects_ratings=self.generateProjectsRatings())
            students.append(student)
        return students

    def generateInstance(self, number_projects, number_students):   
        self.projects = self.generateProjects(number_projects=number_projects)
        self.students = self.generateStudents(number_students=number_students)
        self.instance = Instance(
                students=self.students,
                projects=self.projects
            )
        
        return self.instance

g = Generator()

instance_sizes = [(10,100),(20,200), (30, 300), (50,500), (100,1000)]

for instance_size in instance_sizes:
    number_projects, number_students = instance_size
    data = g.generateInstance(number_students = number_students,number_projects = number_projects).model_dump_json()
    with open(f"instances/data_s{number_students}_g{number_projects}.json", 'w') as f:
        f.write(data)

    with open(f"instances/data_s{number_students}_g{number_projects}.json") as f:
        test = f.read()
        instance: Instance = Instance.model_validate_json(test)

    print(instance)