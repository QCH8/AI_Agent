import os
from google.genai import types

schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Allows for the writing of the file",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path leading to the file to be read.",
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="The written data to write in the file.",
            ),
        },
    ),
)

def write_file(working_directory, file_path, content):
    
    workdir = os.path.realpath(working_directory)
    target= os.path.realpath(os.path.join(working_directory, file_path))

    if os.path.commonpath([workdir, target]) != workdir:
        return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'
    

    try:
        os.makedirs(os.path.dirname(target), exist_ok=True)
    except Exception as e:
        return f"Error: creating directory: {e}"
    
    
    try : 
        with open(target, "w") as f:
            f.write(content)
            return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'



    except Exception as e:
        return f'Error: {e}'