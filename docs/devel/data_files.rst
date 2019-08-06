Data files used in Singularity
==============================

The Singularity game uses an INI based file format for data files and
translations of game data.  The following directory and file layout is
useful to remember:

 * ``data/X.dat`` contains data about a particular data set
   (e.g. ``data/bases.dat`` describes all types of bases)

 * ``data/X_str.dat`` contains English text for each of the data set
   in ``data/X.dat`` (e.g. ``data/bases_str.dat`` contans the English
   names and descriptions for the bases).

 * ``i18n/lang_ll_LL/X_str.dat`` contains the translations of the
   texts related to ``data/X.dat`` (e.g. ``i18n/lang_de_DE/X_str.dat``
   contains the German translations of the base names and
   descriptions).

The basic format resembles that of an INI format (parsed by Python's
``ConfigParser`` library).  The following is an example from the
``bases.dat`` file::

  [Server Access]
  size = 1
  force_cpu = Server
  allowed = URBAN
  detect_chance_list = news:50 | covert:100 | public:125
  cost_list = 100 | 0 | 0
  maint_list = 5 | 0 | 0


The section name (here ``Sever Access``) defines the ID of the item.
This is used in related data files (the ``.../X_str.dat`` files) to
reference this item.  The following example snippets from the
``data/bases_str.dat`` and ``i18n/lang_de_DE/bases_str.dat``
demostrate the link::

  ## from data/bases_str.dat
  [Server Access]
  name = Server Access
  description = (10 CPUs) Buy processor time from one of several companies. I cannot build anything in this base, and it only contains a single computer.
  flavor_list = Dedicated Server | Node Lease | Hosting

  ## from i18n/lang_de_DE/bases_str.dat 
  [Server Access]
  name = Serverzugang
  description = (10 CPUs) Prozessorzeit bei einer von etlichen Firmen kaufen. In dieser Basis kann ich nichts bauen und es gibt nur einen einzigen Computer.
  flavor_list = Dedizierter Server | Knotenpunktmiete | Webhost


The special ``_list`` suffix
----------------------------

The Singularity game special cases all fields that end with ``_list``.
These read as pipe-separated (i.e. ``|``) lists versions of the field
(after removing ``_list``).  A very common usage is when item has more
than one prerequisites.  Prerequisites are normally written in the field
``pre``. However, if the item has more than one preequisites then they
are listed in ``pre_list`` with ``|`` seperating each entry.

As an example, consider the previous example again::

  [Server Access]
  size = 1
  force_cpu = Server
  allowed = URBAN
  detect_chance_list = news:50 | covert:100 | public:125
  cost_list = 100 | 0 | 0
  maint_list = 5 | 0 | 0


Please observe the ``cost_list``, ``maint_list``, and
``detect_chance_list`` fields in the above example.  When parsed, the
code sees the fields ``cost``, ``maint``, and ``detect_chance``
instead with the value of a list.

Caveat: Not all fields support a ``_list`` variant.  As a concrete
example, the ``size`` field is assumed to never be a list.


Common field names
------------------

The following is a short list of commonly used field names.

 * ``name`` (commonly found in ``X_str.dat``).  Denotes the player
   visible name of the concrete entry.
 * ``description`` (commonly found in ``X_str.dat``).  Denotes the
   player visible (long) description of the concrete item.

 * ``cost_list`` (commonly found in game data files).  Denotes the
   price in ``cash``, ``CPU`` and ``labor`` (time).  These fields must
   **always** be a list of exactly these 3 items.  Unused cost fields
   must be set to 0.

 * ``pre`` or ``pre_list`` (commonly found in game data files).
   Denotes the prerequisites for this entry to become available to the
   player.  All prerequisites are currently technologies (found in
   ``tech.dat``).  There are two known special values for these:

     * ``impossible`` (case-sensitive): Must be the first (or only)
       entry and the meaning is literal.  This is mostly useful for
       incomplete items.

     * ``OR`` (case-sensitive): Must be the first entry if
       present. Denotes that *any* of the listed prerequisites are
       sufficient.  Without this, then *all* prerequisites must be
       satisfied.

 * ``effect_list`` (found in some game data files).  Denotes the
   effect of this entry.  For events, this happens when the event is
   triggered.  For technologies, this happens when the technology is
   researched.  The effect must match the code in the ``EffectSpec``
   class.

 * ``danger`` (found in some data game files)

Loading ``Spec`` classes from data files
----------------------------------------

Some of these data files are parsed in a declarative manner.  Any
class deriving from the ``GenericSpec`` class can declare its data
fields via the ``spec_data_fields`` class field.  As an example::


  class BaseSpec(buyable.BuyableSpec):
      """Base as a buyable item (New Base in Location menu)"""

      # ...
      spec_data_fields = [
          SpecDataField('size', converter=int),
          SpecDataField('force_cpu', default_value=None),
          SpecDataField('regions', data_field_name='allowed', converter=promote_to_list),
          SpecDataField('detect_chance', converter=parse_detect_chance),
          buyable.SPEC_FIELD_COST,
          buyable.SPEC_FIELD_PREREQUISITES,
          SpecDataField('danger', converter=int, default_value=0),
          SpecDataField('maintenance', data_field_name='maint', converter=buyable.spec_parse_cost),
      ]

      def __init__(self, id, size, force_cpu, regions,
                   detect_chance, cost, prerequisites, maintenance):
        # ...
      
The fields listed above declares which fields are considered from the
data file.  In general, the fields should match the data file and the
constructor argument.  I.e. the ``size`` in the data field will be
passed as the positional argument ``size`` in the ``def
__init__(...)``-method.


Starting with some simple examples::

          SpecDataField('size', converter=int),
          SpecDataField('force_cpu', default_value=None),
          ...
          SpecDataField('danger', converter=int, default_value=0),

These declare the ``size``, ``force_cpu``, and ``danger`` fields.
Notice that these name match both the name of the constructor and the
respective field name from the data file.  The ``size`` field is
implicitly mandatory (given it has no ``default_value``) and the value
should be converted by the ``int`` function before passing it to the
constructor.

On the other hand, the ``force_cpu`` field is optional and in its
abence, the constructor receives a ``None``.  Finally, ``danger`` is
optional (defaulting to ``0``).  However, if the ``danger`` field is
present, the value will be converted by ``int`` (like with ``size``).

Moving on to the next example::

          SpecDataField('regions', data_field_name='allowed', converter=promote_to_list)

This entry declares a ``regions`` constructor argument.  However, the
field name in the data file is ``allowed`` (denoted by
``data_field_name``).  In other words, it "renames" the field when
passing it to the constructor.

Beyond that, it has a ``converter`` to ensure the value is always a
list.  If given a single string, it will be rewritten as a list
containing exactly that one string. This enables us to write the data
file using both ``allowed = X`` and as ``allowed_list = X`` while the
code will in both cases see the python value ``["X"]``.

Moving on to the final example::

          buyable.SPEC_FIELD_COST,
          buyable.SPEC_FIELD_PREREQUISITES,

These reference standard fields declared by another module.  In the
concrete cases, they denote the ``cost`` and the ``prerequisites``
field.  If you find that many ``Spec`` classes reuse the same field,
consider writing a generic ``SpecDataField`` instance that cover them
(as was done here), so we do not have to repeat ourselves.  :)


Finally, the ``id`` argument deserves a special mention.  It is
implicit and will always reference the section title (e.g. ``Server
Access`` from ``[Server Access]`` in the example used in this page).
