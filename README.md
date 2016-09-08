## Bokeh
This tool uses bokeh, built on python:
http://bokeh.pydata.org/en/latest/.
The site has good documentation in the User Guide and Reference.

There is also an active google group for issues:
https://groups.google.com/a/continuum.io/forum/#!forum/bokeh

And of course, python has pretty good documentation too:
https://docs.python.org/2.7/tutorial/

## Setting Up
Get Anaconda for python 2.7 at:
https://www.continuum.io/downloads

Get gdxpds for reading gdx files into python:
https://github.com/NREL/gdx-pandas
Follow the instructions for installation on the readme

Then, here are the Bokeh installation instructions:
http://bokeh.pydata.org/en/latest/docs/installation.html
Easiest way, with Anaconda, from the command line:
conda install bokeh

Then, git clone this repo onto your computer.
- Side note: I had an issue pushing to this repo with a putty generated key. To fix, according to instructions i wrote for NREL repo, i had to change origin in .git/config from git@ to https://. See https://help.github.com/articles/which-remote-url-should-i-use/ and
https://help.github.com/articles/changing-a-remote-s-url/

## Running
From command line, cd into this git repo and type
    bokeh serve --show .