UW-DNMR v0.0.1 (alpha)
**********************

**UW-DNMR** (Un-Windowed Dynamic NMR; pronounced "You Dee En Em Arr") is a
Python implementation of the core features of WinDNMR by Hans Reich. The
long-term goal is to replicate the features of WinDNMR and to provide a
useful open-source application for Mac and Linux as well as Windows.

A secondary, (overly?)ambitious goal is to provide code and documentation of
sufficient quality that it can serve as a tutorial for others on how to
simulate NMR spectra and create a scientific application in Python.

Installation and Use
====================

The project is alpha and subject to change. The master branch should
maintain a functional program. If you're curious, and have a Python 3
installation, you can download the project folders, install the requirements in requirements.txt if necessary, and run main.py from the command line.

TODO
====

See CHANGELOG.rst for the map towards a version 1.0.

Feedback
========

I welcome feedback on this project. Feel free to leave an issue on Github, or
contact me by email (mylastname at udel dot edu).

Acknowledgements
================

Hans Reich (University of Wisconsin-Madison) kindly shared his original Visual
Basic 6 code, which served as a
guide to recreating the functionality and structure of WinDNMR.
Some of the VB6 variable names and gross function structure are
inherited by UW-DNMR, particular in the first-order calculations, but the
math routines were written from scratch by G.S., and any flaws in UW-NMR
calculations are solely attributable to G.S.
UW-DNMR also initializes its simulations with the same variables as
WinDNMR, to compare and verify that the simulations are performing correctly.

The second-order calculations are entirely different from WinDNMR's, and draw
primarily from two sources:

* The lectures at `spindynamics.org <http://spindynamics.org/support.php>`_, particularly Ilya Kuprov's MATLAB code in "Simulation design and coding, Part I/II"
* Examples found on the website of Frank Rioux (St. John's University and College of St. Benedict), particulary this example of tensor algebra: `<http://www.users.csbsju.edu/~frioux/nmr/ABC-NMR-Tensor.pdf>`_

Although "baking the spin Hamiltonian from scratch" is educational, and may
enable the modeling of non-spin-1/2 nuclei in the future, it likely comes at
a performance cost, and may be factored out in future versions.
