# src: https://tex.stackexchange.com/a/683701
import shutil
import os


# NOTE: main function is down below

def ask_existing_folder_name(default_folder_name=None) -> str:
    """ ask user for a folder name. """

    if default_folder_name is None:
        folder_name = input('Please enter an existing directory name:')
    else:
        folder_name = input(
            f'Please enter an existing directory (default = {default_folder_name}):')

        if folder_name in ['', 'y', 'Y']:
            folder_name = default_folder_name

    if os.path.isdir(folder_name):
        return folder_name

    print('That folder does not exist!')
    return ask_existing_folder_name(default_folder_name=default_folder_name)


def ask_new_folder_name(default_folder_name=None) -> str:
    """ ask user to input a new folder name. """
    if default_folder_name is None:
        folder_name = input('Please enter a new directory name:')
    else:
        folder_name = input(f'Please enter a new directory name (default = {default_folder_name}):')

        if folder_name in ['', 'y', 'Y']:
            folder_name = default_folder_name

    if not os.path.isdir(folder_name):
        return folder_name

    print('That folder does already exist!')
    return ask_new_folder_name(default_folder_name=default_folder_name)


def string_found_in_tex_files(string_to_search: str) -> bool:
    """
    return True if there exist a .tex file in the current
    directory or any subdirectory that contains string_to_search.
    """
    print(f"search string {string_to_search}")
    for root, _, files in os.walk("."):
        for filename in files:
            filepath = os.path.join(root, filename)
            if filepath.endswith('.tex') and os.path.isfile(filepath):
                with open(filepath) as file:
                    if string_to_search in file.read():
                        return True
    return False


def main():
    """ interactive CLI that moves unused figures from latex project. """

    print("welcome, we're going to remove all unused figures from this latex project")
    print('NOTE: make sure to run this function from latex project root\n')

    figures_folder_name = ask_existing_folder_name(default_folder_name='figures/')

    print('unused figures are moved to a new directory')
    unused_figures_folder_name = ask_new_folder_name(default_folder_name='unused_figures/')
    os.mkdir(unused_figures_folder_name)

    figure_file_paths = []

    extensions = (".pdf", ".jpg", ".png", ".eps")

    # collect all relative paths to figures
    for root, _, files in os.walk(figures_folder_name):
        for filename in files:
            if filename.endswith(extensions):
                file_path = os.path.join(root, filename)
                figure_file_paths.append(file_path)

    only_used_figures_detected = True
    for file_path in figure_file_paths:

        # take away the extension
        (file_path_without_extension, _) = os.path.splitext(file_path)

        if not string_found_in_tex_files(file_path_without_extension):

            only_used_figures_detected = False

            answer = input(f'{file_path} is unused,' \
                           f'do you want to move it to {unused_figures_folder_name} (Y/n)?')
            if answer in ['n', 'N', 'no']:
                continue

            # move the file
            shutil.move(file_path, unused_figures_folder_name)
            print(f'{file_path} moved to {unused_figures_folder_name}')

    if only_used_figures_detected:
        print('all figures are used :)')


if __name__ == '__main__':
    main()
