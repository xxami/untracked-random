
# PNG2SMD
#
# Converts each pixel in a PNG image to an SMD model (cube per pixel)
# Optimizes for same coloured pixels and adjacent pixels (faces)
# Using: Python-2.5+ (python.org), pypng (code.google.com/p/pypng)
#
# Usage: png2smd.py <-f> <-x> <-y> <-z> [-c]
#
#    -f specify input file (ie. -f file.png) - mandatory
#    -x specify width-per-pixel (ie. -x 32) - mandatory
#    -y specify depth-per-pixel (ie. -y 16) - mandatory
#    -z specify height-per-pixel (ie. -z 32) - mandatory
#    -c specify collision mesh scale (ie. -c 1.0) - optional
#
# if -c is not specified, no collision mesh will be generated
# mesh scale only affects the x and y dimensions (of the image)
# if mesh scale is 0, mesh will be generated based on min/max bounds
#

from __future__ import with_statement
import os
import sys
import png
import getopt
from psmdlib import Model, Objects, UV, Vec3 as Vector

DEBUG = 0

# RGBA structure (r, g, b, a)
class RGBA(object):

    # Constructor
    def __init__(self, r, g, b, a = 255):
        self.r = r
        self.g = g
        self.b = b
        self.a = a

# png.Reader wrapper for reading an 8-bpp RGBA image
class RgbaPngImage8(object):

    # Constructor: Load data from image
    def __init__(self, file_path):
        self.file_path = file_path
        self.file_name = os.path.basename(file_path)

        reader = png.Reader(filename = self.file_path)
        self.data = reader.asRGBA()
        try: data_siz = len(self.data)
        except TypeError: data_siz = 0
        if data_siz == 4: self.validate_file()
        else: raise Exception('Couldn\'t read PNG data')
        
    # Ensure the image is a valid 8-bpp RGBA image
    def validate_file(self):
        self.width, self.height = self.data[0], self.data[1]
        self.bitdepth, self.alpha = None, None
        props = self.data[3]
        if props.has_key('bitdepth'):
            self.bitdepth = props['bitdepth']
        if props.has_key('alpha'):
            self.alpha = props['alpha']
        if (self.width, self.height) >= (256, 256):
            print('Warning: High-res images may result in models with far too many vertices!')
        if not self.bitdepth == 8:
            raise Exception('Image must use 8 bits per channel')
        if not self.alpha:
            raise Exception('Image must have an alpha channel')
        self.image = self.data[2]

# Structure of pixel data with some hints for 3D (pixel to cube) translation
class PixelCube(object):
    
    # Constructor: Setup structure
    def __init__(self, position, colour):
        self.position = position
        self.colour = colour
        self.scale = Vector(1, 1, 1)
        self.ex_faces = list()
        self.visible = True
        
