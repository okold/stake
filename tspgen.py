import numpy
import random

N = int(input("Gimme N: "))

coords = []

for i in range(1,N+1):
    coords.append(str(i) + "," + str(numpy.random.randint(1,N+1)) + "," + str(numpy.random.randint(1,N+1)) + "," + str(random.uniform(1.0,2.0)))

string = "city,x,y,terrain"

for i in coords:
    string += "\n" + i

filename = "tsp" + str(N) + ".csv"

print(string)

f = open(filename, "w")
f.write(string)
f.close()