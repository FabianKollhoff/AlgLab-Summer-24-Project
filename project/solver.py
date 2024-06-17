from typing import Dict, List

import gurobipy as gp
from data_schema import Instance, Project, Solution, Student
from gurobipy import GRB


class _StudentProjectVars:
    """
    A helper class to manage the gurobi variables for the studends and projects selection.
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
        return self.vars_student_in_project[(self.matnr_students[student_matr], project_id)]["var"]

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
        Return all languages of the given students and projects
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
        Run the the given function for all students, projects and programming_languages and return the results in a form of a list.
        """
        list = []
        for student in self._students:
            for project in self._projects:
                for programming_language in project.programming_requirements:
                    list.append(func(programming_language, student, project))
        return list

    def for_each_student_and_project(self, func):
        """
        Run the given function for all students and projects"""
        for student in self._students:
            for project in self._projects:
                func(student, project)

    def for_each_project_with_programming_language(self, func):
        """
        Run the given function for all projects and programming languages
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
                sum(self._studentProjectVars.all_projects_with_student(student=student)) == 1
            )

    def _enforce_every_project_max_number_students(self):
        """
        The method ensures that the number of allocated students doesn't exceed the capacity of the project.
        """
        for project in self._projects:
            self._model.addConstr(
                sum(self._studentProjectVars.all_students_with_project(project=project))
                <= project.capacity
            )

    def _enforce_every_project_empty_or_has_minimum_number_students(self):
        """
        The method enforces that there are not to few students in the project"""
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

    def _enforce_higher_rating(
        self, students: List[Student], lowest_solution_rating: int
    ):
        """ """
        return sum(
            self._studentProjectVars.for_each_student_and_project(
                lambda student, project: self._studentProjectVars.x(student, project)
                if (
                    self._studentProjectVars.rating(student, project)
                    == lowest_solution_rating
                    and student in students
                )
                else 0
            )
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
        The method enforces that there are not to many roles assigned.
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
    A helper class to calculate to calculate the objective concerning the ratings of the students.
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
    A helper class to calculate the objective for the friendg roups.
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

        self.relations = []
        # here get a list of all friend relations as tuple (Student.matr_number,Student.matr_number). Make sure no duplicates are added
        for student in self._students:
            for friend in student.friends:
                if (friend, student.matr_number) not in self.relations:
                    self.relations.append((student.matr_number, friend))

    def get(self):
        # return sum of all friend relations
        return sum(
            self._studentProjectVars.x_matr(stu_a, proj)
            * self._studentProjectVars.x_matr(stu_b, proj)
            for stu_a, stu_b in self.relations
            for proj in self._projects
        )


class SepSolver:
    """
    A solver to solve the SEP project student assignement incoperating project ratings, programmings skills and friend groups.
    """

    def __init__(self, instance: Instance):
        self.students = instance.students
        self.projects = list(instance.projects.values())

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
            students=self.students,
            projects=self.projects,
            studentProjectVars=self._studentProjectVars,
        )
        self._programmingObjective = _ProgrammingObjective(
            students=self.students,
            projects=self.projects,
            programmingVars=self._programmingVars,
        )
        self._friendsObjective = _FriendsObjective(
            students=self.students,
            projects=self.projects,
            studentProjectVars=self._studentProjectVars,
        )

        self.students_no_min_rating = self.students_without_minimum_positive_ratings()
        self.current_best_solution = None

    # if the student does not give a positive rating to at least 20 % of the projects, solver does not add constraints to prioritize their highest ratings
    def get_number_of_positive_ratings(self, student: Student) -> int:
        return sum(1 for rating in student.projects_ratings.values() if rating >= 3)

    def check_minimum_positive_ratings(self, student: Student) -> bool:
        return self.get_number_of_positive_ratings(student) >= 0.2 * len(self.projects)

    def students_without_minimum_positive_ratings(self) -> List[Student]:
        return [
            student
            for student in self.students
            if self.check_minimum_positive_ratings(student) == False
        ]

    def get_project_rating(self, student: Student, project_id: int) -> int:
        return student.projects_ratings[project_id]

    def get_current_solution(self, in_callback: bool = False):
        if in_callback:
            projects = {project.id: [] for project in self.projects}
            for project in self.projects:
                for student in self.students:
                    if (
                        self._model.cbGetSolution(
                            self._studentProjectVars.x(student, project)
                        )
                        > 0.5
                    ):
                        projects[project.id].append(student)
                        print(f"{project.id}", student.matr_number)

            return Solution(projects=projects)

        projects = {project.id: [] for project in self.projects}
        for project in self.projects:
            for student in self.students:
                if self._studentProjectVars.x(student, project).X > 0.5:
                    projects[project.id].append(student)
                    print(f"{project.id}", student.matr_number)

        return Solution(projects=projects)

    def get_solution_ratings(self, solution: Solution) -> Dict[Student, int]:
        solution_ratings = {}
        for project, students in solution.projects.items():
            for student in students:
                current_rating = self.get_project_rating(student, project)
                solution_ratings[student] = current_rating
        return solution_ratings

    def solve(self) -> Solution:
        # reduce the number of lower ratings iteratively
        """def callback(model, where):
        if where == gp.GRB.Callback.MIPSOL:
            solution = self.get_current_solution(in_callback=True)
            solution_ratings = self.get_solution_ratings(solution)

            sum_rating = 0
            for student in solution_ratings:
                sum_rating += solution_ratings[student]
            print("Test sum:", sum_rating)

            current_number_of_ratings = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0} #only counts the relevant students
            optimize_students = []
            #student complies with the minimum positive rating rule are considered for optimization
            for student in solution_ratings:
                if student not in self.students_no_min_rating:
                    optimize_students.append(student)
                    current_number_of_ratings[solution_ratings[student]] += 1
            print("Current solution count:", current_number_of_ratings)
            lowest_solution_rating = min((rating for rating, number in current_number_of_ratings.items() if number > 0), default=None)
            #model.cbLazy(self._projectParticipation._enforce_higher_rating(optimize_students, lowest_solution_rating) <= current_number_of_ratings[lowest_solution_rating] - 1)
        """

        self._model.Params.lazyConstraints = 1

        self._model.setObjective(
            self._ratingObjective.get(),
            gp.GRB.MAXIMIZE,
        )

        self._model.optimize()
        if self._model.status == GRB.OPTIMAL:
            self._model.addConstr(self._ratingObjective.get() >= self._model.getObjective().getValue() * 0.9)
            self._model.setObjective(self._programmingObjective.get(),gp.GRB.MAXIMIZE,
        )

        self._model.optimize()
        if self._model.status == GRB.OPTIMAL:
            self._model.addConstr(self._programmingObjective.get() >= self._model.getObjective().getValue() * 0.9)
            self._model.setObjective(self._friendsObjective.get(),gp.GRB.MAXIMIZE,
        )

        self._model.optimize()  # callback
        if self._model.status == GRB.OPTIMAL:
            if self.current_best_solution is None:
                self.current_best_solution = self.get_current_solution()
                # only add constraint during the first time
                student_ratings = self.get_solution_ratings(self.current_best_solution)
                for student in student_ratings:
                    if student not in self.students_no_min_rating:
                        self._projectParticipation._enforce_maintaining_high_rating(
                            student, student_ratings[student]
                        )
            else:
                self.current_best_solution = self.get_current_solution()

        return self.current_best_solution
