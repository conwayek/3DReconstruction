import numpy as np
import os
import matplotlib.pyplot as plt


cwd = os.getcwd()
file = '/scratch/e.conway/3DReconstruction/COLMAP_SAT/colmap/sfm_perspective/tri_ba/points3D.txt'

with open(file,'r') as f:
    data3d = f.readlines()


##   POINT3D_ID, X, Y, Z, R, G, B, ERROR, TRACK[] as (IMAGE_ID, POINT2D_IDX)
point3d_id = [] ; x3d = [] ; y3d = [] ; z3d = [] ; red = [] ; green = [] ; blue = [] ; error = [] 
nlines = len(data3d)
for i in range(nlines):
    x= data3d[i].split(' ')
    point3d_id.append(x[0])
    x3d.append(x[1])
    y3d.append(x[2])
    z3d.append(x[3])
    red.append(x[4])
    green.append(x[5])
    blue.append(x[6])
    error.append(x[7])


x3d=np.array(x3d,dtype=np.float64)
y3d=np.array(y3d,dtype=np.float64)
z3d=np.array(z3d,dtype=np.float64)

fig = plt.figure()
sc=plt.scatter(x3d,y3d,c=z3d,vmin=45,vmax=55)
plt.colorbar(sc)
plt.savefig('test.png',dpi=400)
plt.close()

