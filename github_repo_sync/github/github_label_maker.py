import github
import logging

class GithubLabelMaker:
    def __init__(self, g, github_owner_name, github_repo_name, verbose=False):
        assert isinstance(github_owner_name, str)
        assert isinstance(github_repo_name, str)

        # Repository either owned by user or one of user's organization
        orgs = [org.login for org in g.get_user().get_orgs()]
        if github_owner_name in orgs:
            owner = g.get_organization(github_owner_name)
        else:
            owner = g.get_user()
        self._repo = owner.get_repo(github_repo_name)
        #logging.info("connected to repository '{0}/{1}'".format(owner.login, self._repo.name))

    def _find_label(self, name):
        try:
            if name is None:
                name = ''
            return self._repo.get_label(name)
        except github.UnknownObjectException as e:
            logging.info(e)
            return None

    def _get_labels_def(self, labels_from):
        assert labels_from
        if isinstance(labels_from, dict):
            labels_def = [labels_from]
        else:
            labels_def = labels_from
        assert isinstance(labels_from, list)
        assert isinstance(labels_from[0], dict)
        return labels_def

    def _get_label_properties(self, label_def):
        assert isinstance(label_def, dict)
        assert 'name' in label_def
        assert 'color' in label_def
        name = label_def['name']
        color = label_def['color']
        if color.startswith('#'):
            color = color[1:]
        description = github.GithubObject.NotSet
        if 'description' in label_def:
            description = label_def['description']
        return name, color, description

    def add_label(self, label_def):
        name, color, description, *_ = self._get_label_properties(label_def)
        self._repo.create_label(name, color, description)

    def delete_label(self, label_def_or_name):
        if isinstance(label_def_or_name, str):
            name = label_def_or_name
        else:
            name, *_ = self._get_label_properties(label_def_or_name)
        label = self._find_label(name)
        if label:
            label.delete()
            return True
        else:
            return False

    def edit_label(self, label_def, old_name):
        name, color, description = self._get_label_properties(label_def)
        label = self._find_label(old_name)
        if label:
            label.edit(name, color, description)
            return True
        else:
            return False

    def get_label(self, name):
        label = self._find_label(name)
        if not label:
            logging.info("label '{0}' not found".format(name))
        label_def = { "name" : label.name, "color": "#{0}".format(label.color) }
        if label.description is not github.GithubObject.NotSet:
            label_def['description'] = label.description
        return label_def

    def get_labels(self):
        labels_def = []
        repo_labels = self._repo.get_labels()
        for label in repo_labels:
            label_def = { "name" : label.name, "color": "#{0}".format(label.color) }
            if label.description is not github.GithubObject.NotSet:
                label_def['description'] = label.description
            labels_def.append(label_def)
        return labels_def

    def get_issues(self, label):
        lbl = self._repo.get_label(label["name"])   # this could be made more efficient if we build the label type manually.
        issues = self._repo.get_issues(state='open',sort='created',direction='asc',labels=[lbl])
        return issues