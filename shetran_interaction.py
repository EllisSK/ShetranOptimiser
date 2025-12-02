import subprocess
import csv
import json

import xml.etree.ElementTree as ET

from pathlib import Path

def run_shetran(exe_path: Path, rundata_path: Path):
    """
    Executes a SHETRAN simulation.
    
    :param exe_path: Full path to Shetran exe file location.
    :type exe_path: Path
    :param rundata_path: Full path to rundata file location.
    :type rundata_path: Path
    """
    
    if not exe_path.exists():
        print(f"Error: Executable not found at {exe_path}")
        return
    if not rundata_path.exists():
        print(f"Error: Rundata file not found at {rundata_path}")
        return

    working_dir = rundata_path.parent
    
    command = [str(exe_path), '-f', str(rundata_path)]
    
    print(f"Starting SHETRAN run for: {rundata_path.name}...")

    try:
        result = subprocess.run(
            command,
            cwd=working_dir,
            capture_output=False,
            text=True
        )

        if not result.returncode == 0:
            print(f"Simulation failed with error:\n {result.stderr}")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def run_preprocessor(prep_exe_path: Path, xml_file_path: Path):
    """
    Executes the SHETRAN Pre-processor.
    
    :param prep_exe_path: Full path to pre-processor exe file location.
    :type prep_exe_path: Path
    :param xml_file_path: Full path to XML file location.
    :type xml_file_path: Path
    """
    
    if not prep_exe_path.exists():
        print(f"Error: Pre-processor executable not found at {prep_exe_path}")
        return
    if not xml_file_path.exists():
        print(f"Error: Input file not found at {xml_file_path}")
        return

    working_dir = xml_file_path.parent
    
    command = [str(prep_exe_path), str(xml_file_path)]
    
    print(f"Starting Pre-processor run for: {xml_file_path.name}...")
    print(f"Working Directory: {working_dir}")

    try:
        result = subprocess.run(
            command,
            cwd=working_dir,
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print("Pre-processing completed successfully.")
        else:
            print(f"Pre-processing failed with error: {result.stderr}")

    except Exception as e:
        print(f"An unexpected error occurred: {e}") 

def load_shetran_params(json_filepath: Path) -> dict:
    """
    Load a configuration json file of parameters and their bounds.
    
    :param json_filepath: Full file path to config json.
    :type json_filepaths: Path
    """
    with open(json_filepath, 'r') as f:
        data = json.load(f)

    return data

def read_xml_file(xml_file_path: Path) -> dict:
    """
    Read an XML file that is an input to the Shetran pre-processor.
    
    :param xml_file_path: Full path to XML file location.
    :type xml_file_path: Path
    """
    veg_detail_start_idx = 12
    soil_prop_start_idx = 22

    xml_dict = {
        "VegetationDetails" : [],
        "SoilProperties" : []
    }

    with open(xml_file_path, "r", encoding="utf-8") as file:
        xml_list = [line.strip() for line in file]

    for line in range(veg_detail_start_idx, veg_detail_start_idx+7):
        content = xml_list[line][18:-19]
        content = content.split(",")
        
        p = {}
        p["Descriptors"] = {
            "Veg Type #" : int(content[0]),
            "Vegetation Type" : content[1]
        }
        p["Parameters"] = {
            "Canopy storage capacity (mm)" : float(content[2]),
            "Leaf area index" : float(content[3]),
            "Maximum rooting depth(m)" : float(content[4]),
            "AE/PE at field capacity" : float(content[5]),
            "Strickler overland flow coefficient" : float(content[6])
        }
        xml_dict["VegetationDetails"].append(p)

    for line in range(soil_prop_start_idx, soil_prop_start_idx+7):
        content = xml_list[line][14:-15]
        content = content.split(",")
        
        p = {}
        p["Descriptors"] = {
            "Soil Number" : int(content[0]),
            "Soil Type" : content[1]
        }
        p["Parameters"] = {
            "Saturated Water Content" : float(content[2]),
            "Residual Water Content" : float(content[3]),
            "Saturated Conductivity (m/day)" : float(content[4]),
            "vanGenuchten- alpha (cm-1)" : float(content[5]),
            "vanGenuchten-n" : float(content[6])
        }
        xml_dict["SoilProperties"].append(p)

    return xml_dict

def modify_xml_file(xml_file_path: Path, parameters: dict):
    """
    Modify an existing XML file that is an input to the Shetran pre-processor.
    
    :param xml_file_path: Full path to XML file location.
    :type xml_file_path: Path
    :param parameters: Dictionary of paramaeters and the values to change them to.
    :type parameters: dict
    """
    print(parameters)

    veg_detail_start_idx = 12
    soil_prop_start_idx = 22

    with open(xml_file_path, "r", encoding="utf-8") as file:
        xml_list = [line.strip() for line in file]

    for line in range(0, 7):
        xml_idx = veg_detail_start_idx+line
        
        v_num = parameters["VegetationDetails"][line]["Descriptors"]["Veg Type #"]
        v_type = parameters["VegetationDetails"][line]["Descriptors"]["Vegetation Type"]
        csc = float(parameters["VegetationDetails"][line]["Parameters"]["Canopy storage capacity (mm)"])
        lai = float(parameters["VegetationDetails"][line]["Parameters"]["Leaf area index"])
        mrd = float(parameters["VegetationDetails"][line]["Parameters"]["Maximum rooting depth(m)"])
        aepe = float(parameters["VegetationDetails"][line]["Parameters"]["AE/PE at field capacity"])
        sofc = float(parameters["VegetationDetails"][line]["Parameters"]["Strickler overland flow coefficient"])
        
        content = f"<VegetationDetail>{v_num},{v_type}, {float(csc):.1f}, {float(lai):.1f}, {float(mrd):.1f}, {float(aepe):.1f}, {float(sofc):.1f}</VegetationDetail>"
        xml_list[xml_idx] = content

    for line in range(0, 7):
        xml_idx = soil_prop_start_idx+line

        s_num = parameters["SoilProperties"][line]["Descriptors"]["Soil Number"]
        s_type = parameters["SoilProperties"][line]["Descriptors"]["Soil Type"]
        sws = parameters["SoilProperties"][line]["Parameters"]["Saturated Water Content"]
        rwc = parameters["SoilProperties"][line]["Parameters"]["Residual Water Content"]
        sc = parameters["SoilProperties"][line]["Parameters"]["Saturated Conductivity (m/day)"]
        vga = parameters["SoilProperties"][line]["Parameters"]["vanGenuchten- alpha (cm-1)"]
        vgn = parameters["SoilProperties"][line]["Parameters"]["vanGenuchten-n"]

        content = f"<SoilProperty>{s_num},{s_type}, {float(sws):.4f}, {float(rwc):.4f}, {float(sc):.4f}, {float(vga):.4f}, {float(vgn):.4f}</SoilProperty>"
        xml_list[xml_idx] = content

    xml_list.append("")

    with open(xml_file_path, "w", encoding="utf-8") as file:
        file.write("\n".join(xml_list))