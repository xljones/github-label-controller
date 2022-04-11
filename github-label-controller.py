#
# github-label-controller
#
# Xander Jones [2020]
# Bugsnag
#
# This is based on the github-label-maker (https://github.com/mloskot/github-label-maker)
#
import argparse
import json
import logging
import os
import sys
import glm
import github

_VERSION = "1.1.0"

'''
    Load the label scheme. This should be a JSON list of "owner" and
    "repository" bundled keys'. If the file does not exist, the script will exit.

    Arguments:
        args: the user provided arguments from the main thread
'''
def _load_labels_scheme(args):
    print("\r\n🏷️  LOADING LABELS SCHEME")
    if os.path.exists(args.labels):
        print("├── Using '{0}' label scheme".format(args.labels))
        with open(args.labels, 'r') as file:
            labels = json.load(file)
        print("└── {0} labels have been loaded".format(str(len(labels))))
        return labels
    else:
        print("└── File '{0}' does not exist".format(args.labels))
        exit(1)

'''
    Load the repository scheme. This should be a JSON list of "aliases" (list),
    "name", "description", and "color" bundled keys. If the file does not exist,
    the script will exit.

    Arguments:
        args: the user provided arguments from the main thread
'''
def _load_repos_scheme(args):
    print("\r\n🗄️  LOADING REPOS SCHEME")
    if os.path.exists(args.repos):
        print("├── Using '{0}' repository scheme".format(args.repos))
        with open(args.repos, 'r') as file:
            repositories = json.load(file)
        print("└── {0} repositories have been loaded".format(str(len(repositories))))
        return repositories
    else:
        print("└── File '{0}' does not exist".format(args.repos))
        exit(1)

'''
    A check to see if, for a given label 'repo_label', does it need to be edited
    to comply with the 'scheme_label'. This checks for the color and description
    only. Returns True if edit is required, returns False if not.

    Arguments:
        lm: the github label maker object
        repo_label: the label of the repository to be compared
        scheme_label: the label from the scheme to be compared.
'''
def _label_diff_check(lm, repo_label, scheme_label):
    edit_required = False
    if repo_label['description'] == scheme_label['description']:
        print("        ├── ⚪️ The description matches, no changes")
    else:
        edit_required = True
        print("        └── 🔵 The description does not match")
        print("            ├── Scheme description:  '{0}'".format(scheme_label['description']))
        print("            └── will overwrite:      '{0}'".format(repo_label['description']))
    if repo_label['color'] == scheme_label['color']:
        print("        └── ⚪️ The color matches ({0}), no changes".format(repo_label['color']))
    else:
        edit_required = True
        print("        └── 🔵 The color does not match.")
        print("            ├── Scheme color:    {0}".format(scheme_label['color']))
        print("            └── will overwrite:  {0}".format(repo_label['color']))
    if not repo_label['name'] == scheme_label['name']:
        edit_required = True
    return edit_required

