from typing import List

import gurobipy as gp
from data_schema import Instance, Solution, Student
from gurobipy import GRB
from solver_constraints import (
    _ProjectParticipationConstraint,
    _StudentProgrammingConstraint,
)
from solver_objectives import (
    _FriendsObjective,
    _OptSizeOjective,
    _ProgrammingObjective,
    _RatingObjective,
)
from solver_vars import _EmptyProjectVars, _ProgrammingVars, _StudentProjectVars


class SepSolver:
    """
    A solver to solve the SEP project student assignement incoporating project ratings, programmings skills and friend groups.
    """

    def __init__(self, instance: Instance):
        self.students = instance.students
        self.projects = list(instance.projects.values())
        self.students_min_rating = self.students_with_minimum_positive_ratings()

        self.current_objective = 0

        self._model = gp.Model()

        self._studentProjectVars = _StudentProjectVars(
            students=self.students, projects=self.projects, model=self._model
        )
        self._emptyProjectVars = _EmptyProjectVars(
            projects=self.projects, model=self._model
        )
        self._programmingVars = _ProgrammingVars(
            students=self.students, projects=self.projects, model=self._model
        )

        self._projectParticipation = _ProjectParticipationConstraint(
            students=self.students,
            projects=self.projects,
            studentProjectVars=self._studentProjectVars,
            emptyProjectVars=self._emptyProjectVars,
            model=self._model,
        )
        self._studentProgrammingConstraint = _StudentProgrammingConstraint(
            students=self.students,
            projects=self.projects,
            studentProjectVars=self._studentProjectVars,
            programmingVars=self._programmingVars,
            model=self._model,
        )

        self._ratingObjective = _RatingObjective(
            students=self.students_min_rating,
            projects=self.projects,
            studentProjectVars=self._studentProjectVars,
        )
        self._programmingObjective = _ProgrammingObjective(
            students=self.students,
            projects=self.projects,
            programmingVars=self._programmingVars,
        )
        self._friendsObjective = _FriendsObjective(
            model=self._model,
            students=self.students,
            projects=self.projects,
            studentProjectVars=self._studentProjectVars,
        )
        self._optSizeObjective = _OptSizeOjective(
            model=self._model,
            students=self.students,
            projects=self.projects,
            studentProjectVars=self._studentProjectVars
        )

        self.current_best_solution = None

    # if the student does not give a positive rating to at least 20 % of the projects, solver does not add constraints to prioritize their highest ratings
    def get_number_of_positive_ratings(self, student: Student) -> int:
        return sum(1 for rating in student.projects_ratings.values() if rating >= 3)

    def check_minimum_positive_ratings(self, student: Student) -> bool:
        return self.get_number_of_positive_ratings(student) >= 0.2 * len(self.projects)

    def students_with_minimum_positive_ratings(self) -> List[Student]:
        return [
            student
            for student in self.students
            if self.check_minimum_positive_ratings(student) is True
        ]

    def get_current_solution(self):
        projects = {project.id: [] for project in self.projects}
        roles = {student.matr_number: 0 for student in self.students}
        for project in self.projects:
            for student in self.students:
                if self._studentProjectVars.x(student, project).X > 0.5:
                    for programming_language in project.programming_requirements:
                        if self._programmingVars.x(programming_language=programming_language, student=student, project=project).X > 0.5:
                            roles[student.matr_number] = student.programming_language_ratings[programming_language]
                    projects[project.id].append(student)
        return Solution(projects=projects, roles=roles)

    def solve(self) -> Solution:
        self._model.setObjective(
            self._ratingObjective.get(),
            gp.GRB.MAXIMIZE,
        )

        self._model.optimize()

        if self._model.status == GRB.OPTIMAL:
            self._model.addConstr(
                self._ratingObjective.get()
                >= self._model.getObjective().getValue() * 1
            )
            self._model.setObjective(
                self._programmingObjective.get(),
                gp.GRB.MAXIMIZE,
            )

        self._model.optimize()
        if self._model.status == GRB.OPTIMAL:
            self._model.addConstr(
                self._programmingObjective.get()
                >= self._model.getObjective().getValue() * 0.99
            )
            self._model.setObjective(
                self._friendsObjective.get(),
                gp.GRB.MAXIMIZE,
            )

        self._model.optimize()
        if self._model.status == GRB.OPTIMAL:
            self._model.addConstr(
                self._friendsObjective.get()
                >= self._model.getObjective().getValue() * 0.99
            )
            self._model.setObjective(
                self._optSizeObjective.get(),
                gp.GRB.MINIMIZE,
            )

        self._model.optimize()
        if self._model.status == GRB.OPTIMAL:
            self.current_best_solution = self.get_current_solution()

        return self.current_best_solution

    def solve_next_objective(self) -> Solution:
        if self.current_objective == 0:
            self._model.setObjective(
                self._ratingObjective.get(),
                gp.GRB.MAXIMIZE
            )

            self._model.optimize()
            if self._model.status == GRB.OPTIMAL:
                self._model.addConstr(
                    self._ratingObjective.get()
                    >= self._model.getObjective().getValue() * 1
                )

            if self._model.status == GRB.OPTIMAL:
                self.current_best_solution = self.get_current_solution()
        elif self.current_objective == 1:
            self._model.setObjective(
                self._programmingObjective.get(),
                gp.GRB.MAXIMIZE,
            )

            self._model.optimize()
            if self._model.status == GRB.OPTIMAL:
                self.current_best_solution = self.get_current_solution()
                self._model.addConstr(
                    self._programmingObjective.get()
                    >= self._model.getObjective().getValue() * 1
                )
        elif self.current_objective == 2:
            self._model.setObjective(
                self._friendsObjective.get(),
                gp.GRB.MAXIMIZE,
            )
            self._model.optimize()

            if self._model.status == GRB.OPTIMAL:
                self.current_best_solution = self.get_current_solution()
                self._model.addConstr(
                self._friendsObjective.get()
                    >= self._model.getObjective().getValue() * 0.99
                )
                self._model.optimize()
        elif self.current_objective == 3:
            self._model.setObjective(
                self._optSizeObjective.get(),
                gp.GRB.MINIMIZE,
            )
            self._model.optimize()
            if self._model.status == GRB.OPTIMAL:
                self.current_best_solution = self.get_current_solution()
        self.current_objective += 1
        return self.current_best_solution
