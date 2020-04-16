# github-label-controller

This is based on the [github-label-maker](https://github.com/mloskot/github-label-maker)

Python module and script to manage GitHub labels.

## Requirements

* [PyGithub](https://github.com/PyGithub/PyGithub) 1.47

## Usage

Output of `python3 github-label-controller.py -h`:

```
usage: github-label-controller.py [-h] -r REPOS -l LABELS -t TOKEN [-e] [-d]
                                  [-v]

Make GitHub labels from definitions in labels/

optional arguments:
  -h, --help            show this help message and exit

required arguments:
  -r REPOS, --repos REPOS
                        GitHub repository scheme. A JSON list of "owner" and
                        "repository" bundled keys
  -l LABELS, --labels LABELS
                        GitHub label scheme. A JSON list of "aliases" (list),
                        "name", "description", and "color" bundled keys
  -t TOKEN, --token TOKEN
                        GitHub personal access token. Generated here:
                        https://github.com/settings/tokens

optional arguments:
  -e, --execute         Execute the changes. Without this only a dry-run
                        happens
  -d, --delete          Deletes any repo that is not associated with the
                        scheme, and has not associated open issues or PRs
  -v, --verbose         Turn on verbose logging
```
