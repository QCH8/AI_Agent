import os
import subprocess
from google.genai import types

schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Allows the execution of the python file, and returns the output from the interpreter.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path leading to the Python file to execute, relative to the working directory.",
            ),
            "args": types.Schema(
                type=types.Type.ARRAY,
                description="Optionnal arguments to pass to the Python file",
                items=types.Schema(type=types.Type.STRING),
            ),
        },
        required=["file_path"],
    ),
)




def run_python_file(working_directory, file_path, args=[]):
    workdir = os.path.realpath(working_directory)
    target = os.path.realpath(os.path.join(working_directory, file_path))

    if os.path.commonpath([workdir, target]) != workdir:
        return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
    
    if not os.path.exists(target):
        return f'Error: File "{file_path}" not found.'
    
    if not target.endswith(".py"):
        return f'Error: "{file_path}" is not a Python file.'
    
    command_list = ["python", target] + list(args)

    try:
        completed = subprocess.run(command_list, cwd=workdir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30, text=True)

        output_lines=[]
        #format result string here
        if completed.stdout:
            output_lines.append("STDOUT: "+ completed.stdout)

        if completed.stderr:
            output_lines.append("STDERR: " + completed.stderr)
        
        if completed.returncode !=0:
            output_lines.append(f"Process exited with code {completed.returncode}")

        if not completed.stderr and not completed.stdout:
            return f"No output produced."
        return "\n".join(output_lines)
    except Exception as e:
        return f"Error: executing Python file: {e}"