# -*- coding: utf-8 -*-
"""
Created on Tue Feb 13 11:59:14 2024

@author: sib16nk
"""

from generate_pattern import Pattern, circle
from math import pi, ceil
import numpy as np
import time
from concurrent.futures import ProcessPoolExecutor
import gc  # Importiere Garbage Collector

diameters = [1.7, 2.0]  # Liste der verschiedenen Durchmesser
overlap1_list = [1.20, 1.00, 0.90, 0.80, 1.20, 1.10, 1.00, 0.90, 1.20, 1.10, 1.00, 0.90, 1.20, 1.10, 1.00, 0.90]
overlap2_list = [1.20, 1.00, 0.90, 0.80, 1.00, 0.95, 0.90, 0.85, 0.95, 0.90, 0.85, 0.80, 0.90, 0.85, 0.80, 0.75]
resolution = [25,1]
sizexum = 115  # aimed lattice size in um
sizeyum = 90

x_abstand = 125000  # Abstand zwischen den Spalten
y_abstand = 110000  # Abstand zwischen den Zeilen
spalten = 4
flat_top = False
zeilen = ceil(len(overlap1_list) / spalten)

def hex_corners(center, distance, i, offsetx=0, offsety=0, flat_top=False):
    if flat_top:
        angle_deg = 60 * i
    else:
        angle_deg = 60 * i - 30
    angle_rad = pi / 180 * angle_deg
    return [center[0] + distance * np.cos(angle_rad) - offsetx, center[1] + distance * np.sin(angle_rad) - offsety]

def round_up_even(number):
    # Runden Sie die Zahl zur nächsten ganzen Zahl auf
    round_up = ceil(number)
    if round_up % 2 != 0:
        round_up -= 1
    return round_up

