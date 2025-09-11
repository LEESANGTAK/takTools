# Description

This example is meant to illustrate how associative operators work, how to implement them, and how to annotate them.

Three operators are implemented in this example:

* `group()`: a binary operator that takes two input strings and concatenates them with parentheses and a '+' symbol to produce an output. `(<input1>+<input2>)`
* `group_associative_LeftToRight()`: an associative operator that takes two input strings and concatenates them with parentheses and a '+' symbol to produce an output. Because this operator is associative, it will be instantiated with only one dynamic input port. An additional port is added as soon as a connection is made to an existing port. The associative operation is `LeftToRight`, meaning that its inputs will be grouped starting at the first input. `(((<input1>+<input2>)+<input3>)+<input4>))`
* `group_associative_RightToLeft()`: an associative operator that takes two input strings and concatenates them with parentheses and a '+' symbol to produce an output. Because this operator is associative, it will be instantiated with only one dynamic input port. An additional port is added as soon as a connection is made to an existing port. The associative operation is `RightToLeft`, meaning that its inputs will be grouped starting at the last connected input. `(<input1>+(<input2>+(<input3>+<input4>)))`

See the [Bifrost Developer Help for information on associative operators](https://help.autodesk.com/view/BIFROST/ENU/?guid=Bifrost_DevHelp_AssociativeOperators_html).

# Building the example with CMake
Directions on how to build this example can be found in the [sdk/examples/README.md file](../README.md) of your Bifrost installation.
