PROJECT := EOSim

.DEFAULT_GOAL := all

DOC = docs

.PHONY: docs docs_clean

help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  all        to perform clean-up and installation"
	@echo "  install    to set up the python package (pip install -e .)"
	@echo "  runtest    to perform unit testing"
	@echo "  testlog    to perform unit testing with no log capture"
	@echo "  fulltest   to perform unit testing with no log capture and with verbose"
	@echo "  clean      to remove *.pyc files and __pycache__ directories"
	@echo "  bare       to uninstall the package and remove *egg*"

all: bare install

install: 
# cartopy installation to be done prior to this. If using conda, can be done using the command `conda install -c conda-forge cartopy`
# In case of Runtime errors involving numpy (after installation), try the following command: `pip install numpy --upgrade --ignore-installed`
	pip install -e .

clean: docs_clean
	@echo "Cleaning up..."
	@find . -name "*.pyc" -delete
	@find . -type d -name __pycache__ -print0 | xargs -0 rm -rf

bare: clean
	pip uninstall -y $(PROJECT) 
	rm -rf $(PROJECT).egg-info .eggs
