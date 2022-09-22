#  ===============================================================================================================
#  Copyright (c) 2019, Cornell University. All rights reserved.
#
#  Redistribution and use in source and binary forms, with or without modification, are permitted provided that
#  the following conditions are met:
#
#      * Redistributions of source code must retain the above copyright otice, this list of conditions and
#        the following disclaimer.
#
#      * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and
#        the following disclaimer in the documentation and/or other materials provided with the distribution.
#
#      * Neither the name of Cornell University nor the names of its contributors may be used to endorse or
#        promote products derived from this software without specific prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED
#  WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
#  A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDERS OR CONTRIBUTORS BE LIABLE
#  FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
#  TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
#  HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
#   NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY
#  OF SUCH DAMAGE.
#
#  Author: Kai Zhang (kz298@cornell.edu)
#
#  The research is based upon work supported by the Office of the Director of National Intelligence (ODNI),
#  Intelligence Advanced Research Projects Activity (IARPA), via DOI/IBC Contract Number D17PC00287.
#  The U.S. Government is authorized to reproduce and distribute copies of this work for Governmental purposes.
#  ===============================================================================================================


from colmap.read_model import read_model
import numpy as np
import json
import os


def read_tracks(colmap_images, colmap_points3D):
    all_tracks = []     # list of dicts; each dict represents a track
    all_points = []     # list of all 3D points
    view_keypoints = {} # dict of lists; each list represents the triangulated key points of a view


    for point3D_id in colmap_points3D:
        point3D = colmap_points3D[point3D_id]
        image_ids = point3D.image_ids
        point2D_idxs = point3D.point2D_idxs

        cur_track = {}
        cur_track['xyz'] = (point3D.xyz[0], point3D.xyz[1], point3D.xyz[2])
        cur_track['err'] = point3D.error

        cur_track_len = len(image_ids)
        assert (cur_track_len == len(point2D_idxs))
        all_points.append(list(cur_track['xyz'] + (cur_track['err'], cur_track_len) + tuple(point3D.rgb)))

        pixels = []
        for i in range(cur_track_len):
            image = colmap_images[image_ids[i]]
            img_name = image.name
            point2D_idx = point2D_idxs[i]
            point2D = image.xys[point2D_idx]
            assert (image.point3D_ids[point2D_idx] == point3D_id)
            pixels.append((img_name, point2D[0], point2D[1]))

            if img_name not in view_keypoints:
                view_keypoints[img_name] = [(point2D[0], point2D[1]) + cur_track['xyz'] + (cur_track_len, ), ]
            else:
                view_keypoints[img_name].append((point2D[0], point2D[1]) + cur_track['xyz'] + (cur_track_len, ))

        cur_track['pixels'] = sorted(pixels, key=lambda x: x[0]) # sort pixels by the img_name
        all_tracks.append(cur_track)

    return all_tracks, all_points, view_keypoints


def read_camera_dict(colmap_cameras, colmap_images):
    camera_dict = {}
    for image_id in colmap_images:
        image = colmap_images[image_id]

        img_name = image.name
        cam = colmap_cameras[image.camera_id]

        img_size = (cam.width, cam.height)
        params = tuple(cam.params)
        qvec = tuple(image.qvec)
        tvec = tuple(image.tvec)

        # w, h, fx, fy, cx, cy, s, qvec, tvec
        camera_dict[img_name] = img_size + params + qvec + tvec

    return camera_dict


def extract_camera_dict(sparse_dir, ext='.txt'):
    colmap_cameras, colmap_images, _ = read_model(sparse_dir, ext)

    camera_dict = read_camera_dict(colmap_cameras, colmap_images)

    return camera_dict


def extract_all_to_dir(sparse_dir, out_dir, ext='.txt'):
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)

    camera_dict_file = os.path.join(out_dir, 'kai_cameras.json')
    xyz_file = os.path.join(out_dir, 'kai_points.txt')
    track_file = os.path.join(out_dir, 'kai_tracks.json')
    keypoints_file = os.path.join(out_dir, 'kai_keypoints.json')
    
    colmap_cameras, colmap_images, colmap_points3D = read_model(sparse_dir, ext)
    camera_dict = read_camera_dict(colmap_cameras, colmap_images)
    with open(camera_dict_file, 'w') as fp:
        json.dump(camera_dict, fp, indent=2, sort_keys=True)

    all_tracks, all_points, view_keypoints = read_tracks(colmap_images, colmap_points3D)
    np.savetxt(xyz_file, np.array(all_points), header='# format: x, y, z, reproj_err, track_len, color(RGB)', fmt='%.6f')

    with open(track_file, 'w') as fp:
        json.dump(all_tracks, fp)

    with open(keypoints_file, 'w') as fp:
        json.dump(view_keypoints, fp)


if __name__ == '__main__':
    sparse_dir = '/data2/kz298/mvs3dm_result/MasterProvisional2/colmap/sfm_perspective/init_triangulate'
    out_dir = '/data2/kz298/tmp'
    extract_all_to_dir(sparse_dir, out_dir)
