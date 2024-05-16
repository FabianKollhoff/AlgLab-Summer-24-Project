from gurobipy import GRB
import gurobipy as gp

from data_schema import Project, Student, Instance, Solution

class _ProjectVars():
    
    def __init__(self, students, projects, model) -> None:
        
        self.students = students
        self.projects = projects
        
        self._model = model

        #variables whether student is in project
        self.vars_student_in_project = {
            (student.matr_number, project_id):{"var": self._model.addVar(vtype=gp.GRB.BINARY, name=f"x_{student.matr_number}_{project_id}"),
                                            "rating": student.projects_ratings[project_id]
                                 } for student in self.students for project_id in self.projects
        }

        #variable whether project is empty
        self.vars_project_empty = {
            project_id: self._model.addVar(vtype=gp.GRB.BINARY, name=f"e_{project_id}") for project_id in projects
        }

    def var_student_in_project(self, student_matr, project_id):
        return self.vars_student_in_project[(student_matr, project_id)]["var"] 
    
    def rating_student_in_project(self, student_matr, project_id):
        return self.vars_student_in_project[(student_matr, project_id)]["rating"] 
    
    def var_project_is_empty(self, project_id):
        return self.vars_project_empty[project_id]

class SepSolver():

    def __init__(self, instance: Instance):
        self.students = instance.students
        self.projects = instance.projects

        self._model = gp.Model()

        self._project_vars = _ProjectVars(students=self.students, projects=self.projects, model=self._model)

        #enforce that every student is in exactly one project
        for student in self.students:
            self._model.addConstr(sum([self._project_vars.var_student_in_project(student.matr_number, project) for project in self.projects]) == 1)

        #enforce that every project has only a limit amount of students participating
        for project in self.projects:
            self._model.addConstr(sum([self._project_vars.var_student_in_project(student.matr_number, project) for student in self.students]) 
                                  <= self.projects[project].capacity)
        
        #enforce that every project is empty or has a mimum number of participants 
        for project_id in self.projects:
            self._model.addConstr(sum([self._project_vars.var_student_in_project(student.matr_number, project_id) for student in self.students]) <= self._project_vars.var_project_is_empty(project_id=project_id) * self.projects[project_id].capacity)
            self._model.addConstr(sum([self._project_vars.var_student_in_project(student.matr_number, project_id) for student in self.students]) >= self.projects[project_id].min_capacity * self._project_vars.var_project_is_empty(project_id))

        #set objective
        self._model.setObjective(sum([self._project_vars.var_student_in_project(student.matr_number, project) * self._project_vars.rating_student_in_project(student.matr_number, project) for project in self.projects for student in self.students]), gp.GRB.MAXIMIZE)

    def solve(self) -> Solution:
        self._model.optimize()
        if self._model.status == GRB.OPTIMAL:
            print("Optimal")

        projects = {project:[] for project in self.projects}

        for project in self.projects:
            for student in self.students:
                if self._project_vars.var_student_in_project(student.matr_number, project).X > 0.5:
                    projects[project].append(student)
                    print(f"{project}", student.matr_number)

        return Solution(projects=projects)