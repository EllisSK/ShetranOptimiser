import subprocess
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
    pass