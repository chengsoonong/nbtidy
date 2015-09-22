"""Extract file read and file write statements from jupyter notebooks.
Try to figure out the data flow from the file names.
"""
import re
import nbformat

reader_names = ['read_csv']
writer_names = ['to_csv', 'savefig']

def find_filenames(fname):
    """Look inside code cells, extract filenames"""
    nb = nbformat.read(fname, as_version=4)
    input_files = []
    output_files = []
    for cell in nb.cells:
        if cell.cell_type != 'code':
            continue
        cell_id = cell.execution_count
        if cell_id is not None:
            #print('Code cell %d' % cell_id)
            code_str = cell.source
            #print(code_str)
            input_files.extend(code2name(code_str, reader_names))
            output_files.extend(code2name(code_str, writer_names))
    return input_files, output_files

def code2name(code_str, keywords):
    """Extract the file name from a piece of code"""
    names = []
    for keyword in keywords:
        for match in re.finditer(r'(.*)%s(.*)' % keyword, code_str):
            fname = match.group(2).split("'")[1]
            names.append(fname)
    return names

def debug_parser(fname):
    print('parsing %s' % fname)
    input_files, output_files = find_filenames(fname)
    print('Input files')
    print(input_files)
    print('Output files')
    print(output_files)

if __name__ == '__main__':
    dir_name = 'examples'
    for name in ['toyA', 'toyB', 'toyC']:
        fname = '%s/%s.ipynb' % (dir_name, name)
        debug_parser(fname)
