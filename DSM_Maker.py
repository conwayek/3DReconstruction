import matplotlib.pyplot as plt
from scipy import signal
import math
import time
from interp3d import interp_3d
from scipy.interpolate import RegularGridInterpolator
import rasterio
import os
import numpy as np
import netCDF4 as nc4
import tqdm

cwd = os.getcwd()
folder = os.listdir(cwd)
tifs=[]
for i in range(len(folder)):
    if(('.nc' in folder[i])):
        tifs.append(os.path.join(cwd,folder[i]))


tifs = np.array(tifs)
nfiles = len(tifs)

# Step 1 - make a large 2d array of lon and lat, for which we have coverage
# nfiles = n limits of lon/lat

minima_lat = np.zeros(nfiles)
minima_lon = np.zeros(nfiles)
maxima_lat = np.zeros(nfiles)
maxima_lon = np.zeros(nfiles)
file_order = np.zeros(nfiles)
raw_lon = np.ndarray(shape=(nfiles),dtype=np.object_)#np.zeros((200,nfiles))
raw_lat = np.ndarray(shape=(nfiles),dtype=np.object_)#np.zeros((200,nfiles))

func = np.ndarray(shape=(nfiles),dtype=np.object_)

for i in range(nfiles):
    band = nc4.Dataset(tifs[i]).variables['Elevation'][:,:]
    raw_lon[i] = nc4.Dataset(tifs[i]).variables['Longitude'][:] 
    raw_lat[i] = nc4.Dataset(tifs[i]).variables['Latitude'][:] 

    #band[band==10000.0] = 0.0

    maxima_lon[i] = np.max(raw_lon[i])
    minima_lon[i] = np.min(raw_lon[i])
    maxima_lat[i] = np.max(raw_lat[i])
    minima_lat[i] = np.min(raw_lat[i])

    t = np.ones((band.shape))
    iband = np.stack((band,t),axis=2)
    iband = np.dstack((iband,t))
    iband[:,:,1] = iband[:,:,0]
    z = np.ones(3)
    z[0] = 0
    z[1] = 1
    z[2] = 2

    func[i] = interp_3d.Interp3D(iband,raw_lat[i],raw_lon[i],z)
    #func[i] = RegularGridInterpolator((raw_lat[i],raw_lon[i]),band)

nlon=0
nlat=0
lon=[]
lat=[]
for i in range(nfiles):
    if(i==0):
        lat.append(raw_lat[i])
        lon.append(raw_lon[i])
        lat=np.array(lat)
        lon=np.array(lon)
        lon = lon.flatten()
        lat = lat.flatten()
    else:
        lat = np.concatenate((lat,raw_lat[i]))
        lon = np.concatenate((lon,raw_lon[i]))



lat = np.linspace(np.min(lat) , np.max(lat), 40000 )
lon = np.linspace(np.min(lon) , np.max(lon), 80000 )
#lat = np.linspace(24.9,35.2, 1000)#40000 )
#lon = np.linspace(-100.00,-110, 1000)#80000 )

tag = np.zeros((len(lat),len(lon)))
for i in tqdm.tqdm(range(len(lon))):
    #print(i)
    for k in range(len(lat)):
        done=False
        for j in range(nfiles):
            if( (lon[i] <= maxima_lon[j] ) and (lat[k] <= maxima_lat[j]) and (lon[i] >= minima_lon[j] ) and (lat[k] >= minima_lat[j]) ):
                tag[k,i] = func[j]((lat[k],lon[i],0.0000))
                #tag[k,i] = 1
                done=True
                #print(lon[i],' ',lat[k],' ',tag[k,i])
                #tag[k,i] = func[j](np.array([lat[k],lon[i]]))
                if(tag[k,i] < 0 or tag[k,i] == 10000.0 ):
                    tag[k,i] = 0.0
                    #print(lon[i],' ',lat[k],' ',tag[k,i])
                #    exit()
        #if(done==False):
        #     tag[k,i] = 0.0
        #    print('No Coverage ',lon[i],' ',lat[k])
        #exit()


split_lon = [] 
split_lat = [] 

for i in range(len(lat)):
    for j in range(nfiles):
        if( (math.isclose(lat[i],maxima_lat[j],abs_tol=0.05)) or (math.isclose(lat[i],minima_lat[j],abs_tol=0.05))  ):
            split_lat.append(int(i))
for i in range(len(lon)):
    for j in range(nfiles):
        if( (math.isclose(lon[i],maxima_lon[j],abs_tol=0.05)) or (math.isclose(lon[i],minima_lon[j],abs_tol=0.05))  ):
            split_lon.append(int(i))


for i in range(len(split_lon)):
    tag[:,split_lon[i]] = np.nan
for i in range(len(split_lon)):
    tag[:,split_lon[i]] = np.nanmean(tag[:,split_lon[i]-1:split_lon[i]+1],axis=1)

for i in range(len(split_lat)):
    tag[split_lat[i],:] = np.nan
for i in range(len(split_lat)):
    tag[split_lat[i],:] = np.nanmean(tag[split_lat[i]-1:split_lat[i]+1,:],axis=0)

tag[0,:] = np.nan
tag[0,:] = np.nanmean(tag[0:2,:],axis=0)
tag[-1,:] = np.nan
tag[-1,:] = np.nanmean(tag[-2:,:],axis=0)

tag[:,0] = np.nan
tag[:,0] = np.nanmean(tag[:,0:2],axis=1)
tag[:,-1] = np.nan
tag[:,-1] = np.nanmean(tag[:,-2:],axis=1)


tag[tag<0] = 0.0

#tag[np.isfinite(tag)!=True] = 0.0

idx = np.argsort(lon)
lon=lon[idx]
tag=tag[:,idx]
idx = np.argsort(lat)
lat=lat[idx]
tag=tag[idx,:]


plt.imshow(tag,aspect='auto',origin='lower',extent=[np.min(lon),np.max(lon),np.min(lat),np.max(lat)])
plt.savefig('test.png',dpi=1000)
plt.close()

filesave = 'DEM_Large.nc'
f = nc4.Dataset(filesave,'w', format='NETCDF4')

f.createDimension('nlon',len(lon))
f.createDimension('nlat',len(lat))

band = f.createVariable('Elevation','f4',('nlat','nlon'))
longitude = f.createVariable('Longitude','f4',('nlon'))
latitude = f.createVariable('Latitude','f4',('nlat'))

band[:,:] = tag
longitude[:] =  lon
latitude[:]  =  lat
f.close()


