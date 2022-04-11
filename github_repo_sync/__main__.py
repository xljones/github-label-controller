import argparse
import logging

from github_repo_sync.github.authenticator import GithubAuthenticator

import github_repo_sync.github.label.lib as lib
import github_repo_sync.const as const

parser = argparse.ArgumentParser(description='Synchronize GitHub repositories from a set scheme accross an organization')
required_args = parser.add_argument_group('required arguments')
required_args.add_argument('-t', '--token', help='GitHub personal access token. Generated here: https://github.com/settings/tokens', required=True)
optional_args = parser.add_argument_group('optional arguments')
optional_args.add_argument('-r', '--repos', help='GitHub repository scheme. A JSON list of "owner" and "repository" bundled keys', default="schemes/repos/default.json")
optional_args.add_argument('-l', '--labels', help='GitHub label scheme. A JSON list of "aliases" (list), "name", "description", and "color" bundled keys', default="schemes/labels/default.json")
optional_args.add_argument('-e', '--execute', help='Execute the changes (adding new labels and editing labels only). Without this only a dry-run happens', action='store_true')
optional_args.add_argument('-d', '--delete', help='Deletes any repo label that is not associated with the scheme, and has not associated open issues or PRs. This needs to be used in conjunction with -e/--execute', action='store_true')
optional_args.add_argument('-v', '--verbose', help='Turn on verbose logging', action='store_true')
args = parser.parse_args()

print("\r\n>> GitHub Repo Sync —— Xander Jones —— v" + const.VERSION)

if args.verbose:
    logging.basicConfig(level=logging.INFO)

labels = lib.load_labels_scheme(args)
repositories = lib.load_repos_scheme(args)

print("\r\n🌐 CONNECTING TO GITHUB")
gh = GithubAuthenticator(args.token)

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
    lib.scan_repos(gh.get_auth(), repositories, labels, args)

else:
    print("└── Unable to authenticate with GitHub - exiting")
    exit(1)