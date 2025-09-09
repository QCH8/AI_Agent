import os
from google.genai import types

schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in the specified directory along with their sizes, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="The directory to list files from, relative to the working directory. If not provided, lists files in the working directory itself.",
            ),
        },
    ),
)


def get_files_info(working_directory, directory="."):

    try:

        full_path = os.path.join(working_directory, directory)
        absolute_path = os.path.abspath(full_path)
        absolute_working_dir = os.path.abspath(working_directory)

        if not absolute_path.startswith(absolute_working_dir):
            return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'
        
        if not os.path.isdir(absolute_path):
            return f'Error: "{directory}" is not a directory'
        
        directory_list = []
        entries = os.listdir(absolute_path)
        for entry in entries:
            entry_path = os.path.join(absolute_path, entry)
            entry_is_dir = os.path.isdir(entry_path)
            directory_list.append(f"- {entry}: file_size={os.path.getsize(entry_path)} bytes, is_dir={entry_is_dir}")
        return "\n".join(directory_list)
    except Exception as e:
        return f"Error: {str(e)}"




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