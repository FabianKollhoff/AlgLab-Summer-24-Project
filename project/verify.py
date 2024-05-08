from data_schema import Project, Student, Instance
from solver import SepSolver

def solve_sep_instance(filepath: str):
    with open(filepath) as f:
        instance: Instance = Instance.model_validate_json(f.read())

    solver = SepSolver(instance)
    solver.solve()

solve_sep_instance(filepath="./instances/data_s1000_g100.json")