import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from data_schema import Instance, Solution
from pydantic import BaseModel


class Benchmarks(BaseModel):
    instance: Instance
    solution: Solution

    def log(self):
        # logger = logging.getLogger('logger')

        # self.log_avg_util()

        # self.log_proj_util()

        # self.log_median_group_size()

        #self.log_avg_proj_rating()

        # self.log_avg_rating()

        # self.log_rating_sums()
        # TODO: log the number of partner requests that were fulfilled

        # TODO: log graph of friend relations that were (not) fulfilled
        #self.log_friend_graph()
        self.log_programming_requirements()

    def log_rating_sums(self):
        # plot bar chart for student ratings in solution
        ratings = [1, 2, 3, 4, 5]
        rating_sums = {rat: 0 for rat in ratings}
        for project in self.solution.projects:
            for student in self.solution.projects[project]:
                rating_sums[student.projects_ratings[project]] += 1

        x = np.array(ratings)
        y = np.array(list(rating_sums.values()))

        return x,y

    def log_avg_rating(self):
        # log the average rating of students in the solution
        num_students = len(self.instance.students)
        avg_rating_per_student = (
            sum(
                stu.projects_ratings[proj]
                for proj in self.solution.projects
                for stu in self.solution.projects[proj]
            )
            / num_students
        )

        return avg_rating_per_student
        # logger.info('The average rating of students in solution is: %f', avg_rating_per_student)

    def log_avg_proj_rating(self):
        # for each project log the average rating per student
        ratings = []
        for proj in self.solution.projects:
            # if project is empty, continue
            if len(self.solution.projects[proj]) == 0:
                continue
            avg_rating = sum(
                stu.projects_ratings[proj] for stu in self.solution.projects[proj]
            ) / len(self.solution.projects[proj])
            ratings.append(avg_rating)
            # logger.info('The average student rating of project %s is: %f', self.instance.projects[proj].name, avg_rating)
        # x axis are the projects
        projs = list(self.solution.projects)
        x = np.array(projs)
        y = np.array(ratings)
        return x,y

    def log_median_group_size(self):
        # log the median group size
        group_sizes = [
            len(self.solution.projects[proj]) for proj in self.solution.projects
        ]
        group_sizes.sort()
        return group_sizes[round(len(group_sizes) / 2)]
        # logger.info('The median group size in the solution is: %i', group_sizes[round(len(group_sizes) / 2)])

    def log_proj_util(self):
        # log the utilization of every individual project
        utils = []
        project_names = []

        for project in self.solution.projects:
            # logger.info('The utilization of project %s is: %f', self.instance.projects[proj].name, len(self.solution.projects[proj]) / self.instance.projects[proj].capacity)
            print(
                f"The utilization of project {self.instance.projects[project].name} is: {len(self.solution.projects[project]) / self.instance.projects[project].capacity}"
            )
            utils.append(
                len(self.solution.projects[project])
                / self.instance.projects[project].capacity
            )
            project_names.append(self.instance.projects[project].name)
        # create plot
        x = np.array(project_names)
        y = np.array(utils)
        return x,y


    def log_avg_util(self):
        # compute average utilazation of project capacities
        avg_utilization = sum(
            len(self.solution.projects[proj]) / self.instance.projects[proj].capacity
            for proj in self.solution.projects
        ) / len(self.solution.projects)
        # logger.info('The average utilization of project capacities is: %f', avg_utilization)
        print(f"The average utilization of project capacities is: {avg_utilization}")

    def log_friend_graph(self):
        graph = nx.Graph()
        num_greens = 0
        num_reds = 0
        # for each student in solution add friends as edges in graph
        for proj in self.solution.projects:
            for student in self.solution.projects[proj]:
                for friend in student.friends:
                    # check if this friend is in the same project: if yes make edge green, if not red
                    nums = [stu.matr_number for stu in self.solution.projects[proj]]
                    if friend in nums:
                        graph.add_edge(student.matr_number, friend, color="green")
                        num_greens += 1
                    else:
                        graph.add_edge(student.matr_number, friend, color="red")
                        num_reds += 1

        layout = nx.kamada_kawai_layout(graph)
        colors = [graph.edges[e]["color"] for e in graph.edges]
        nx.draw_networkx(
            graph, pos=layout, edge_color=colors, node_size=15, with_labels=False
        )
        fig, ax = plt.subplots()
        ax.title(f"Friend graph. G:{num_greens} R:{num_reds}")
        ax.show()
        return ax.gcf()

    def log_programming_requirements(self):
        # in solution: For each project log for each programming language % of how students that meet requirement
        project_requirements_fullfilled_precentage = []
        project_names = []
        for project_id in self.solution.projects:
            project = self.instance.projects[project_id]
            project_requirements_count = 0.0
            fullfilled_programming_requirements = 0.0
            for programming_language in project.programming_requirements:
                project_requirements_count += project.programming_requirements[programming_language]
            if project_requirements_count == 0:
                project_requirements_fullfilled_precentage.append(1)
                project_names.append(project.name)
                continue

            for student in self.solution.projects[project_id]:
                fullfilled_programming_requirements += (self.solution.roles[student.matr_number]/4)

            project_requirements_fullfilled_precentage.append(fullfilled_programming_requirements/project_requirements_count)
            project_names.append(project.name)
            
            # create plot
        x = np.array(project_names)
        y = np.array(project_requirements_fullfilled_precentage)
        return x,y


if __name__ == "__main__":
    pass
