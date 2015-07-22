from fabric.api import *
from fabric.contrib.files import *
from path import path as ppath

app = env.app = {
    'buildout_repo': 'https://svn.eionet.europa.eu/repositories/Naaya/buildout/envirowindows/',
    'bundle_repo': 'https://svn.eionet.europa.eu/repositories/Naaya/trunk/eggs/NaayaBundles-EW/',
}

from localcfg import *

app.update({
    'buildout_var': app['repo']/'src/buildout-ew',
    'bundle_var': app['repo']/'src/NaayaBundles-EW',
})


@task
def ssh():
    open_shell("cd '%(repo)s'" % app)


def _svn_repo(repo_path, origin_url, update=True):
    if not exists(repo_path/'.svn'):
        run("mkdir -p '%s'" % repo_path)
        with cd(repo_path):
            run("svn co '%s' ." % origin_url)

    elif update:
        with cd(repo_path):
            run("svn up")

@task
def _update_repos():
    _svn_repo(app['buildout_var'], app['buildout_repo'], update=True)
    _svn_repo(app['bundle_var'], app['bundle_repo'], update=True)

@task
def restart_ew():
    run("%(repo)s/bin/buildout -c %(repo)s/buildout.cfg" % app)
    run("%(repo)s/bin/zope-instance-ew-0 stop" % app)
    run("sleep 0.5")
    run("%(repo)s/bin/zope-instance-ew-0 start" % app)
    run("sleep 5")
    run("%(repo)s/bin/zope-instance-ew-1 stop" % app)
    run("sleep 0.5")
    run("%(repo)s/bin/zope-instance-ew-1 start" % app)
    run("sleep 5")
    run("%(repo)s/bin/zope-instance-ew-2 stop" % app)
    run("sleep 0.5")
    run("%(repo)s/bin/zope-instance-ew-2 start" % app)
    run("sleep 5")
    run("%(repo)s/bin/zope-instance-ew-3 stop" % app)
    run("sleep 0.5")
    run("%(repo)s/bin/zope-instance-ew-3 start" % app)
    run("sleep 5")
    run("%(repo)s/bin/zope-instance-technologies stop" % app)
    run("sleep 0.5")
    run("%(repo)s/bin/zope-instance-technologies start" % app)
    run("sleep 5")
    run("%(repo)s/bin/zope-instance-test stop" % app)
    run("sleep 0.5")
    run("%(repo)s/bin/zope-instance-test start" % app)

@task
def update_ew():
    execute('_update_repos')
    execute('restart_ew')

@task
def shutdown_ew():
    run("%(repo)s/bin/poundctl stop" % app)
    run("%(repo)s/bin/zope-instance-ew-0 stop" % app)
    run("sleep 0.5")
    run("%(repo)s/bin/zope-instance-ew-1 stop" % app)
    run("sleep 0.5")
    run("%(repo)s/bin/zope-instance-ew-2 stop" % app)
    run("sleep 0.5")
    run("%(repo)s/bin/zope-instance-ew-3 stop" % app)
    run("sleep 0.5")
    run("%(repo)s/bin/zeoserver-ew stop" % app)
    run("sleep 5")
    run("%(repo)s/bin/zope-instance-technologies stop" % app)
    run("sleep 0.5")
    run("%(repo)s/bin/zope-instance-test stop" % app)

@task
def start_ew():
    run("%(repo)s/bin/zeoserver-ew start" % app)
    run("%(repo)s/bin/zope-instance-ew-0 start" % app)
    run("sleep 0.5")
    run("%(repo)s/bin/zope-instance-ew-1 start" % app)
    run("sleep 0.5")
    run("%(repo)s/bin/zope-instance-ew-2 start" % app)
    run("sleep 0.5")
    run("%(repo)s/bin/zope-instance-ew-3 start" % app)
    run("sleep 0.5")
    run("%(repo)s/bin/poundctl start" % app)
    run("sleep 0.5")
    run("%(repo)s/bin/zope-instance-technologies start" % app)
    run("sleep 0.5")
    run("%(repo)s/bin/zope-instance-test start" % app)

