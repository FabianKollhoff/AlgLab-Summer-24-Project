from data_schema import Project, Student, Instance

import math
import random

class Generator():

    def randomStudentRankingProject(self):
        rating = random.random()
        distribution = (0.2,0.1,0.4,0.1)
        if rating <= distribution[0]:
            return 5
        if rating <= distribution[0] + distribution[1]:
            return 4
        if rating <= distribution[0] + distribution[1]+ distribution[2]:
            return 3
        if rating <= distribution[0] + distribution[1] + distribution[2] + distribution[3]:
            return 2
        return 1

    def randomProjectCapacity(self):
        capacity = random.randint(5, 16)
        self.sumProjectsCapacity += capacity
        min_capacity = random.randint(5, capacity)
        return (capacity, min_capacity)
    
    #maybe skill requirement better ?
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

    def generateProjectsRatings(self):
        return {project : self.randomStudentRankingProject() for project in self.projects}
    
    def generateProgrammingLanguageRatings(self):
        return {"Python":random.randint(0,4), "Java":random.randint(0,4), "C/C++":random.randint(0,1), "PHP":random.randint(0,1), "SQL":random.randint(0,1)}

    def generateStudents(self, number_students):
        students = []
        for i in range(number_students):
            student = Student(last_name="Doe", first_name="Joe", matr_number=i, projects_ratings={}, programming_language_ratings=self.generateProgrammingLanguageRatings())
            students.append(student)
        return students
    
    def generateVetos(self):
        prohibited_students = []
        score = random.random()
        if score <= 0.1:
            prohibited_students = random.sample(self.students, math.ceil(math.log10(len(self.students))) + 1)
        return prohibited_students

    def generateInstance(self, number_projects, number_students):
        self.sumProjectsCapacity = 0
        self.students = self.generateStudents(number_students=number_students)
        self.projects = self.generateProjects(number_projects=number_projects, number_students=number_students)
        for student in self.students:
            student.projects_ratings = self.generateProjectsRatings()
        self.instance = Instance(
                students=self.students,
                projects=self.projects
            )
        
        return self.instance

g = Generator()

instance_sizes = [(10,100),(20,200), (30, 300), (50,500), (100,1000)]

for instance_size in instance_sizes:
    number_projects, number_students = instance_size
    data = g.generateInstance(number_students = number_students,number_projects = number_projects).model_dump_json(indent=2)
    with open(f"instances/data_s{number_students}_g{number_projects}.json", 'w') as f:
        f.write(data)

    with open(f"instances/data_s{number_students}_g{number_projects}.json") as f:
        test = f.read()
        instance: Instance = Instance.model_validate_json(test)
        assert(len(instance.projects) == number_projects)
        assert(len(instance.students) == number_students)