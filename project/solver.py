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
        return iter(self.vars_programming_language_student_in_project.items())

    def all_languages(self, student, project):
        for programming_language in project.programming_requirements:
            if self.x(programming_language, student, programming_language) is not None:
                yield self.x(programming_language, student, project)

    def all_students(self, programming_language, project):
        for student in self._students: 
            if self.x(programming_language, student, programming_language) is not None:
                yield self.x(programming_language, student, project)

#better name needed
class _StudentProjectConstraint():
    def __init__(self, students, projects, studentProjectVars, emptyProjectVars, model):
        self._students = students
        self._projects = projects
        self._studentProjectVars = studentProjectVars
        self._emptyProjectVars = emptyProjectVars
        self._model = model

    def _enforce_every_student_in_exactly_one_project(self):
        for student in self._students:
            self._model.addConstr(sum(self._studentProjectVars.all_projects_with_student(student)) == 1)

    def _enforce_every_project_max_number_students(self):
        for project in self._projects:
            self._model.addConstr(sum(self._studentProjectVars.all_students_with_project(project)) <= project.capacity)

    def _enforce_every_project_empty_or_has_minimum_number_students(self):
        for project in self._projects:
            self._model.addConstr(sum(self._studentProjectVars.all_students_with_project(project)) <= self._emptyProjectVars.x(project) * project.capacity)
            self._model.addConstr(sum(self._studentProjectVars.all_students_with_project(project)) >= self._emptyProjectVars.x(project) * project.min_capacity)

    def _enforce_vetos(self):
        #enforce project vetos
        for project in self._projects:
            self._model.addConstr(sum([self._studentProjectVars.x(student, project) for student in project.veto]) == 0)

class _StudentProgrammingConstraint():
    def __init__(self, students, projects, studentProjectVars, programmingVars, model):
        self._students = students
        self._projects = projects
        self._studentProjectVars = studentProjectVars
        self._programmingVars = programmingVars
        self._model = model

    def _enforce_student_only_is_in_one_project_and_has_one_role(self):
        for student in self._students:
            for project in self._projects:
                self._model.addConstr(sum(self._programmingVars.all_languages(student, project)) <= self._studentProjectVars.x(student, project))

    def _enforce_maximum_number_roles_project_assigned(self):
        for project in self._projects:
            for programming_language in project.programming_requirements:
                self._model.addConstr(sum(self._programmingVars.all_students(programming_language, project)) <= project.programming_requirements[programming_language])  

class _RatingObjective():
    def __init__(self, students, projects, studentProjectVars):
        self._students = students
        self._projects = projects
        self._studentProjectVars = studentProjectVars

    def sum(self):
        return sum([self._studentProjectVars.x(student, project) * self._studentProjectVars.rating(student, project) 
                    for project in self._projects 
                    for student in self._students])
    
class _ProgrammingObjective():
    def __init__(self, students, projects, programmingVars):
        self._students = students
        self._projects = projects
        self._programmingVars = programmingVars

    def sum(self):
        to_sum = []
        for student in self._students:
            for project in self._projects:
                for programming_language in project.programming_requirements:
                    to_sum.append(self._programmingVars.x(programming_language,student,project) * student.programming_language_ratings[programming_language])
        return sum(to_sum)

class SepSolver():

    def __init__(self, instance: Instance):
        self.students = instance.students
        self.projects = list(instance.projects.values())
    
        #calculate how good student matches project
        self._model = gp.Model()

        self._studentProjectVars = _StudentProjectVars(students=self.students, projects=self.projects, model=self._model)
        self._emptyProjectVars = _EmptyProjectVars(projects=self.projects, model=self._model)
        self._programmingVars = _ProgrammingVars(students=self.students, projects=self.projects, model=self._model)

        self._studentProjectConstraint = _StudentProjectConstraint(self.students, self.projects, self._studentProjectVars, self._emptyProjectVars, self._model)
        self._studentProgrammingConstraint = _StudentProgrammingConstraint(self.students, self.projects, self._studentProjectVars, self._programmingVars, self._model)
        
        self._studentProjectConstraint._enforce_every_student_in_exactly_one_project()
        self._studentProjectConstraint._enforce_every_project_max_number_students()
        self._studentProjectConstraint._enforce_every_project_empty_or_has_minimum_number_students()
        self._studentProjectConstraint._enforce_vetos()

        self._studentProgrammingConstraint._enforce_student_only_is_in_one_project_and_has_one_role()
        self._studentProgrammingConstraint._enforce_maximum_number_roles_project_assigned()
        

        self._ratingObjective = _RatingObjective(self.students, self.projects, self._studentProjectVars)
        self._programmingObjective = _ProgrammingObjective(self.students, self.projects, self._programmingVars)

        self._model.setObjective(self._ratingObjective.sum() + 0.3*self._programmingObjective.sum(), gp.GRB.MAXIMIZE)

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