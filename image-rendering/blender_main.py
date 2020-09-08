import bpy
import os
import csv
import math
import mathutils
import numpy
import random

def delete_objects():
    '''Delete all objects
    Inputs:
    -- None
    Outputs:
    -- None
    '''
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.select_all(action='SELECT')
    n = len(bpy.context.selected_objects)
    bpy.ops.object.delete()

def delete_cameras():
    '''Delete all cameras
    Inputs:
    -- None
    Outputs:
    -- None
    '''  
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.select_pattern(pattern="Camera*")
    n = len(bpy.context.selected_objects)
    bpy.ops.object.delete()

def delete_lamps():
    '''Delete all lamps
    Inputs:
    -- None
    Outputs:
    -- None
    ''' 
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.select_pattern(pattern="New Lamp*")
    n = len(bpy.context.selected_objects)
    bpy.ops.object.delete()
    
def delete_unused_materials():
    '''Delete all unused materials (also done automatically after reload)
    Inputs:
    -- None
    Outputs:
    -- None
    '''
    i = 0
    for mat in bpy.data.materials:
        if mat.users == 0:
            name = mat.name
            bpy.data.materials.remove(mat)
            i = i + 1

def delete_unused_textures():
    '''Delete all unused textures.
    Inputs:
    -- None
    Outputs:
    -- None
    ''' 
    i = 0
    for tex in bpy.data.textures:
        if tex.users == 0:
            name = tex.name
            bpy.data.textures.remove(tex)
            i = i + 1

def add_stl_object(name, path):
    '''Upload an STL file
    Inputs:
    -- name: object name
    -- path: path to STL file
    Outputs:
    -- obj: the uploaded STL object
    ''' 
    delete_objects()
    delete_unused_materials()
    delete_unused_textures()
    bpy.ops.import_mesh.stl(filepath=path)
    obj = bpy.context.object
    obj.name = name
    return obj

def set_stl_object_loc(obj, new_loc):
    '''Set the location of an uploaded STL object
    Inputs:
    -- obj: STL object
    -- new_loc: the new location (in [x,y,z])
    Outputs:
    -- None
    '''
    obj.location[0] = new_loc[0]
    obj.location[1] = new_loc[1]
    obj.location[2] = new_loc[2]


def add_sphere(name, location, radius):
    '''add a smooth uniform radius sphere to the current scene at a given location
    Inputs:
    -- name: name for the new sphere
    -- new_loc: location for the new sphere (in [x,y,z])
    -- radius: radius of the sphere
    Outputs:
    -- obj: the sphere object
    '''
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=16, ring_count=16, size=radius,#*2.0
        location=location, rotation=[0,0,0], calc_uvs=True)
    obj = bpy.context.object
    obj.name = name
    bpy.ops.object.shade_smooth()
    return obj

def update_camera(camera, new_loc=(0,0,0), rot=(0,0,0)):
    ''' Focus the camera in a particular direction and place the camera at a specific location.
    Inputs:
    -- camera: camera object
    -- new_loc: new location of the camera, default at (0,0,0)
    -- rot: new rotation, in euler angles (x,y,z), of the camera wrt fixed 3D scene axes, default at (0,0,0)
    Outputs:
    -- camera.location: new_loc
    '''
    camera.track_axis = 'POS_Z'
    camera.rotation_mode = 'XYZ'
    camera.rotation_euler[0] = rot[0]
    camera.rotation_euler[1] = rot[1]
    camera.rotation_euler[2] = rot[2]
    camera.location = new_loc
    return camera.location

def set_light_location(location):
    ''' Deletes all existing lamps, creates a new lamp and adds it at a specified location
    Inputs:
    -- location: new location (in [x,y,z])
    Outputs:
    -- lamp_obj: new lamp object
    '''
    item='LAMP'
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.select_by_type(type=item)
    bpy.ops.object.delete()
    scene = bpy.context.scene
    lamp_data = bpy.data.lamps.new(name="New Lamp", type='POINT')
    lamp_object = bpy.data.objects.new(name="New Lamp", object_data=lamp_data)
    scene.objects.link(lamp_object)
    lamp_object.location = location
    lamp_object.select = True
    scene.objects.active = lamp_object    
    return lamp_object

def set_light_location_Sun(location, intensity):
    ''' Deletes all existing lamps, creates a new lamp, of type "sun," with a specified intensity and adds it at a specified location
    Inputs:
    -- location: new location (in [x,y,z])
    -- intensity: new lamp intensity
    Outputs:
    -- lamp_obj: new lamp object
    '''
    item='LAMP'
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.select_by_type(type=item)
    bpy.ops.object.delete()
    scene = bpy.context.scene
    lamp_data = bpy.data.lamps.new(name="New Lamp", type='SUN')
    lamp_object = bpy.data.objects.new(name="New Lamp", object_data=lamp_data)
    scene.objects.link(lamp_object)
    lamp_object.location = location
    lamp_object.data.energy = intensity
    lamp_object.select = True
    scene.objects.active = lamp_object
    return lamp_object

