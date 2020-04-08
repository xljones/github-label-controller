# github-label-controller

This is based on the [github-label-maker](https://github.com/mloskot/github-label-maker)

Python module and script to manage GitHub labels the saner way:

## Requirements

* [PyGithub](https://github.com/PyGithub/PyGithub) 1.47

## Usage

Output of `python3 github-label-controller.py -h` should be self-explanatory.

```
usage: github-label-controller.py [-h] -r REPOS -l LABELS -t TOKEN [-e] [-v]

Make GitHub labels from definitions in labels/

optional arguments:
  -h, --help            show this help message and exit

required arguments:
  -r REPOS, --repos REPOS
                        GitHub repository scheme (.json)
  -l LABELS, --labels LABELS
                        GitHub label scheme (.json)
  -t TOKEN, --token TOKEN
                        GitHub personal access token

optional arguments:
  -e, --execute         Execute the changes. Without this only a dry-run
                        happens
  -v, --verbose         Turn on verbose logging
```
