# This optimization will use bang-bang controls (making u an integer)

import numpy as np
from scipy.optimize import minimize, Bounds
from scipy import integrate as int
import scipy.linalg
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
import math
import csv
from gekko import GEKKO


# create GEKKO model
m = GEKKO()

# make time from 0 to 5 seconds
nt = 21
m.time = np.linspace(0,3,nt)

# options
m.options.NODES = 100
m.options.SOLVER = 1
m.options.IMODE = 6 # MPC mode
# m.options.IMODE = 9 #dynamic ode sequential
m.options.MAX_ITER = 500
m.options.MV_TYPE = 0
m.options.DIAGLEVEL = 0

# final time
tf = m.MV(value=1.0,lb=0.0,ub=100)

# tf = m.FV(value=5.0)
tf.STATUS = 1

# some constants
g = 650 # Gravity
# v_end = 500

# force (thruster)
u = m.MV(integer=True,lb=0,ub=1)
u.STATUS = 1
u.DCOST = 1e-5

# variables intial conditions are placed here
s = m.Var(value=100, lb = 0, ub = 4000)
v = m.Var(value=0.0,lb=-1*2400,ub=2400)

# integral over time for u^2
u2 = m.Var(value=0)
m.Equation(u2.dt() == 0.5*u**2)

# differential equations
m.Equation(s.dt()==v)
# m.Equation(v.dt()==((u*991.666) - g))
m.Equation(v.dt()==((u*(991.666+60)) - g)) #testing different acceleration value that i get from data


# end time variables to multiply u2 by to get total value of integral
p = np.zeros(nt)
p[-1] = 1.0
final = m.Param(value = p)

# halfway cell number
nhalf = len(m.time) / 2
print(nhalf)
nhalf = round(nhalf)

# specify endpoint conditions
# m.fix(s, pos=nhalf,val=200.0) #Hard constraints, makes the derivative zero also
# m.fix(s, pos=nhalf+30,val=500.0) #Hard constraints, makes the derivative zero also

# m.fix(v, pos=nhalf,val=0.0)
m.Obj(final*1e3*(s-1000)**2) # Soft constraints
m.Obj(final*1e3*(v-0)**2)


# minimize thrust used
m.Obj(u2*final)
# m.Obj(tf) #final time objective

# Optimize launch
m.solve()

print('Optimal Solution (final time): ' + str(tf.value[0]))

# scaled time
ts = m.time * tf.value[0]
print(u.value)

# plot results
plt.figure(1)
plt.subplot(3,1,1)
plt.plot(ts,s.value,'r-',linewidth=2)
plt.ylabel('Position')
plt.legend(['s (Position)'])

plt.subplot(3,1,2)
plt.plot(ts,v.value,'b-',linewidth=2)
plt.ylabel('Velocity')
plt.legend(['v (Velocity)'])

# plt.subplot(4,1,3)
# plt.plot(ts,mass.value,'k-',linewidth=2)
# plt.ylabel('Mass')
# plt.legend(['m (Mass)'])

plt.subplot(3,1,3)
plt.plot(ts,u.value,'g-',linewidth=2)
plt.ylabel('Force')
plt.legend(['u (Force)'])

plt.xlabel('Time')

#export csv

f = open('optimization_data.csv', 'w', newline = "")
writer = csv.writer(f)
writer.writerow(['time', 's', 'v', 'u']) # , 'vx', 'vy', 'vz', 'ax', 'ay', 'az', 'quaternion', 'boost', 'roll', 'pitch', 'yaw'])
for i in range(len(m.time)):
    row = [m.time[i], s.value[i], v.value[i], u.value[i]]
    writer.writerow(row)
    print('wrote row', row)


plt.show()
