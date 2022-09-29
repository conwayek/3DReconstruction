#!bin/bash
# command to run VisSat for Large Region on SDE
# Example is for Jacksonville, FL. 

podman run -v /data/e.conway:/3DReconstruction/ containers.rc.northeastern.edu/usace/colmap:v3.8 python3 /3DReconstruction/3DReconstruction/VisSat/RunJVille.py > RunJVille.out


