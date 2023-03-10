Usage
=====

Three fundamental abstract classes are used here: ``Test``, which
focuses on testing specific conditions given an input data,
``DataValidator``, which focuses on validating a specific type of data,
and ``DataModel`` which focuses on validating a sample (composed by
multiple types of data).

``Check``
~~~~~~~~~

A ``Check`` is a generic class that can be used as the base for data
checks. These data checks, after being defined
(``check = Check(target="hello")``), can then be called with a given
input argument (``check("hello)``) and the output (``True``) tells us
whether the check has passed (``True`` if the check has passed,
``False`` otherwise).

The check above considers only simple comparison - this is hardly useful
when we want to perform more complicated comparisons. For example, we
may want to know if our data is within a given range. To do this, we can
define novel dataclasses from ``Test`` that perform *exactly* these
comparisons, by redefining the ``unpack`` and ``compare`` methods:

.. code:: python

   from imdm import Test

   @dataclass
   class CheckRange(Test):
       target: Tuple[Union[int,float],Union[int,float]]
       
       def __post_init__(self):
           name = self.get_name()
           self._success_msg = f"Target shape {name} contains input values"
           self._fail_msg = f"Target shape {name} does not contain input values"

       def unpack(self, x: Any) -> Any:
           return np.min(x),np.max(x)

       def compare(self, unpacked_x: Any) -> bool:
           within_range = True
           if self.target[0] is not None:
               if unpacked_x[0] < self.target[0]:
                   within_range = False
           if self.target[1] is not None:
               if unpacked_x[1] > self.target[1]:
                   within_range = False
           return within_range

By redefining our ``unpack`` and ``compare`` methods, we can ensure that
the correct checks are performed. These methods are then executed in the
``__call__`` method of the ``Test`` abstract class:

.. code:: python

       def __call__(self, x: Any) -> bool:
           """Performs the comparison using the input data and defines the 
           ``self.msg``.

           Args:
               x (Any): input data.

           Returns:
               bool: whether the comparison was successful or not.
           """
           if self.target is None:
               return self.target
           unpacked_x = self.unpack(x)
           result = self.compare(unpacked_x)
           if result == True:
               self.msg = self._success_msg
           if result == False:
               self.msg = self._fail_msg
           return result

A ``msg`` attribute is defined with either ``_success_msg`` or
``_fail_msg``, depending on whether the result is ``True`` or ``False``.
This is helpful in case verbosity is important for your applications.

``DataValidators``
~~~~~~~~~~~~~~~~~~

Defining ``DataValidators`` is relatively easy:

.. code:: python

   from mridm import DataValidator

   data_validator = DataValidator(type=str,length=11,shape=None,range=None)

and running data validations is just as easy:

.. code:: python

   output = data_validator.validate("test_string")

   print(output)

   >>> {"type":True,"length":True,"shape":None,"range":None}

The ``DataValidator`` method automatically checks for ``type``,
``length``, ``shape`` and ``range`` (if specified). If necessary, users
can also add their own methods. For example, if you would to check
whether a given path exists:

.. code:: python

   import os

   data_validator.add_test(key="path",test_fn=os.path.exists,data_stage="raw")

   output = data_validator.validate("test_string")

   print(output)

   >>> {"type":True,"length":True,"shape":None,"range":None,"path":False}

Easy! All arguments are relatively clear, but ``data_stage`` is somewhat
more ellusive; for this reason we introduce here the concept of three
data stages:

-  ``raw`` - the input exactly as it is. This is useful to test whether
   a file exists.
-  ``preprocessed_data`` - if a ``preprocess_fn`` is specified in the
   ``DataValidator`` constructor, tests can be applied to these
   functions. For instance, the ``type`` check is automatically ran on
   the ``preprocessed_data`` stage.
-  ``value_data`` - some files (SITK-readable files, for instance)
   require some non-obvious wrangling before one can actually use their
   values as ``numpy`` arrays, which is the assumed format for checking
   the ``range``. This function (``value_fn``) is applied to the output
   of ``preprocess_fn``.

If no ``preprocess_fn`` or ``value_fn`` are supplied, then
``preprocessed_data`` and ``value_fn`` will be identical to the input
data.

``DataModel``
~~~~~~~~~~~~~

A ``DataModel`` is simply a structure of ``DataValidators``, i.e.

.. code:: python

   from mridm import DataValidator,DataModel

   data_model = DataModel(structures={
       "a":DataValidator(type=str,length=11,shape=None,range=None),
       "b":DataValidator(type=int,length=None,shape=None,range=[-10,10])
       })

This ``data_model`` can then be applied to any given data input that
follows a structure similar to ``data_model.structures``.

MRI- and image-specific data validators
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

An easy-to-use data validators have been implemented specifically for
image data (``ImageFile``). We work with images, so these were especially
useful for me.

Additionally, since we work with a lot of MRI data, specific methods for
MRI data were also implemented (``DicomFile`` and ``SitkFile``). A more
generic method for ``numpy`` files has also been (``NumpyFile``).

``pprint``
~~~~~~~~~~

``pprint`` is a simple function that allows you to more easily inspect
the output of ``DataValidator`` and ``DataModel``. It comes with
colours!