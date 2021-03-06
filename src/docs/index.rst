.. MEANS documentation master file, created by
   sphinx-quickstart on Fri Dec 11 13:57:44 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

MEANS
===================================================================================

MEANS is python package for Moment Expansion Approximation, iNference and Simulation.

We present a free, user-friendly tool implementing an efficient `moment expansion approximation with parametric closures`_ that integrates well with the IPython interactive environment. Our package enables the analysis of complex stochastic systems without any constraints on the number of species and moments studied and the type of rate laws in the system. In addition to the approximation method our package provides numerous tools to help non-expert users in stochastic analysis.

.. _`moment expansion approximation with parametric closures`: http://scitation.aip.org/content/aip/journal/jcp/138/17/10.1063/1.4802475

Installation
-----------------

Please follow detailed instructions in Github_.

.. _Github: https://github.com/theosysbio/means

Tutorial
===============

An interactive tutorial on getting started with MEANS can be found on `our Github page`_.
We recommend trying it out directly using Jupyter_ interactive environment.

.. _`our Github page`: https://github.com/theosysbio/means/tree/master/tutorial/README.md
.. _Jupyter: http://jupyter.org/

API Reference
==================

.. toctree::

    means.approximation
    means.core
    means.examples
    means.inference
    means.io
    means.simulation
    means.util

