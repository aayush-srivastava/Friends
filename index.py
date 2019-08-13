import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib
import sys
from PyQt5 import QtWidgets

infinity = float('inf')

# Read Input Files
f = open('input.txt', 'r')
readLines = f.readlines()
f.close()

# Isolate data into proper data structures from read file
peopleCount = int(readLines[0])
names = np.array([x.strip() for x in readLines[1:1+peopleCount]])
adjacencyMatrix = np.array([y.strip().split(',') for y in readLines[1+peopleCount:11+peopleCount]]).astype(int)
names_indices = {name: index for index, name in enumerate(names)}

# Generate graph
G=nx.Graph()
# Add Nodes
G.add_nodes_from(names)
# Add Edges
for from_idx, to_names_list in enumerate(adjacencyMatrix):
    for to_idx, is_edge in enumerate(to_names_list):
        if is_edge == 1:
            G.add_edge(names[from_idx], names[to_idx])

# Generate friend suggestions
all_scores = {}
for src_idx, src in enumerate(names):
    scores = [0] * peopleCount
    scores[src_idx] = -infinity
    neighbours = list(G.neighbors(src))
    neighbours = list(zip(neighbours, [1] * len(neighbours)))
    for neighbour, distance in neighbours:
        scores[names_indices[neighbour]] = -infinity
    is_friend = list(map(lambda x: x == -infinity, scores))
    visited = [False] * peopleCount
    visited[src_idx] = True
    while len(neighbours) != 0:
        this_neighbour, this_distance = neighbours[0]
        neighbour_index = names_indices[this_neighbour]
        if visited[neighbour_index]:
            if neighbour_index == src_idx:
                neighbours.pop(0)
                continue
            if not is_friend[neighbour_index]:
                scores[neighbour_index] += (2.0 ** (-1 * (this_distance - 2)))
            neighbours.pop(0)
            continue
        visited[neighbour_index] = True
        next_neighbours = list(G.neighbors(this_neighbour))
        next_unvisited_neighbours = list(filter(lambda x: not visited[names_indices[x]], next_neighbours))
        neighbours += list(zip(next_unvisited_neighbours, [this_distance + 1] * len(next_unvisited_neighbours)))
        scores[neighbour_index] += (2.0 ** (-1 * (this_distance - 2)))
        neighbours.pop(0)
    scores = list(zip(names, scores))
    sorted_scores = sorted(scores, key=lambda x: x[1], reverse=True)
    sorted_scores = list(filter(lambda x: x[1] != -infinity, sorted_scores))
    all_scores[src] = sorted_scores

# Graph UI
nx.draw_networkx(G)
plt.show(block=False)

# Suggestions UI
app = QtWidgets.QApplication(sys.argv)

# Table Widget
tableWidget = QtWidgets.QTableWidget()
tableWidget.setRowCount(0)
tableWidget.setColumnCount(2)
tableWidget.setColumnWidth(0, 250)
tableWidget.setColumnWidth(1, 200)
def updateTable(index):
    person_name = names[index]
    scores = all_scores[person_name]
    tableWidget.setRowCount(len(scores))
    for score_idx, score_item in enumerate(scores):
        p_name, score = score_item
        tableWidget.setItem(score_idx, 0, QtWidgets.QTableWidgetItem(p_name))
        tableWidget.setItem(score_idx, 1, QtWidgets.QTableWidgetItem(str(score)))
updateTable(0)

# ComboBox Widget
comboBox = QtWidgets.QComboBox()
comboBox.setObjectName(("comboBox"))
for name in names:
    comboBox.addItem(name)
def dropdownIndexChange(idx):
    updateTable(idx)
comboBox.currentIndexChanged.connect(dropdownIndexChange)

# Layout
box = QtWidgets.QVBoxLayout()
box.addWidget(comboBox)
box.addWidget(tableWidget)

# Main Window
window = QtWidgets.QWidget()
window.setLayout(box)
window.setFixedSize(500, 500)
window.show()
window.show()

# Execute app
app.exec_()