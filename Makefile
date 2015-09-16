# This is not a Makefile for building things!
#
# Tidy up ipython notebooks before committing to git.

TARGET="examples/linalg-opt.ipynb"

all: debug worksheet clean

debug:
	python ipynbhelper.py --debug $(TARGET)

worksheet:
	python ipynbhelper.py --render $(TARGET)

solution:
	python ipynbhelper.py --render --solution $(TARGET)

clean:
	find . -name "*.pyc" | xargs rm -f
	python ipynbhelper.py --clean $(TARGET)

clean-data:
	find . -name "*.pkl" | xargs rm -f
	find . -name "*.npy" | xargs rm -f
	find . -name "*.mmap" | xargs rm -f

pdf:
	python ipynbhelper.py --render --solution $(TARGET)
	ipython nbconvert --to latex --post PDF $(TARGET)
