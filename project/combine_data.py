import os
import json

directory = 'project/instances/students'

students = []

for filename in os.listdir(directory):
    if filename.endswith('.json'):
        filepath = os.path.join(directory, filename)
        with open(filepath, 'r') as file:
            student_data = json.load(file)
            students.append(student_data)
            
combined_data = {"students": students}
            
directory = 'project/instances/projects'

projects = []
            
for filename in os.listdir(directory):
    if filename.endswith('.json'):
        filepath = os.path.join(directory, filename)
        with open(filepath, 'r') as file:
            project_data = json.load(file)
            projects.append(project_data)

combined_data.update({"projects": projects})

with open('project/instances/SEP_data.json', 'w') as outfile:
    json.dump(combined_data, outfile, indent=4)