def set_camera_location(location):
    ''' Deletes all existing cameras, creates a new one and adds it at a specified location
    Inputs:
    -- location: new location (in [x,y,z])
    Outputs:
    -- camera_obj: new camera object
    '''
    item='CAMERA'
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.select_by_type(type=item)
    bpy.ops.object.delete()
    scene = bpy.context.scene
    camera_object = bpy.data.objects.new(name="Camera")
    scene.objects.link(camera_object)
    camera_object.location = location
    camera_object.select = True
    scene.objects.active = camera_object
    return camera_object



def scene_setup(body_loc, sun_loc, stl_path):
    ''' Sets up the scene to include the desired objects. This uploads an STL file of the asteroid Itokawa (Data from JAXA) and creates a sun, both at specified locations.
    Make sure the mode is selected to 'Cycles Render.'

    It is recommended to change this method to whatever initial scene is desired

    Inputs:
    -- body_loc: location of stl object
    -- sun_loc: location of the "sun" lamp
    -- stl_path: path to stl file that is to be uploaded
    Outputs:
    -- None
    '''

    delete_objects()
    # the following uploads an stl object and links it to the current scene    
    obj = add_stl_object('asteroid-itokawa', itokawa)
    set_stl_object_loc(obj, body_loc)
    scene = bpy.data.scenes["Scene"]
    scene.use_nodes = True
    nodes = scene.node_tree.nodes
    for node in nodes:
        nodes.remove(node)    
    node_renderLayers = nodes.new(type='CompositorNodeRLayers')
    node_composite = nodes.new('CompositorNodeComposite')
    links = scene.node_tree.links
    link = links.new(node_renderLayers.outputs[0], node_composite.inputs[0])
    # the following adds a lamp and links it to the current scene
    delete_lamps()
    light_loc = sun_loc
    if 'Sun-1' in bpy.data.objects:
        bpy.ops.object.select_all(action='DESELECT')
        bpy.data.objects['Sun-1'].select = True
        bpy.ops.object.delete()
    add_sun(1, sun_loc, 1, 2000.0, 'Sun') # luminosity value not correct here
    world = bpy.data.worlds["World"]
    world.use_nodes = True
    nodes = world.node_tree.nodes
    for node in nodes:
        nodes.remove(node)

if __name__ == '__main__':
    # locations vars
    body_loc = [0.5,0.5,0] #units are in km
    sun_loc = [-25,-35,0] #units are in km
    # paths
    dir = os.path.dirname(bpy.data.filepath) + os.sep
    stl_path = dir + 'stl_files/itokawa_f3145728.stl' # stl file path
    blender_path = 'D:/project/itokawa_blender/' # path which contains the necessary files to be read (pos_xyz_filename, euler_pose_xyz_filename)
    pos_xyz_filename = '_pos_xyz.npy' # file which contains the time-correlated sequence of positions in the sequence
    euler_pose_xyz_filename = '_euler_pose_xyz.npy' # file which contains the time-correlated sequence of euler angle rotations in the sequence
    write_path = 'D:/project/itokawa_x/' # path to folder where rendered images are written
    write_file_name = 'FILL_IN_WITH_DESIRED_FILE_NAME'
    ''' SCENE SETUP '''
    scene_setup(body_loc, sun_loc, stl_path)

    # load position and rotation files for the sequence
    pos_xyz = numpy.load(blender_path+pos_xyz_filename) # formatted as a list of lists which contain x,y,z positions at each time step
    euler_pose_xyz = numpy.load(blender_path+euler_pose_xyz_filename) # formatted as a list of lists which contain x,y,z euler angles at each time step
    len_pos_xyz = len(pos_xyz)
    # loop through each time step and render/save the camera view
    for i in range(len_pos_xyz):
        file_num = i
        cam_loc = [pos_xyz[i,0],pos_xyz[i,1],pos_xyz[i,2]]
        camera_rot = [euler_pose_xyz[i,0],euler_pose_xyz[i,1],euler_pose_xyz[i,2]]
        delete_cameras()
        # create and set up stereo camera. for monocular camera, see methods above
        bpy.ops.object.camera_add(location=cam_loc, rotation=camera_rot)
        bpy.context.scene.camera=bpy.data.objects['Camera']
        bpy.context.scene.render.use_multiview = True
        bpy.context.object.data.lens = 15
        bpy.context.object.data.stereo.convergence_mode = 'PARALLEL'
        bpy.context.object.data.stereo.interocular_distance = 0.01
        # make the background black
        bpy.context.scene.world.horizon_color = (0, 0, 0) 
        scene = bpy.data.scenes["Scene"]
        scene.render.alpha_mode = 'SKY'
        # set rendered image settings
        scene.render.resolution_x = 1024
        scene.render.resolution_y = 1024
        scene.render.resolution_percentage = 100
        scene.render.filepath = write_path + write_file_name +'.png'
        # render and save image
        bpy.ops.render.render( write_still=True )