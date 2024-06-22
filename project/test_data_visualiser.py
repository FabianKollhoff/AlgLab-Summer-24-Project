import json
import matplotlib.pyplot as plt

def readData(file_path):
    # reads in the data of the json file we are interested in
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def calculateAverages(data):
    # calculates the average score each project gets and returns it in a dict
    project_scores = {}
    project_counts = {}
    
    for student in data['students']:
        ratings = student['projects_ratings']
        for project, score in ratings.items():
            if project not in project_scores:
                project_scores[project] = 0
                project_counts[project] = 0
            project_scores[project] += score
            project_counts[project] += 1
    return {project: project_scores[project] / project_counts[project] for project in project_scores}

def calculateDistribution(data, number_projects):
    # calculates the number of 1,2,3,4,5-ratings each project recieves
    projects = {str(i): [0,0,0,0,0] for i in range(number_projects)}
    for student in data["students"]:
        ratings = student["projects_ratings"]
        for id, score in ratings.items():
            current_project = projects[id]
            current_project[score-1] += 1
            projects[id] = current_project
    return projects
    
def visualizeDistribution(projects):
    # visualizes the number of 1,2,3,4,5-ratings each project recieves
    for id, rating in projects.items():
        print(f"project: {id} ratings([1,2,3,4,5]): {rating}")
        print("###########################################################")  

def plotAverages(average_scores):
    # plots the average rating each project recieves in a bar chart (y-axis: average rating, x-axis: id of the project)
    projects = list(average_scores.keys())
    scores = list(average_scores.values())
    
    plt.figure(figsize=(10, 5))
    plt.bar(projects, scores, color='skyblue')
    plt.xlabel('Projects')
    plt.ylabel('Average Score')
    plt.title('Average Scores of Projects')
    plt.xticks(rotation=45)
    plt.ylim(0, 5)
    plt.tight_layout()
    plt.show()
    
    
file_path = "instances/data_s100_g10.json"
data = readData(file_path)
distribution = calculateDistribution(data, 10)
visualizeDistribution(distribution)
averages = calculateAverages(data)
plotAverages(averages)

