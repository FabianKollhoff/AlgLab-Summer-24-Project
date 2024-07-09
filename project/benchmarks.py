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
        #self.log_programming_requirements()
        self.log_opt_sizes()

    def log_rating_sums(self):
        # plot bar chart for student ratings in solution
        ratings = [1, 2, 3, 4, 5]
        rating_sums = {rat: 0 for rat in ratings}
        for proj in self.solution.projects:
            for stu in self.solution.projects[proj]:
                rating_sums[stu.projects_ratings[proj]] += 1

        x = np.array(ratings)
        y = np.array(list(rating_sums.values()))

        # get current figure
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
        # logger.info('The median group size in the solution is: %i', group_sizes[round(len(group_sizes) / 2)])

    def log_proj_util(self):
        # log the utilization of every individual project
        utils = []
        for proj in self.solution.projects:
            # logger.info('The utilization of project %s is: %f', self.instance.projects[proj].name, len(self.solution.projects[proj]) / self.instance.projects[proj].capacity)
            print(
                f"The utilization of project {self.instance.projects[proj].name} is: {len(self.solution.projects[proj]) / self.instance.projects[proj].capacity}"
            )
            utils.append(
                len(self.solution.projects[proj])
                / self.instance.projects[proj].capacity
            )
        # create plot
        projs = list(self.solution.projects)
        x = np.array(projs)
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
        languages = list(self.instance.students[0].programming_language_ratings.keys())
        for proj in self.solution.projects:
            percentages = []

            for lang, req in self.instance.projects[proj].programming_requirements.items():
                # get number of students with language skill > required skill for this lang
                num_stu = sum(1 for stu in self.solution.projects[proj] if stu.programming_language_ratings[lang] > req)
                percentages.append(num_stu/len(self.solution.projects[proj]))
            x = list(range(len(languages)))
            barplot = plt.bar(x, percentages, width=0.5, color='b', align='center')
            plt.bar_label(barplot, labels=[str(int(el*100)) + "%" for el in percentages], label_type="edge")
            plt.title(" % of students that meet the programming requirement")
            plt.xticks(x, languages)
            plt.show()
        return plt.gcf()
    
    def log_opt_sizes(self):
        #for each project in solution: plot size in solution and opt_size
        # create plot
        projs = list(self.solution.projects)
        x = np.arange(len(projs))
        y = np.array([self.instance.projects[proj].opt_size for proj in self.instance.projects])
        bar1 = plt.bar(x - 0.2, y, width=0.2, color="r", label='Optimal Sizes')
        plt.bar_label(bar1, labels=y, label_type="edge")

        y = np.array([len(self.solution.projects[proj]) for proj in self.instance.projects])
        bar2 = plt.bar(x, y, width=0.2, color="b", label='actual sizes')
        plt.bar_label(bar2, labels=y, label_type="edge")

        y = np.array([self.instance.projects[proj].capacity for proj in self.instance.projects])
        bar3 = plt.bar(x + 0.2, y, width=0.2, color="g", label='capacity')
        plt.bar_label(bar3, labels=y, label_type="edge")
        
        plt.title("Project sizes in solution vs optimal size vs capacity")
        plt.xticks(x, projs)
        plt.xlabel("Projects")
        plt.ylabel("Number of students")
        plt.legend()
        plt.show()
        return x,y




if __name__ == "__main__":
    pass
