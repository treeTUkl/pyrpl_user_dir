import numpy

start = -10
end = 10
stepsize = 1
if stepsize == 0.0:
    pass
else:
    for x in numpy.arange(start, end+stepsize, stepsize):
        print(x)