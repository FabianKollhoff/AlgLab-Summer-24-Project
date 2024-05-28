from data_schema import Project, Student, Instance
import json

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

    def generateProject(self, i):
        capacity, min_capacity = self.randomProjectCapacity()
        return Project(id=i, name=str(i), capacity=capacity, min_capacity=min_capacity)

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

    def generateStudents(self, number_students):
        students = []
        #generate the pre-defined friendgroups
        friendships = self.generateFriendgroups(number_students)
        for i in range(number_students):
            #student = Student(last_name="Doe", first_name="Joe", matr_number=i, projects_ratings=self.generateProjectsRatings(), friends=self.generateRandomFriends(i, number_students))
            student = Student(last_name="Doe", first_name="Joe", matr_number=i, projects_ratings=self.generateProjectsRatings(), friends=friendships[i])
            students.append(student)
        return students
    
    def generateRandomFriends(self, student_matr, number_students):
        # smaple from 0-2 random matr_numbers as friends of student. Make sure own matr_number not in friends
        num_friends = random.randint(0, 2)
        #print(number_students, student_matr)
        nums = list(range(number_students))
        nums.remove(student_matr)
        friends = random.sample(nums, num_friends)
        #print(friends)
        return friends
    
    def generateFriendgroups(self, number_students):
        #alternative: after students are generated, generate friend groups and add them individually to students list. To make sure
        # friend relationship is mutual. Have pre-generated dict (for every student give their friends)
        # generate some friend group, make sure these groups dont overlap. Groups of size 2 or 3
        nums = list(range(number_students))
        #get 20 samples of distict groups of 2 or 3 students
        groups = []
        friends = {i: [] for i in nums}
        for i in range(20):
            size = random.randint(2,3)
            group = random.sample(nums, size)
            for stu in group:
                nums.remove(stu)
            groups.append(group)
        #add the friend relations to the friends dict
        for group in groups:
            for stu in group:
                friends[stu] = [i for i in group if i != stu]
        
        return friends



    def generateInstance(self, number_projects, number_students):
        self.sumProjectsCapacity = 0
        self.projects = self.generateProjects(number_projects=number_projects, number_students=number_students)
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
        assert(len(instance.projects) == number_projects)
        assert(len(instance.students) == number_students)