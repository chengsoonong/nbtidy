# nbtidy
Tidying jupyter notebooks

## Tidying up worksheets

We are using [jupyter notebooks](https://jupyter.org/) for the tutorial exercises and assignments in the [Introduction to Statistical Machine Learning](http://programsandcourses.anu.edu.au/course/comp4670) course. The tool ```ipynbhelper.py``` was written mainly to strip the solution cells from tutorial sheets.

* ```ipynbhelper.py``` is most easily used via the ```Makefile```.
* Solution cells can be markdown or code cells. These cells start with ```### Solution``` and ```# Solution``` on a line by itself respectively.

## Related resources

* [nbconvert](http://nbconvert.readthedocs.org/en/latest/) is the main way to interact with the JSON file representing the notebook.
* [NBDiff](http://nbdiff.org/): A diffing and merging tool for the IPython Notebook
* [nbgrader](http://nbgrader.readthedocs.org/en/stable/) helps the instructor to manage assignments, with added bells and whistles for [JupyterHub](https://github.com/jupyter/jupyterhub).

