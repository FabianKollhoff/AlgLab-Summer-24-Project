from typing import List

import gurobipy as gp
from data_schema import Instance, Project, Solution, Student
from gurobipy import GRB

from  solver_vars import _ProgrammingVars, _StudentProjectVars, _EmptyProjectVars

class _ProjectParticipationConstraint:
    """
    A helper class to enforce the constraints regarding the participation and allocation of the students to projects.
    """

    def _enforce_every_student_in_exactly_one_project(self):
        """
        The method enforces that every student is at least in one project and at most in one project.
        """
        for student in self._students:
            self._model.addConstr(
                sum(self._studentProjectVars.all_projects_with_student(student=student))
                == 1
            )

    def _enforce_every_project_max_number_students(self):
        """
        The method ensures that the number of allocated students does not exceed the capacity of the project.
        """
        for project in self._projects:
            self._model.addConstr(
                sum(self._studentProjectVars.all_students_with_project(project=project))
                <= project.capacity
            )

    def _enforce_every_project_empty_or_has_minimum_number_students(self):
        """
        The method enforces that there are not too few students in the project."""
        for project in self._projects:
            self._model.addConstr(
                sum(self._studentProjectVars.all_students_with_project(project))
                <= self._emptyProjectVars.x(project) * project.capacity
            )
            self._model.addConstr(
                sum(self._studentProjectVars.all_students_with_project(project))
                >= self._emptyProjectVars.x(project) * project.min_capacity
            )

    def _enforce_vetos(self):
        """
        The method enforces that the student is banned from the project.
        """
        for project in self._projects:
            self._model.addConstr(
                sum(
                    [
                        self._studentProjectVars.x(student, project)
                        for student in project.veto
                    ]
                )
                == 0
            )

    def _enforce_maintaining_high_rating(self, student: Student, rating: int):
        """ """
        for project in self._projects:
            if student.projects_ratings[project.id] < rating:
                self._model.addConstr(
                    sum([self._studentProjectVars.x(student, project)]) == 0
                )

    def __init__(
        self,
        students: List[Student],
        projects: List[Project],
        studentProjectVars: _StudentProjectVars,
        emptyProjectVars: _EmptyProjectVars,
        model: gp.Model,
    ):
        self._students = students
        self._projects = projects
        self._studentProjectVars = studentProjectVars
        self._emptyProjectVars = emptyProjectVars
        self._model = model

        self._enforce_every_student_in_exactly_one_project()
        self._enforce_every_project_max_number_students()
        self._enforce_every_project_empty_or_has_minimum_number_students()
        self._enforce_vetos()


class _StudentProgrammingConstraint:
    """
    A helper class to enforce the constraints regarding the role allocation in the projects.
    """

    def _enforce_student_only_is_in_one_project_and_has_one_role(self):
        """
        The method enforces that every student is assigned exactly one role in a single project.
        """
        self._programmingVars.for_each_student_and_project(
            lambda student, project: self._model.addConstr(
                sum(self._programmingVars.all_languages(student, project))
                <= self._studentProjectVars.x(student, project)
            )
        )

    def _enforce_maximum_number_roles_project_assigned(self):
        """
        The method enforces that there are not too many roles assigned.
        """
        self._programmingVars.for_each_project_with_programming_language(
            lambda project, programming_language: self._model.addConstr(
                sum(self._programmingVars.all_students(programming_language, project))
                <= project.programming_requirements[programming_language]
            )
        )

    def __init__(
        self,
        students: List[Student],
        projects: List[Project],
        studentProjectVars: _StudentProjectVars,
        programmingVars: _ProgrammingVars,
        model: gp.Model,
    ):
        self._students = students
        self._projects = projects
        self._studentProjectVars = studentProjectVars
        self._programmingVars = programmingVars
        self._model = model

        self._enforce_student_only_is_in_one_project_and_has_one_role()
        self._enforce_maximum_number_roles_project_assigned()