'''
    Main called function which for a list of repositories, will scan through
    each checking the labels agains the label scheme to see what changes need
    to be made. If the -e (execute) option is enabled, the changes will be made
    for edits and addition of labels. If -e (execute) and -d (delete) options
    are enabled, additionally to editing and adding, labels not found in the
    scheme will be deleted from the repo; if and only if they are not linked to
    an open Issue or Pull Request.

    Arguments:
        auth: the GitHub authorization object produced using glm.GithubAuthenticator()
        repositories: a list of the repositories (loaded through the JSON scheme)
        scheme_labels: a list of the labels to apply (loaded through the JSON scheme)
        args: the user provided arguments from the main thread
'''
def _scan_repos(auth, repositories, scheme_labels, args):
    _count_correct = 0
    _count_missing_from_scheme = 0
    _count_missing_from_repo = 0
    _count_require_updates = 0
    for repo in repositories:
        for index, scheme_label in enumerate(scheme_labels):
            scheme_labels[index]['repo_match'] = False

        print("\r\nConnecting to repository '{0}' owned by '{1}'".format(repo['repository'], repo['owner']))
        lm = glm.GithubLabelMaker(auth, repo['owner'], repo['repository'], verbose=args.verbose)
        repo_labels = lm.get_labels()

        for repo_label in repo_labels:
            # print(">> SCANNING FOR REPO LABEL {0}".format(repo_label['name']))
            print("└── {0} (repo label)".format(repo_label['name']))
            label_scheme_found = None
            edit_required = False

            for index, scheme_label in enumerate(scheme_labels):
                if repo_label['name'] == scheme_label['name']:
                    print("    └── {0} (scheme label)".format(scheme_label['name']))
                    print("        ├── ⚪️ The name matches, no changes")
                    edit_required = _label_diff_check(lm, repo_label, scheme_label)
                    label_scheme_found = scheme_label
                    scheme_labels[index]['repo_match'] = True
                else:
                    for scheme_alias in scheme_label['aliases']:
                        if repo_label['name'] == scheme_alias:
                            print("    └── {0} (alias of '{1}' scheme label)".format(scheme_alias, scheme_label['name']))
                            print("        └── 🔵 The name doesn't match")
                            print("            ├── Scheme name:     '{0}'".format(scheme_label['name']))
                            print("            └── will overwrite:  '{0}'".format(repo_label['name']))
                            edit_required = _label_diff_check(lm, repo_label, scheme_label)
                            label_scheme_found = scheme_label
                            scheme_labels[index]['repo_match'] = True
                            break
            if label_scheme_found == None:
                _count_missing_from_scheme += 1
                print("    └── 🔴 No scheme label or alias was found for this repo label, it will be deleted")
                if (args.execute and args.delete):
                    linked_issues = lm.get_issues(repo_label).totalCount
                    if linked_issues == 0:
                        try:
                            lm.delete_label(repo_label['name'])
                        except Exception as e:
                            print("    └── ⚠️  Error deleting label: {0} [status code: {1}]".format(e.data, e.status))
                        else:
                            print("    └── ✅ Success: this label has been deleted")
                    else:
                        print("    └── ⚠️  Label not deleted, there are {0} open issues or PRs".format(linked_issues))
            elif label_scheme_found and edit_required:
                _count_require_updates += 1
                if args.execute:
                    try:
                        lm.edit_label(label_scheme_found, repo_label['name'])
                    except Exception as e:
                        print("    └── ⚠️  Error updating label: {0} [status code: {1}]".format(e.data, e.status))
                    else:
                        print("    └── ✅ Success: this label has been updated")
            else:
                _count_correct += 1

        for scheme_label in scheme_labels:
            if not scheme_label['repo_match']:
                _count_missing_from_repo += 1
                print("└── {0}".format(scheme_label['name']))
                print("    └── 🔵 This label was found in scheme, but not in repo, it will be created with".format(scheme_label['name']))
                print("        ├── color:        '{0}'".format(scheme_label['color']))
                print("        └── description:  '{0}'".format(scheme_label['description']))
                if args.execute:
                    try:
                        lm.add_label(scheme_label)
                    except Exception as e:
                        print("    └── ❌ Error adding label: {0} [status code: {1}]".format(e.data, e.status))
                    else:
                        print("    └── ✅ Success: this label has been added")

    if not args.execute:
        print("\r\n🌐 ACROSS ALL REPOS: ")
        print("├── ⚪️ Labels correct:      {0} (no changes)".format(_count_correct))
        print("├── 🔴 Missing from scheme: {0} (will be deleted, if not linked issues with -e/--execute AND -d/--delete options)".format(_count_missing_from_scheme))
        print("├── 🔵 Missing from repo:   {0} (will be added with -e/--execute option)".format(_count_missing_from_repo))
        print("└── 🔵 Needing updates:     {0} (will be updated with -e/--execute option)".format(_count_require_updates))

'''
    Entry point to script. This is not designed to be imported into another
    script. Alert the user if this happens.
'''
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Make GitHub labels from definitions in labels/')
    required_args = parser.add_argument_group('required arguments')
    required_args.add_argument('-t', '--token', help='GitHub personal access token. Generated here: https://github.com/settings/tokens', required=True)
    optional_args = parser.add_argument_group('optional arguments')
    optional_args.add_argument('-r', '--repos', help='GitHub repository scheme. A JSON list of "owner" and "repository" bundled keys', default="schemes/repos/bugsnag.json")
    optional_args.add_argument('-l', '--labels', help='GitHub label scheme. A JSON list of "aliases" (list), "name", "description", and "color" bundled keys', default="schemes/labels/bugsnag.json")
    optional_args.add_argument('-e', '--execute', help='Execute the changes (adding new labels and editing labels only). Without this only a dry-run happens', action='store_true')
    optional_args.add_argument('-d', '--delete', help='Deletes any repo label that is not associated with the scheme, and has not associated open issues or PRs. This needs to be used in conjunction with -e/--execute', action='store_true')
    optional_args.add_argument('-v', '--verbose', help='Turn on verbose logging', action='store_true')
    args = parser.parse_args()

    print("\r\n>> github-label-controller.py —— Xander Jones —— v" + _VERSION)

    if args.verbose:
        glm.set_verbose_logging()

    labels = _load_labels_scheme(args)
    repositories = _load_repos_scheme(args)

    print("\r\n🌐 CONNECTING TO GITHUB")
    gh = glm.GithubAuthenticator(args.token)

    if gh.is_authenticated():
        print("├── Authorized to GitHub as user '{0}'".format(gh.get_username()))
        print("└── Rate limit: {0}, remaining: {1}".format(gh.get_rate_limit().core.limit, gh.get_rate_limit().core.remaining))
        if args.execute:
            approve = input("🔒  You've enabled --execute. This will update and add new labels. Are you sure? [Y/n]: ")
            if not approve.lower() == "y":
                print(">> User did not authorize changes")
                exit(1)
        if args.delete:
            approve = input("🔒  You've enabled --delete. This will delete labels that do not match the scheme and have no associated open issues/PRs. Are you sure? [Y/n]: ")
            if not approve.lower() == "y":
                print(">> User did not authorize changes")
                exit(1)
        _scan_repos(gh.get_auth(), repositories, labels, args)

    else:
        print("└── Unable to authenticate with GitHub - script exiting")
        exit(1)
else:
    print("Error: This script should be invoked directly")
