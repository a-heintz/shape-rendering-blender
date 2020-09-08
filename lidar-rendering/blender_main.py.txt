import bpy
from bpy import data as D
from bpy import context as C
from mathutils import *
from math import *
import numpy as np
import blensor

num_seqs_start = 50
num_seqs = 5000
num_seqs_end = num_seqs_start + num_seqs
# total number of steps in the orbit (each scan is taken at 0.6 seconds)
time_final = 6000
# list of each of the steps
time_trajectory = list(range(0,time_final))
seqs = list(np.linspace(num_seqs_start,num_seqs_end,num_seqs).astype(int))
nums_points = 128
nums_points = [nums_points**2, nums_points**2]

def create_and_save_scan(data_path, traj_path, thetas_path, seq, num, xyz_traj, thetas_traj, lens_angle_w, lens_angle_h, flength, num_points):
    new_xyz_loc = xyz_traj[num] / 1000.
    
    new_theta = thetas_traj[num]
    print(new_xyz_loc, new_theta)
    scanner = bpy.data.objects["Camera"]
    scanner.location = new_xyz_loc
    scanner.rotation_euler[0] = new_theta[0]
    scanner.rotation_euler[1] = new_theta[1]
    scanner.rotation_euler[2] = new_theta[2]
    '''
    Scan the scene with the Velodyne scanner and save it
                to the file "/tmp/scan.pcd"
                Note: The data will actually be saved to /tmp/blender_scans/scan00000.pcd
                and /tmp/scan_noisy00000.pcd
    '''
    evd_file_path = data_path+'blender_scans/scan_seq_'+str(int(seq)).zfill(6)+'_num_'+str(num).zfill(6)+'_.pcd'
    pt_dim = int(np.floor(np.sqrt(num_points)))
    blensor.tof.scan_advanced(scanner, max_distance = 20, evd_file= evd_file_path, 
                                add_blender_mesh = False, add_noisy_blender_mesh = False, tof_res_x = pt_dim, tof_res_y = pt_dim, 
                                lens_angle_w=lens_angle_w, lens_angle_h=lens_angle_h, flength = flength,  evd_last_scan=True, 
                                noise_mu=0.0, noise_sigma=0.000, timestamp = 0.0, backfolding=False)
                                
idx = 0
#for idx in range(len(nums_points)):
num_points = nums_points[idx]
if idx == 0:
    data_path = 'D:/pcl_reg_nav/data_'+str(num_points)+'pts_large/'
if idx == 1:
    data_path = 'D:/pcl_reg_nav/data_'+str(num_points)+'pts/'
traj_path = data_path+'data/trajectories/blender/positions/'
thetas_path = data_path+'data/trajectories/blender/thetas/'
for seq in range(num_seqs_start, num_seqs):
    try:
        xyz_trajectory = np.load(traj_path+str(int(seq)).zfill(6)+'.npy')
        thetas_trajectory = np.load(thetas_path+str(int(seq)).zfill(6)+'.npy')   
        if idx == 0:
            xyz_trajectory_large_image_idx = list(range(0,time_final,time_final // 30))
            xyz_trajectory = xyz_trajectory[xyz_trajectory_large_image_idx]
            thetas_trajectory = thetas_trajectory[xyz_trajectory_large_image_idx]
        dist = np.linalg.norm(xyz_trajectory, 2, axis=1)
        for num in range(len(xyz_trajectory[:])):
            r = dist[num] / 1000.
            print('dist, ', r)
            foc_length = r / 9. * 1500.
            print('fl, ', foc_length)
            if idx == 0:
                create_and_save_scan(data_path, traj_path, thetas_path, seq, num, xyz_trajectory, thetas_trajectory, 60, 60, foc_length, num_points)
            if idx == 1:
                create_and_save_scan(data_path, traj_path, thetas_path, seq, num, xyz_trajectory, thetas_trajectory, 30, 30, foc_length, num_points)
    except Exception as ex:        
        print(ex)