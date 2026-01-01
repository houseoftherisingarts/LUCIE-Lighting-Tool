import ezdxf
import csv
import math
import sys
import os

# ==========================================
# CONFIGURATION
# ==========================================
# The script will look for this file name to measure!
INPUT_CAD_FILE = "my_plan.dxf" 

# Defaults (If we can't read the file)
CEILING_HEIGHT = 10.0   
TARGET_FC = 50          
LUMENS_PER_FIXTURE = 4200 
FIXTURE_LABEL = "TypeA" 

def get_dxf_dimensions(filename):
    """
    Opens a real DXF file and measures its bounding box.
    Returns: width (X), length (Y)
    """
    if not os.path.exists(filename):
        print(f"[ERROR] Could not find file: {filename}")
        print("Make sure the .dxf file is on your Desktop!")
        sys.exit()

    try:
        doc = ezdxf.readfile(filename)
        msp = doc.modelspace()
        
        # This function automatically finds the 'box' around all lines
        # Note: This assumes the drawing is clean (no junk lines miles away)
        extent = msp.get_extents() 
        
        # Calculate size
        width = extent.max.x - extent.min.x
        length = extent.max.y - extent.min.y
        
        print(f"[READING] Found Drawing Extents:")
        print(f"   Min Point: {extent.min}")
        print(f"   Max Point: {extent.max}")
        
        return width, length, extent.min.x, extent.min.y
        
    except Exception as e:
        print(f"[ERROR] Failed to read DXF: {e}")
        sys.exit()

def generate_agi_files():
    print(f"--- STARTING AI INTERN ---")
    
    # 1. MEASURE THE INPUT PLAN
    # -------------------------
    print(f"Reading file: {INPUT_CAD_FILE}...")
    real_width, real_length, start_x, start_y = get_dxf_dimensions(INPUT_CAD_FILE)
    
    print(f"[ANALYSIS] Room Detected: {real_width:.2f} ft x {real_length:.2f} ft")
    
    # 2. CREATE LIGHTING GRID
    # -----------------------
    # Logic: Area * TargetFC / (Lumens * CU * LLF)
    area = real_width * real_length
    needed_lumens = (TARGET_FC * area) / (0.8 * 0.9)
    total_lights = math.ceil(needed_lumens / LUMENS_PER_FIXTURE)
    
    # Calculate Rows/Cols based on shape
    aspect_ratio = real_width / real_length
    rows = math.sqrt(total_lights / aspect_ratio)
    cols = total_lights / rows
    rows, cols = max(1, round(rows)), max(1, round(cols))
    
    print(f"[DECISION] Placing {int(rows*cols)} lights ({int(cols)}x{int(rows)} grid).")

    # 3. EXPORT LOCATIONS (TXT)
    # -------------------------
    spacing_x = real_width / cols
    spacing_y = real_length / rows
    
    txt_name = "Project_Lights_Auto.txt"
    with open(txt_name, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Label", "X", "Y", "Z", "Orient", "Tilt"])
        
        for r in range(int(rows)):
            for c in range(int(cols)):
                # We add 'start_x' and 'start_y' to match the original CAD coordinates!
                x = start_x + (c * spacing_x) + (spacing_x / 2)
                y = start_y + (r * spacing_y) + (spacing_y / 2)
                z = CEILING_HEIGHT - 0.5 
                
                writer.writerow([FIXTURE_LABEL, f"{x:.2f}", f"{y:.2f}", f"{z:.2f}", 0, 0])
                
    print(f"[SUCCESS] Created: {txt_name}")
    print("--- DONE ---")

if __name__ == "__main__":
    generate_agi_files()
