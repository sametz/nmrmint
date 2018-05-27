nmrmint (version 0.3 beta)
**************************

.. image:: docs/source/_static/screenshot.png

`Documentation on Read the Docs <https://nmrmint.readthedocs.io/en/latest/>`_

`PDF Documentation`_.

.. _PDF Documentation: docs/nmrmint.pdf

**nmrmint** is an application for creating simulated complete NMR spectra
(currently \ :sup:`1`\ H NMR only) for use in chemical education. The
application will
'mint' an NMR spectrum from user-provided chemical shifts and coupling
constants.

I strongly believe that using actual experimental data for classes and exams
is to be preferred. However, sometimes it can be hard to find spectra of
sufficient quality for printing on exams. You may have a spectrum that
would be easily solved at higher field strength, but you can only find
spectra taken in lower fields where second-order effects make analysis more
difficult. Or, conversely, you may have a high-quality spectrum that you want
simulated at lower field strengh in order to demonstrate second-order
features such as AB quartets, ABX systems, or AA'XX' (e.g. para-substituted
benzenes). In such cases, nmrmint will provide you with that spectrum you
need for tomorrow's quiz.

For each subspectrum simulation, the user can choose either first-order
simulation for individual chemical shift-equivalent nuclei (doublets, triplets,
doublet-of-doublets, etc.), or a second-order simulation of a two- to
eight-nuclei spin system.

**Version 0.3 (beta)** features a completely reworked, more user-friendly GUI
than v0.2 (alpha). The following features have been added:

* Individual subspectra can be created, added, deleted, and cycled through
* Individual subspectra can be toggled between being added to the total
  spectrum, and not being added.
* Each subspectrum can have its own linewidth (peak width at half height)
  set, allowing simulation of broadened signals such as OH/NH protons.
* The frequency of the spectrometer (i.e. frequency in MHz that TMS protons
  resonate at) can be changed at will, updating the entire spectrum.
* The minimum/maximum ppm limits for the total spectrum can be changed.
  Currently the limit is hardcoded from -1 to +15 ppm.

Desirable features, and known issues, include:

* Second-order simulation of > 8 nuclei. Currently, the calculations slow
  down dramatically with > 8 nuclei. Future code optimizations may allow this
  to be expanded. There may also be simplifications possible for larger
  systems, such as alkyl chains attached to a carbon with diastereotopic
  protons.
* Creating expansions. The current workaround is to use the min/max ppm
  entries and individually save these "zoom-ins" of the total spectrum. The
  built-in matplotlib toolbar allows for expanding regions of the spectrum, but
  the built-in "save" (floppy disk icon) saves both top and bottom spectra as
  a .png file that would require editing.
* simulating other spectra, such as carbon-13.

and in the longer term:

* integration
* peak picking
* expansions

Installation and Use
====================

The project is beta and subject to change. The master branch should
maintain a functional program. If you're curious, and have a Python 3
installation (v3.6 was used for development), you can download the project
folders, install the requirements in requirements.txt if necessary, and run
main.py from the command line.

Standalone, executable 1-file applications for Mac, Windows and Linux are
planned for a future release.

TODO
====

See CHANGELOG.rst for the map towards a version 1.0.

Feedback
========

The author is neither a professional programmer nor a professional NMR
spectroscopist. I welcome feedback on this project. Feel free to leave an
issue on Github, or contact me by email (mylastname at udel dot edu).

Acknowledgements
================

This project is inspired by Hans Reich's WINDNMR application. **nmrmint**
initializes its simulations with the same variables as WINDNMR's defaults,
to verify that the simulation is performing correctly.
