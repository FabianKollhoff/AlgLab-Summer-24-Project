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

        self.vars_programming_language_student_in_project = {
            (programming_language ,student.matr_number, project_id): self._model.addVar(vtype=gp.GRB.BINARY, name=f"p_{programming_language}_{student.matr_number}_{project_id}")
              for student in self.students for project_id in self.projects for programming_language in self.projects[project_id].programming_requirements if programming_language in self.students[student.matr_number].programming_language_ratings
        }

    def var_student_in_project(self, student_matr, project_id):
        return self.vars_student_in_project[(student_matr, project_id)]["var"] 
    
    def rating_student_in_project(self, student_matr, project_id):
        return self.vars_student_in_project[(student_matr, project_id)]["rating"] 
    
    def var_project_is_empty(self, project_id):
        return self.vars_project_empty[project_id]
    
    def var_programming_language_student_in_project(self, programming_language, student_matr, project_id):
        if (programming_language, student_matr, project_id) not in self.vars_programming_language_student_in_project:
            return None
        return self.vars_programming_language_student_in_project[(programming_language, student_matr, project_id)]

class SepSolver():

    def __init__(self, instance: Instance):
        self.students = instance.students
        self.projects = instance.projects

        #calculate how good student matches project

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

        #programming skills soft constraint
        #every student is assigned at most one role in one project
        #for student in self.students:
        #    self._model.addConstr(sum([self._project_vars.var_programming_language_student_in_project(programming_language, student.matr_number, project_id) for project_id in self.projects for programming_language in self.projects[project_id].programming_requirements 
        #                               if self._project_vars.var_programming_language_student_in_project(programming_language, student.matr_number, project_id) is not None]) <= 1)

        #enforce that student is only assigned one for role for a project he is in
        for student in self.students:
            for project in self.projects:
                self._model.addConstr(sum([self._project_vars.var_programming_language_student_in_project(programming_language, student.matr_number, project_id) for programming_language in self.projects[project_id].programming_requirements if self._project_vars.var_programming_language_student_in_project(programming_language, student.matr_number, project_id) is not None]) <= self._project_vars.var_student_in_project(student.matr_number, project))

        #enforce that only the necessary number of students are to be counted
        for project in self.projects:
            for programming_language in self.projects[project_id].programming_requirements:
                self._model.addConstr(sum([self._project_vars.var_programming_language_student_in_project(programming_language, student.matr_number, project_id) for student in self.students if self._project_vars.var_programming_language_student_in_project(programming_language, student.matr_number, project_id) is not None ]) <= self.projects[project_id].programming_requirements[programming_language])

        #enforce project vetos
        for project in self.projects:
            self._model.addConstr(sum([self._project_vars.var_student_in_project(student.matr_number, project) for student in self.projects[project].veto]) == 0)
        
        #set objective
        self._model.setObjective(sum([self._project_vars.var_student_in_project(student.matr_number, project) * self._project_vars.rating_student_in_project(student.matr_number, project) for project in self.projects for student in self.students]) + 
                                     sum([var_programming_language_student_in_project for _,var_programming_language_student_in_project in self._project_vars.vars_programming_language_student_in_project.items()]), gp.GRB.MAXIMIZE)

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