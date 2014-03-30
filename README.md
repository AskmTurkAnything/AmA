# Ask mTurk Anything

*Michael Kosler, Nishaanth Narayanan*

## Dependencies

* [boto](http://boto.readthedocs.org/en/latest/)

## Credentials

Your AWS credentials must be located in a `~/.boto` file. You can find more about how to do this in the [getting started tutorial](http://boto.readthedocs.org/en/latest/getting_started.html)

## Instructions

To submit a file for study question generation:

    python ama_cli.py filename [-h] [-a number of assignments per chunk] [-c cost per chunk] [-t tags]

To receive verified study questions for your file:

    python receiver.py number_of_assignments

## Output

The output of the receiver is a text file title today's date, with each returned chunk appending its results to that file.
