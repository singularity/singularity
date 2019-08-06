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

