"""
Generates an ultra-luxurious iridescent molten metallic fluid artwork
matching the exact colors and organic ribbon flows from the user's reference.
"""

import os
import math
import numpy as np
from PIL import Image, ImageFilter

os.makedirs("frontend/assets", exist_ok=True)

width, height = 1920, 1080

# Coordinate grid
x = np.linspace(-2.2, 2.2, width)
y = np.linspace(-1.3, 1.3, height)
X, Y = np.meshgrid(x, y)

# Construct undulating 3D fluid ribbon heightfields
# Multiple wave harmonics to create twisted molten metallic chrome ribbons
Z1 = np.sin(1.8 * X + 1.2 * Y) * np.cos(1.4 * X - 1.1 * Y)
Z2 = np.sin(2.4 * np.sqrt(X**2 + Y**2 + 0.2) - 0.9 * X + 1.3 * Y)
Z3 = np.cos(0.8 * X**2 - 1.2 * Y**2 + 0.5 * X * Y)

# Combined fluid manifold
Z = 0.55 * Z1 + 0.35 * Z2 + 0.25 * Z3

# Compute surface normal approximations for specular chrome lighting
dZ_dx, dZ_dy = np.gradient(Z, 4.4 / width, 2.6 / height)
norm = np.sqrt(dZ_dx**2 + dZ_dy**2 + 1.0)
Nx = -dZ_dx / norm
Ny = -dZ_dy / norm
Nz = 1.0 / norm

# Primary light source (top-right warm golden/cyan)
Lx, Ly, Lz = 0.6, -0.7, 0.9
L_len = math.sqrt(Lx**2 + Ly**2 + Lz**2)
Lx, Ly, Lz = Lx / L_len, Ly / L_len, Lz / L_len

# Secondary ambient light (top-left cool turquoise)
L2x, L2y, L2z = -0.7, -0.5, 0.8
L2_len = math.sqrt(L2x**2 + L2y**2 + L2z**2)
L2x, L2y, L2z = L2x / L2_len, L2y / L2_len, L2z / L2_len

diff1 = np.clip(Nx * Lx + Ny * Ly + Nz * Lz, 0, 1)
diff2 = np.clip(Nx * L2x + Ny * L2y + Nz * L2z, 0, 1)

# Specular reflections (Blinn-Phong)
Vx, Vy, Vz = 0.0, 0.0, 1.0
Hx, Hy, Hz = Lx + Vx, Ly + Vy, Lz + Vz
H_len = np.sqrt(Hx**2 + Hy**2 + Hz**2)
spec1 = np.clip((Nx * Hx + Ny * Hy + Nz * Hz) / H_len, 0, 1) ** 28

H2x, H2y, H2z = L2x + Vx, L2y + Vy, L2z + Vz
H2_len = np.sqrt(H2x**2 + H2y**2 + H2z**2)
spec2 = np.clip((Nx * H2x + Ny * H2y + Nz * H2z) / H2_len, 0, 1) ** 32

# Iridescent color mapping based on ribbon depth, angle, and curvature
angle = np.arctan2(Ny, Nx) + Z * 1.5
curvature = np.abs(dZ_dx) + np.abs(dZ_dy)

# Base iridescent metallic color palettes
# Cyan/Teal (cool highlights)
r_teal = 15.0 / 255.0
g_teal = 180.0 / 255.0
b_teal = 175.0 / 255.0

# Liquid Gold / Champagne Bronze (warm reflections)
r_gold = 225.0 / 255.0
g_gold = 175.0 / 255.0
b_gold = 110.0 / 255.0

# Deep Lilac / Purple (shadow reflections)
r_purple = 110.0 / 255.0
g_purple = 75.0 / 255.0
b_purple = 135.0 / 255.0

# Deep obsidian base
r_dark = 8.0 / 255.0
g_dark = 10.0 / 255.0
b_dark = 16.0 / 255.0

# Interpolation weights across the fluid
t_gold = np.clip(np.sin(angle * 1.2 + 0.8) * 0.5 + 0.5, 0, 1) ** 1.8
t_teal = np.clip(np.cos(angle * 1.4 - 0.4) * 0.5 + 0.5, 0, 1) ** 1.5
t_purple = np.clip(np.sin(Z * 3.0 + 1.2) * 0.5 + 0.5, 0, 1)

# Organic fluid mask: focus richness across center and right, deep dark on left/borders
radial_vignette = np.clip(1.35 - 0.55 * (X**2 + 0.8 * Y**2), 0.15, 1.0)
flow_intensity = np.clip(0.4 + 0.6 * diff1 + 0.4 * diff2 + 0.3 * curvature, 0, 1.2)

# Compose final RGB channels
R = (r_dark * (1 - t_gold) + r_gold * t_gold * 1.2 + r_purple * t_purple * 0.4) * flow_intensity + spec1 * 0.95 + spec2 * 0.4
G = (g_dark * (1 - t_teal) + g_teal * t_teal * 1.1 + g_gold * t_gold * 0.65) * flow_intensity + spec1 * 0.85 + spec2 * 0.7
B = (b_dark * (1 - t_purple) + b_teal * t_teal * 0.85 + b_purple * t_purple * 1.1) * flow_intensity + spec1 * 0.75 + spec2 * 0.9

# Apply vignette
R = np.clip(R * radial_vignette * 255.0, 0, 255).astype(np.uint8)
G = np.clip(G * radial_vignette * 255.0, 0, 255).astype(np.uint8)
B = np.clip(B * radial_vignette * 255.0, 0, 255).astype(np.uint8)

# Stack to image
rgb = np.stack([R, G, B], axis=-1)
img = Image.fromarray(rgb, "RGB")

# Apply subtle smooth photographic softening to achieve silky molten glass look
img = img.filter(ImageFilter.GaussianBlur(radius=1.2))

img.save("frontend/assets/liquid_metallic_hero.jpg", quality=95)
print("Generated frontend/assets/liquid_metallic_hero.jpg successfully!")