# Used to represent an image in 3D cubes
class PixelCubeImage(object):

    # Constructor: Create needed cubes from an RgbaPngImage8 image
    def __init__(self, img):
        self.original_file_name = img.file_name
        self.width, self.height = img.width, img.height
        self.colour_palette = {}
        self.cubes = []
        self.positions2d = []
        x, y, i = 0, 0, 0
        for row in img.image:
            i = 0
            row_siz = len(row)
            if row_siz >= 4:
                while i < row_siz:
                    vpos = Vector(x, y, 0)
                    rgba = self.get_rgba_from_palette(
                        row[i], row[i+1], row[i+2], row[i+3])
                    self.cubes.append(PixelCube(vpos, rgba))
                    if not rgba.a == 0:
                        self.positions2d.append((vpos.x, vpos.y))
                    x += 1
                    i += 4
            else: raise Exception('Unexpected end-of-file')
            x = 0
            y += 1

    # Use colour palette as a cache to return colours
    def get_rgba_from_palette(self, r, g, b, a):
        if (r, g, b, a) in self.colour_palette:
            return self.colour_palette[(r, g, b, a)]
        else:
            self.colour_palette[(r, g, b, a)] = RGBA(r, g, b, a)
            return self.colour_palette[(r, g, b, a)]
        
    # Optimize for adjacent rows of the same colour
    def optimize_rows(self):
        cube_prev = PixelCube(Vector(-1, -1, -1), RGBA(-1, -1, -1, -1))
        for cube in self.cubes:
            if cube.colour.a == 0: cube.visible = False
            else:
                col, colp = cube.colour, cube_prev.colour
                pos, posp = cube.position, cube_prev.position
                if pos.y == posp.y and colp.a > 0:
                    if (col.r, col.g, col.b) == (colp.r, colp.g, colp.b):
                        cube_prev.scale.x += 1
                        cube.visible = False
                        continue
            cube_prev = cube
            
    # Optimize for adjacent columns of the same colour
    def optimize_columns(self):
        x = 0
        cube_prev = PixelCube(Vector(-1, -1, -1), RGBA(-1, -1, -1, -1))
        while x < self.width:
            for i in reversed(range(x, self.width * self.height, self.width)):
                cube = self.cubes[i]
                col, colp = cube.colour, cube_prev.colour
                pos, posp = cube.position, cube_prev.position
                if cube_prev.scale.x > 1:
                    cube_prev = cube
                    continue
                if cube.visible and cube.scale.x == 1 and cube_prev.visible and pos.x == posp.x:
                    if (col.r, col.g, col.b) == (colp.r, colp.g, colp.b):
                        cube_prev.scale.y += 1
                        cube.visible = False
                        continue
                cube_prev = cube
            x += 1
            
    # Optimize generated faces to cut down on unnecessary drawing
    def optimize_faces(self):
        in_pos2d = lambda x, y: (x, y) in self.positions2d
        for cube in self.cubes:
            if not cube.visible: continue
            x, y = cube.position.x, cube.position.y
            inc_faces = {
                'left' : False, 'right' : False, 'top' : False, 'bottom' : False }
            for ix in range(x, x + cube.scale.x):
                if in_pos2d(ix-1, y):
                    if not inc_faces['left'] and not 'left' in cube.ex_faces:
                        cube.ex_faces.append('left')
                else:
                    inc_faces['left'] = True
                    if 'left' in cube.ex_faces: cube.ex_faces.remove('left')
                if in_pos2d(ix+1, y):
                    if not inc_faces['right'] and not 'right' in cube.ex_faces:
                        cube.ex_faces.append('right')
                else:
                    inc_faces['right'] = True
                    if 'right' in cube.ex_faces: cube.ex_faces.remove('right')
                if in_pos2d(ix, y-1):
                    if not inc_faces['top'] and not 'top' in cube.ex_faces:
                        cube.ex_faces.append('top')
                else:
                    inc_faces['top'] = True
                    if 'top' in cube.ex_faces: cube.ex_faces.remove('top')
                if in_pos2d(ix, y+1):
                    if not inc_faces['bottom'] and not 'bottom' in cube.ex_faces:
                        cube.ex_faces.append('bottom')
                else:
                    inc_faces['bottom'] = True
                    if 'bottom' in cube.ex_faces: cube.ex_faces.remove('bottom')
            if cube.scale.y == 1: continue
            for iy in reversed(range((y - cube.scale.y)+1, y+1)):
                if in_pos2d(x-1, iy):
                    if not inc_faces['left'] and not 'left' in cube.ex_faces:
                        cube.ex_faces.append('left')
                else:
                    inc_faces['left'] = True
                    if 'left' in cube.ex_faces: cube.ex_faces.remove('left')
                if in_pos2d(x+1, iy):
                    if not inc_faces['right'] and not 'right' in cube.ex_faces:
                        cube.ex_faces.append('right')
                else:
                    inc_faces['right'] = True
                    if 'right' in cube.ex_faces: cube.ex_faces.remove('right')
                if in_pos2d(x, iy-1):
                    if not inc_faces['top'] and not 'top' in cube.ex_faces:
                        cube.ex_faces.append('top')
                else:
                    inc_faces['top'] = True
                    if 'top' in cube.ex_faces: cube.ex_faces.remove('top')
                if in_pos2d(x, iy+1):
                    if not inc_faces['bottom'] and not 'bottom' in cube.ex_faces:
                        cube.ex_faces.append('bottom')
                else:
                    inc_faces['bottom'] = True
                    if 'bottom' in cube.ex_faces: cube.ex_faces.remove('bottom')
                    
    # Return list of PixelCubes uses to construct the image
    def get_cubes(self):
        return self.cubes
        
    # Return the colour palette
    def get_colour_palette(self):
        return self.colour_palette

    # Optimize data such that the produced model will be semi-efficient
    def optimize(self):
        self.optimize_rows()
        self.optimize_columns()
        self.optimize_faces()
        
    # Write the SMD model
    def write(self, file_name, vdimensions, texture_file, uvmap, collisions = None):
        uvcoord = lambda: uvmap[(rgba.r, rgba.g, rgba.b)]
        mdl = Model('mdl_' + file_name)
        cc = mdl.create(Objects.Cube)
        offset = Vector(float(self.width) / 2.0, float(vdimensions.y) / 2.0, float(self.height) / 2.0)
        x, y, x2, y2 = self.width +1 , self.height +1, -1, -1
        for cube in self.cubes:
            if not cube.visible:
                pos, scale, rgba = cube.position, cube.scale, cube.colour
                if rgba.a > 0:
                    if pos.x < x: x = pos.x
                    if pos.y < y: y = pos.y
                    if pos.x > x2: x2 = pos.x
                    if pos.y > y2: y2 = pos.y
                continue
            pos, scale, rgba = cube.position, cube.scale, cube.colour
            if pos.x < x: x = pos.x
            if pos.y < y: y = pos.y
            if pos.x > x2: x2 = pos.x
            if pos.y > y2: y2 = pos.y
            pos.x -= offset.x
            pos.y -= offset.z - 1
            pos.z -= offset.y
            cc.draw_cube(Vector(float(0) - offset.y, float(pos.x * vdimensions.x), float(-pos.y * vdimensions.z)),
                Vector(float(vdimensions.y), float(vdimensions.x * scale.x), float(vdimensions.z * scale.y)),
                texture_file, { 'top' : uvcoord(), 'bottom' : uvcoord(), 'front' : uvcoord(),
                    'right' : uvcoord(), 'back' : uvcoord(), 'left' : uvcoord(), },
                cube.ex_faces)
        mdl.save()
        if not collisions == None:
            mdl = Model('mdl_' + file_name.replace('.smd', '') + '_phys.smd')
            cc = mdl.create(Objects.Cube)
            auto_bb_collide = False
            if collisions == 0.0:
                auto_bb_collide = True
                w, h = (x2-x)+1, (y2-y)+1
                collisions = 1.0
            else:
                w, h = self.width, self.height
                offset = Vector(float(w * collisions * vdimensions.x) / 2.0,
                    float(vdimensions.y) / 2.0,
                    float((h * collisions * vdimensions.z) / 2.0))
            pos = Vector(0 if not auto_bb_collide else (x * vdimensions.x),
                0 if not auto_bb_collide else (((self.height - y2)-1) * vdimensions.z),
                0)
            scale = Vector(w * collisions, vdimensions.y, h * collisions)
            uvcoord = lambda: uvmap.values()[0]
            pos.x -= offset.x if not auto_bb_collide else offset.x * vdimensions.x
            pos.y -= offset.z if not auto_bb_collide else offset.z * vdimensions.z
            pos.z -= offset.y if not auto_bb_collide else offset.y * vdimensions.y
            cc.draw_cube(Vector(float(0) - offset.y, float(pos.x), float(pos.y)),
                         Vector((vdimensions.y), float(scale.x * vdimensions.x), float(scale.z * vdimensions.z)),
                texture_file, { 'top' : uvcoord(), 'bottom' : uvcoord(), 'front' : uvcoord(),
                    'right' : uvcoord(), 'back' : uvcoord(), 'left' : uvcoord(), },
                [])
            mdl.save()
        
    # Test to make sure faces are correctly optimized
    def test_render_face_visualization(self, f):
        pix2d = [[0]*(self.width*4) for i in range(self.height)]
        for cube in self.cubes:
            if not cube.visible and cube.colour.a == 0:
                continue
            if not cube.scale.x > 1:
                if not cube.scale.y > 1 and cube.visible:
                    rgb = [255,255,255]
                    if 'left' in cube.ex_faces: rgb = [rgb[0]-80,rgb[1],rgb[2]]
                    if 'right' in cube.ex_faces: rgb = [rgb[0]-80,rgb[1],rgb[2]-80]
                    if 'top' in cube.ex_faces: rgb = [rgb[0], rgb[1]-80,rgb[2]]
                    if 'bottom' in cube.ex_faces: rgb = [rgb[0], rgb[1]-80,rgb[2]-80]
                    pos = ((cube.position.x+1)*4)-4
                    pix2d[cube.position.y][pos] = rgb[0]
                    pix2d[cube.position.y][pos+1] = rgb[1]
                    pix2d[cube.position.y][pos+2] = rgb[2]
                    pix2d[cube.position.y][pos+3] = 255
                continue
            pos = ((cube.position.x+1) * 4)-4
            rgb = [255,255,255]
            if 'left' in cube.ex_faces: rgb = [rgb[0]-80,rgb[1],rgb[2]]
            if 'right' in cube.ex_faces: rgb = [rgb[0]-80,rgb[1],rgb[2]-80]
            if 'top' in cube.ex_faces: rgb = [rgb[0], rgb[1]-80,rgb[2]]
            if 'bottom' in cube.ex_faces: rgb = [rgb[0], rgb[1]-80,rgb[2]-80]
            for i in range(pos, pos + cube.scale.x * 4, 4):
                pix2d[cube.position.y][i] = rgb[0]
                pix2d[cube.position.y][i+1] = rgb[1]
                pix2d[cube.position.y][i+2] = rgb[2]
                pix2d[cube.position.y][i+3] = 255
        for cube in self.cubes:
            if cube.scale.y > 1:
                rgb = [255,255,255]
                if 'left' in cube.ex_faces: rgb = [rgb[0]-80,rgb[1],rgb[2]]
                if 'right' in cube.ex_faces: rgb = [rgb[0]-80,rgb[1],rgb[2]-80]
                if 'top' in cube.ex_faces: rgb = [rgb[0], rgb[1]-80,rgb[2]]
                if 'bottom' in cube.ex_faces: rgb = [rgb[0], rgb[1]-80,rgb[2]-80]
                for y in range(0, cube.scale.y):
                    pix2d[cube.position.y-y][((cube.position.x+1)*4)-4] = rgb[0]
                    pix2d[cube.position.y-y][(((cube.position.x+1)*4)-4)+1] = rgb[1]
                    pix2d[cube.position.y-y][(((cube.position.x+1)*4)-4)+2] = rgb[2]
                    pix2d[cube.position.y-y][(((cube.position.x+1)*4)-4)+3] = 255
        png.from_array(pix2d, 'RGBA').save(f)

    # Test to make sure optimizations are applied to the correct parts of the image
    def test_render_optimizer_visualization(self, f):
        pix2d = [[0]*(self.width*4) for i in range(self.height)]
        for cube in self.cubes:
            if not cube.visible and cube.colour.a == 0:
                continue
            if not cube.scale.x > 1: continue
            pos = ((cube.position.x+1) * 4)-4
            for i in range(pos, pos + cube.scale.x * 4, 4):
                pix2d[cube.position.y][i] = 255
                pix2d[cube.position.y][i+1] = 0
                pix2d[cube.position.y][i+2] = 0
                pix2d[cube.position.y][i+3] = 255
        for cube in self.cubes:
            if cube.scale.y > 1:
                for y in range(0, cube.scale.y):
                    pix2d[cube.position.y-y][((cube.position.x+1)*4)-4] = 0
                    pix2d[cube.position.y-y][(((cube.position.x+1)*4)-4)+1] = 0
                    pix2d[cube.position.y-y][(((cube.position.x+1)*4)-4)+2] = 255
                    pix2d[cube.position.y-y][(((cube.position.x+1)*4)-4)+3] = 255
        png.from_array(pix2d, 'RGBA').save(f)

    # Test to make sure ALL image data is stored correctly
    def test_render_image(self, f):
        pix2d = [[0]*(self.width*4) for i in range(self.height)]
        for cube in self.cubes:
            if (cube.position.x, cube.position.y) in self.positions2d:
                pix2d[cube.position.y][((cube.position.x+1) * 4)-4] = cube.colour.r
                pix2d[cube.position.y][((cube.position.x+1) * 4)-3] = cube.colour.g
                pix2d[cube.position.y][((cube.position.x+1) * 4)-2] = cube.colour.b
                pix2d[cube.position.y][((cube.position.x+1) * 4)-1] = cube.colour.a
        png.from_array(pix2d, 'RGBA').save(f)
        
