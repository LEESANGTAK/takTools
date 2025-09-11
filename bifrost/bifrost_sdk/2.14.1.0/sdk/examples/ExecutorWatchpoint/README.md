# ExecutorWatchpoint example

This example is a command line application that shows how to create watchpoint for a custom type (C++ user type).

It uses the Amino cpp2json tool (See [CMakeLists.txt](src/CMakeLists.txt))
to process a c++ file ([PeriodicTableElement.h](src/PeriodicTableElement.h)) which contains
a user type ([PeriodicTableElement]) to generate a json file
which will be loaded in bifrost. The generated json file contains the translated c++ type.

This example use the user defined watchpoint library ([PeriodicTableElementWatchpoint](src/PeriodicTableElementWatchpoint.cpp)) to
extract data from PeriodicTableElement object instances.
