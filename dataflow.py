"""Extract file read and file write statements from jupyter notebooks.
Try to figure out the data flow from the file names.
"""
import re
import nbformat
from graphviz import Digraph

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

def construct_dict(dir_name, fnames):
    """Contruct a dictionary, like a dask graph,
    from the list of input notebooks.
    """
    workflow = {}
    for name in fnames:
        input_files, output_files = find_filenames(dir_name+'/'+name)
        workflow[name] = {'input': input_files, 'output': output_files}
    return workflow


def to_graphviz(workflow):
    """Convert dictionary to a dot graph."""
    g = Digraph()

    seen = set()
    cache = {}

    for nbname, v in workflow.items():
        g.node(nbname, shape='box')
        for fname in v['input']:
            if fname not in seen:
                seen.add(fname)
                g.node(fname, shape='hexagon')
            g.edge(fname, nbname)
        for fname in v['output']:
            if fname not in seen:
                seen.add(fname)
                g.node(fname, shape='hexagon')
            g.edge(nbname, fname)
    return g


if __name__ == '__main__':
    fnames = []
    dir_name = 'examples'
    for name in ['toyA', 'toyB', 'toyC']:
        fnames.append('%s.ipynb' % name)
    workflow = construct_dict(dir_name, fnames)
    print(workflow)
    g = to_graphviz(workflow)
    data = g.pipe(format='pdf')
    with open('toy.pdf', 'wb') as f:
        f.write(data)
