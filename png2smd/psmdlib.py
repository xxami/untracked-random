
# Partial SMD Model Writer Lib
#
# Helps create valid .smd model files (static only)
# Using: Python-2.5+ (python.org)
#

from __future__ import with_statement

class Meta(object): pass
class Objects(object): pass

# SMD string formatter for meta information sections
Meta.Header = \
'''version 1
nodes
    0 "root" -1
end
skeleton
    time 0
    0 0.000000 0.000000 0.000000 0.000000 0.000000 0.000000
end
triangles
'''

Meta.Footer = '''end'''

# SMD string formatter for a single triangle
Meta.Triangle = \
'''%s
0    %s %s %s    %s %s %s    %s %s
0    %s %s %s    %s %s %s    %s %s
0    %s %s %s    %s %s %s    %s %s
'''

# 3D Vector (x, y, z)
class Vec3(object):

    # Constructor
    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z

# Normal vectors
Vec3.Up = Vec3(0, 0, 1)
Vec3.Down = Vec3(0, 0, -1)
Vec3.Backward = Vec3(-1, 0, 0)
Vec3.Forward = Vec3(1, 0, 0)
Vec3.Left = Vec3(0, -1, 0)
Vec3.Right = Vec3(0, 1, 0)
Vec3.Empty = Vec3(0, 0, 0)
        
# UV Texture co-ordinates (u, v)
class UV(object):

    # Constructor
    def __init__(self, u, v):
        self.u, self.v = u, v
    
# 3D SMD Model API  
class Model(object):

    # Constructor
    def __init__(self, file_name):
        self.file = file_name
        self.objects = list()
    
    # Adds an object to the model and returns its instance
    def create(self, obj):
        if issubclass(obj, ObjectMaker_TriangularFace):
            self.objects.append(obj())
            return self.objects[-1]
        else: raise TypeError('Invalid object type')
        
    # Saves the SMD file
    def save(self):
        with open(self.file, 'w') as f:
            f.write(Meta.Header)
            for obj in self.objects:
                f.write(obj.get_triangles())
            f.write(Meta.Footer)
    
# Base SMD triangle drawing code
class ObjectMaker_TriangularFace(object):

    # Constructor
    def __init__(self):
        self.triangles = str()
    
    # Write a triangle in the SMD format
    def draw_triangle(self, mat, vp1, vp2, vp3, vn1, vn2, vn3, uv1, uv2, uv3):
        self.triangles += Meta.Triangle % (
            mat,
            vp1.x, vp1.y, vp1.z, vn1.x, vn1.y, vn1.z, uv1.u, uv1.v,
            vp2.x, vp2.y, vp2.z, vn2.x, vn2.y, vn2.z, uv2.u, uv2.v,
            vp3.x, vp3.y, vp3.z, vn3.x, vn3.y, vn3.z, uv3.u, uv3.v)
            
    # Return all triangle data (ie. model data)
    def get_triangles(self):
        return self.triangles

# Model.create's public accessor wrapper for the ObjectMaker_TriangularFace class
Objects.TriangularFace = ObjectMaker_TriangularFace

