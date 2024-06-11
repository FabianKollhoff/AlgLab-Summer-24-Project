from data_schema import Project, Student, Instance
import json

import math
import random

class Generator():

    def randomStudentType(self):
        rating = random.random()
        distribution = (0.2,0.1,0.4,0.1)
        if rating <= distribution[0]:
            # cracked student
            project_distribution = (0.4, 0.1, 0.1, 0,1)
            skills = (2, 2, 2, 2, 2)
        if rating <= distribution[0] + distribution[1]:
            # basic student
            project_distribution = (0.3, 0.1, 0.3, 0,1)
            skills = (4, 2, 2, 3, 4)
        if rating <= distribution[0] + distribution[1]+ distribution[2]:
            # python bro
            project_distribution = (0.3, 0.1, 0.1, 0,4)
            skills = (2, 3, 3, 3, 4)
        if rating <= distribution[0] + distribution[1] + distribution[2] + distribution[3]:
            # web developer
            project_distribution = (0.3, 0.2, 0.1, 0,4)
            skills = (4, 3, 3, 2, 2)
        if rating > distribution[0] + distribution[1] + distribution[2] + distribution[3]:
            # got here by copying homework
            project_distribution = (0.4, 0.2, 0.1, 0,1)
            skills = (4, 4, 4, 4, 4)
        return project_distribution, skills
    
    def randomStudentRankingProject(self, project_id, num_students, percent_fav_projects):
        bonus = 0
        if project_id <= int(num_students / percent_fav_projects):
            bonus = 0.5
        rating = random.random()
        project_distribution, skills = self.randomStudentType()
        if rating <= project_distribution[0] + bonus:
            return 5
        if rating <= project_distribution[0] + project_distribution[1]:
            return 4
        if rating <= project_distribution[0] + project_distribution[1]+ project_distribution[2]:
            return 3
        if rating <= project_distribution[0] + project_distribution[1] + project_distribution[2] + project_distribution[3]:
            return 2
        return 1
    

    def randomProjectCapacity(self):
        capacity = random.randint(5, 16)
        self.sumProjectsCapacity += capacity
        min_capacity = random.randint(5, capacity)
        return (capacity, min_capacity)
    
    def genererateProgrammingRequirements(self):
        programming_requirements = {"Python":random.randint(0,3), "Java":random.randint(0,3), "C/C++":random.randint(0,3), "PHP":random.randint(0,3), "SQL":random.randint(0,3)}
        return programming_requirements

    def generateProject(self, i):
        capacity, min_capacity = self.randomProjectCapacity()
        return Project(id=i, name=str(i), capacity=capacity, min_capacity=min_capacity, veto=self.generateVetos(), programming_requirements=self.genererateProgrammingRequirements())

    def generateProjects(self, number_projects, number_students):
        projects = {i : self.generateProject(i) for i in range(number_projects)}
        while self.sumProjectsCapacity < number_students:
            for project in projects:
                randomAdative = random.randint(1,6)
                self.sumProjectsCapacity += randomAdative
                projects[project].capacity += randomAdative
                if self.sumProjectsCapacity > number_students:
                    break
        print(self.sumProjectsCapacity)
        return projects


    def generateProjectsRatings(self, percent_fav_projects):
        return {project : self.randomStudentRankingProject(project, number_students, percent_fav_projects) for project in self.projects}
    
    def generateSkillRatings(self):
        data, skills = self.randomStudentType()
        skill_dict = {"Python": skills[0]}
        skill_dict.update({"Java": skills[1]})
        skill_dict.update({"C/C++": skills[2]})
        skill_dict.update({"SQL": skills[3]})
        skill_dict.update({"PHP": skills[4]})
        return skill_dict

    def generateStudents(self, number_students):
        students = []
        for i in range(number_students):
            student = Student(last_name="Doe", first_name="Joe", matr_number=i, projects_ratings={}, programming_language_ratings=self.generateSkillRatings())
            students.append(student)
        return students
    
    def generateVetos(self):
        prohibited_students = []
        score = random.random()
        if score <= 0.1:
            prohibited_students = random.sample(self.students, math.ceil(math.log10(len(self.students))) + 1)
        return prohibited_students

    def generateInstance(self, number_projects, number_students, percent_fav_projects):
        self.sumProjectsCapacity = 0
        self.students = self.generateStudents(number_students=number_students)
        self.projects = self.generateProjects(number_projects=number_projects, number_students=number_students)
        for student in self.students:
            student.projects_ratings = self.generateProjectsRatings(percent_fav_projects)
        self.instance = Instance(
                students=self.students,
                projects=self.projects
            )
        
        return self.instance
    
                

g = Generator()

instance_sizes = [(10,100),(20,200), (30, 300), (50,500), (100,1000)]

for instance_size in instance_sizes:
    number_projects, number_students = instance_size
    data = g.generateInstance(number_students = number_students,number_projects = number_projects, percent_fav_projects=10).model_dump_json(indent=2)
    with open(f"instances/data_s{number_students}_g{number_projects}.json", 'w') as f:
        f.write(data)

    with open(f"instances/data_s{number_students}_g{number_projects}.json") as f:
        test = f.read()
        instance: Instance = Instance.model_validate_json(test)
        assert(len(instance.projects) == number_projects)
        assert(len(instance.students) == number_students)