# Generates a texture containing image colours and maps UV co-ordinates to them
class ImageColoursUVMap(object):

    # Constructor: Create textures/UV map from a list of container colours
    def __init__(self, texture_name, texture_colours):
        self.file_name = 'tex_' + texture_name
        self.colours = texture_colours
        self.image = []
        self.image_size = (0, 0)
        self.image_width = 0
        self.image_height = 0
        self.map = {}
        self.generate_textures()
        self.create_uv_map()
        
    # Create the UV map
    def create_uv_map(self):
        x, y, x2, y2, w, h = 0, 0, 16, 16, float(self.image_width), float(self.image_height)
        for c, rgba in self.colours.iteritems():
            if rgba.a == 0: continue
            self.map[c[:-1]] = {
                'top-left' : UV(float(x+4) / w, float(y+4) / h),
                'top-right' : UV(float(x2-4) / w, float(y+4) / h),
                'bottom-left' : UV(float(x+4) / w, float(y2-4) / h),
                'bottom-right' : UV(float(x2-4) / w, float(y2-4) / h),
            }
            x += 16
            x2 += 16
    
    # Generate textures (each 16x16 block is a unique colour from left->right)
    def generate_textures(self):
        for c, rgba in self.colours.iteritems():
            if not rgba.a == 0:
                self.draw_texture(16, 16, rgba)
        self.render_texture()
            
    # Helper function to draw a single 16x16 block of the texture
    def draw_texture(self, siz_x, siz_y, rgba):
        for y in xrange(siz_y):
            if y > len(self.image)-1:
                self.image.append(list())
            for x in xrange(siz_x):
                self.image[y].append(rgba.r)
                self.image[y].append(rgba.g)
                self.image[y].append(rgba.b)
        self.image_width = self.image_width + siz_x
        self.image_height = siz_y
            
    # Write the texture to an image file (PNG format)
    def render_texture(self):
        png.from_array(self.image, 'RGB').save(self.file_name)
            
    # Return the entire UV map
    def get_uv_map(self):
        return self.map
            
    # Return the UV co-ordinate for the appropriate given colour
    def get_uv_coord(self, rgba):
        return self.map[(rgba.r, rgba.g, rgba.b)]
        
