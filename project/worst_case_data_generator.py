from data_schema import Instance, Project, Student
from ortools.sat.python import cp_model
import numpy as np
import random
import math

class Generator():
    def randomProjectCapacity(self):
        capacity = random.randint(5, 16)
        self.sumProjectsCapacity += capacity
        min_capacity = random.randint(5, capacity)
        return (capacity, min_capacity)
    
    def genererateProgrammingRequirements(self):
        return {
            "Python": random.randint(0, 3),
            "Java": random.randint(0, 3),
            "C/C++": random.randint(0, 3),
            "PHP": random.randint(0, 3),
            "SQL": random.randint(0, 3),
        }
    
    def generateNormalProject(self, i):
        capacity, min_capacity = self.randomProjectCapacity()
        return Project(
            id=i,
            name=str(i),
            capacity=capacity,
            min_capacity=min_capacity,
            veto=[],
            programming_requirements=self.genererateProgrammingRequirements(),
        )
        
    def generateNormalProjects(self, number_projects, number_students):
        projects = {i: self.generateNormalProject(i) for i in range(number_projects)}
        while self.sumProjectsCapacity < number_students:
            for project in projects:
                randomAdative = random.randint(1, 6)
                self.sumProjectsCapacity += randomAdative
                projects[project].capacity += randomAdative
                if self.sumProjectsCapacity > number_students:
                    break
        print(self.sumProjectsCapacity)
        return projects
    
    def randomStudentType(self):
         # create a random type of student. types differ in their capabilities in different programming languages
        rating = random.random()
        distribution = (0.2, 0.1, 0.4, 0.1)
        if rating <= distribution[0]:
            # cracked student
            skills = (4, 4, 4, 4, 4)
        if rating > distribution[0] and rating <= distribution[0] + distribution[1]:
            # basic student
            skills = (2, 3, 3, 1, 2)
        if (
            rating > distribution[0] + distribution[1]
            and rating <= distribution[0] + distribution[1] + distribution[2]
        ):
            # python bro
            skills = (4, 2, 2, 2, 1)
        if (
            rating > distribution[0] + distribution[1] + distribution[2]
            and rating
            <= distribution[0] + distribution[1] + distribution[2] + distribution[3]
        ):
            # web developer
            skills = (3, 2, 2, 4, 4)
        if (
            rating
            > distribution[0] + distribution[1] + distribution[2] + distribution[3]
        ):
            # got here by copying homework
            skills = (1, 1, 1, 1, 1)
        return skills

    def randomStudentRankingProject(self, project_distribution):
        # students give a project a random rating, depending on the probabilities calculated in calculateRatingProbabilities()
        rating = random.random()
        if rating <= project_distribution[0]:
            return 1
        if rating <= project_distribution[0] + project_distribution[1]:
            return 2
        if (
            rating
            <= project_distribution[0]
            + project_distribution[1]
            + project_distribution[2]
        ):
            return 3
        if (
            rating
            <= project_distribution[0]
            + project_distribution[1]
            + project_distribution[2]
            + project_distribution[3]
        ):
            return 4
        return 5
    
    def generateSkillRatings(self):
        # create a dict consisting of all programming languages and the skill level of the student
        skills = self.randomStudentType()
        skill_dict = {"Python": skills[0]}
        skill_dict.update({"Java": skills[1]})
        skill_dict.update({"C/C++": skills[2]})
        skill_dict.update({"SQL": skills[3]})
        skill_dict.update({"PHP": skills[4]})
        return skill_dict
    
    def generateDistribution(self, projects):
        # generate a random distribution of the average rating each project gets from the students
        number_projects = len(projects)

        # start with an average rating of 3
        average_ratings = [3 for i in range(number_projects)]

        # generate noise to increase spread
        jitter_amount = 2
        noise = np.random.uniform(
            low=-jitter_amount, high=jitter_amount, size=number_projects
        )
        # add noise to the average rating to create a diverse number of average ratings
        average_ratings = average_ratings + noise

        # Clamp ratings to be between 1 and 5
        average_ratings = np.clip(average_ratings, 1, 5)
        return {
            project: self.calculateRatingProbabilities(rating)
            for project, rating in zip(projects, average_ratings)
        }

    def calculateRatingProbabilities(self, average_rating):
        model = cp_model.CpModel()
        # define variables for probabilities, elevate the upper bound because we are working with integers
        p1 = model.NewIntVar(0, 100, "p1")
        p2 = model.NewIntVar(0, 100, "p2")
        p3 = model.NewIntVar(0, 100, "p3")
        p4 = model.NewIntVar(0, 100, "p4")
        p5 = model.NewIntVar(0, 100, "p5")
        # ensure that probabilities add up to 1
        model.Add(p1 + p2 + p3 + p4 + p5 == 100)
        # ensure that probabilities are not to small
        model.Add(p1 >= 10)
        model.Add(p2 >= 10)
        model.Add(p3 >= 10)
        model.Add(p4 >= 10)
        model.Add(p5 >= 10)
        # minimize distance between sum of weighted probabilities and average_rating
        difference = model.NewIntVar(-10000, 10000, "difference")
        abs_difference = model.NewIntVar(0, 10000, "abs_difference")
        model.Add(
            difference
            == (1 * p1 + 2 * p2 + 3 * p3 + 4 * p4 + 5 * p5) - int(average_rating * 100)
        )
        model.AddAbsEquality(abs_difference, difference)
        model.Minimize(abs_difference)
        # solve model, return prababilities as a list
        solver = cp_model.CpSolver()
        status = solver.Solve(model)
        probabilities = []
        # if feasible, return the probabillities of each rating
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            total = (
                solver.Value(p1)
                + solver.Value(p2)
                + solver.Value(p3)
                + solver.Value(p4)
                + solver.Value(p5)
            )
            probabilities = [
                solver.Value(p1) / total,
                solver.Value(p2) / total,
                solver.Value(p3) / total,
                solver.Value(p4) / total,
                solver.Value(p5) / total,
            ]
        return probabilities
    
    def generateNormalStudents(self, number_students):
        students = []
        # generate distribution of average ratings
        self.distribution = self.generateDistribution(self.projects)
        # generate the pre-defined friendgroups
        friendships = self.generateFriendgroups(number_students)
        for i in range(number_students):
            student = Student(
                last_name="Doe",
                first_name="Joe",
                matr_number=i,
                projects_ratings={},
                programming_language_ratings=self.generateSkillRatings(),
                friends=friendships[i],
            )
            students.append(student)
        return students
    
    def generateRandomFriends(self, student_matr, number_students):
        # sample from 0-2 random matr_numbers as friends of student. Make sure own matr_number not in friends
        num_friends = random.randint(0, 2)
        nums = list(range(number_students))
        nums.remove(student_matr)

        return random.sample(nums, num_friends)
    
    def generateFriendgroups(self, number_students):
        # alternative: after students are generated, generate friend groups and add them individually to students list. To make sure
        # friend relationship is mutual. Have pre-generated dict (for every student give their friends)
        # generate some friend group, make sure these groups dont overlap. Groups of size 2 or 3
        nums = list(range(number_students))
        # get number_studens/3 samples of distict groups of 2 or 3 students
        groups = []
        friends = {i: [] for i in nums}
        for _i in range(int(number_students/3)):
            size = random.randint(2, 3)
            print(f"students{number_students}, size{size}, nums{nums}")
            group = random.sample(nums, size)
            for stu in group:
                nums.remove(stu)
            groups.append(group)
        # add the friend relations to the friends dict
        for group in groups:
            for stu in group:
                friends[stu] = [i for i in group if i != stu]

        return friends
    
    def generateProjectsRatings(self):
        return {
            project: self.randomStudentRankingProject(self.distribution[project])
            for project in self.projects
        }
        
    def generateVetos(self):
        prohibited_students = []
        score = random.random()
        # low probability of vetos
        if score <= 0.1:
            prohibited_students = random.sample(
                # only one to four students (depending on the total number of students)
                self.students,
                math.ceil(math.log10(len(self.students))) + 1,
            )
        return prohibited_students
    
    'worst case method: uniform skill requirements'
    def genererateUniformProgrammingRequirements(self, language):
        # every project requires expert skills in one programming language
        languages = ["Python", "Java", "C/C++", "PHP", "SQL"]
        requirements = {}
        for l in languages:
            if l == language:
                requirements.update({language: 3})
            else:
                requirements.update({l: random.randint(0, 3)})
        return requirements
    
    'worst case method: uniform skill requirements'
    def generateUniformRequirementsProject(self, i):
        capacity, min_capacity = self.randomProjectCapacity()
        return Project(
            id=i,
            name=str(i),
            capacity=capacity,
            min_capacity=min_capacity,
            veto=[],
            programming_requirements=self.genererateProgrammingRequirements(),
        )
    'worst case method: uniform skill requirements'    
    def generateUniformRequirementsProjects(self, number_projects, number_students):
        projects = {i: self.generateUniformRequirementsProject(i) for i in range(number_projects)}
        while self.sumProjectsCapacity < number_students:
            for project in projects:
                randomAdative = random.randint(1, 6)
                self.sumProjectsCapacity += randomAdative
                projects[project].capacity += randomAdative
                if self.sumProjectsCapacity > number_students:
                    break
        print(self.sumProjectsCapacity)
        return projects
    
    'worst case method: uniform skill requirements'
    def generateUniformRequirementsInstance(self, number_projects, number_students):
        self.sumProjectsCapacity = 0
        self.projects = self.generateUniformRequirementsProjects(
            number_projects=number_projects, number_students=number_students
        )
        self.students = self.generateNormalStudents(number_students=number_students)
        for student in self.students:
            student.projects_ratings = self.generateProjectsRatings()
        for project in self.projects:
            self.projects[project].veto = self.generateVetos()
        self.instance = Instance(students=self.students, projects=self.projects)

        return self.instance
    
    'worst case method: extreme ratings'
    def generateExtremeStudents(self, number_students):
        students = []
        # generate the pre-defined friendgroups
        friendships = self.generateFriendgroups(number_students)
        for i in range(number_students):
            student = Student(
                last_name="Doe",
                first_name="Joe",
                matr_number=i,
                projects_ratings={},
                programming_language_ratings=self.generateSkillRatings(),
                friends=friendships[i],
            )
            students.append(student)
        return students
    
    'worst case method: extreme ratings 5'
    def studentExtremeProjectRatingFive(self):
        return 5
    
    'worst case method: extreme ratings 5'
    def generateExtremeProjectsRatingsFive(self):
        return {
            project: self.studentExtremeProjectRatingFive()
            for project in self.projects
        }
    
    'worst case method: extreme ratings 5'
    def generateExtremeInstanceFive(self, number_projects, number_students):
        self.sumProjectsCapacity = 0
        self.projects = self.generateNormalProjects(
            number_projects=number_projects, number_students=number_students
        )
        self.students = self.generateExtremeStudents(number_students=number_students)
        for student in self.students:
            student.projects_ratings = self.generateExtremeProjectsRatingsFive()
        for project in self.projects:
            self.projects[project].veto = self.generateVetos()
        self.instance = Instance(students=self.students, projects=self.projects)

        return self.instance
    
    'worst case method: extreme ratings 1'
    def studentExtremeProjectRatingOne(self):
        return 1
    
    'worst case method: extreme ratings 1'
    def generateExtremeProjectsRatingsOne(self):
        return {
            project: self.studentExtremeProjectRatingOne()
            for project in self.projects
        }
    
    'worst case method: extreme ratings 1'
    def generateExtremeInstanceOne(self, number_projects, number_students):
        self.sumProjectsCapacity = 0
        self.projects = self.generateNormalProjects(
            number_projects=number_projects, number_students=number_students
        )
        self.students = self.generateExtremeStudents(number_students=number_students)
        for student in self.students:
            student.projects_ratings = self.generateExtremeProjectsRatingsOne()
        for project in self.projects:
            self.projects[project].veto = self.generateVetos()
        self.instance = Instance(students=self.students, projects=self.projects)

        return self.instance
    
    'worst case method: extreme vetos'
    def generateExtremeVetos(self, project):
        # one project has a lot of vetos
        prohibited_students = []
        if project == 1:
            prohibited_students = random.sample(
                # 10% of all student are vetoed against
                self.students,
                int(len(self.students)/5),
            )
        return prohibited_students
    
    'worst case method: extreme vetos'
    def generateExtremeVetoInstance(self, number_projects, number_students):
        self.sumProjectsCapacity = 0
        self.projects = self.generateNormalProjects(
            number_projects=number_projects, number_students=number_students
        )
        self.students = self.generateNormalStudents(number_students=number_students)
        for student in self.students:
            student.projects_ratings = self.generateProjectsRatings()
        for project in self.projects:
            self.projects[project].veto = self.generateExtremeVetos(1)
        self.instance = Instance(students=self.students, projects=self.projects)

        return self.instance
    
g = Generator()
# generate uniform skill requirements
data1 = g.generateUniformRequirementsInstance(
        number_students=20, number_projects=200
    ).model_dump_json(indent=2)
with open(f"instances/data_worst_case_uniform_requirements.json", "w") as f:
        f.write(data1)
# generate extreme rating 5
data2 = g.generateExtremeInstanceFive(
        number_students=20, number_projects=200
    ).model_dump_json(indent=2)
with open(f"instances/data_worst_case_extreme_rating_5.json", "w") as f:
        f.write(data2)
# generate extreme rating 1
data3 = g.generateExtremeInstanceOne(
        number_students=20, number_projects=200
    ).model_dump_json(indent=2)
with open(f"instances/data_worst_case_extreme_rating_1.json", "w") as f:
        f.write(data3)
# generate extreme vetos
data4 = g.generateExtremeVetoInstance(
        number_students=20, number_projects=200
    ).model_dump_json(indent=2)
with open(f"instances/data_worst_case_extreme_vetos.json", "w") as f:
        f.write(data4)
        