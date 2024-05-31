from gurobipy import GRB
import gurobipy as gp

from data_schema import Project, Student, Instance, Solution

class _StudentProjectVars():
    def __init__(self, students, projects, model) -> None:
        self._students = students
        self._projects = projects

        self._model = model
    
        #variables whether student is in project
        self.vars_student_in_project = {
            (student, project):{"var": self._model.addVar(vtype=gp.GRB.BINARY, name=f"x_{student.matr_number}_{project.id}"),
                                "rating": student.projects_ratings[project.id]
                                 } for student in self._students for project in self._projects
        }

    def x(self, student, project_id):
        return self.vars_student_in_project[(student, project_id)]["var"]
    
    def rating(self, student, project_id):
        return self.vars_student_in_project[(student, project_id)]["rating"]
    
    def all_projects_with_student(self, student):
        for project in self._projects:
            yield self.x(student, project)
    
    def all_students_with_project(self, project):
        for student in self._students:
            yield self.x(student, project)

    def __iter__(self):
        return iter(self.vars_student_in_project.items())

        
class _EmptyProjectVars():
    def __init__(self, projects, model) -> None:

        #variable whether project is empty
        self.vars_project_empty = {
            project: model.addVar(vtype=gp.GRB.BINARY, name=f"e_{project.id}") for project in projects
        }

    def x(self, project):
        return self.vars_project_empty[project]

class _ProgrammingVars():
    
    def __init__(self, students, projects, model) -> None:   
        self._students = students
        self._projects = projects
        self._model = model

        self.vars_programming_language_student_in_project = {
            (programming_language ,student, project): self._model.addVar(vtype=gp.GRB.BINARY, name=f"p_{programming_language}_{student.matr_number}_{project.id}")
            for student in students 
            for project in projects 
            for programming_language in projects[project.id].programming_requirements 
            if programming_language in student.programming_language_ratings
        }
    
    #var programming student in project
    def x(self, programming_language, student, project):
        if (programming_language, student, project) not in self.vars_programming_language_student_in_project:
            return None
        return self.vars_programming_language_student_in_project[(programming_language, student, project)]
    
    def __iter__(self):
        """
        Iterate over all variables.
        """
        return iter(self.vars_programming_language_student_in_project.values())

    def all_languages(self, student, project):
        for programming_language in project.programming_requirements:
            if self.x(programming_language, student, programming_language) is not None:
                yield self.x(programming_language, student, project)

    def all_students(self, programming_language, project):
        for student in self._students: 
            if self.x(programming_language, student, programming_language) is not None:
                yield self.x(programming_language, student, project)

class SepSolver():

    def __init__(self, instance: Instance):
        self.students = instance.students
        self.projects = list(instance.projects.values())
    
        #calculate how good student matches project

        self._model = gp.Model()

        self._studentProjectVars = _StudentProjectVars(students=self.students, projects=self.projects, model=self._model)
        self._emptyProjectVars = _EmptyProjectVars(projects=self.projects, model=self._model)
        self._programmingVars = _ProgrammingVars(students=self.students, projects=self.projects, model=self._model)

        #enforce that every student is in exactly one project
        for student in self.students:
            self._model.addConstr(sum(self._studentProjectVars.all_projects_with_student(student)) == 1)

        #enforce that every project has only a limit amount of students participating
        for project in self.projects:
            self._model.addConstr(sum(self._studentProjectVars.all_students_with_project(project)) <= project.capacity)
        
        #enforce that every project is empty or has a mimum number of participants 
        for project in self.projects:
            self._model.addConstr(sum(self._studentProjectVars.all_students_with_project(project)) <= self._emptyProjectVars.x(project) * self.projects[project.id].capacity)
            self._model.addConstr(sum(self._studentProjectVars.all_students_with_project(project)) >= self._emptyProjectVars.x(project) *  self.projects[project.id].min_capacity)

        #programming skills soft constraint
        #every student is assigned at most one role in one project
        #for student in self.students:
        #    self._model.addConstr(sum([self._project_vars.var_programming_language_student_in_project(programming_language, student.matr_number, project_id) for project_id in self.projects for programming_language in self.projects[project_id].programming_requirements 
        #                               if self._project_vars.var_programming_language_student_in_project(programming_language, student.matr_number, project_id) is not None]) <= 1)

        #enforce that student is only assigned one for role for a project he is in
        for student in self.students:
            for project in self.projects:
                self._model.addConstr(sum(self._programmingVars.all_languages(student, project)) <= self._studentProjectVars.x(student, project))

        #enforce that only the necessary number of students is to be counted
        for project in self.projects:
            for programming_language in self.projects[project.id].programming_requirements:
                self._model.addConstr(sum(self._programmingVars.all_students(programming_language, project)) <= project.programming_requirements[programming_language])

        #enforce project vetos
        for project in self.projects:
            self._model.addConstr(sum([self._studentProjectVars.x(student, project) for student in project.veto]) == 0)
        
        #set objective
        self._model.setObjective(sum([self._studentProjectVars.x(student, project) * self._studentProjectVars.rating(student, project) for project in self.projects for student in self.students]) + 
                                     sum([var for var in self._programmingVars]), gp.GRB.MAXIMIZE)

    def solve(self) -> Solution:
        self._model.optimize()
        if self._model.status == GRB.OPTIMAL:
            print("Optimal")

        projects = {project.id :[] for project in self.projects}

        for project in self.projects:
            for student in self.students:
                if self._studentProjectVars.x(student, project).X > 0.5:
                    projects[project.id].append(student)
                    print(f"{project.id}", student.matr_number)

        return Solution(projects=projects)