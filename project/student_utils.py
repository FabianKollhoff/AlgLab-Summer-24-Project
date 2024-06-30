from typing import List

import gurobipy as gp
from data_schema import Instance, Project, Solution, Student
from gurobipy import GRB


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


class _RatingObjective:
    """
    A helper class to calculate the objective concerning the ratings of the students.
    """

    def __init__(
        self,
        students: List[Student],
        projects: List[Project],
        studentProjectVars: _StudentProjectVars,
    ):
        self._students = students
        self._projects = projects
        self._studentProjectVars = studentProjectVars

    def get(self):
        return sum(
            self._studentProjectVars.for_each_student_and_project(
                lambda student, project: self._studentProjectVars.x(student, project)
                * self._studentProjectVars.rating(student, project)
            )
        )


class _ProgrammingObjective:
    """
    A helper class to calculate the objective for the programming languages concerning the skills and role assignment.
    """

    def __init__(
        self,
        students: List[Student],
        projects: List[Project],
        programmingVars: _ProgrammingVars,
    ):
        self._students = students
        self._projects = projects
        self._programmingVars = programmingVars

    def get(self):
        return sum(
            self._programmingVars.for_each(
                lambda programming_language, student, project: self._programmingVars.x(
                    programming_language, student, project
                )
                * student.programming_language_ratings[programming_language]
            )
        )


class _FriendsObjective:
    """
    A helper class to calculate the objective for the friend groups.
    """

    def __init__(
        self,
        model,
        students: List[Student],
        projects: List[Project],
        studentProjectVars: _StudentProjectVars,
    ):
        self._students = students
        self._projects = projects
        self._studentProjectVars = studentProjectVars

        self.relations = []
        # here get a list of all friend relations as tuple (Student.matr_number,Student.matr_number). Make sure no duplicates are added.
        for student in self._students:
            for friend in student.friends:
                if friend != student.matr_number:
                    for proj in self._projects:
                        relation = model.addVar(
                            vtype=gp.GRB.BINARY, name=f"relation_{student.matr_number}_{friend}"
                        )
                        self.relations.append(relation)
                        model.addConstr(relation<=self._studentProjectVars.x_matr(student.matr_number, proj))
                        model.addConstr(relation<= self._studentProjectVars.x_matr(friend, proj))

    def get(self):
        # return sum of all friend relations
        return sum(
            relation for relation in self.relations
        )