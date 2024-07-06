from typing import List

import gurobipy as gp
from data_schema import Project, Student
from solver_vars import _ProgrammingVars, _StudentProjectVars


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
                * (student.programming_language_ratings[programming_language] - 1)
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
