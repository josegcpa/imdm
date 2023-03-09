.. imdm documentation master file, created by
   sphinx-quickstart on Wed Mar  8 21:57:35 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

``imdm`` - Python data models for images (and other stuff!)
===========================================================

.. toctree::
   :maxdepth: 2

   install
   usage
   unit_tests
   modules

What's the point
----------------

This module contains a few helpful and flexible data models which can be
easily extended for other applications. Here, I focused on making some
(very) specific validators focusing on MRI data. These can be used to
test DICOM files, SITK-readable images or numpy-loadable arrays. Other 
image formats (PNG, JPEG, GIF, etc.) are also supported through PIL. This
package is supposed to help researchers and developers quickly test 
whether or not a given object or file is compatible with their pipeline.

We are, at the moment, not planning on including any more checks, placing
the "burden" of developing novel validators and models on users who like
our flexible ``Test``, ``DataValidator`` and ``DataModel`` classes.
