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
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print("Simulation completed successfully.")
        else:
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
            print("Pre-processing failed with error: {result.stderr}")

    except Exception as e:
        print(f"An unexpected error occurred: {e}") 

def modify_xml_file(xml_file_path: Path, parameters: dict):
    """
    Modify an existing XML file that is an input to the Shetran pre-processor.
    
    :param xml_file_path: Full path to XML file location.
    :type xml_file_path: Path
    :param parameters: Dictionary of paramaeters and the values to change them to.
    :type parameters: dict
    """
    try:
        tree = ET.parse(xml_file_path)
        root = tree.getroot()
    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
        return
    
    table_config = {
        'VegetationDetails': 'VegetationDetail',
        'SoilProperties': 'SoilProperty',
        'SoilDetails': 'SoilDetail'
    }

    for param_name, new_value in parameters.items():
        if param_name in table_config:
            _update_table_entries(root, param_name, table_config[param_name], new_value)
        else:
            element = root.find(param_name)
            if element is not None:
                element.text = str(new_value)
            else:
                print(f"Warning: Tag <{param_name}> not found in XML.")

    tree.write(xml_file_path, encoding='unicode', xml_declaration=True)

def load_shetran_params(json_filepath: Path) -> dict:
    """
    Load a configuration json file of parameters and their bounds.
    
    :param json_filepath: Full file path to config json.
    :type json_filepaths: Path
    """
    with open(json_filepath, 'r') as f:
        data = json.load(f)

    if "SoilDetails" in data:
        converted_soil_details = {}
        for key_str, val in data["SoilDetails"].items():
            try:
                key_tuple = tuple(int(x.strip()) for x in key_str.split(','))
                converted_soil_details[key_tuple] = val
            except ValueError:
                print(f"Warning: Could not convert key '{key_str}' to tuple. Keeping as string.")
                converted_soil_details[key_str] = val
        
        data["SoilDetails"] = converted_soil_details

    return data

def _update_table_entries(root, table_tag, row_tag, updates):
    parent = root.find(table_tag)
    if parent is None:
        print(f"Warning: Table block <{table_tag}> not found.")
        return

    rows = parent.findall(row_tag)
    if not rows:
        return

    header_element = rows[0]
    header_data = next(csv.reader([header_element.text]))
    headers = [h.strip() for h in header_data]

    for row_id_input, col_updates in updates.items():
        found_row = False
        for row_element in rows[1:]:
            current_csv = next(csv.reader([row_element.text]))
            current_data = [c.strip() for c in current_csv]
        
            if table_tag == 'SoilDetails':
                if isinstance(row_id_input, (list, tuple)) and len(row_id_input) == 2:
                    if current_data[0] == str(row_id_input[0]) and current_data[1] == str(row_id_input[1]):
                        _apply_row_updates(row_element, current_data, headers, col_updates)
                        found_row = True
                        break
            
            else:
                if current_data[0] == str(row_id_input):
                    _apply_row_updates(row_element, current_data, headers, col_updates)
                    found_row = True
                    break
        
        if not found_row:
            print(f"Warning: ID {row_id_input} not found in {table_tag}")

def _apply_row_updates(xml_element, data_list, headers, col_updates):
    for col_name, value in col_updates.items():
        try:
            idx = headers.index(col_name)
            data_list[idx] = str(value)
            print(f"Updated {col_name} -> {value}")
        except ValueError:
            print(f"Error: Column '{col_name}' not found in headers.")
            
    xml_element.text = ", ".join(data_list)