GlowScript 3.2 VPython

# 1. Scene Setup
scene.background = color.black
scene.title = "Irregular Gem: Center of Mass Analysis"
scene.width = 800
scene.height = 600

# 2. Gem vertices (The 2D shape/footprint)
gem_vertices = [
    vec(0, -4, 0), vec(3, -2, 0), vec(4, 1, 0), vec(2, 4, 0),
    vec(-1, 3.5, 0), vec(-4, 2, 0), vec(-3, -1, 0)
]

# 3. Physics Functions
def gem_height(x, y):
    return 2 + 0.5*sin(x) + 0.3*cos(y)

def density(x, y, z):
    # Density increases as we move to the right (+x)
    return 1 + 0.5 * x

def is_inside(x, y, poly):
    n = len(poly)
    inside = False
    p1x, p1y = poly[0].x, poly[0].y
    for i in range(n + 1):
        p2x, p2y = poly[i % n].x, poly[i % n].y
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xints = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xints:
                        inside = not inside
        p1x, p1y = p2x, p2y
    return inside

# 4. Numerical Triple Integration for Center of Mass
nx = ny = nz = 25 
x_vals = [-4 + 8*i/(nx-1) for i in range(nx)]
y_vals = [-4 + 8*i/(ny-1) for i in range(ny)]
z_vals = [-3 + 6*i/(nz-1) for i in range(nz)]

dx, dy, dz = x_vals[1]-x_vals[0], y_vals[1]-y_vals[0], z_vals[1]-z_vals[0]
dV = dx*dy*dz

total_mass = 0
rx = ry = rz = 0

for x in x_vals:
    for y in y_vals:
        if is_inside(x, y, gem_vertices):
            h = gem_height(x, y)
            for z in z_vals:
                if -h <= z <= h:
                    m = density(x, y, z) * dV
                    total_mass += m
                    rx += x * m
                    ry += y * m
                    rz += z * m

Cx, Cy, Cz = rx/total_mass, ry/total_mass, rz/total_mass
com_vec = vec(Cx, Cy, Cz)

# 5. Create Gem Geometry
faces = []
vertices_top = []
vertices_bottom = []

for v in gem_vertices:
    z_h = gem_height(v.x, v.y)
    vertices_top.append(vec(v.x, v.y, z_h))
    vertices_bottom.append(vec(v.x, v.y, -z_h))

c_top, c_bot = vec(0,0,2), vec(0,0,-2)
gem_col = vec(0, 0.2, 0.8) # Deep Blue
core_col = vec(0, 0.8, 1)   # Bright Cyan

for i in range(len(vertices_top)):
    v1, v2 = vertices_top[i], vertices_top[(i+1)%len(vertices_top)]
    faces.append(triangle(vs=[vertex(pos=c_top, color=core_col), vertex(pos=v1, color=gem_col), vertex(pos=v2, color=gem_col)]))
    b1, b2 = vertices_bottom[i], vertices_bottom[(i+1)%len(vertices_bottom)]
    faces.append(triangle(vs=[vertex(pos=c_bot, color=vec(0,0,0.3)), vertex(pos=b2, color=gem_col), vertex(pos=b1, color=gem_col)]))

for i in range(len(vertices_top)):
    v1, v2 = vertices_top[i], vertices_top[(i+1)%len(vertices_top)]
    b1, b2 = vertices_bottom[i], vertices_bottom[(i+1)%len(vertices_bottom)]
    faces.append(triangle(vs=[vertex(pos=v1, color=gem_col), vertex(pos=v2, color=gem_col), vertex(pos=b1, color=gem_col)]))
    faces.append(triangle(vs=[vertex(pos=v2, color=gem_col), vertex(pos=b2, color=gem_col), vertex(pos=b1, color=gem_col)]))

opal = compound(faces, opacity=0.8)
# 6. DISPLAY PHYSICS DATA
print("---------- PHYSICS REPORT ----------")
print("1. TOTAL MASS: ", round(total_mass, 2), " units")
print("2. DENSITY FUNCTION: ρ(x,y,z) = 1 + 0.5x")
print("   (Mass increases as X becomes more positive)")
print("3. CENTER OF MASS (x,y,z):")
print("   [", round(Cx, 2), ",", round(Cy, 2), ",", round(Cz, 2), "]")
print("4. CALCULATION MATH: Triple Riemann Sum")
print("   Formula: R_cm = (1/M) * Σ (r * density * dV)")
print("5. VOLUME VOXELS: ", nx * ny * nz, " total cubes checked")
print("------------------------------------")
# 7. VISUAL LABELS AND MARKERS ---
com_marker = sphere(pos=com_vec, radius=0.25, color=color.cyan, emissive=True)

# This label must be written carefully to avoid indentation errors
com_label = label(pos=com_vec, 
    text='Center of Mass\n' + str(round(Cx,2)) + ', ' + str(round(Cy,2)) + ', ' + str(round(Cz,2)), 
    xoffset=40, yoffset=40, height=12, border=4, font='sans')
# 8. Animation Loop
while True:
    rate(60)
    opal.rotate(angle=0.01, axis=vec(0, 1, 0), origin=com_vec)
    
    # Keep the label tracking the COM marker
    com_label.pos = com_vec
