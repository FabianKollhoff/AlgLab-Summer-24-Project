from pydantic import BaseModel
from typing import Dict, List
from data_schema import Project, Student, Instance, Solution
import logging
import matplotlib.pyplot as plt
import numpy as np
import networkx as nx

class Benchmarks(BaseModel):
    instance: Instance
    solution: Solution

    def log(self):
        #logger = logging.getLogger('logger')
        #ALTERNATIVE: store all the statistics as lists/dict and only log them on demand e.g. benchmarks.log_meadian_group_size() etc.
        
        #self.log_avg_util()
        
        #self.log_proj_util()
        
        #self.log_median_group_size()
        
        #self.log_avg_proj_rating()

        #self.log_agv_rating()

        #self.log_rating_sums()
        #TODO: log the number of partner requests that were fulfilled

        #TODO: log graph of friend relations that were (not) fulfilled
        self.log_friend_graph()

    def log_rating_sums(self):
        #plot bar chart for student ratings in solution
        ratings = [1, 2, 3, 4 , 5]
        rating_sums = {rat:0 for rat in ratings}
        for proj in self.solution.projects:
            for stu in self.solution.projects[proj]:
                rating_sums[stu.projects_ratings[proj]] += 1
    
        x = np.array(ratings)
        y = np.array(list(rating_sums.values()))
        plt.bar(x,y)
        plt.title("Occurence of rating in solution")
        plt.show()
    
    def log_agv_rating(self):
        #log the average rating of students in the solution
        num_students = len(self.instance.students)
        avg_rating_per_student = sum(stu.projects_ratings[proj] for proj in self.solution.projects for stu in self.solution.projects[proj] ) / num_students
        #logger.info('The average rating of students in solution is: %f', avg_rating_per_student)
    
    def log_avg_proj_rating(self):
        #for each project log the average rating per student
        ratings = []
        for proj in self.solution.projects:
            #if project is empty, continue
            if len(self.solution.projects[proj]) == 0:
                continue
            avg_rating = sum(stu.projects_ratings[proj] for stu in self.solution.projects[proj]) / len(self.solution.projects[proj])
            ratings.append(avg_rating)
            #logger.info('The average student rating of project %s is: %f', self.instance.projects[proj].name, avg_rating)
        #x axis are the projects
        projs = [i for i in self.solution.projects]
        x = np.array(projs)
        y = np.array(ratings)
        plt.bar(x,y)
        plt.title("Average rating of students in project")
        plt.show()

    def log_median_group_size(self):
        #log the median group size
        group_sizes = [len(self.solution.projects[proj]) for proj in self.solution.projects]
        group_sizes.sort()
        #logger.info('The median group size in the solution is: %i', group_sizes[round(len(group_sizes) / 2)])

    def log_proj_util(self):
        #log the utilization of every individual project
        utils = []
        for proj in self.solution.projects:
            #logger.info('The utilization of project %s is: %f', self.instance.projects[proj].name, len(self.solution.projects[proj]) / self.instance.projects[proj].capacity)
            print(f"The utilization of project {self.instance.projects[proj].name} is: {len(self.solution.projects[proj]) / self.instance.projects[proj].capacity}")
            utils.append(len(self.solution.projects[proj]) / self.instance.projects[proj].capacity)
        #create plot
        projs = [i for i in self.solution.projects]
        x = np.array(projs)
        y = np.array(utils)
        plt.bar(x,y)
        plt.title("Utilization of project capacities")
        plt.show()

    def log_avg_util(self):
        #compute average utilazation of project capacities
        avg_utilization = sum(len(self.solution.projects[proj]) / self.instance.projects[proj].capacity for proj in self.solution.projects) / len(self.solution.projects)
        #logger.info('The average utilization of project capacities is: %f', avg_utilization)
        print(f"The average utilization of project capacities is: {avg_utilization}")

    def log_friend_graph(self):
        graph = nx.Graph()
        #for each student in solution add friends as edges in graph
        for proj in self.solution.projects:
            for student in self.solution.projects[proj]:
                for friend in student.friends:
                    #check if this friend is in the same project: if yes make edge green, if not red
                    nums = [stu.matr_number for stu in self.solution.projects[proj]]
                    if friend in nums:
                        graph.add_edge(student.matr_number, friend, color="green")
                    else:
                        graph.add_edge(student.matr_number, friend, color="red")

        layout = nx.kamada_kawai_layout(graph)
        colors = [graph.edges[e]["color"] for e in graph.edges]
        nx.draw_networkx(graph, pos=layout,edge_color=colors, node_size=15, with_labels=False)
        plt.title("Friend graph")
        plt.show()


if __name__ == "__main__":
    pass
