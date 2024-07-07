import os


def check_conditions(valid_files_list,
                     file_dir,
                     file_name,
                     file_extension,
                     excluded_folders=None,
                     excluded_files=None,
                     excluded_extensions=None):
    """!
    @brief Performs the validation checks to determine if the file is not a part of the exclusions

    @param[in] valid_files_list : list of the files (includes path and extension) that are not a part of the exclusions.
                                  This list is appended to throughout the execution of this function.

    @param[in] file_dir : string of the directory for the file (filename and extension not included)

    @param[in] file_name : string of the filename (extension and path not included)

    @param[in] file_extension : string of the file's extension that includes the "." (filename and path not included)

    @param[in] excluded_folders : list containing strings of folders to exclude

    @param[in] excluded_files : list containing strings of filenames to exclude

    @param[in] excluded_extensions : list containing strings of extensions to exclude

    @param[out] valid_files_list : same as the input list, except, if the provided file information did not meet any of
                                   the exclusions (for folder/filename/extension), then it will include the full path to
                                   the current file
    """
    # check folders
    if excluded_folders is not None:
        for curr_ex_folder in excluded_folders:
            if curr_ex_folder in file_dir:
                return valid_files_list

    # check file names
    if excluded_files is not None:
        for curr_ex_file in excluded_files:
            if curr_ex_file in file_name:
                return valid_files_list

    # check file_extensions
    if excluded_extensions is not None:
        for curr_ex_ext in excluded_extensions:
            if curr_ex_ext in file_extension:
                return valid_files_list

    valid_files_list.append(os.path.join(file_dir, file_name + file_extension))
    return valid_files_list


def search_dir(start_dir,
               excluded_folders=None,
               excluded_files=None,
               excluded_extensions=None):
    """!
    @brief Searches the provided directory for files that are not a part of any of the exclusions (contains inputs for
           folders, filenames, and extensions).

    @param[in] start_dir : string for the top-level folder to search within

    @param[in] excluded_folders : list containing strings of folders to exclude

    @param[in] excluded_files : list containing strings of filenames to exclude

    @param[in] excluded_extensions : list containing strings of extensions to exclude

    @param[out] valid_files_list : same as the input list, except, if the provided file information did not meet any of
                                   the exclusions (for folder/filename/extension), then it will include the full path to
                                   the current file
    """
    valid_files_list = []
    for root, dirs, files in os.walk(start_dir):
        for curr_file in files:
            file_name, file_extension = os.path.splitext(curr_file)
            valid_files_list = check_conditions(valid_files_list,
                                                root,
                                                file_name,
                                                file_extension,
                                                excluded_folders,
                                                excluded_files,
                                                excluded_extensions
                                                )
    return valid_files_list


if __name__ == "__main__":
    given_dir = "D:/Mitchell/Work/Thesis/2D2C_PIV/"
    excluded_folders_in = ["Data", "Hotwire"]
    excluded_files_in = ["table_results", "graph_inputs"]
    excluded_extensions_in = ["vc7", "asv", "mat", "m", "fig"]
    files_out = search_dir(given_dir,
                           excluded_folders=excluded_folders_in,
                           excluded_files=excluded_files_in,
                           excluded_extensions=excluded_extensions_in)
    print(files_out)