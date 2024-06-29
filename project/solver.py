from typing import List

import gurobipy as gp
from data_schema import Instance, Project, Solution, Student
from gurobipy import GRB

from student_utils import _StudentProjectVars, _ProjectParticipationConstraint, _RatingObjective, _EmptyProjectVars, _ProgrammingVars, _StudentProgrammingConstraint, _ProgrammingObjective, _FriendsObjective



class SepSolver:
    """
    A solver to solve the SEP project student assignement incoporating project ratings, programmings skills and friend groups.
    """

    def __init__(self, instance: Instance):
        self.students = instance.students
        self.projects = list(instance.projects.values())
        self.students_min_rating = self.students_with_minimum_positive_ratings()

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
            students=self.students_min_rating,  # TODO: test with instances
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

    def get_project_rating(self, student: Student, project_id: int) -> int:
        return student.projects_ratings[project_id]

    def get_current_solution(self):
        projects = {project.id: [] for project in self.projects}
        for project in self.projects:
            for student in self.students:
                if self._studentProjectVars.x(student, project).X > 0.5:
                    projects[project.id].append(student)
                    print(f"{project.id}", student.matr_number)

        return Solution(projects=projects)

    def solve(self) -> Solution:
        self._model.setObjective(
            self._ratingObjective.get(),
            gp.GRB.MAXIMIZE,
        )

        self._model.optimize()
        if self._model.status == GRB.OPTIMAL:
            self._model.addConstr(
                self._ratingObjective.get()
                >= self._model.getObjective().getValue() * 0.9
            )
            self._model.setObjective(
                self._programmingObjective.get(),
                gp.GRB.MAXIMIZE,
            )

        self._model.optimize()
        if self._model.status == GRB.OPTIMAL:
            self._model.addConstr(
                self._programmingObjective.get()
                >= self._model.getObjective().getValue() * 0.9
            )
            self._model.setObjective(
                self._friendsObjective.get(),
                gp.GRB.MAXIMIZE,
            )

        self._model.optimize()
        if self._model.status == GRB.OPTIMAL:
            self.current_best_solution = self.get_current_solution()

        return self.current_best_solution
