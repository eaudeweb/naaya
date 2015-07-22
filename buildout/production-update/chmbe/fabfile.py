from fabric.api import *
from fabric.contrib.files import *

app = env.app = {
    'buildout_repo': 'https://svn.eionet.europa.eu/repositories/Naaya/buildout/chm-be',
    'bundle_repo': 'https://svn.eionet.europa.eu/repositories/Naaya/trunk/eggs/NaayaBundles-CHMBE/',
}

from localcfg import *

app.update({
    'buildout_var': app['repo']/'src/buildout-chm-be',
    'bundle_var': app['repo']/'src/NaayaBundles-CHMBE',
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
def restart_chmbe():
    run("%(repo)s/bin/buildout -c %(repo)s/buildout.cfg" % app)
    run("%(repo)s/bin/zope-instance-biodiv-0 stop" % app)
    run("sleep 0.5")
    run("%(repo)s/bin/zope-instance-biodiv-0 start" % app)
    run("sleep 5")
    run("%(repo)s/bin/zope-instance-biodiv-1 stop" % app)
    run("sleep 0.5")
    run("%(repo)s/bin/zope-instance-biodiv-1 start" % app)
    run("sleep 5")
    run("%(repo)s/bin/zope-instance-cop10 stop" % app)
    run("sleep 0.5")
    run("%(repo)s/bin/zope-instance-cop10 start" % app)
    run("sleep 5")
    run("%(repo)s/bin/zope-instance-training stop" % app)
    run("sleep 0.5")
    run("%(repo)s/bin/zope-instance-training start" % app)

@task
def update_chmbe():
    execute('_update_repos')
    execute('restart_chmbe')

@task
def shutdown_chmbe():
    run("%(repo)s/bin/poundctl stop" % app)
    run("%(repo)s/bin/zope-instance-biodiv-0 stop" % app)
    run("sleep 0.5")
    run("%(repo)s/bin/zope-instance-biodiv-1 stop" % app)
    run("sleep 0.5")
    run("%(repo)s/bin/zeo-server stop" % app)
    run("sleep 0.5")
    run("%(repo)s/bin/zope-instance-cop10 stop" % app)
    run("sleep 0.5")
    run("%(repo)s/bin/zope-instance-training stop" % app)

@task
def start_chmbe():
    run("%(repo)s/bin/zeo-server start" % app)
    run("%(repo)s/bin/zope-instance-biodiv-0 start" % app)
    run("sleep 0.5")
    run("%(repo)s/bin/zope-instance-biodiv-1 start" % app)
    run("sleep 0.5")
    run("%(repo)s/bin/poundctl start" % app)
    run("sleep 0.5")
    run("%(repo)s/bin/zope-instance-cop10 start" % app)
    run("sleep 0.5")
    run("%(repo)s/bin/zope-instance-training start" % app)
