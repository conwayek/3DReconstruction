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


import os
from colmap_sfm_utils import write_template_perspective
import json
import colmap_sfm_commands
from colmap.extract_sfm import extract_camera_dict


def make_subdirs(sfm_dir):
    subdirs = [
                sfm_dir,
                os.path.join(sfm_dir, 'tri'),
                os.path.join(sfm_dir, 'tri_ba')
    ]

    for item in subdirs:
        if not os.path.exists(item):
            os.mkdir(item)


def run_sfm(work_dir, sfm_dir, init_camera_file, weight):
    make_subdirs(sfm_dir)

    img_dir = os.path.join(sfm_dir, 'images')
    db_file = os.path.join(sfm_dir, 'database.db')

    colmap_sfm_commands.run_sift_matching(img_dir, db_file, camera_model='PERSPECTIVE')

    with open(init_camera_file) as fp:
        init_camera_dict = json.load(fp)
    with open(os.path.join(sfm_dir, 'init_camera_dict.json'), 'w') as fp:
        json.dump(init_camera_dict, fp, indent=2, sort_keys=True)

    # iterate between triangulation and bundle adjustment
    for reproj_err_threshold in [32.0, 2.0]:
        # triangulate
        init_template = os.path.join(sfm_dir, 'init_template.json')
        write_template_perspective(init_camera_dict, init_template)
        tri_dir = os.path.join(sfm_dir, 'tri')
        colmap_sfm_commands.run_point_triangulation(img_dir, db_file, tri_dir, init_template,
                                                    reproj_err_threshold, reproj_err_threshold, reproj_err_threshold)

        # global bundle adjustment
        tri_ba_dir = os.path.join(sfm_dir, 'tri_ba')
        colmap_sfm_commands.run_global_ba(tri_dir, tri_ba_dir, weight)

        # update camera dict
        init_camera_dict = extract_camera_dict(tri_ba_dir)

    with open(os.path.join(sfm_dir, 'init_ba_camera_dict.json'), 'w') as fp:
        json.dump(init_camera_dict, fp, indent=2, sort_keys=True)

    # for later uses: check how big the image-space translations are
    with open(os.path.join(sfm_dir, 'init_camera_dict.json')) as fp:
        pre_bundle_cameras = json.load(fp)

    with open(os.path.join(sfm_dir, 'init_ba_camera_dict.json')) as fp:
        after_bundle_cameras = json.load(fp)

    result = ['img_name, delta_cx, delta_cy\n', ]
    for img_name in sorted(pre_bundle_cameras.keys()):
        # w, h, fx, fy, cx, cy, s, qw, qx, qy, qz, tx, ty, tz
        pre_bundle_params = pre_bundle_cameras[img_name]
        after_bundle_params = after_bundle_cameras[img_name]
        delta_cx = after_bundle_params[4] - pre_bundle_params[4]
        delta_cy = after_bundle_params[5] - pre_bundle_params[5]

        result.append('{}, {}, {}\n'.format(img_name, delta_cx, delta_cy))

    with open(os.path.join(sfm_dir, 'principal_points_adjustment.csv'), 'w') as fp:
        fp.write(''.join(result))
