# GitHub Repo Sync

Synchronize GitHub repositories from a set scheme accross an organization. This is based on the [github-label-maker](https://github.com/mloskot/github-label-maker)

## [Requirements](./requirements.txt)

* Python 3
* [PyGithub](https://github.com/PyGithub/PyGithub) v1.47

## Installation

Clone this repository with

```sh
git clone https://github.com/xljones/github-repo-sync.git
```

Then, install the requirements with

```sh
cd github-repo-sync && python -m pip install -r requirements.txt
```

## Usage

```
usage: python -m github_repo_sync [-h] -t TOKEN [-r REPOS] [-l LABELS] [-e]
                                  [-d] [-v]



optional arguments:
  -h, --help            show this help message and exit

required arguments:
  -t TOKEN, --token TOKEN
                        GitHub personal access token. Generated here:
                        https://github.com/settings/tokens

optional arguments:
  -r REPOS, --repos REPOS
                        GitHub repository scheme. A JSON list of "owner" and
                        "repository" bundled keys
  -l LABELS, --labels LABELS
                        GitHub label scheme. A JSON list of "aliases" (list),
                        "name", "description", and "color" bundled keys
  -e, --execute         Execute the changes (adding new labels and editing
                        labels only). Without this only a dry-run happens
  -d, --delete          Deletes any repo label that is not associated with the
                        scheme, and has not associated open issues or PRs.
                        This needs to be used in conjunction with -e/--execute
  -v, --verbose         Turn on verbose logging
```

* The default repository scheme is located in `schemes/repos/default.json`, but you can force a different repo scheme with the `-r` flag.
* The default labelling scheme is located in `schemes/labels/default.json`, but you can force a different label scheme with the `-l` flag.

### Examples

To view the outputs that would be made in a dry-run, using the default schemes.

```sh
python -m github_repo_sync -t TOKEN
```

To execute the changes (addition of labels, editing of labels, but *not* deletion of labels)

```sh
python -m github_repo_sync -t TOKEN -e
```

To execute the changes, as above, but including deletion of labels

```
python -m github_repo_sync -t TOKEN -e -d
```

## Troubleshooting

* If you see `⚠️  Error [updating|deleting|adding] label: {'message': 'Not Found', 'documentation_url': 'https://developer.github.com/v3/issues/labels/#update-a-label'} [status code: 404]`, it's likely that your authentication token has permission to view the repository and labels, but not to update, add, or delete them.

* If you see `ModuleNotFoundError: No module named 'github'`, make sure you've installed the requirements prior to running this script. See [Requirements](#Requirements).