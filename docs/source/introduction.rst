Introduction to nmrmint v0.35.0 (beta)
======================================


**nmrmint** is an applicaiton for creating simulated, complete NMR spectra
for use in chemical education. Currently, the application is limited to \ :sup:`1`\ H NMR only, but expanding this to other nuclei such as \ :sup:`13`\ C is feasible.

The current version of pyDNMR will simulate spectra for the two-site
exchange of two spin-1/2 nuclei, either uncoupled (two singlets at the
slow-exchange limit), or coupled (two doublets, or AB quartet, at the
slow-exchange limit).

The short-term goal of this project is to create platform-specific executable files ("apps") for educational use. For example, the rate constant for nuclear exchange can be adjusted up and down to demonstrate coalescence of signals.

The longer-term goal of this project is to add simulations for more complex systems, and to provide additional tools (e.g. importation of NMR spectra, and matching experimental to simulated lineshapes) that would result in an application suitable for researchers as well as educators.

A secondary purpose of this project is to provide a test case for the author to learn how to properly test, package, and distribute software.