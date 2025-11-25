import subprocess
from pathlib import Path

def run_shetran(exe_path: Path, rundata_path: Path):
    """
    Executes a SHETRAN simulation.

    Args:
        exe_path (Path): Full path to the shetran executable.

        rundata_path (Path): Full path to the rundata file.
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

def run_preprocessor(prep_exe_path: Path, input_file_path: Path):
    """
    Executes the SHETRAN Pre-processor.
    
    Args:
        prep_exe_path (Path): Full path to the pre-processor executable.

        input_file_path (Path): Full path to the XML file.
    """
    
    if not prep_exe_path.exists():
        print(f"Error: Pre-processor executable not found at {prep_exe_path}")
        return
    if not input_file_path.exists():
        print(f"Error: Input file not found at {input_file_path}")
        return

    working_dir = input_file_path.parent
    
    command = [str(prep_exe_path), str(input_file_path)]
    
    print(f"Starting Pre-processor run for: {input_file_path.name}...")
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