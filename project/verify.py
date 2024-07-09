from _alglab_utils import CHECK, main, mandatory_testcase
from benchmarks import Benchmarks
from data_schema import Instance
from solver import SepSolver


def solve_sep_instance(filepath: str):
    with open(filepath) as f:
        instance: Instance = Instance.model_validate_json(f.read())

    solver = SepSolver(instance)
    solution = solver.solve()

    CHECK(solution is not None, "The returned solution must not be 'None'!")

    # check every project has a mimium and maximum number of participants or is empty
    for project in solution.projects:
        CHECK(
            len(solution.projects[project]) <= instance.projects[project].capacity,
            f"Too many students in project: {project}!",
        )
        CHECK(
            len(solution.projects[project]) == 0
            or len(solution.projects[project])
            >= instance.projects[project].min_capacity,
            f"Project {project} has {len(solution.projects[project])} students with less then the minimum required of {instance.projects[project].min_capacity}!",
        )
        # check if solution complies with project vetos
        for student_solution in solution.projects[project]:
            CHECK(
                student_solution not in instance.projects[project].veto,
                f"The returned solution contains a prohibited student {student_solution.matr_number} in project {project}!",
            )

    # check if every student is contained in exactly one project
    for student_instance in instance.students:
        count_student_in_solution = 0
        for project in solution.projects:
            for student_solution in solution.projects[project]:
                if student_instance.matr_number == student_solution.matr_number:
                    count_student_in_solution += 1
        CHECK(
            count_student_in_solution == 1,
            f"The returned solution contains a student {student_instance} {count_student_in_solution} times!",
        )

    data = solution.model_dump_json(indent=2)
    with open(f"solution/solution_of_{len(instance.projects)}_{len(instance.students)}.json", "w") as f:
        f.write(data)

    benchmark = Benchmarks(instance=instance, solution=solution)
    benchmark.log()
    return instance, solution

def genererate_solver(filepath: str):
    with open(filepath) as f:
        instance: Instance = Instance.model_validate_json(f.read())

    solver = SepSolver(instance)

    return solver, instance

def solve_next_objective(solver: SepSolver, instance: Instance):
    solution = solver.solve_next_objective()

    CHECK(solution is not None, "The returned solution must not be 'None'!")

    # check every project has a mimium and maximum number of participants or is empty
    for project in solution.projects:
        CHECK(
            len(solution.projects[project]) <= instance.projects[project].capacity,
            f"Too many students in project: {project}!",
        )
        CHECK(
            len(solution.projects[project]) == 0
            or len(solution.projects[project])
            >= instance.projects[project].min_capacity,
            f"Project {project} has {len(solution.projects[project])} students with less then the minimum required of {instance.projects[project].min_capacity}!",
        )
        # check if solution complies with project vetos
        for student_solution in solution.projects[project]:
            CHECK(
                student_solution not in instance.projects[project].veto,
                f"The returned solution contains a prohibited student {student_solution.matr_number} in project {project}!",
            )

    # check if every student is contained in exactly one project
    for student_instance in instance.students:
        count_student_in_solution = 0
        for project in solution.projects:
            for student_solution in solution.projects[project]:
                if student_instance.matr_number == student_solution.matr_number:
                    count_student_in_solution += 1
        CHECK(
            count_student_in_solution == 1,
            f"The returned solution contains a student {student_instance} {count_student_in_solution} times!",
        )

    data = solution.model_dump_json(indent=2)
    with open(f"solution/solution_of_{len(instance.projects)}_{len(instance.students)}.json", "w") as f:
        f.write(data)

    return solution




@mandatory_testcase(max_runtime_s=30)
def s100_g10():
    solve_sep_instance(filepath="./instances/data_s100_g10.json")


@mandatory_testcase(max_runtime_s=30)
def s200_g20():
    solve_sep_instance(filepath="./instances/data_s200_g20.json")


@mandatory_testcase(max_runtime_s=60)
def s300_g30():
    solve_sep_instance(filepath="./instances/data_s300_g30.json")


@mandatory_testcase(max_runtime_s=90)
def s500_g50():
    solve_sep_instance(filepath="./instances/data_s500_g50.json")


@mandatory_testcase(max_runtime_s=300)
def s1000_g100():
    solve_sep_instance(filepath="./instances/data_s1000_g100.json")

@mandatory_testcase(max_runtime_s=60)
def worst_case_uniform_requirements():
    solve_sep_instance(filepath="./instances/data_worst_case_uniform_requirements.json")

@mandatory_testcase(max_runtime_s=60)
def worst_case_extreme_ratings_5():
    solve_sep_instance(filepath="./instances/data_worst_case_extreme_rating_5.json")

@mandatory_testcase(max_runtime_s=60)
def worst_case_extreme_ratings_1():
    solve_sep_instance(filepath="./instances/data_worst_case_extreme_rating_1.json")

@mandatory_testcase(max_runtime_s=60)
def worst_case_extreme_vetos():
    solve_sep_instance(filepath="./instances/data_worst_case_extreme_vetos.json")


@mandatory_testcase(max_runtime_s=90)
def s1000_g50():
    solve_sep_instance(filepath="./instances/data_s1000_g50.json")


if __name__ == "__main__":
    main()
