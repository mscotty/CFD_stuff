import os


def filter_files(top_folder, inclusions=None, exclusions=None):
    """
    Filter files in a top-level folder based on inclusion and exclusion criteria.

    Parameters:
    - top_folder (str): The top-level folder to search.
    - inclusions (dict): Dictionary specifying inclusion criteria.
                        Keys can be 'names', 'folders', 'extensions'.
    - exclusions (dict): Dictionary specifying exclusion criteria.
                        Keys can be 'names', 'folders', 'extensions'.

    Returns:
    - List of file paths that meet the criteria.
    """

    def check_criteria(filename, folder, extension):
        folder_suffix = folder.lstrip(top_folder)
        # Check exclusion criteria
        if exclusions:
            if 'folders' in exclusions and any(fol in folder_suffix for fol in exclusions['folders']):
                return False
            if 'names' in exclusions and any(name in filename for name in exclusions['names']):
                return False
            if 'extensions' in exclusions and any(filename.endswith(ext) for ext in exclusions['extensions']):
                return False

        # Check inclusion criteria
        if inclusions:
            if 'folders' in inclusions and not any(fol in folder_suffix for fol in inclusions['folders']):
                return False
            if 'names' in inclusions and not any(name in filename for name in inclusions['names']):
                return False
            if 'extensions' in inclusions and not any(extension==ext for ext in inclusions['extensions']):
                return False

        return True

    result = []

    for foldername, subfolders, filenames in os.walk(top_folder):
        for filename in filenames:
            full_path = os.path.join(foldername, filename).replace('\'', '/')

            # Split the filename into name and extension
            name, extension = os.path.splitext(filename)

            if check_criteria(name, foldername, extension):
                result.append(full_path)

    return result


if __name__ == "__main__":
    # Example usage:
    top_folder = 'D:/Mitchell/Work/civilian/python'
    #inclusions = {'names': ['example_file'], 'folders': ['PythonCode'], 'extensions': ['.txt']}
    inclusions = {'folders': ['misc'], 'extensions': ['.py']}
    #exclusions = {'names': ['exclude_file'], 'folders': ['exclude_folder'], 'extensions': ['.pdf']}
    exclusions = None#{'folders': ['.env']}

    result = filter_files(top_folder, inclusions=inclusions, exclusions=exclusions)
    print(result)
