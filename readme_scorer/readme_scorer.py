"""
Run the README scorer from within Python or the command line

@author: luke
@author: peter
"""

## Imports ##
import os
import git
import argparse

## Constants ##
README_NAMES = ['README', 'readme', 'README.md', 'readme.md']
EXCLUDE_FILES = ['.gitignore', '.gitattributes', '__init__.py'] # Note: do not put README files here!
EXCLUDE_EXTNS = ['.png','.pyc','.pyc'] # Committed file extensions that do not require explanation

## Functions ##



def calc_readme_score(fpath, total_described=0, total_found=0, html=None, verbose=True):
    """
    Recursive function to loop through a file directory to calculate how many files are listed
    and how many are described in the folders' README files. Pass fpath argument to specify the top
    level folder.
    """
    files = find_files(fpath)

    # Try to find a README file
    my_readme = None
    for readme in README_NAMES:
        if readme in files:
            my_readme = readme
            break

    if my_readme is None:
        total_found += len(files)
        if verbose:
            print(files)
        if html is not None:
            for file in files: html.add_excluded_file(file)
        total_described += 0
    else:
        total_found, total_described, html = get_no_files_in_readme(fpath, my_readme, files,
                                                                    total_found, total_described,
                                                                    html
                                                                   )

    # Recursive call to each subfolder
    dirs = [d for d in os.listdir(fpath) if os.path.isdir(os.path.join(fpath, d)) and d != '.git']
    for subfolder in dirs:
        if html is not None:
            html.add_directory(subfolder)
            html.increment_layer()

        total_described, total_found, html = calc_readme_score(os.path.join(fpath, subfolder),
                                                               total_described, total_found, 
                                                               html, verbose
                                                              )

    if html is not None:
        html.decrement_layer()

    assert total_found >= total_described
    return total_described, total_found, html

def correct_file(file):
    if '/' in file:
        return False
    if file in EXCLUDE_FILES:
        return False
    if not file.strip():
        return False
    _, extension = os.path.splitext(file)

    if extension in EXCLUDE_EXTNS:
        return False
    return True

def find_files(fpath):
    # Get all git-tracked files from this filepath (fpath)
    git_obj = git.cmd.Git(fpath)
    files = [file for file in git_obj.ls_files().split('\n') if correct_file(file)]
    return files

def get_no_files_in_readme(fpath, my_readme, files, total_found, total_described, html):
    with open(os.path.join(fpath, my_readme), 'r') as file:
        described = file.readlines()

    for file in files:
        # Don't need to describe the README file
        if file == my_readme:
            continue

        total_found += 1
        file_found = False
        for line in described:
            # Must use backticks to properly describe the file
            if '`' + file + '`' in line:
                file_found = True
                break

        if file_found:
            total_described += 1
            if html is not None:
                html.add_included_file(file)
        else:
            if html is not None:
                html.add_excluded_file(file)

    return total_found, total_described, html


class HtmlReport:
    def __init__(self, outfile, initial_html_text):
        self.text = ""
        self.initial_html_text = initial_html_text
        self.outfile = outfile
        self.layer_no = 0

    def print_layer_start(self):#hit_end_array):
        self.text += "<pre>" + "\t"*self.layer_no
        self.text += "├──"

    def print_layer_end(self):
        self.text += "</pre>"*self.layer_no

    def increment_layer(self):
        self.layer_no += 1

    def decrement_layer(self):
        self.layer_no -= 1

    def finalise_report(self, total_described, total_found):
        init_text = "<h2>README Coverage: {}% </h2>".format(int(100*total_described/total_found))
        init_text += "<h3>Total Found={}, Total Described={}</h3>".format(total_found, total_described)
        self.text = self.initial_html_text + init_text + self.text + "</body></html>"

    #TODO escape this...
    def add_directory(self, dir_name):
        self.text += "<h4 class='direct'>"
        self.print_layer_start()
        self.text += dir_name
        self.print_layer_end()
        self.text += "</h4>"+ "\n"

    def add_included_file(self, file_name):
        self.text += "<h4 class='included_file'>"
        self.print_layer_start()
        self.text += file_name
        self.print_layer_end()
        self.text += "</h4>" + "\n"

    def add_excluded_file(self, file_name):
        self.text += "<h4 class='excluded_file'>"
        self.print_layer_start()
        self.text += file_name
        self.print_layer_end()
        self.text += "</h4>" + "\n"

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Calculate README score on a given directory')
    parser.add_argument('path', help='the file directory of interest')
    args = parser.parse_args()

    found, total, _ = calc_readme_score(args.path, verbose=False)
    score = 100 * found / total
    print('README score: %.2f%% (%d / %d)' % (score, found, total))
