import csv
import os
import re
import random
import json
from data_schema import Project, Student, Instance

class ExampleGenerator():
    def __init__(self, file_path, num_projects):
       self.num_projects = num_projects
       self.sumProjectsCapacity = 0
       self.data = {}
       self.project_ratings = {}
       self.skills = {}
       
       if not os.path.isfile(file_path):
        raise FileNotFoundError(f"No such file: '{file_path}'")
       with open(file_path, mode='r', newline='', encoding='utf-8') as csvfile:
           csv_reader = csv.DictReader(csvfile)
           for id, row in enumerate(csv_reader):
               self.data[id] = row
               
       self.format_projects()
       self.format_skills()
       self.projects_to_ratings(self.num_projects)
       self.skills_to_ratings()
       self.students = self.generateStudents()
    
    def randomProjectCapacity(self):
        capacity = random.randint(5, 16)
        self.sumProjectsCapacity += capacity
        return capacity   
       
    def format_projects(self):
        for id, row in self.data.items():
            project_number_choice_1 = ''.join(filter(str.isdigit, row['Erstwunsch']))
            self.data[id]['Erstwunsch'] = int(project_number_choice_1)
            
            project_number_choice_2 = ''.join(filter(str.isdigit, row['Zweitwunsch']))
            self.data[id]['Zweitwunsch'] = int(project_number_choice_2)
            
            project_number_choice_3 = ''.join(filter(str.isdigit, row['Drittwunsch']))
            self.data[id]['Drittwunsch'] = int(project_number_choice_3)
    
    def format_skills(self):
        for id,row in self.data.items():
            if "Kenntnisse" in row:
                languages = row["Kenntnisse"].split('#')
                language_proficiency = {}
                for language in languages:
                    match = re.match(r'(\w+)\s*\((\w+)\)', language.strip())
                    if match:
                        lang_name, proficiency = match.groups()
                        language_proficiency[lang_name] = proficiency
                self.data[id]["Kenntnisse"] = language_proficiency
                
    def projects_to_ratings(self, num_projects):
        rating = random.random()
        for id,row in self.data.items():
            student_ratings = {}
            for i in range(num_projects):
                if row["Erstwunsch"] == i:
                    student_ratings.update({i: 5})
                elif row["Zweitwunsch"] == i:
                    if rating > 0.5:
                        student_ratings.update({i: 5})
                    else:
                        student_ratings.update({i: 4})
                elif row["Drittwunsch"] == i:
                    if rating > 0.5:
                        student_ratings.update({i: 4})
                    else:
                        student_ratings.update({i: 3})
                else:
                    rating = random.randint(1,3)
                    student_ratings.update({i: rating})
            self.project_ratings.update({id: student_ratings})
            
    def skills_to_ratings(self):
        for id,row in self.data.items():
            student_skills = {}
            kenntnisse = row["Kenntnisse"]
            rating = random.random()
            if "Python" in kenntnisse:
                if kenntnisse["Python"] == "Anfänger":
                    if rating > 0.5:
                        student_skills.update({"Python": 2})
                    else:
                        student_skills.update({"Python": 1})
                else:
                    if rating > 0.5:
                        student_skills.update({"Python": 4})
                    else:
                        student_skills.update({"Python": 5})
            else:
                new_rating = random.randint(1,3)
                student_skills.update({"Python": new_rating})
            if "Java" in kenntnisse:
                if kenntnisse["Java"] == "Anfänger":
                    if rating > 0.5:
                        student_skills.update({"Java": 2})
                    else:
                        student_skills.update({"Java": 1})
                else:
                    if rating > 0.5:
                        student_skills.update({"Java": 4})
                    else:
                        student_skills.update({"Java": 5})
            else:
                new_rating = random.randint(1,3)
                student_skills.update({"Java": new_rating})
            if "SQL" in kenntnisse:
                if kenntnisse["SQL"] == "Anfänger":
                    if rating > 0.5:
                        student_skills.update({"SQL": 2})
                    else:
                        student_skills.update({"SQL": 1})
                else:
                    if rating > 0.5:
                        student_skills.update({"SQL": 4})
                    else:
                        student_skills.update({"SQL": 5})
            else:
                new_rating = random.randint(1,3)
                student_skills.update({"SQL": new_rating})
            if "C++" in kenntnisse:
                if kenntnisse["C++"] == "Anfänger":
                    if rating > 0.5:
                        student_skills.update({"C++": 2})
                    else:
                        student_skills.update({"C++": 1})
                else:
                    if rating > 0.5:
                        student_skills.update({"C++": 4})
                    else:
                        student_skills.update({"C++": 5})
            else:
                new_rating = random.randint(1,3)
                student_skills.update({"C++": new_rating})
            if "PHP" in kenntnisse:
                if kenntnisse["PHP"] == "Anfänger":
                    if rating > 0.5:
                        student_skills.update({"PHP": 2})
                    else:
                        student_skills.update({"PHP": 1})
                else:
                    if rating > 0.5:
                        student_skills.update({"PHP": 4})
                    else:
                        student_skills.update({"PHP": 5})
            else:
                new_rating = random.randint(1,3)
                student_skills.update({"PHP": new_rating})
            self.skills.update({id: student_skills})
       
    def generateStudents(self):
        students = []
        for id, row in self.data.items():
            student = Student(last_name=row["Nachname"], first_name=row["Vorname"], matr_number=row["MatrikelNr"], projects_ratings=self.project_ratings[id], skills_ratings=self.skills[id])
            students.append(student)
        return students
    
    def generateProjects(self, number_projects, number_students):
        projects = {i : Project(id=i, name=str(i), capacity=self.randomProjectCapacity()) for i in range(number_projects)}
        while self.sumProjectsCapacity < number_students:
            for project in projects:
                randomAdative = random.randint(1,6)
                self.sumProjectsCapacity += randomAdative
                projects[project].capacity += randomAdative
                if self.sumProjectsCapacity > number_students:
                    break
        print(self.sumProjectsCapacity)
        return projects
    
    def generateInstance(self):
        return Instance(students=self.students, projects=self.generateProjects(self.num_projects, len(self.students)))


file_path = 'examples/sep_registrations_1.csv'
eg = ExampleGenerator(file_path, 18)
data = eg.generateInstance().model_dump_json()
with open(f"examples/example_data_1.json", 'w') as f:
    f.write(data)
with open(f"examples/example_data_1.json") as f:
        test = f.read()
        instance: Instance = Instance.model_validate_json(test)
        assert(len(instance.projects) == 18)
        assert(len(instance.students) == 162)

        
file_path = 'examples/sep_registrations_2.csv'
eg = ExampleGenerator(file_path, 19)
data = eg.generateInstance().model_dump_json()
with open(f"examples/example_data_2.json", 'w') as f:
    f.write(data)
with open(f"examples/example_data_2.json") as f:
        test = f.read()
        instance: Instance = Instance.model_validate_json(test)
        assert(len(instance.projects) == 19)
        assert(len(instance.students) == 162)