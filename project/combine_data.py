import json
import os


def combine_data():
    directory = 'instances/students'

    students = []

    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            filepath = os.path.join(directory, filename)
            with open(filepath, 'r') as file:
                student_data = json.load(file)
                students.append(student_data)

    combined_data = {"students": students}

    directory = 'instances/projects'

    projects = {}

    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            filepath = os.path.join(directory, filename)
            with open(filepath) as file:
                project_data = json.load(file)
                project_id = project_data["id"]
                projects[project_id] = project_data

    veto_file = "instances/veto.json"
    if os.path.exists(veto_file):
            with open(veto_file, 'r') as file:
                veto_data = json.load(file)
                for project in veto_data:
                    matr_number = veto_data[project]
                    student_list = []
                    for student in combined_data["students"]:
                        if int(matr_number) == student["matr_number"]:
                            student_list.append(student)
                            projects[int(project)]["veto"] = student_list

    combined_data.update({"projects": projects})


    with open('instances/SEP_data.json', 'w') as outfile:
        json.dump(combined_data, outfile, indent=4)
