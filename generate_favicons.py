import os
from PIL import Image, ImageDraw


def generate_favicons() -> None:
    # Paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    web_dir = os.path.join(base_dir, 'rg_web', 'src')
    assets_dir = os.path.join(web_dir, 'assets')

    os.makedirs(assets_dir, exist_ok=True)

    ico_path = os.path.join(web_dir, 'favicon.ico')
    svg_path = os.path.join(assets_dir, 'favicon.svg')

    # 1. Generate ICO using Pillow (Camera Icon)
    size = (512, 512)

    # Create the background scene
    # 1.1 Helper: Vertical Gradient
    def create_vertical_gradient(size, start_color, end_color):
        base = Image.new('RGBA', size, start_color)
        bottom = Image.new('RGBA', size, end_color)
        mask = Image.new('L', size)
        mask_data = []
        for y in range(size[1]):
            mask_data.extend([int(255 * (y / size[1]))] * size[0])
        mask.putdata(mask_data)
        base.paste(bottom, (0, 0), mask=mask)
        return base

    # Sky Gradient: Deep Sky Blue to Lighter Blue
    sky_top = (30, 144, 255)  # Dodger Blue
    sky_bottom = (176, 224, 230)  # Powder Blue
    scene = create_vertical_gradient(size, sky_top, sky_bottom)
    scene_draw = ImageDraw.Draw(scene)

    # Draw Sun with Glow
    sun_color = (255, 223, 0)  # Golden Yellow
    sun_glow = (255, 255, 200, 100)  # Pale Yellow, Semi-transparent
    sun_x, sun_y = 380, 80
    sun_r = 50
    # Glow (simulated with larger circle, low alpha - requires separate layer)
    glow_layer = Image.new('RGBA', size, (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow_layer)
    glow_draw.ellipse([sun_x - sun_r - 20, sun_y - sun_r - 20,
                      sun_x + sun_r + 20, sun_y + sun_r + 20], fill=sun_glow)
    scene.alpha_composite(glow_layer)
    # Core Sun
    scene_draw.ellipse([sun_x - sun_r, sun_y - sun_r,
                       sun_x + sun_r, sun_y + sun_r], fill=sun_color)

    # Draw Mountains (More realistic tones)
    mt_back_left = (46, 139, 87)  # SeaGreen
    mt_back_right = (60, 179, 113)  # MediumSeaGreen
    mt_front = (34, 139, 34)  # ForestGreen
    snow_color = (255, 250, 250)  # Snow

    # Mountain 1 (Left Back)
    scene_draw.polygon([(0, 512), (150, 200), (300, 512)], fill=mt_back_left)
    scene_draw.polygon([(112, 280), (150, 200), (188, 280)], fill=snow_color)

    # Mountain 2 (Right Back)
    scene_draw.polygon(
        [(200, 512), (400, 180), (600, 512)], fill=mt_back_right)
    scene_draw.polygon([(360, 246), (400, 180), (440, 246)], fill=snow_color)

    # Mountain 3 (Center Foreground - darker for contrast)
    scene_draw.polygon([(100, 512), (256, 250), (412, 512)], fill=mt_front)

    # Create and apply rounded Mask
    mask = Image.new('L', size, 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle([(0, 0), size], radius=100, fill=255)

    final_bg = Image.new('RGBA', size, (0, 0, 0, 0))
    final_bg.paste(scene, (0, 0), mask=mask)

    # Prepare to draw camera on top
    draw = ImageDraw.Draw(final_bg)

    # --- Draw Camera Icon (Canon 5D Mark IV Style) ---
    cam_black = (20, 20, 20)      # Deep Black/Grey
    cam_grip = (10, 10, 10)       # Darker textured grip
    cam_shadow = (0, 0, 0, 140)   # Drop shadow

    cx, cy = 256, 260

    # Body Dimensions
    w_body, h_body = 360, 240
    # MOVED DOWN: cy = 280
    cx, cy = 256, 280

    x1, y1 = cx - w_body//2, cy - h_body//2
    x2, y2 = cx + w_body//2, cy + h_body//2

    # 1. Shadows (Simplified shape for robustness)
    draw.rounded_rectangle([x1+10, y1+10, x2+10, y2+10],
                           radius=20, fill=cam_shadow)

    # 2. Main Body Block (Bottom)
    draw.rounded_rectangle([x1, y1 + 40, x2, y2],
                           radius=15, fill=cam_black)  # Lower chassis

    # 3. Grip (Viewer's Left side / Camera's Right)
    # The 5D grip is prominent.
    grip_w = 90
    draw.rounded_rectangle(
        [x1, y1 + 10, x1 + grip_w, y2], radius=15, fill=cam_grip)

    # Finger indent on Grip
    draw.chord([x1 + 65, y1 + 60, x1 + 115, y1 + 200],
               110, 250, fill=cam_black)

    # 4. Top Plates (Shoulders)
    # Left Shoulder (Grip side, tall with shutter) - Lowered significantly - BARELY VISIBLE
    draw.polygon([(x1, y1+40), (x1+20, y1 + 35), (x1+grip_w,
                 y1 + 32), (x1+grip_w, y1+40)], fill=cam_black)

    # Right Shoulder (Mode dial side - Viewer Right)
    draw.polygon([(x2-100, y1+40), (x2-90, y1+15),
                 (x2, y1+15), (x2, y1+40)], fill=cam_black)

    # 5. Pentaprism Hump (Curved "Canon" style)
    hm_w = 140
    # Reduced height: was y1 - 45 for ref, chord top -80
    # New: Flatten the curve a bit

    # Draw base of hump
    draw.rectangle([cx - hm_w//2 + 10, y1, cx + hm_w //
                   2 - 10, y1 + 40], fill=cam_black)
    # Draw curved top (Barely visible: y1-12)
    draw.chord([cx - hm_w//2, y1 - 12, cx + hm_w//2,
               y1 + 30], 190, 350, fill=cam_black)

    # Hot Shoe (Lowered to match)
    shoe_top = y1 - 8
    draw.rectangle([cx - 20, shoe_top, cx + 20,
                   shoe_top + 5], fill=(50, 50, 50))

    # 6. Controls
    # Shutter Button (Angled on grip, flatted/barely visible)
    draw.ellipse([x1 + 30, y1 + 8, x1 + 60, y1 + 15], fill=(40, 40, 40))

    # Mode Dial (Right Shoulder - Barely visible)
    draw.rectangle([x2 - 50, y1 + 35, x2 - 10, y1 + 37], fill=(30, 30, 30))

    # Self-timer light/LED (MOVED TO RIGHT, Round & 3D)
    led_x = x2 - 45
    led_y = y1 + 70
    led_r = 8
    # Dark bevel/ring
    draw.ellipse([led_x - led_r - 2, led_y - led_r - 2, led_x +
                 led_r + 2, led_y + led_r + 2], fill=(10, 0, 0))
    # Main Glassy Red
    draw.ellipse([led_x - led_r, led_y - led_r, led_x +
                 led_r, led_y + led_r], fill=(180, 0, 0))
    # Highlight
    draw.ellipse([led_x - 3, led_y - 5, led_x + 2, led_y],
                 fill=(255, 200, 200, 230))

    # Markings
    # "5D" Placeholder (White text area)
    draw.rectangle([x2 - 50, y2 - 40, x2 - 20, y2 - 25],
                   fill=(180, 180, 180))  # Silver badge

    # 7. Lens System (EF Mount style)
    # Silver Mount Ring
    draw.ellipse([cx - 110, cy - 110, cx + 110, cy + 110],
                 fill=(180, 180, 180))

    # Black inner barrel
    draw.ellipse([cx - 105, cy - 105, cx + 105, cy + 105], fill=(10, 10, 10))

    # Red Ring (L-Series)
    draw.ellipse([cx - 100, cy - 100, cx + 100, cy + 100],
                 outline=(200, 0, 0), width=4)

    # Inner glass frame
    draw.ellipse([cx - 90, cy - 90, cx + 90, cy + 90], fill=(20, 20, 30))

    # Glass (Big front element)
    draw.ellipse([cx - 80, cy - 80, cx + 80, cy + 80], fill=(5, 5, 20))

    # Reflections (Green/Magenta coating)
    draw.ellipse([cx + 20, cy - 50, cx + 60, cy - 20], fill=(0, 255, 100, 40))
    draw.ellipse([cx - 50, cy + 30, cx - 30, cy + 50], fill=(255, 0, 255, 40))
    draw.ellipse([cx + 30, cy - 40, cx + 40, cy - 30],
                 fill=(255, 255, 255, 180))

    # Save as ICO (containing multiple sizes)
    final_bg.save(ico_path, format='ICO', sizes=[
                  (256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
    print(f"Generated ICO at: {ico_path}")

    # 2. Generate SVG
    # Updated text for SVG to include drop shadows and layers

    svg_content = """<svg width="512" height="512" viewBox="0 0 512 512" fill="none" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <clipPath id="round-corner">
            <rect width="512" height="512" rx="100" />
        </clipPath>
        
        <!-- Filters -->
        <filter id="dropshadow" height="130%">
            <feGaussianBlur in="SourceAlpha" stdDeviation="3"/>
            <feOffset dx="4" dy="4" result="offsetblur"/>
            <feComponentTransfer>
                <feFuncA type="linear" slope="0.5"/>
            </feComponentTransfer>
            <feMerge> 
                <feMergeNode in="offsetblur"/>
                <feMergeNode in="SourceGraphic"/> 
            </feMerge>
        </filter>
        
        <!-- Gradients -->
        <linearGradient id="skyGrad" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" style="stop-color:#1E90FF;stop-opacity:1" /> <!-- DodgerBlue -->
            <stop offset="100%" style="stop-color:#B0E0E6;stop-opacity:1" /> <!-- PowderBlue -->
        </linearGradient>
        
        <radialGradient id="sunGrad" cx="50%" cy="50%" r="50%" fx="50%" fy="50%">
            <stop offset="0%" style="stop-color:#FFFACD;stop-opacity:1" /> <!-- LemonChiffon -->
            <stop offset="100%" style="stop-color:#FFD700;stop-opacity:1" /> <!-- Gold -->
        </radialGradient>
        
        <linearGradient id="mtLeftGrad" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" style="stop-color:#2E8B57;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#3CB371;stop-opacity:1" />
        </linearGradient>
        
        <linearGradient id="mtRightGrad" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" style="stop-color:#3CB371;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#2E8B57;stop-opacity:1" />
        </linearGradient>

        <linearGradient id="lensGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:#666;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#333;stop-opacity:1" />
        </linearGradient>
    </defs>
    
    <!-- Background Group with Clip Path -->
    <g clip-path="url(#round-corner)">
        <!-- Gradient Sky -->
        <rect width="512" height="512" fill="url(#skyGrad)"/>
        
        <!-- Sun with Gradient -->
        <circle cx="380" cy="80" r="50" fill="url(#sunGrad)"/>
        
        <!-- Mountains (Green with Gradient) -->
        <polygon points="0,512 150,200 300,512" fill="url(#mtLeftGrad)"/>
        <polygon points="112,280 150,200 188,280" fill="#F0F8FF"/> <!-- Snowcap -->
        
        <polygon points="200,512 400,180 600,512" fill="url(#mtRightGrad)"/>
        <polygon points="360,246 400,180 440,246" fill="#F0F8FF"/> <!-- Snowcap -->
        
        <polygon points="100,512 256,250 412,512" fill="#228B22"/> <!-- ForestGreen (Foreground) -->
    </g>
    
    <!-- Camera Group with Filter -->
    <!-- CENTERED HORIZONTALLY: transform="translate(0, 40)" -->
    <g filter="url(#dropshadow)" transform="translate(0, 40)">
        
        <!-- Hump Base (Lowered start from 80 to 95) -->
        <rect x="180" y="95" width="152" height="31" fill="#141414"/>
        <!-- Pentaprism Curve (Flatted) -->
        <path d="M180 95 C180 90 210 88 256 88 C302 88 332 90 332 95" fill="#141414"/>
        <!-- Hot Shoe -->
        <rect x="236" y="85" width="40" height="6" fill="#323232"/>
        
        <!-- Main Body Chassis -->
        <rect x="66" y="126" width="380" height="260" rx="20" fill="#191919"/>
        
        <!-- Shutter/Grip Side (Left of viewer) - Lowered -->
        <rect x="76" y="120" width="90" height="10" rx="2" fill="#141414"/>
        <path d="M76 130 H166 V370 C166 380 156 386 146 386 H96 C86 386 76 380 76 370 V130 Z" fill="#0A0A0A"/>
        <!-- Finger Grove -->
        <path d="M130 180 Q 90 280 130 350" stroke="#121212" stroke-width="4" fill="none"/>
        
        <!-- Mode Dial Side (Right of viewer) - Lowered -->
        <rect x="366" y="120" width="60" height="10" rx="2" fill="#141414"/>
        <rect x="380" y="118" width="30" height="2" fill="#282828"/> <!-- Dial itself (Barely visible) -->
        
        <!-- Shutter Button Area - Lowered -->
        <path d="M96 122 L146 121 L146 130 L96 130 Z" fill="#1E1E1E"/>
        <ellipse cx="121" cy="122" rx="15" ry="2" fill="#282828"/> <!-- Button Base (Flat) -->
        <ellipse cx="121" cy="122" rx="12" ry="1" fill="#111"/> <!-- Button Top (Barely visible) -->
        
        <!-- Red Self Timer Light (Round & 3D, Right Side) -->
        <g transform="translate(410, 160)">
             <!-- Bezel/Socket -->
            <circle cx="0" cy="0" r="10" fill="#1A0505"/>
            <!-- Glassy Red LED -->
            <circle cx="0" cy="0" r="8" fill="#D00000"/>
            <!-- Inner Depth Gradient simulation -->
            <radialGradient id="ledGlow">
                <stop offset="0%" stop-color="#FF3333"/>
                <stop offset="100%" stop-color="#990000"/>
            </radialGradient>
            <circle cx="0" cy="0" r="8" fill="url(#ledGlow)"/>
            <!-- Specular Highlight -->
            <ellipse cx="-3" cy="-3" rx="3" ry="2" transform="rotate(-45)" fill="#FFF" fill-opacity="0.8"/>
        </g>
        
        <!-- RG Badge Area -->
        <rect x="390" y="340" width="40" height="20" fill="#333"/>
        <text x="395" y="355" font-family="Arial" font-size="14" fill="#DDD" font-weight="bold">RG</text>

        <!-- Lens Mount -->
        <circle cx="256" cy="256" r="115" fill="#C0C0C0"/>
        
        <!-- Lens Barrel -->
        <circle cx="256" cy="256" r="110" fill="#0A0A0A"/>
        
        <!-- Red Ring (L-Series) -->
        <circle cx="256" cy="256" r="105" stroke="#C81414" stroke-width="5" fill="none"/>
        
        <!-- Inner Frame -->
        <circle cx="256" cy="256" r="95" fill="#1E1E1E"/>
        
        <!-- Glass -->
        <circle cx="256" cy="256" r="85" fill="#050510"/>
        
        <!-- Reflections -->
        <ellipse cx="286" cy="226" rx="25" ry="15" transform="rotate(-45 286 226)" fill="#00FF66" fill-opacity="0.2"/>
        <ellipse cx="226" cy="286" rx="20" ry="10" transform="rotate(-45 226 286)" fill="#FF00FF" fill-opacity="0.2"/>
        <circle cx="290" cy="220" r="8" fill="#FFF" fill-opacity="0.7"/>

    </g>
</svg>"""

    with open(svg_path, 'w', encoding='utf-8') as f:
        f.write(svg_content)
    print(f"Generated SVG at: {svg_path}")


if __name__ == "__main__":
    generate_favicons()
