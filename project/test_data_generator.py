import math
import random

import numpy as np
from data_schema import Instance, Project, Student
from ortools.sat.python import cp_model


class Generator:
    def randomStudentType(self):
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

    def generateProject(self, i):
        capacity, min_capacity = self.randomProjectCapacity()
        return Project(
            id=i,
            name=str(i),
            capacity=capacity,
            min_capacity=min_capacity,
            veto=[],
            programming_requirements=self.genererateProgrammingRequirements(),
        )

    def generateProjects(self, number_projects, number_students):
        projects = {i: self.generateProject(i) for i in range(number_projects)}
        while self.sumProjectsCapacity < number_students:
            for project in projects:
                randomAdative = random.randint(1, 6)
                self.sumProjectsCapacity += randomAdative
                projects[project].capacity += randomAdative
                if self.sumProjectsCapacity > number_students:
                    break
        print(self.sumProjectsCapacity)
        return projects

    def generateProjectsRatings(self):
        return {
            project: self.randomStudentRankingProject(self.distribution[project])
            for project in self.projects
        }

    def generateSkillRatings(self):
        skills = self.randomStudentType()
        skill_dict = {"Python": skills[0]}
        skill_dict.update({"Java": skills[1]})
        skill_dict.update({"C/C++": skills[2]})
        skill_dict.update({"SQL": skills[3]})
        skill_dict.update({"PHP": skills[4]})
        return skill_dict

    def generateStudents(self, number_students):
        students = []
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
        # get 20 samples of distict groups of 2 or 3 students
        groups = []
        friends = {i: [] for i in nums}
        for _i in range(20):
            size = random.randint(2, 3)
            group = random.sample(nums, size)
            for stu in group:
                nums.remove(stu)
            groups.append(group)
        # add the friend relations to the friends dict
        for group in groups:
            for stu in group:
                friends[stu] = [i for i in group if i != stu]

        return friends

    def generateDistribution(self, projects):
        number_projects = len(projects)

        # Generate ratings using a normal distribution with a wider spread
        # average_ratings = np.random.normal(4.5, 1.0, number_projects)
        average_ratings = [3 for i in range(number_projects)]

        # generate noise to increase spread
        jitter_amount = 2
        noise = np.random.uniform(
            low=-jitter_amount, high=jitter_amount, size=number_projects
        )
        # print(f"noise: {noise}")
        average_ratings = average_ratings + noise

        # Clamp ratings to be between 1 and 5
        average_ratings = np.clip(average_ratings, 1, 5)
        # print(average_ratings)
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

    def generateInstance(self, number_projects, number_students):
        self.sumProjectsCapacity = 0
        self.projects = self.generateProjects(
            number_projects=number_projects, number_students=number_students
        )
        self.students = self.generateStudents(number_students=number_students)
        for student in self.students:
            student.projects_ratings = self.generateProjectsRatings()
        for project in self.projects:
            self.projects[project].veto = self.generateVetos()
        self.instance = Instance(students=self.students, projects=self.projects)

        return self.instance


g = Generator()

instance_sizes = [(10, 100), (20, 200), (30, 300), (50, 500), (100, 1000)]

for instance_size in instance_sizes:
    number_projects, number_students = instance_size
    data = g.generateInstance(
        number_students=number_students, number_projects=number_projects
    ).model_dump_json(indent=2)
    with open(f"instances/data_s{number_students}_g{number_projects}.json", "w") as f:
        f.write(data)

    with open(f"instances/data_s{number_students}_g{number_projects}.json") as f:
        test = f.read()
        instance: Instance = Instance.model_validate_json(test)
        assert len(instance.projects) == number_projects
        assert len(instance.students) == number_students
