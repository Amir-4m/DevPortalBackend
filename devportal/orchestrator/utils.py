import os

import pygit2
from github import Github


def get_local_dir():
    from .models import Settings
    local_dir = Settings.objects.get(key='local-dir')
    return local_dir.value


def _github_init(repo):
    access_token = repo.account.creds
    # using an access token
    g = Github(access_token)
    return g


def _github_get_org(g, repo):
    try:
        org = g.get_organization(repo.account.name)
    except Exception as e:
        # raise e
        org = g.get_user()
    return org


def github_create_repo(repo):
    g = _github_init(repo)
    org = _github_get_org(g, repo)
    try:
        remote_repo = org.create_repo(repo.name, private=True, auto_init=True)
    except Exception as e:
        print(e)
        raise e
    del g
    del org
    return remote_repo


def github_check_repo(repo):
    g = _github_init(repo)
    try:
        remote_repo = g.get_repo("{0}/{1}".format(repo.account.name, repo.name))
    except Exception as e:
        print(e)
        remote_repo = None
    del g
    return remote_repo


def github_clone(repo, repo_dir):
    try:
        # Delete before clone in case the folder is already there
        import shutil
        shutil.rmtree(repo_dir, ignore_errors=True)
        callbacks = pygit2.RemoteCallbacks(pygit2.UserPass('x-oauth-basic', repo.account.creds))
        pygit2.clone_repository(repo.url, repo_dir, callbacks=callbacks)
    except Exception as e:
        print(e)
        raise e


def git_pull(local_url, repo, remote_name='origin', branch='master'):
    print("Pulling git {0}".format(local_url))
    local_url = pygit2.Repository(pygit2.discover_repository(local_url))
    callbacks = pygit2.RemoteCallbacks(pygit2.UserPass('x-oauth-basic', repo.account.creds))
    for remote in local_url.remotes:
        if remote.name == remote_name:
            remote.fetch(callbacks=callbacks)
            try:
                remote_master_id = local_url.lookup_reference('refs/remotes/origin/%s' % (branch)).target
            except KeyError as e:
                if branch == 'master':
                    branch = 'main'
                    remote_master_id = local_url.lookup_reference('refs/remotes/origin/%s' % (branch)).target
                else:
                    raise e

            merge_result, _ = local_url.merge_analysis(remote_master_id)
            # Up to date, do nothing
            if merge_result & pygit2.GIT_MERGE_ANALYSIS_UP_TO_DATE:
                return
            # We can just fastforward
            elif merge_result & pygit2.GIT_MERGE_ANALYSIS_FASTFORWARD:
                local_url.checkout_tree(local_url.get(remote_master_id))
                try:
                    master_ref = local_url.lookup_reference('refs/heads/%s' % (branch))
                    master_ref.set_target(remote_master_id)
                except KeyError:
                    local_url.create_branch(branch, local_url.get(remote_master_id))
                local_url.head.set_target(remote_master_id)
            elif merge_result & pygit2.GIT_MERGE_ANALYSIS_NORMAL:
                local_url.merge(remote_master_id)

                if local_url.index.conflicts is not None:
                    for conflict in local_url.index.conflicts:
                        print('Conflicts found in:', conflict[0].path)
                    raise AssertionError('Conflicts, ahhhhh!!')

                user = local_url.default_signature
                tree = local_url.index.write_tree()
                commit = local_url.create_commit('HEAD',
                                                 user,
                                                 user,
                                                 'Merge!',
                                                 tree,
                                                 [local_url.head.target, remote_master_id])
                # We need to do this or git CLI will think we are still merging.
                local_url.state_cleanup()
            else:
                raise AssertionError('Unknown merge analysis result')


def git_commit(local_url, message):
    local_url = pygit2.Repository(pygit2.discover_repository(local_url))
    local_url.index.add_all()
    local_url.index.write()
    tree = local_url.index.write_tree()
    parent, ref = local_url.resolve_refish(refish=local_url.head.name)
    local_url.create_commit(
        ref.name,
        local_url.default_signature,
        local_url.default_signature,
        message,
        tree,
        [parent.oid],
    )