def create_pattern_in_memory(index, overlap1, overlap2, flat_top, x_offset, y_offset, start_x, start_y, spalten, diameter, resolution):
    result = []
    start_time = time.time()

    width = np.sqrt(3) * diameter * overlap1 + diameter
    height = 2 * diameter * overlap1 + diameter
    
    if flat_top:
        width = 2 * diameter * overlap1 + diameter
        height = np.sqrt(3) * diameter * overlap1 + diameter
    else:
        height = 2 * diameter * overlap1 + diameter
        width = np.sqrt(3) * diameter * overlap1 + diameter

    center = [width / 2, height / 2]
    cc_dist1 = diameter * overlap1
    cc_dist2 = diameter * (overlap1 + overlap2)

    off = resolution[0] / 2

    shiftx = round(2 * (np.sqrt(3) * diameter * overlap1 + np.sqrt(3) / 2 * diameter * overlap2) * 1000)
    shifty = round((2 * diameter * overlap1 + diameter * overlap2) * 1000)

    nx = round_up_even(sizexum // width)  # Calculation for nx
    ny = round_up_even(sizeyum // height)  # Calculation for ny
    repx = int(nx // 2)  # Calculation for repx

    # Definiere die Pattern-Namen mit shiftx, shifty, repx und ny
    pn1 = f"VA{overlap1}_VB{overlap2}_1,{shiftx},{shifty},{repx},{ny}"
    pattern_name1 = pn1.replace(".", "p")

    pn2 = f"VA{overlap1}_VB{overlap2}_2,{shiftx},{shifty},{repx},{ny}"
    pattern_name2 = pn2.replace(".", "p")

    pn3 = f"VA{overlap1}_VB{overlap2}_3,{shiftx},{shifty},{repx},1"
    pattern_name3 = pn3.replace(".", "p")

    pn4 = f"VA{overlap1}_VB{overlap2}_4,{shiftx},{shifty},{repx},1"
    pattern_name4 = pn4.replace(".", "p")

    pn5 = f"VA{overlap1}_VB{overlap2}_5,{shiftx},{shifty},1,{ny}"
    pattern_name5 = pn5.replace(".", "p")

    # Alle Muster erstellen (pattern_name1 bis pattern_name5)
    for pattern_name, n_circles, n_subtract_circles, add_offset, subtract_offset, offsetx, offsety, corn_offsety in [
        (pattern_name1, 6, 3, 0, 0, 0, 0, 0),
        (pattern_name2, 6, 3, 0, 0, shiftx / 2, round(diameter * (overlap1 + 0.5 * overlap2) * 1000), 0),
        (pattern_name3, 3, 2, 1, 1, shiftx / 2, 0, diameter * overlap1 + diameter * overlap2 / 2),
        (pattern_name4, 3, 1, 4, 0, 0, ny * shifty, 0),
        (pattern_name5, 6, 1, 0, 2, repx * shiftx, 0, 0),
    ]:
        if overlap1 >= 1 and overlap2 >= 1:
            # Füge Kreise direkt als String hinzu
            pattern_string = "D " + pattern_name + '\n' + "I 1" + '\n' + "C 100" + '\n'
            for i in range(n_circles):
                corners = hex_corners(center, cc_dist1, i + add_offset, offsety=corn_offsety)
                
                # Extrahiere x- und y-Position
                x_pos = round(corners[0] * 1e3 + x_offset + offsetx)
                y_pos = round(corners[1] * 1e3 + y_offset + offsety)
                
                # Berechne den Durchmesser
                radius = round(diameter / 2 * 1e3)
                
                # Füge die Kreise im String-Format hinzu: "CIRCLE x-pos y-pos radius"
                pattern_string += f"CIRCLE {x_pos}, {y_pos}, {radius}\n"
            pattern_string += "END" + '\n'
        else:
            pattern = Pattern(width * 1e3 + off, height * 1e3 + off, resolution, pattern_name)
            # Add circles using cc_dist1 with offset for starting index
            for i in range(n_circles):
                corners = hex_corners(center, cc_dist1, i + add_offset, offsety=corn_offsety)
                pattern.add_parametrized_shape(circle, corners[0] * 1e3, corners[1] * 1e3, diameter / 2 * 1e3)
    
            # Subtract circles using cc_dist2 with offset for starting index
            for i in range(n_subtract_circles):
                corners = hex_corners(center, cc_dist2, i + subtract_offset, offsety=corn_offsety)
                pattern.add_parametrized_shape(circle, corners[0] * 1e3, corners[1] * 1e3, diameter / 2 * 1e3, boolean_operation="subtract")
    
            pattern_string = pattern.export_pattern(complete=True, export=False, offsetx=x_offset + offsetx, offsety=y_offset + offsety)
        result.append(pattern_string)
        
        # Lösche das Pattern, um den Speicher freizugeben
        if overlap1 < 1 or overlap2 < 1:
            del pattern

        # Aufforderung zur Speicherbereinigung
        gc.collect()

    end_time = time.time()
    duration = end_time - start_time
    return "\n\n".join(result), duration, index  # Rückgabe des Ergebnisses und der Dauer

if __name__ == "__main__":

    # Iteration über die verschiedenen Durchmesser
    for diameter in diameters:
        results = []
        
        start_x = 0

        # Anpassung der Start-Y-Koordinate basierend auf dem Durchmesser
        if diameter == 2.0:
            start_y = 75000  # 300000
        elif diameter == 1.7:
            start_y = 75000
        else:
            start_y = 0

        file_name = f"HC_TOPO_EnO_d{diameter}_res_{resolution[0]}_{spalten}x{zeilen}_SB.pat"

        # Threads erzeugen die Muster in den Speicher
        with ProcessPoolExecutor(max_workers=16) as executor:
            run_start = time.time()
            futures = []
            for index, (overlap1, overlap2) in enumerate(zip(overlap1_list, overlap2_list)):
                x_offset = start_x + x_abstand * (index % spalten)
                y_offset = start_y + y_abstand * (index // spalten)

                futures.append(
                    executor.submit(
                        create_pattern_in_memory,
                        index,
                        overlap1,
                        overlap2,
                        flat_top,
                        x_offset,
                        y_offset,
                        start_x,
                        start_y,
                        spalten,
                        diameter,
                        resolution,
                    )
                )

            # Sammeln aller Resultate
            for future in futures:
                pattern_result, pattern_duration, pattern_index = future.result()  # Aufteilen in Resultat und Dauer
                results.append(pattern_result)
                print(f"Pattern {pattern_index} took {pattern_duration:.2f} seconds")  # Ausgabe der Zeit für jedes Pattern
                
            run_end = time.time()
            print(f"All patterns with diameter {diameter} generated in {run_end - run_start:.2f} seconds")

        # Schreiben in die Datei nach Abschluss aller Threads
        with open(file_name, "w") as file:
            file.write("\n\n".join(results))