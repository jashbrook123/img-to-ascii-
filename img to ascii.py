import pygame
import moderngl
import sys
from array import array
from PIL import Image

v = open("vertex_shader.glsl")
f = open("fragment_shader.glsl")



wh = (600,600)
w,h = 600,600
cell_width,cell_height = 6,6

ascii_chars = " .:-=+*#%@"
char_len = len(ascii_chars)
atlas_row = 1
atlas_col = 10
glyph_width,glyph_height = cell_width,cell_height

file_name = input("What is the name of the file (ohne extension - must be png):\n")

screen= pygame.display.set_mode(wh, pygame.OPENGL | pygame.DOUBLEBUF)
display = pygame.Surface(wh)

img = pygame.image.load(f"{file_name}.png").convert_alpha()
img = pygame.transform.scale(img,wh)

ctx = moderngl.create_context()

atlas_surface = pygame.image.load("ascii_atlas_big.png").convert()
atlas_bytes = pygame.image.tostring(atlas_surface,"RGB")
atlas_tex = ctx.texture(
    (atlas_surface.get_width(), atlas_surface.get_height()),
    3,  # grayscale
    atlas_bytes
)



clock = pygame.time.Clock()

        
quad_buffer = ctx.buffer(data=array("f",[
    -1.0,1.0,0.0,0.0,
    1.0,1.0,1.0,0.0,
    -1.0,-1.0,0.0,1.0,
    1.0,-1.0,1.0,1.0,
]))    
program  = ctx.program(vertex_shader = v.read(),
                       fragment_shader = f.read()
                       )
render_object = ctx.vertex_array(program,[(quad_buffer, "2f 2f", "vert","texcoord")])

def surf_to_texture(surf):
    tex = ctx.texture(surf.get_size(), 4)
    tex.filter = (moderngl.NEAREST,moderngl.NEAREST)
    tex.swizzle = "BGRA"
    tex.write(surf.get_view("1"))
    return tex

def save_screenshot(ctx, filename):
    data = ctx.screen.read(components=4, alignment=1)
    width, height = ctx.screen.size
    img = Image.frombytes("RGBA", (width, height), data)
    img = img.transpose(Image.FLIP_TOP_BOTTOM)
    img.save(f"{filename}.png")
    print("Saved", filename)

have_saved = False
while True:
    
    display.fill((0,0,0))

    display.blit(img,(0,0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                cell_width += 1
                cell_height += 1
            if event.key == pygame.K_s:
                cell_width -= 1
                cell_height -= 1
    
    frame_tex = surf_to_texture(display)
    frame_tex.use(0)
    atlas_tex.use(1)
    program["tex"] = 0
    program["atlas_tex"] = 1
    program["resolution"] = wh
    program["cell_width"] = cell_width
    program["cell_height"] = cell_height
    program["atlas_col"] = atlas_col
    program["atlas_row"] = atlas_row
    
    render_object.render(mode=moderngl.TRIANGLE_STRIP)
    if have_saved == False:
        save_screenshot(ctx,f"{file_name}_ascii")
        have_saved = True
        
    pygame.display.flip()
    frame_tex.release()
    clock.tick(60)
