import os
import sys

sys.path.append('/3DReconstruction/3DReconstruction/VisSat/')

with open('/3DReconstruction/3DReconstruction/VisSat/Regions_JVille.txt','r') as f:
    lines = f.readlines()

nregions = len(lines)

for i in range(nregions):
    line = lines[i].split(' ')
    workdir = '/3DReconstruction/3DReconstruction/VisSat/DSMJVille_'+str(int(float(line[0])))+'_'+str(int(float(line[1])))
    datadir = '/3DReconstruction/3DReconstruction/JacksonvilleWV3/'
    cmd = str("python3 /3DReconstruction/3DReconstruction/VisSat/stereo_pipeline.py --config_file /3DReconstruction/3DReconstruction/VisSat/Test.json \
--easting {} --northing {} --zone {} --hemi {} --width {} --height {} --workdir {} --datadir {} --env {} ")
    #os.system(cmd.format(str(line[0]),str(line[1]),str(line[3].split('\n')[0]),str(line[2]),1000,1000,workdir,datadir,'SDE'))
    print(cmd.format(str(line[0]),str(line[1]),str(line[3].split('\n')[0]),str(line[2]),1000,1000,workdir,datadir,'SDE'))
