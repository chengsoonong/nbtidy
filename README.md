# nbtidy
Tidying jupyter notebooks

## Visualise the flow of data

#### Dependencies

- graphviz
- nbformat

#### Quick start
By looking at the code sections of jupyter notebooks, try to figure out when files are read and written. Construct a graph showing the flow, and render it as a PDF.

```bash
# Generate some data
cd examples
python generate_toy.py
cd ..
# Draw the dataflow diagram
python dataflow.py -d examples toyA.ipynb toyB.ipynb toyC.ipynb -t -o toy.pdf
```

The results are in toy.pdf

## Tidying up worksheets

We are using [jupyter notebooks](https://jupyter.org/) for the tutorial exercises and assignments in the [Introduction to Statistical Machine Learning](http://programsandcourses.anu.edu.au/course/comp4670) course. The tool ```ipynbhelper.py``` was written mainly to strip the solution cells from tutorial sheets.

* ```ipynbhelper.py``` is most easily used via the ```Makefile```.
* Solution cells can be markdown or code cells. These cells start with ```### Solution``` and ```# Solution``` on a line by itself respectively.

## Related resources

* [nbconvert](http://nbconvert.readthedocs.org/en/latest/) is the main way to interact with the JSON file representing the notebook.
* [NBDiff](http://nbdiff.org/): A diffing and merging tool for the IPython Notebook
* [nbgrader](http://nbgrader.readthedocs.org/en/stable/) helps the instructor to manage assignments, with added bells and whistles for [JupyterHub](https://github.com/jupyter/jupyterhub).
