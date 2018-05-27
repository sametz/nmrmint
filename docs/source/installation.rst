Installation and Execution
==========================

Single-file, click-to-run executables for Windows, Mac OSX and Linux are anticipated but not available yet. See the `CHANGELOG <https://github.com/sametz/nmrmint/blob/master/CHANGELOG.rst>`_ for the map towards a Version 1 release.

The essential package components required to run the application are main.py plus the nmrmint subfolder and its contents. The project was developed with Python 3.6; older versions may work, but have not been tested yet.

The dependencies listed in requirements.txt are also required.
If pip is installed, the following command should automatically install the required dependencies::

>>>pip install -r requirements.txt

If you are familiar with virtual environments (e.g. using virtualenv, venv, or conda), you may wish to create one specifically for running this code, and install Python 3.6 and requirements there. If you use an Anaconda installation of Python, it is quite easy to set up and switch between different environments. See `the conda documentation`_ for details.

.. _the conda documentation: https://conda.io/docs/using/envs.html

Once the required code has been downloaded, and requirements installed, the nmrmint application can be launched by running main.py from the command line within the top-level nmrmint directory: ::

    $ python main.py
