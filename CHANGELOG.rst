##########
Change Log
##########

All notable changes to this project will be documented in this file.

The format is inspired by `Keep a Changelog <http://keepachangelog.com/en/0.3.0/>`_ and tries to adhere to `Semantic Versioning <http://semver.org>`_. The author interprets the terms below as follows:

* **pre-alpha status**: the app runs, but there is no formal unit or functional testing.


* **alpha status**: pre-alpha, plus implementation of unit and functional tests.


* **beta status**: alpha, plus documentation, implementation of all anticipated Version 1.0.0 features, and installation requirements.


* **release candidate status**: beta, plus standalone executable(s) for Windows, Mac OS X, and Linux.


* **Version 1.0.0 release**: a minimal app suitable for educational use and not requiring execution from the command line interface.

0.3.1 - 2018-05-28
------------------

Fixed
^^^^^

* Second-order toolbars no longer are unresponsive after a refresh.

* Updating a numerical entry no longer calls the recalculation of spectra twice, so updates now occur faster (this is especially noticeable with large second-order spin systems).

0.3.0 - 2018-05-27 (beta release)
----------------------------------

Added
^^^^^

* Subspectra Navigation: Can now create, delete, and swap between individual subspectrum simulations, and toggle whether or not they are added to the total spectrum simulation.

* PDF and EPS exporting of the simulated spectrum.
   * Can select landcape or portrait mode for EPS exports.

* Toolbars now have a "reset" button to restore them to their default settings.

* PDF documentation (HTML documentation via github.io to follow in a later patch).

Changed
^^^^^^^

* Each subspectrum can have its own linewidth setting. This allows, for example, adding a broad singlet for a hydroxyl proton undergoing exchange.

* The spectrometer frequency can be changed at any time, and will update the subspectrua and total spectrum plots accordingly.

* The resolution for the plots (number of data points) has been increased. To accomodate this, the maximum spectral window is currently hard-coded to be -1 to +15 ppm.

* "v min" and "v max" settings allow the user to set the minimum and maximum ppm range for their total spectrum.

Removed
^^^^^^^

* "Clear Current/Total Spectrum" buttons (replaced by subspectrum navigation options).

* "Back" and "Forward" history buttons (replaced by subspectrum navigation options)

* "Add to Total Spectrum" button in toolbars (replaced by subspectrum navigation options).


0.2.0 - 2017-10-25 (alpha release)
----------------------------------

Commit of actual nmrmint application with basic functionality in place.

0.1.0 - 2017-10-14 (pre-alpha release)
--------------------------------------

Initial Commit
