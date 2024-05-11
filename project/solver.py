from gurobipy import GRB
import gurobipy as gp

from data_schema import Project, Student, Instance, Solution

class SepSolver():

    def __init__(self, instance: Instance):
        self.students = instance.students
        self.projects = instance.projects

        self._model = gp.Model()


        #x_(student, project) checks whether student is in project
        self.student_project_selection = {
            (student.matr_number, project):{"var": self._model.addVar(vtype=gp.GRB.BINARY, name=f"x_{student.matr_number}_{project}"),
                                            "rating": student.projects_ratings[project]
                                 } for student in self.students for project in self.projects
        }

        #enforce that every student is in exactly one project
        for student in self.students:
            self._model.addConstr(sum([self.student_project_selection[(student.matr_number, project)]["var"] for project in self.projects]) == 1)

        #enforce that every project has only a limit amount of students participating
        for project in self.projects:
            self._model.addConstr(sum([self.student_project_selection[(student.matr_number, project)]["var"] for student in self.students]) 
                                  <= self.projects[project].capacity)
        
        #set objective
        self._model.setObjective(sum(
            [self.student_project_selection[(student.matr_number, project)]["var"] * self.student_project_selection[(student.matr_number, project)]["rating"] for project in self.projects for student in self.students]
            , gp.GRB.MAXIMIZE)
            )

    def solve(self) -> Solution:
        self._model.optimize()
        if self._model.status == GRB.OPTIMAL:
            print("Optimal")

        projects = {project:[] for project in self.projects}

        for project in self.projects:
            for student in self.students:
                if self.student_project_selection[(student.matr_number, project)]["var"].X > 0.5:
                    projects[project].append(student)
                    print(f"{project}", student.matr_number)

        return Solution(projects=projects)