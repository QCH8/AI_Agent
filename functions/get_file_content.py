import os
from config import MAX_CHARS
from google.genai import types

schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description=f"Returns up to {MAX_CHARS} characters of the specified file within the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the file to be read, relative to the working directory.",
            ),
        },
    ),
)


def get_file_content(working_directory, file_path):
    
    full_path = os.path.join(working_directory, file_path)
    absolute_path = os.path.abspath(full_path)
    absolute_working_path = os.path.abspath(working_directory)

    if not absolute_path.startswith(absolute_working_path):
        return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'
    
    if not os.path.isfile(absolute_path):
        return f'Error: File not found or is not a regular file: "{file_path}"'

    try:
        with open(absolute_path, "r") as f:
        
            file_content_string = f.read(MAX_CHARS)  # Read up to 10000 characters
        
            next_char = f.read(1)  # Try to read one more character
        
            if next_char:  # If there was more content, we truncated
                return file_content_string + f'[...File "{file_path}" truncated at 10000 characters]'
            else:  # If no more content, return as-is
                return file_content_string
    except Exception as e:
        return f'Error reading file "{file_path}": {e}'






    """
    Here are some standard library functions you'll find helpful:

    os.path.abspath(): Get an absolute path from a relative path
    os.path.join(): Join two paths together safely (handles slashes)
    .startswith(): Check if a string starts with a substring
    os.path.isdir(): Check if a path is a directory
    os.listdir(): List the contents of a directory
    os.path.getsize(): Get the size of a file
    os.path.isfile(): Check if a path is a file
    .join(): Join a list of strings together with a separator
"""