# Very Large Scale Integration
*Solutions using Constraint Programming, SAT and SMT solvers*

## Installation
Install the requirements using
```
pip install -r requirements.txt
```

Note that in order to use CP model Minizinc need to be installed on the machine while for SAT and SMT Z3-solver need to be installed.

## Usage
### CP
Usage:

```
usage: python cp.py [-h] --models [MODELS ...] --instances [INSTANCES ...] [--csv CSV] [--output OUTPUT] [--plot] [--solver {chuffed,gecode}] [--free-search] [--timeout TIMEOUT]

Run minizinc vlsi solving method

optional arguments:
  -h, --help            show this help message and exit
  --models [MODELS ...], -m [MODELS ...]
                        Model(s) to use. Leave empty to use all.
  --instances [INSTANCES ...], -i [INSTANCES ...]
                        Instances(s) to load. Leave empty to use all.
  --csv CSV, -csv CSV   Save csv files in specified directory.
  --output OUTPUT, -o OUTPUT
                        Save results files in specified directory.
  --plot, -p            Plot final result. Defaults to false.
  --solver {chuffed,gecode}, -solver {chuffed,gecode}, -s {chuffed,gecode}
                        Solver that Minizinc will use. Defaults to Chuffed.
  --free-search, -f     Perform free search. Defaults to false.
  --timeout TIMEOUT, -timeout TIMEOUT, -t TIMEOUT
                        Execution time contraint in seconds. Defaults to 300s (5m).
```

### SAT
Usage:

```
usage: python sat.py [-h] --models [MODELS ...] --instances [INSTANCES ...] [--csv CSV] [--plot] [--output OUTPUT] [--timeout TIMEOUT]

Run minizinc vlsi solving method

optional arguments:
  -h, --help            show this help message and exit
  --models [MODELS ...], -m [MODELS ...]
                        Model(s) to use. Leave empty to use all.
  --instances [INSTANCES ...], -i [INSTANCES ...]
                        Instances(s) to load. Leave empty to use all.
  --csv CSV, -csv CSV   Save csv files in specified directory.
  --plot, -p            Plot final result. Defaults to false.
  --output OUTPUT, -o OUTPUT
                        Save results files in specified directory.
  --timeout TIMEOUT, -timeout TIMEOUT, -t TIMEOUT
                        Execution time contraint in seconds. Defaults to 300s (5m).
```

### SMT
Usage:

```
usage: python smt.py [-h] --models [MODELS ...] --instances [INSTANCES ...] [--csv CSV] [--plot] [--output OUTPUT] [--timeout TIMEOUT]

Run minizinc vlsi solving method

optional arguments:
  -h, --help            show this help message and exit
  --models [MODELS ...], -m [MODELS ...]
                        Model(s) to use. Leave empty to use all.
  --instances [INSTANCES ...], -i [INSTANCES ...]
                        Instances(s) to load. Leave empty to use all.
  --csv CSV, -csv CSV   Save csv files in specified directory.
  --plot, -p            Plot final result. Defaults to false.
  --output OUTPUT, -o OUTPUT
                        Save results files in specified directory.
  --timeout TIMEOUT, -timeout TIMEOUT, -t TIMEOUT
                        Execution time contraint in seconds. Defaults to 300s (5m).
```