def main(args):
    try:
        opts, args = getopt.getopt(args[1:], 'f:x:y:z:c:')
    except getopt.GetoptError, err:
        print(str(err))
        print('Usage: png2smd.py <-f input_file> <-x width> <-y depth> <-z height> [-c scale]')
        print('Note: <> are mandatory, where as [] are optional. See README for more details')
        return -1
    input_file, width, depth, height, collisions = None, None, None, None, None
    
    try:
        for opt, val in opts:
            if opt == '-f' and len(val) > 0: input_file = str(val)
            if opt == '-x' and len(val) > 0: width = int(val)
            if opt == '-y' and len(val) > 0: depth = int(val)
            if opt == '-z' and len(val) > 0: height = int(val)
            if opt == '-c' and len(val) > 0: collisions = float(val)
        if not input_file or not width or not depth or not height:
            raise Exception()
    except:
        print('Usage: png2smd.py <-f input_file> <-x width> <-y depth> <-z height> [-c scale]')
        print('Note: <> are mandatory, where as [] are optional. See README for more details')
        return -1
    
    try:
        err = 0
        print('Reading input file...')
        png_file = RgbaPngImage8(input_file)
        print('Converting between image formats...')
        image3d = PixelCubeImage(png_file)
        
        ##
        if DEBUG:
            print('Testing image...')
            image3d.test_render_image('test_image.png')
        ##
            
        print('Optimizing...')
        image3d.optimize()
        
        ##
        if DEBUG:
            print('Testing optimizations...')
            image3d.test_render_optimizer_visualization('test_image2.png')
            print('Testing face visibility...')
            image3d.test_render_face_visualization('test_image3.png')
        ##
            
        print('Generating textures and UV map...')
        imageuv = ImageColoursUVMap(image3d.original_file_name,
            image3d.get_colour_palette())
        print('Writing SMD model data...')
        image3d.write(image3d.original_file_name.replace('.png', '.smd'),
            Vector(width, depth, height),
            imageuv.file_name, imageuv.get_uv_map(), collisions)
    except IOError as e:
        err += 1
        print('Error: %s' % str(e))
        
    if err: return -1
    print('Finished! Bye~')
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv if (len(sys.argv) > 1) else
        'png2smd.py -f test.png -x 32 -y 16 -z 32 -c 1.0'.split()))

