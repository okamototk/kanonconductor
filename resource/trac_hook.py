# -*- coding:utf8 -*-

import os, re
from bzrlib import branch
from bzrlib.remote import RemoteBranch
from bzrlib.config import BranchConfig, LocationConfig, GlobalConfig
from bzrlib.transport.pathfilter import PathFilteringTransport
from bzrlib.transport.chroot import ChrootTransport

from bzrlib.lazy_import import lazy_import
from trac.util.datefmt import utc
lazy_import(globals(), '''
import datetime
from bzrlib import urlutils
from trac.env import open_environment
from trac.versioncontrol import IRepositoryChangeListener, RepositoryManager, Changeset
from trac.core import ExtensionPoint
''')

def get_branch_url(branch):
    """Get real path of chrooted branch."""
    tran = branch._transport
    if isinstance(tran, (ChrootTransport, PathFilteringTransport)):
        root = tran.external_url()
        relpath = tran.base_path
        url = root + relpath[1:-1*len("/.bzr/branch/")]
    else:
        url = branch.user_transport.abspath('')
    if not url.endswith('/'):
        url += '/'
    return url

    
"""
monkey patch to use locations.conf server side
see https://bugs.launchpad.net/bzr/+bug/302593
"""
if not hasattr(BranchConfig, "_get_location_config_org"):
    BranchConfig._get_location_config_org = BranchConfig._get_location_config
    def get_location_config(self):
        if self._location_config is not None:
            return self._location_config
        if isinstance(self.branch._transport, (ChrootTransport, PathFilteringTransport)):
            self._location_config = LocationConfig(get_branch_url(self.branch))
            return self._location_config
        else:
            return self._get_location_config_org()

    BranchConfig._get_location_config = get_location_config

mail_re = re.compile(u'<([^@]+)@[^@]+>')
def create_dummy_changeset(repos, revstr, revision):            
    author = ";".join(
            [mail_re.sub(u'<\\1@...>', x) for x in revision.get_apparent_authors()]
            )
    date = datetime.datetime.fromtimestamp(revision.timestamp, utc)
    return Changeset(repos, revstr, revision.message, author, date)


def post_change_branch_tip_hook(params):
    """Main routine of hook"""
    if params.old_revno > params.new_revno:
        return

    branch = params.branch
    if isinstance(branch, RemoteBranch):
        return

    config = branch.get_config()

    trac_env = config.get_user_option("trac_env")
    if not trac_env:
        return

    env = open_environment(trac_env)
    env.log.debug("trac env=%s" % trac_env)
    rm = RepositoryManager(env)
    branch_path = urlutils.local_path_from_url(get_branch_url(branch))
    env.log.debug("bzr branch=%s" % branch_path)
    
    # Find repository instance managed by trac.
    for r in rm.get_real_repositories():
        base = r.get_base().replace('\\', '/')
        if not base.endswith('/'):
            base += '/'
        if branch_path.startswith(base):
            repos = r
            prefix = branch_path[len(base):].replace('/', ',')
            break
    else:
        return

    # Update tickets via IRepositoryChangeListener
    for revno in range(params.old_revno+1, params.new_revno+1):
        revstr = u"%s%d" % (prefix, revno)
        env.log.debug("added : %s" % revstr)
        revision = branch.repository.get_revision(branch.get_rev_id(revno))
        changeset = create_dummy_changeset(repos, revstr, revision)
        for listener in rm.change_listeners:
            listener.changeset_added(repos, changeset)

branch.Branch.hooks.install_named_hook('post_change_branch_tip', post_change_branch_tip_hook,
                                 'post change branch tip hook for Trac')

