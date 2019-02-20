"""Utility script to be used to cleanup the notebooks before git commit

This a mix from @minrk's various gists.

Copied from Olivier Griesel's parallel ipython tutorial:
https://github.com/ogrisel/parallel_ml_tutorial

Added: https://gist.github.com/minrk/3836889

"""

import time
import sys
import os
import io
import argparse
try:
    from queue import Empty
except:
    # Python 2 backward compat
    from Queue import Empty

import nbformat
from jupyter_client import KernelManager
from ipyparallel import Client

try:
    FileNotFoundError
except NameError:
    FileNotFoundError = IOError
    
solution_placeholder_markdown = u'### <span style="color:blue">Answer</span>\n<i>--- replace this with your solution, add and remove code and markdown cells as appropriate ---</i>'
solution_placeholder_code = u'# replace this with your solution, add and remove code and markdown cells as appropriate'
solution_markers = ['# solution', '## solution', '### solution', '#### solution']

assert KernelManager  # to silence pyflakes


def is_solution_cell(cell):
    cell_start = cell.source.lower()[:30]
    is_solution = False
    for s in solution_markers:
        if cell_start.startswith(s):
            is_solution = True
    return is_solution


def remove_outputs(nb):
    num_outputs = 0
    for cell in nb.cells:
        if cell.cell_type == 'code':
            num_outputs += 1
            cell.outputs = []
            if 'execution_count' in cell:
                cell['execution_count'] = None
    print('removed %d code outputs' % num_outputs)

def remove_solution_code(nb):
    scrubbed = 0
    cells = 0
    for cell in nb.cells:
        if cell.cell_type != 'code':
            continue
        cells += 1
        if is_solution_cell(cell):
            cell.source = solution_placeholder_code
            scrubbed += 1
            cell.outputs = []
    print('scrubbed %i/%i code cells from notebook' % (scrubbed, cells))

def remove_solution_text(nb):
    scrubbed = 0
    cells = 0
    for cell in nb.cells:
        if cell.cell_type != 'markdown':
            continue
        cells += 1
        if is_solution_cell(cell):
            scrubbed += 1
            cell.source = solution_placeholder_markdown
    print('scrubbed %i/%i markdown cells from notebook' % (scrubbed, cells))

def run_cell(kernel_client, cell, timeout=300):
    if not hasattr(cell, 'source'):
        return [], False
    kernel_client.execute(cell.source)
    # wait for finish, maximum 5min by default
    reply = kernel_client.get_shell_msg(timeout=timeout)['content']
    if reply['status'] == 'error':
        failed = True
        print("\nFAILURE:")
        print(cell.source)
        print('-----')
        print("raised:")
        print('\n'.join(reply['traceback']))
    else:
        failed = False

    # Collect the outputs of the cell execution
    outs = []
    while True:
        try:
            msg = kernel_client.get_iopub_msg(timeout=2)
        except Empty:
            break
        msg_type = msg['msg_type']
        if msg_type in ('status', 'execute_input'):
            continue
        elif msg_type == 'clear_output':
            outs = []
            continue

        content = msg['content']
        out = nbformat.NotebookNode(output_type=msg_type)
        if msg_type == 'stream':
            out.name = content['name']
            out.text = content['text']
        elif msg_type in ('display_data', 'execute_result'):
            out.metadata = content['metadata']
            out.data = content['data']
            if msg_type == 'execute_result':
                out.execution_count = content['execution_count']

        elif msg_type == 'error':
            out.ename = content['ename']
            out.evalue = content['evalue']
            out.traceback = content['traceback']
        elif msg_type == 'execute_input':
            print(content)
        else:
            print("unhandled iopub msg: %s" % msg_type)
        outs.append(out)

    # Special handling of ipcluster restarts
    if '!ipcluster stop' in cell.source:
        # wait some time for cluster commands to complete
        for i in range(10):
            try:
                if len(Client()) == 0:
                    break
            except FileNotFoundError:
                pass
            sys.stdout.write("@"); sys.stdout.flush()
            time.sleep(5)
    if '!ipcluster start' in cell.source:
        # wait some time for cluster commands to complete
        for i in range(10):
            try:
                if len(Client()) > 0:
                    break
            except FileNotFoundError:
                pass
            sys.stdout.write("#"); sys.stdout.flush()
            time.sleep(5)
    return outs, failed


def run_notebook(nb):
    km = KernelManager()
    km.start_kernel(stderr=open(os.devnull, 'w'))
    kc = km.client()
    kc.start_channels()

    # simple ping:
    kc.execute("pass")
    kc.get_shell_msg()

    cells = 0
    failures = 0
    for cell in nb.cells:
        if cell.cell_type != 'code':
            continue

        outputs, failed = run_cell(kc, cell)
        cell.outputs = outputs
        cells += 1
        cell['execution_count'] = cells
        failures += failed
        sys.stdout.write('.')
        sys.stdout.flush()

    print()
    #print("ran notebook %s" % nb.metadata.name)
    print("    ran %3i cells" % cells)
    if failures:
        print("    %3i cells raised exceptions" % failures)
    kc.stop_channels()
    km.shutdown_kernel()
    del km


def process_notebook_file(fname, action, output_fname):
    print('-' * 20 + '\n', action, '\n', fname, '\n', output_fname, '\n', '-' * 20 + '\n')
    
    orig_wd = os.getcwd()
    with io.open(fname, 'r') as f:
        nb = nbformat.read(f, as_version=4)
    os.chdir(os.path.dirname(fname))

    if action == 'check':
        run_notebook(nb)
    elif action == 'sol':
        run_notebook(nb)
    elif action == 'work':
        run_notebook(nb)
        remove_outputs(nb)
        remove_solution_text(nb)
        remove_solution_code(nb)
    elif action == 'clean':
        remove_outputs(nb)
        assert output_fname is None
        output_fname = fname
    else:
        raise Exception(action)

    os.chdir(orig_wd)

    if output_fname is not None:
        with io.open(output_fname, 'w') as f:
            nb = nbformat.write(nb, f)
            print('wrote', output_fname)


def take_action(action, target, outpath):
    
    if outpath is None:
        output_fname = None
    else:
        assert os.path.exists(outpath), '%s does not exist' % outpath
        outpath = os.path.abspath(args.outpath)
        new_name = os.path.splitext(os.path.basename(target))[0] + ('-%s.ipynb' % action)
        output_fname = os.path.join(outpath, new_name)

    process_notebook_file(target, action=action, output_fname=output_fname)


if __name__ == '__main__':
    
    allowed_actions = ['work', 'sol', 'check', 'clean']
    outputing_actions = ['work', 'sol', 'clean']

    parser = argparse.ArgumentParser()
    parser.add_argument('action', help='|'.join(allowed_actions), type=str)
    parser.add_argument('target', help='target file path', type=str)
    parser.add_argument('-o', '--outpath', dest='outpath', help='output directory path', type=str, default=None)
    
    args = parser.parse_args()
    args.target = os.path.abspath(args.target)

    assert args.action in allowed_actions, args.action
    if args.action in outputing_actions:
        assert args.outpath is not None, ('outpath reqired for action = ' + args.action)
    else:
        assert args.outpath is None, ('outpath not required for action = ' + args.action)
    if args.action == 'clean':
        assert args.outpath == 'overwrite', 'outpath must equal "overwrite"'
        args.outpath = None

    take_action(args.action, args.target, args.outpath)
