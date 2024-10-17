# -*- coding: utf-8 -*-
"""
Parallelized pattern generation script
Created on Tue Feb 13 11:59:14 2024
@author: sib16nk
"""

from generate_pattern import Pattern, circle
from math import pi, ceil
import numpy as np
import time
from concurrent.futures import ProcessPoolExecutor
import gc  # Importiere Garbage Collector

diameter_list = [1.7, 2.0, 2.5] #list of diameters
overlap_list = [0.7, 0.75, 0.80, 0.85, 0.90, 0.95, 1.00, 1.05, 1.10, 1.15, 1.20, 1.25, 1.3] #list of overlaps
resolution = [25,1] #resolution in nm
start_x = 115000 #initial offset in x-direction
start_y = 2500 #initial offset in y-direction
x_abstand = 20000

# function to calculate the positions in the hexagon
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

# Funktion zur Generierung und Speicherung eines Musters
def create_pattern_in_memory(index, overlap, flat_top, x_offset, y_offset, start_x, start_y, diameter, resolution):
    result = []
    start_time = time.time()
    
    # print(f"Generating pattern {pattern_name} with overlap {overlapp}")

    if flat_top:
        width = 2 * diameter * overlap + diameter
        height = np.sqrt(3) * diameter * overlap + diameter
    else:
        height = 2 * diameter * overlap + diameter
        width = np.sqrt(3) * diameter * overlap + diameter

    center = [width / 2, height / 2]
    cc_dist = diameter * overlap
    off = resolution[0] / 2
    
    if flat_top:
        pattern_name = f"hexf_d{diameter}_{overlap}".replace(".", "p")
    else:
        pattern_name = f"hexp_d{diameter}_{overlap}".replace(".", "p")

    if overlap >= 1:
        # Füge Kreise direkt als String hinzu
        pattern_string = ""
        for i in range(6):
            # Berechne die Ecken
            corners = hex_corners(center, cc_dist, i, flat_top=flat_top)
            
            # Extrahiere x- und y-Position
            x_pos = round(corners[0] * 1e3 + start_x - (1000 * width / 2) + x_offset)
            y_pos = round(corners[1] * 1e3 + start_y + y_offset)
            
            # Berechne den Durchmesser
            radius = round(diameter / 2 * 1e3)
            
            # Füge die Kreise im String-Format hinzu: "CIRCLE x-pos y-pos radius"
            pattern_string += f"CIRCLE {x_pos}, {y_pos}, {radius}\n"
    else:
        # Initialisiere Pattern-Objekt
        pattern = Pattern(width * 1e3 + off, height * 1e3 + off, resolution, pattern_name)
    
        # Füge die Kreise hinzu
        for i in range(6):
            corners = hex_corners(center, cc_dist, i, flat_top=flat_top)
            pattern.add_parametrized_shape(circle, corners[0] * 1e3, corners[1] * 1e3, diameter / 2 * 1e3)
        pattern_string = pattern.export_pattern(complete=False, export=False,
                                                offsetx=start_x - (1000 * width / 2) + x_offset,
                                                offsety=start_y + y_offset)
    result.append(pattern_string)
        
    # Lösche das Pattern-Objekt, um Speicher freizugeben
    if overlap < 1:
        del pattern

    # Speicher freigeben
    gc.collect()
    end_time = time.time()
    duration = end_time - start_time
    return "\n\n".join(result), duration, index  # return of result, duration and index

#     print(f"All patterns generated in {run_end - run_start:.2f} seconds")

# Hauptfunktion
if __name__ == "__main__":
    # Zu Beginn des Skripts die Datei überschreiben (oder eine neue Datei anlegen)
    for x in range(2):
        flat_top = (x == 0)
        if flat_top:
            file_name = f"hexagons_res{resolution[0]}_flat.pat"
        else:
            file_name = f"hexagons_res{resolution[0]}_peak.pat"
        
        # Datei einmalig neu erstellen oder alte Datei überschreiben
        with open(file_name, "w") as file:
            pass  # Leere Datei erstellen oder bestehende Datei überschreiben

        # Iteration über die verschiedenen Durchmesser
        for diameter in diameter_list:
            results = []
            # Anpassung der Start-Y-Koordinate basierend auf dem Durchmesser
            if diameter == 1.7:
                y_offset = 0
            elif diameter == 2.0:
                y_offset = 20000
            elif diameter == 2.5:
                y_offset = 40000
            else:
                y_offset = 0

            # Threads erzeugen die Muster in den Speicher
            with ProcessPoolExecutor(max_workers=13) as executor:
                run_start = time.time()
                futures = []
                for index, overlap in enumerate(overlap_list):
                    x_offset = start_x + x_abstand * index

                    futures.append(
                        executor.submit(
                            create_pattern_in_memory,
                            index,
                            overlap,
                            flat_top,
                            x_offset,
                            y_offset,
                            start_x,
                            start_y,
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

            # Anhängen an die Datei nach Abschluss aller Threads
            with open(file_name, "a") as file:  # "a" -> "append"
                form_diameter = str(diameter).replace(".", "p")
                if flat_top:
                    file.write(f"D hexagon_flat_{form_diameter}" + '\n' + "I 1" + '\n' + "C 100" + '\n')
                else:
                    file.write(f"D hexagon_peak_{form_diameter}" + '\n' + "I 1" + '\n' + "C 100" + '\n')
                file.write("\n\n".join(results))
                file.write("END" + '\n')


        