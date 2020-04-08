# github-label-controller.py - sane labels for GitHub made easy
#
# Written by Mateusz Loskot <mateusz at loskot dot net>
# Updated by Xander Jones to enable aliases, and multiple repository configuration
#
# This is free and unencumbered software released into the public domain.
#
import argparse
import json
import logging
import os
import sys
import glm
import github

_VERSION = "1.0.0"

def _check_labels_match(lm, repo_label, local_label, old_name):
    edit_required = False
    if repo_label['description'] == local_label['description']:
        print("        ├── ✅ The description matches, no changes")
    else:
        edit_required = True
        print("        └── ❌ The description does not match")
        print("            ├── Scheme description:  '{0}'".format(local_label['description']))
        print("            └── will overwrite:      '{0}'".format(repo_label['description']))
    if repo_label['color'] == local_label['color']:
        print("        └── ✅ The color matches ({0}), no changes".format(repo_label['color']))
    else:
        edit_required = True
        print("        └── ❌ The color does not match.")
        print("            ├── Scheme color:    {0}".format(local_label['color']))
        print("            └── will overwrite:  {0}".format(repo_label['color']))
    if not repo_label['name'] == local_label['name']:
        edit_required = True
    return edit_required

def _scan_repos(auth, repositories, local_labels, execute):
    _count_correct = 0
    _count_missing_from_scheme = 0
    _count_missing_from_repo = 0
    _count_require_updates = 0
    for repo in repositories:
        for index, local_label in enumerate(local_labels):
            local_labels[index]['repo_match'] = False

        print("\r\nConnecting to repository '{0}' owned by '{1}'".format(repo['repository'], repo['owner']))
        lm = glm.GithubLabelMaker(auth, repo['owner'], repo['repository'], verbose=args.verbose)
        repo_labels = lm.get_labels()

        for repo_label in repo_labels:
            # print(">> SCANNING FOR REPO LABEL {0}".format(repo_label['name']))
            print("└── {0} (repo label)".format(repo_label['name']))
            label_scheme_found = None
            edit_required = False

            for index, local_label in enumerate(local_labels):
                if repo_label['name'] == local_label['name']:
                    print("    └── {0} (local label)".format(local_label['name']))
                    print("        ├── ✅ The name matches, no changes")
                    edit_required = _check_labels_match(lm, repo_label, local_label, None)
                    label_scheme_found = local_label
                    local_labels[index]['repo_match'] = True
                else:
                    for local_alias in local_label['aliases']:
                        if repo_label['name'] == local_alias:
                            print("    └── {0} (alias of '{1}')".format(local_alias, local_label['name']))
                            print("        └── ❌ The name doesn't match")
                            print("            ├── Scheme name:     '{0}'".format(local_label['name']))
                            print("            └── will overwrite:  '{0}'".format(repo_label['name']))
                            edit_required = _check_labels_match(lm, repo_label, local_label, repo_label['name'])
                            label_scheme_found = local_label
                            local_labels[index]['repo_match'] = True
                            break
            if label_scheme_found == None:
                _count_missing_from_scheme += 1
                print("    └── ⚠️  No local label or alias was found for this repo label")
            elif label_scheme_found and edit_required:
                _count_require_updates += 1
                if execute:
                    lm.edit_label(label_scheme_found, repo_label['name'])
            else:
                _count_correct += 1

        for local_label in local_labels:
            if not local_label['repo_match']:
                _count_missing_from_repo += 1
                print("└── {0}".format(local_label['name']))
                print("    └── ❌ This label was found in scheme, but not in repo, it will be created with".format(local_label['name']))
                print("        ├── color:        '{0}'".format(local_label['color']))
                print("        └── description:  '{0}'".format(local_label['description']))
                if execute:
                    lm.add_label(local_label)
    if not execute:
        print("\r\nACCROSS ALL REPOS: ")
        print(">> ✅ Labels correct:      {0} (no changes)".format(_count_correct))
        print(">> ⚠️  Missing from scheme: {0} (will be ignored)".format(_count_missing_from_scheme))
        print(">> ❌ Missing from repo:   {0} (will be added with -e/--execute option)".format(_count_missing_from_repo))
        print(">> ❌ Needing updates:     {0} (will be updated with -e/--execute option)".format(_count_require_updates))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Make GitHub labels from definitions in labels/')
    required_args = parser.add_argument_group('required arguments')
    required_args.add_argument('-r', '--repos', help='GitHub repository scheme (.json)', required=True)
    required_args.add_argument('-l', '--labels', help='GitHub label scheme (.json)', required=True)
    required_args.add_argument('-t', '--token', help='GitHub personal access token', required=True)
    optional_args = parser.add_argument_group('optional arguments')
    optional_args.add_argument('-e', '--execute', help='Execute the changes. Without this only a dry-run happens', action='store_true')
    optional_args.add_argument('-v', '--verbose', help='Turn on verbose logging', action='store_true')
    args = parser.parse_args()

    print("\r\n>> github-label-maker.py —— Xander Jones —— v" + _VERSION)

    if args.verbose:
        glm.set_verbose_logging()

    repositories = []
    labels = []

    print("\r\nLOADING LABELS SCHEME")
    if os.path.exists(args.labels):
        print(">> Using '{0}' label scheme".format(args.labels))
        with open(args.labels, 'r') as file:
            labels = json.load(file)
        print(">> {0} labels have been loaded".format(str(len(labels))))
    else:
        logging.error("File '{0}' does not exist".format(args.labels))
        exit(1)

    print("\r\nLOADING REPOS SCHEME")
    if os.path.exists(args.repos):
        print(">> Using '{0}' repository scheme".format(args.repos))
        with open(args.repos, 'r') as file:
            repositories = json.load(file)
        print(">> {0} repositories have been loaded".format(str(len(repositories))))
    else:
        logging.error("File '" + args.repos + "' does not exist")
        exit(1)

    print("\r\nCONNECTING TO GITHUB")
    gh = glm.GithubAuthenticator(args.token)
    if gh.is_authenticated():
        print(">> Authorized to GitHub as user '{0}'".format(gh.get_username()))
        print(">> Rate limit: {0}, remaining: {1}".format(gh.get_rate_limit().core.limit, gh.get_rate_limit().core.remaining))
        if (args.execute):
            approve = input("You've enabled --execute for this. Are you sure you want to make changes? [Y/n]: ")
            if (approve.lower() == "y"):
                _scan_repos(gh.get_auth(), repositories, labels, args.execute)
            else:
                print(">> User did not authorize changes")
                exit(1)
        else:
            _scan_repos(gh.get_auth(), repositories, labels, args.execute)
    else:
        print("\r\n>> Unable to authenticate with GitHub - script exiting")
        exit(1)
