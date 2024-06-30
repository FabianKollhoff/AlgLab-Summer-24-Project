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

        self.log_avg_proj_rating()

        # self.log_avg_rating()

        # self.log_rating_sums()
        # TODO: log the number of partner requests that were fulfilled

        # TODO: log graph of friend relations that were (not) fulfilled
        #self.log_friend_graph()
        #self.log_programming_requirements()

    def log_rating_sums(self):
        # plot bar chart for student ratings in solution
        ratings = [1, 2, 3, 4, 5]
        rating_sums = {rat: 0 for rat in ratings}
        for proj in self.solution.projects:
            for stu in self.solution.projects[proj]:
                rating_sums[stu.projects_ratings[proj]] += 1

        x = np.array(ratings)
        y = np.array(list(rating_sums.values()))
        barplot = plt.bar(x, y)
        plt.bar_label(barplot, labels=y, label_type="edge")
        plt.title("Occurence of rating in solution")
        plt.show()
        # get current figure
        return plt.gcf()

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
        projs = [i for i in self.solution.projects]
        x = np.array(projs)
        y = np.array(ratings)
        plt.bar(x, y)
        plt.title("Average rating of students in project")
        plt.show()
        return plt.gcf()

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
        projs = [i for i in self.solution.projects]
        x = np.array(projs)
        y = np.array(utils)
        plt.bar(x, y)
        plt.title("Utilization of project capacities")
        plt.show()
        return plt.gcf()

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
        plt.title(f"Friend graph. G:{num_greens} R:{num_reds}")
        plt.show()
        return plt.gcf()

    def log_programming_requirements(self):
        # in solution: For each project log for each programming language if requirement was met.
        # per language 2 bar charts: On the left requirement for language, on the right number of students with skill > 1 for respective language.
        languages = list(self.instance.students[0].programming_language_ratings.keys())
        for proj in self.solution.projects:
            #get list of all requirements
            reqs = []
            num_students_with_skill = []

            ax  = plt.subplot()
            for lang, req in self.instance.projects[proj].programming_requirements.items():
                # get number of students with language skill for this lang
                num_stu = sum(1 for stu in self.solution.projects[proj] if stu.programming_language_ratings[lang] > 1)
                reqs.append(req)
                num_students_with_skill.append(num_stu)
            x = list(range(len(languages)))
            ax.bar([el - 0.2 for el in x], reqs, width=0.4, color='b', align='center', label="re")
            ax.bar([el + 0.2 for el in x], num_students_with_skill, width=0.4, color='r', align='center', label="num students")
            ax.set_title("Programming requirements for Project. B=Required, R=Num students")
            plt.xticks(x, languages)
            plt.show()
        return plt.gcf()


if __name__ == "__main__":
    pass
