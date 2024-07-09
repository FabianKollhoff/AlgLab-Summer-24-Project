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
        [self._studentProjectVars.x(student, project) * self._studentProjectVars.rating(student=student, project=project)
            for student in self._students
             for project in self._projects
        ]
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
                * (student.programming_language_ratings[programming_language])
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

class _OptSizeOjective:
    """
    A helper class to calculate the objective concerning the optimal size of the projects.
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
        self._model = model

        self.deviations = []
        self.abs_deviations = []
        for proj in self._projects:
            deviation = model.addVar(
                            vtype=gp.GRB.INTEGER, name="deviation_of_"
                        )

            opt_size = int((proj.capacity + proj.min_capacity) / 2)
            model.addConstr(
                deviation == sum(self._studentProjectVars.all_students_with_project(project=proj)) - opt_size
                )
            abs_deviation = model.addVar(vtype=gp.GRB.INTEGER, name="abs_deviation")
            model.addConstr(abs_deviation == gp.abs_(deviation))
            self.deviations.append(deviation)
            self.abs_deviations.append(abs_deviation)
        self._maximum = model.addVar(vtype=gp.GRB.INTEGER, name="max")
        for dev in self.abs_deviations:
            #add constraints to make sure the maximum is >= to all deviations
            model.addConstr(self._maximum >= dev) 

    # try to minimize the sum(deviation of every project from its optimal size)
    # try to minimize the single maximum deviation from a projects optimum. So minimize _maximum
    # maximum = max(deviations). Objective: minimize(maximum)
    # TODO: make it not quadratic ???

    def get(self):
        return self._maximum
        #return sum(el * el for el in self.deviations)
    
    def _enforce_every_project_minimize_deviation(self, limit):
        """
        
        """
        for dev in self.deviations:
            self._model.addConstr(dev <= limit)