# Primitive SMD cube drawing code
class ObjectMaker_Cube(ObjectMaker_TriangularFace):

    # Constructor
    def __init__(self):
        self.triangles = str()
        
    # Draw the triangles necessary to create a square face
    def draw_face(self, vbl, vbr, vtl, vtr, vnorms, mat, uvs, reversed_edge = False):
        if reversed_edge:
            self.draw_triangle(mat,
                vtr, vbr, vbl, vnorms, vnorms, vnorms,
                UV(1, 0) if not uvs else uvs['top-right'],
                UV(1, 1) if not uvs else uvs['bottom-right'],
                UV(0, 1) if not uvs else uvs['bottom-left'])
            self.draw_triangle(mat,
                vbl, vtl, vtr, vnorms, vnorms, vnorms,
                UV(0, 1) if not uvs else uvs['bottom-left'],
                UV(0, 0) if not uvs else uvs['top-left'],
                UV(1, 0) if not uvs else uvs['top-right'])
        else:
            self.draw_triangle(mat,
                vtl, vtr, vbr, vnorms, vnorms, vnorms,
                UV(0, 0) if not uvs else uvs['top-left'],
                UV(1, 0) if not uvs else uvs['top-right'],
                UV(1, 1) if not uvs else uvs['bottom-right'])
            self.draw_triangle(mat,
                vbr, vbl, vtl, vnorms, vnorms, vnorms,
                UV(1, 1) if not uvs else uvs['bottom-right'],
                UV(0, 1) if not uvs else uvs['bottom-left'],
                UV(0, 0) if not uvs else uvs['top-left'])
    
    # Draw the square faces necessary to create a cube
    def draw_cube(self, v1, v2, mats, uvs = False, ex_faces = list()):
        # top face
        bl = Vec3(v1.x, v1.y, v1.z + v2.z)  # bottom left vertex (top)
        br = Vec3(v1.x, v1.y + v2.y, v1.z + v2.z)  # bottom right vertex (top)
        tl = Vec3(v1.x + v2.x, v1.y, v1.z + v2.z)  # top left vertex (top)
        tr = Vec3(v1.x + v2.x, v1.y + v2.y, v1.z + v2.z)  # top right vertex (top)
        if not 'top' in ex_faces: self.draw_face(bl, br, tl, tr, Vec3.Up,
            mats if isinstance(mats, str) else mats['top'], None if not uvs else uvs['top']) 
        # bottom face
        bl = Vec3(v1.x + v2.x, v1.y, v1.z)  # bottom left vertex (bottom)
        br = Vec3(v1.x + v2.x, v1.y + v2.y, v1.z)  # bottom right vertex (bottom)
        tl = Vec3(v1.x, v1.y, v1.z)  # top left vertex (bottom)
        tr = Vec3(v1.x, v1.y + v2.y, v1.z)  # top right vertex (bottom)
        if not 'bottom' in ex_faces: self.draw_face(bl, br, tl, tr, Vec3.Down,
            mats if isinstance(mats, str) else mats['bottom'], None if not uvs else uvs['bottom'])
        # front face
        bl = Vec3(v1.x, v1.y, v1.z)  # bottom left vertex (front)
        br = Vec3(v1.x, v1.y + v2.y, v1.z)  # bottom right vertex (front)
        tl = Vec3(v1.x, v1.y, v1.z + v2.z)  # top left vertex (front)
        tr = Vec3(v1.x, v1.y + v2.y, v1.z + v2.z)  # top right vertex (front)
        if not 'front' in ex_faces: self.draw_face(bl, br, tl, tr, Vec3.Backward,
            mats if isinstance(mats, str) else mats['front'], None if not uvs else uvs['front'])
        # right-side face
        bl = Vec3(v1.x, v1.y + v2.y, v1.z)  # bottom left vertex (right)
        br = Vec3(v1.x + v2.x, v1.y + v2.y, v1.z)  # bottom right vertex (right)
        tl = Vec3(v1.x, v1.y + v2.y, v1.z + v2.z)  # top left vertex (right)
        tr = Vec3(v1.x + v2.x, v1.y + v2.y, v1.z + v2.z)  # top right vertex (right)
        if not 'right' in ex_faces: self.draw_face(bl, br, tl, tr, Vec3.Right,
            mats if isinstance(mats, str) else mats['right'], None if not uvs else uvs['right'], True)
        # back face
        bl = Vec3(v1.x + v2.x, v1.y + v2.y, v1.z)  # bottom left vertex (back)
        br = Vec3(v1.x + v2.x, v1.y, v1.z)  # bottom right vertex (back)
        tl = Vec3(v1.x + v2.x, v1.y + v2.y, v1.z + v2.z)  # top left vertex (back)
        tr = Vec3(v1.x + v2.x, v1.y, v1.z + v2.z)  # top right vertex (back)
        if not 'back' in ex_faces: self.draw_face(bl, br, tl, tr, Vec3.Forward,
            mats if isinstance(mats, str) else mats['back'], None if not uvs else uvs['back'])
        # left-side face
        bl = Vec3(v1.x + v2.x, v1.y, v1.z)  # bottom left vertex (back)
        br = Vec3(v1.x, v1.y, v1.z)  # bottom right vertex (back)
        tl = Vec3(v1.x + v2.x, v1.y, v1.z + v2.z)  # top left vertex (back)
        tr = Vec3(v1.x, v1.y, v1.z + v2.z)  # top right vertex (back)
        if not 'left' in ex_faces: self.draw_face(bl, br, tl, tr, Vec3.Left,
            mats if isinstance(mats, str) else mats['left'], None if not uvs else uvs['left'], True)
        
# Model.create's public accessor wrapper for the ObjectMaker_Cube class
Objects.Cube = ObjectMaker_Cube

