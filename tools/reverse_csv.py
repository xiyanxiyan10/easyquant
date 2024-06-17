import csv

data = []
with open('input.csv', 'r') as file:
    reader = csv.reader(file)
    for row in reader:
        data.append(row)
data.reverse()

with open('output.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(data)
