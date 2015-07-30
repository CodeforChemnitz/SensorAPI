# Sensor Data API

[![Build Status](https://travis-ci.org/CodeforChemnitz/SensorAPI.svg?branch=master)](https://travis-ci.org/CodeforChemnitz/SensorAPI)

This is the first implementation of our API to accept sensor data from a
network of sensors via HTTP. Currently it uses SQLite to save the data
to `/tmp/sensor-data.db`.

## Requirements

    pip install -r requirements.txt

## Run

    python api.py

## Tests

To run the tests:

    pip install -r requirements-test.txt
    CI=true python api.py # this allows to use a predefined api key
    cd tests
    python run.py

## License

The MIT License (MIT)

Copyright (c) 2015 Morris Jobke

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
