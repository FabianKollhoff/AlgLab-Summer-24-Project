from pydantic import BaseModel
from typing import Dict, List
from data_schema import Project, Student, Instance, Solution
import logging
import matplotlib.pyplot as plt
import numpy as np

class Benchmarks(BaseModel):
    def __init__(self, solution: Solution, instance: Instance):
        self.instance = instance
        self.solution = solution
        self.logger = logging.getLogger('logger')

    def log(self):
        #ALTERNATIVE: store all the statistics as lists/dict and only log them on demand e.g. benchmarks.log_meadian_group_size() etc.
        #compute average utilazation of project capacities
        avg_utilization = sum(len(self.solution[proj]) / self.instance.projects[proj].capacity for proj in self.solution.projects) / len(self.solution.projects)
        self.logger.info('The average utilization of project capacities is: %f', avg_utilization)

        #log the utilization of every individual project
        for proj in self.solution.projects:
            self.logger.info('The utilization of project %s is: %f', self.instance.projects[proj].name, len(self.solution[proj]) / self.instance.projects[proj].capacity)

        #log the median group size
        group_sizes = [len(self.solution.projects[proj]) for proj in self.solution.projects].sort()
        self.logger.info('The median group size in the solution is: %i', group_sizes[round(len(group_sizes) / 2)])

        #for each project log the average rating per student
        for proj in self.solution.projects:
            avg_rating = sum(stu.projects_ratings[proj] for stu in self.solution.projects[proj]) / len(self.solution.projects[proj])
            self.logger.info('The average student rating of project %s is: %f', self.instance.projects[proj].name, avg_rating)
        
        #log the average rating of students in the solution
        num_students = len(self.instance.students)
        avg_rating_per_student = sum(stu.projects_ratings[proj] for proj in self.solution.projects for stu in self.solution.projects[proj] ) / num_students
        self.logger.info('The average rating of students in solution is: %f', avg_rating_per_student)

        #plot bar chart for student ratings in solution
        ratings = [1, 2, 3, 4 , 5]
        rating_sums = {rat:0 for rat in ratings}
        for proj in self.solution.projects:
            for stu in self.solution.projects[proj]:
                rating_sums[stu.projects_ratings[proj]] += 1
    
        x = np.array(ratings)
        y = np.array(list(rating_sums.values()))
        plt.bar(x,y)
        plt.show()
        #TODO: log the number of partner requests that were fulfilled

        #TODO: 


if __name__ == "__main__":
    liste = [(i,j) for j in range(3) for i in range(5) ]
    print(liste)
