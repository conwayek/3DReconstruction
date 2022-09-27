import rasterio
import glob
import tarfile
import os
import numpy as np
from geopy import distance
import matplotlib.pyplot as plt
import utm


def main(direct,Nview=10,rangex=2000,rangey=2000):
    
    rpcfiles = []
    nwlons = []
    nwlats = []
    selats = []
    selons = []
    ntffiles = []
    
    files = glob.glob(direct+'/*.NTF')

    for file in files:
        ntffiles.append(file)
        with rasterio.open(file) as f:
            width = f.width
            height = f.height  

        order_id = file.split('-P1BS-')[1].split('.NTF')[0].split('_P001')[0]

        tar = tarfile.open(file.split('.NTF')[0]+'.tar')
        tar.extractall(file.split('.NTF')[0])

        subfolder = 'DVD_VOL_1'
        for x in os.listdir(file.split('.NTF')[0]+'/'+order_id):
            if 'DVD_VOL' in x:
                subfolder = x
                break

        des_folder = os.path.join(file.split('.NTF')[0], order_id, subfolder, order_id)
        rpcfile = glob.glob(des_folder+'/*.XML')[0]
        rpcfiles.append(rpcfile)

        with open(rpcfile,'r') as f:
            rpcdata = f.readlines()
        for line in rpcdata:
            if 'NWLAT' in line:
                NWLAT = np.float64(line.split('<NWLAT>')[1].split('</NWLAT>')[0])
            if 'NWLONG' in line:
                NWLON = np.float64(line.split('<NWLONG>')[1].split('</NWLONG>')[0])
            if 'SELAT' in line:
                SELAT = np.float64(line.split('<SELAT>')[1].split('</SELAT>')[0])
            if 'SELONG' in line:
                SELON = np.float64(line.split('<SELONG>')[1].split('</SELONG>')[0])

        nwlons.append(NWLON)
        nwlats.append(NWLAT)
        selats.append(SELAT)
        selons.append(SELON)    
    
    nwlons = np.array(nwlons,dtype=np.float64)
    nwlats = np.array(nwlats,dtype=np.float64)
    selons = np.array(selons,dtype=np.float64)
    selats = np.array(selats,dtype=np.float64)

    max_lon = np.max(selons) ; min_lon = np.min(nwlons)
    max_lat = np.max(nwlats) ; min_lat = np.min(selats)

    print(min_lon,max_lon)
    print(min_lat,max_lat)

    pt1 = (max_lat,max_lon)
    pt2 = (max_lat,max_lon+1)
    pt3 = (max_lat+1,max_lon)

    vert_dist = distance.distance(pt1,pt2).km
    horz_dist = distance.distance(pt1,pt3).km
    print(vert_dist,horz_dist)

    nres_x = rangex*1e-5 #degrees
    nres_y = nres_x *(vert_dist/horz_dist) # degrees

    npix_x = rangey/0.31
    npix_y = 2000*(vert_dist/horz_dist)/0.31

    print(npix_x,npix_y)    

    lon = np.arange(min_lon,max_lon,nres_x)
    lat = np.arange(min_lat,max_lat,nres_y)
    nlon = len(lon)
    nlat = len(lat)

    tile_count = np.zeros((nlat-1,nlon-1),dtype=int)
    
    for i in range(nlat-1):
        lat_lower = lat[i]
        lat_upper = lat[i+1]
        for j in range(nlon-1):
            lon_left = lon[j]
            lon_right = lon[j+1]

            idy = np.logical_and(nwlats>=lat_upper,selats<=lat_lower)
            idx = np.logical_and(nwlons<=lon_left,selons>=lon_right)
            idf = np.logical_and(idx,idy)
            tile_count[i,j] = np.sum(idf)

            

    for i in range(nlat-1):
        lat_lower = lat[i]
        lat_upper = lat[i+1]
        for j in range(nlon-1):
            lon_left = lon[j]
            lon_right = lon[j+1]
            if(tile_count[i,j]>=Nview):
                #print(lat_upper,lon_left)
                utm_point = utm.from_latlon(lat_upper,lon_left)
                easting = utm_point[0]
                northing = utm_point[1]
                zone = utm_point[2]
                if(lat_upper>=0):
                    hemi = 'N'
                else:
                    hemi = 'S'
                print(easting,northing,hemi,zone)

                
if __name__ == '__main__':
    
    direct = '/scratch/e.conway/3DReconstruction/Jacksonville/Jacksonville_Images'
    main(direct,Nview=10,rangex=2000,rangey=2000)
