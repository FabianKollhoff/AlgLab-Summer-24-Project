from typing import List

import gurobipy as gp
from data_schema import Project, Student


class _StudentProjectVars:
    """
    A helper class to manage the gurobi variables for the students and projects selection.
    """

    def __init__(
        self, students: List[Student], projects: List[Project], model: gp.Model
    ) -> None:
        self._students = students
        self._projects = projects

        self._model = model

        self.matnr_students = {
            student.matr_number: student for student in self._students
        }

        # variables whether student is in project
        self.vars_student_in_project = {
            (student, project): {
                "var": self._model.addVar(
                    vtype=gp.GRB.BINARY, name=f"x_{student.matr_number}_{project.id}"
                ),
                "rating": student.projects_ratings[project.id],
            }
            for student in self._students
            for project in self._projects
        }

    def x(self, student: Student, project_id: int) -> gp.Var:
        """
        Returns the variable assigned to the student and project.
        """
        return self.vars_student_in_project[(student, project_id)]["var"]

    def x_matr(self, student_matr: int, project_id: int) -> gp.Var:
        """
        Returns the variable assigned to the student and project.
        """
        return self.vars_student_in_project[
            (self.matnr_students[student_matr], project_id)
        ]["var"]

    def rating(self, student: Student, project_id: int):
        """
        Returns the rating of the given student for the given project.
        """
        return self.vars_student_in_project[(student, project_id)]["rating"]

    def all_projects_with_student(self, student: Student):
        """
        Returns all the variables for all project of the given student.
        """
        for project in self._projects:
            yield self.x(student, project)

    def all_students_with_project(self, project: Project):
        """
        Returns all the variables for all students of a given project.
        """
        for student in self._students:
            yield self.x(student, project)

    def __iter__(self):
        """
        Iterate overall variables.
        """
        return iter(self.vars_student_in_project.items())

    def for_each_student(self, func):
        """
        For every student the given function is executed.
        """
        for student in self._students:
            func(student)

    def for_each_project(self, func):
        """
        For every project the given function is executed.
        """
        for student in self._students:
            func(student)

    def for_each_student_and_project(self, func):
        """
        For every student and project the given function is executed and all results are returned in form of a list.
        """
        list = []
        for student in self._students:
            for project in self._projects:
                list.append(func(student, project))
        return list


class _EmptyProjectVars:
    """
    A helper class to manage the gurobi variables which specify whether a project is empty.
    """

    def __init__(self, projects: List[Project], model: gp.Model) -> None:
        # variable whether project is empty
        self.vars_project_empty = {
            project: model.addVar(vtype=gp.GRB.BINARY, name=f"e_{project.id}")
            for project in projects
        }

    def x(self, project) -> gp.Var:
        """
        Return the variable of the given project.
        """
        return self.vars_project_empty[project]


class _ProgrammingVars:
    """
    A helper class to manage the gurobi variables for assigning roles for students in projects.
    """

    def __init__(
        self, students: List[Student], projects: List[Project], model: gp.Model
    ) -> None:
        self._students = students
        self._projects = projects
        self._model = model

        self.vars_programming_language_student_in_project = {
            (programming_language, student, project): self._model.addVar(
                vtype=gp.GRB.BINARY,
                name=f"p_{programming_language}_{student.matr_number}_{project.id}",
            )
            for student in students
            for project in projects
            for programming_language in projects[project.id].programming_requirements
            if programming_language in student.programming_language_ratings
        }

    def x(
        self, programming_language: str, student: Student, project: Project
    ) -> gp.Var:
        """
        Return the variable for the given programming language, student and project.
        """
        if (
            programming_language,
            student,
            project,
        ) not in self.vars_programming_language_student_in_project:
            return None
        return self.vars_programming_language_student_in_project[
            (programming_language, student, project)
        ]

    def __iter__(self):
        """
        Iterate over all variables.
        """
        return iter(self.vars_programming_language_student_in_project.items())

    def all_languages(self, student: Student, project: Project):
        """
        Return all languages of the given students and projects.
        """
        for programming_language in project.programming_requirements:
            if self.x(programming_language, student, programming_language) is not None:
                yield self.x(programming_language, student, project)

    def all_students(self, programming_language: str, project: Project):
        """
        Return all students of the given languages and projects.
        """
        for student in self._students:
            if self.x(programming_language, student, programming_language) is not None:
                yield self.x(programming_language, student, project)

    def for_each(self, func):
        """
        Run the given function for all students, projects and programming languages and return the results in form of a list.
        """
        list = []
        for student in self._students:
            for project in self._projects:
                for programming_language in project.programming_requirements:
                    list.append(func(programming_language, student, project))
        return list

    def for_each_student_and_project(self, func):
        """
        Run the given function for all students and projects."""
        for student in self._students:
            for project in self._projects:
                func(student, project)

    def for_each_project_with_programming_language(self, func):
        """
        Run the given function for all projects and programming languages.
        """
        list = []
        for project in self._projects:
            for programming_language in project.programming_requirements:
                list.append(func(project, programming_language))
        return list

