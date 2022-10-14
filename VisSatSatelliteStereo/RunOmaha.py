import os
import sys
import pyproj

sys.path.append('/3DReconstruction/3DReconstruction/VisSat/')

with open('/3DReconstruction/3DReconstruction/VisSat/Regions_Omaha.txt','r') as f:
    lines = f.readlines()

nregions = len(lines)

for i in range(nregions):
    line = lines[i].split(' ')

    hemi = str(line[2])

    if hemi == 'N':
        south = False
    else:
        south = True

    zone_number = int(line[3].split('\n')[0])

    east = float(line[0])
    north = float(line[1])

    proj = pyproj.Proj(proj='utm', ellps='WGS84', zone=zone_number, south=south)
    lon, lat = proj(east, north, inverse=True)

    workdir = '/3DReconstruction/3DReconstruction/VisSat/Omaha_'+str(lon)+'_'+str(lat)
    datadir = '/3DReconstruction/3DReconstruction/OmahaWV3/'


    cmd = str("python3 /3DReconstruction/3DReconstruction/VisSat/stereo_pipeline.py --config_file /3DReconstruction/3DReconstruction/VisSat/Test.json \
--easting {} --northing {} --zone {} --hemi {} --width {} --height {} --workdir {} --datadir {} --env {} ")
    os.system(cmd.format(str(east),str(north),str(zone_number),hemi,1000,1000,workdir,datadir,'SDE'))
    #print(cmd.format(str(line[0]),str(line[1]),str(line[3].split('\n')[0]),str(line[2]),2000,2000,workdir,datadir,'SDE'))
