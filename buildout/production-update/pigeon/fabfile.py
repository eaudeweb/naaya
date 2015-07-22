from fabric.api import *
from fabric.api import env
from fabric.contrib.files import *
from path import path as ppath

app = env.app = {
    'buildout_repo': 'https://svn.eionet.europa.eu/repositories/Naaya/buildout/groupware/zope212/',
    'forum_bundle_repo': 'https://svn.eionet.europa.eu/repositories/Naaya/trunk/eggs/NaayaBundles-Forum/',
}

env.hosts = ['edw@pigeon.eea.europa.eu']

app['forum_repo'] = ppath('/var/local/naaya/forum')
app['projects_repo'] = ppath('/var/local/naaya/projects')
app['archives_repo'] = ppath('/var/local/naaya/archives')

app.update({
    'forum_buildout_var': app['forum_repo']/'src/buildout',
    'forum_bundle_var': app['forum_repo']/'src/NaayaBundles-Forum',
    'projects_buildout_var': app['projects_repo']/'src/buildout',
    'projects_bundle_var': app['projects_repo']/'src/NaayaBundles-Forum',
    'archives_buildout_var': app['archives_repo']/'src/buildout',
    'archives_bundle_var': app['archives_repo']/'src/NaayaBundles-Forum',
})


@task
def ssh():
    open_shell("cd '%(forum_repo)s'" % app)


def _svn_repo(repo_path, origin_url, update=True):
    if not exists(repo_path/'.svn'):
        run("mkdir -p '%s'" % repo_path)
        with cd(repo_path):
            run("svn co '%s' ." % origin_url)

    elif update:
        with cd(repo_path):
            run("svn up")


@task
def _update_forum():
    _svn_repo(app['forum_buildout_var'], app['buildout_repo'], update=True)
    _svn_repo(app['forum_bundle_var'], app['forum_bundle_repo'], update=True)


@task
def _update_projects():
    _svn_repo(app['projects_buildout_var'], app['buildout_repo'], update=True)
    _svn_repo(app['projects_bundle_var'], app['forum_bundle_repo'],
              update=True)


@task
def _update_archives():
    _svn_repo(app['archives_buildout_var'], app['buildout_repo'], update=True)
    _svn_repo(app['archives_bundle_var'], app['forum_bundle_repo'],
              update=True)


@task
def restart_forum():
    run("%(forum_repo)s/bin/buildout -c %(forum_repo)s/buildout.cfg" % app)
    run("%(forum_repo)s/bin/zope-instance-0 stop" % app)
    run("sleep 0.5")
    run("%(forum_repo)s/bin/zope-instance-0 start" % app)
    run("sleep 5")
    run("%(forum_repo)s/bin/zope-instance-1 stop" % app)
    run("sleep 0.5")
    run("%(forum_repo)s/bin/zope-instance-1 start" % app)
    run("sleep 5")
    run("%(forum_repo)s/bin/zope-instance-2 stop" % app)
    run("sleep 0.5")
    run("%(forum_repo)s/bin/zope-instance-2 start" % app)
    run("sleep 5")
    run("%(forum_repo)s/bin/zope-instance-3 stop" % app)
    run("sleep 0.5")
    run("%(forum_repo)s/bin/zope-instance-3 start" % app)


@task
def restart_projects():
    run("%(projects_repo)s/bin/buildout -c %(projects_repo)s/buildout.cfg" %
        app)
    run("%(projects_repo)s/bin/zope-instance-0 stop" % app)
    run("sleep 0.5")
    run("%(projects_repo)s/bin/zope-instance-0 start" % app)
    run("sleep 5")
    run("%(projects_repo)s/bin/zope-instance-1 stop" % app)
    run("sleep 0.5")
    run("%(projects_repo)s/bin/zope-instance-1 start" % app)


@task
def restart_archives():
    run("%(archives_repo)s/bin/buildout -c %(archives_repo)s/buildout.cfg" %
        app)
    run("%(archives_repo)s/bin/zope-instance-0 stop" % app)
    run("sleep 0.5")
    run("%(archives_repo)s/bin/zope-instance-0 start" % app)
    run("sleep 5")
    run("%(archives_repo)s/bin/zope-instance-1 stop" % app)
    run("sleep 0.5")
    run("%(archives_repo)s/bin/zope-instance-1 start" % app)


@task
def update_forum():
    execute('_update_forum')
    execute('restart_forum')


@task
def update_projects():
    execute('_update_projects')
    execute('restart_projects')


@task
def update_archives():
    execute('_update_archives')
    execute('restart_archives')


@task
def update_pigeon():
    execute('_update_forum')
    execute('restart_forum')
    execute('_update_projects')
    execute('restart_projects')
    execute('_update_archives')
    execute('restart_archives')


@task
def shutdown_forum():
    run("%(forum_repo)s/bin/poundctl stop" % app)
    run("%(forum_repo)s/bin/zope-instance-0 stop" % app)
    run("sleep 0.5")
    run("%(forum_repo)s/bin/zope-instance-1 stop" % app)
    run("sleep 0.5")
    run("%(forum_repo)s/bin/zope-instance-2 stop" % app)
    run("sleep 0.5")
    run("%(forum_repo)s/bin/zope-instance-3 stop" % app)
    run("sleep 0.5")
    run("%(forum_repo)s/bin/zeoserver stop" % app)


@task
def shutdown_projects():
    run("%(projects_repo)s/bin/poundctl stop" % app)
    run("%(projects_repo)s/bin/zope-instance-0 stop" % app)
    run("sleep 0.5")
    run("%(projects_repo)s/bin/zope-instance-1 stop" % app)
    run("sleep 0.5")
    run("%(projects_repo)s/bin/zeoserver stop" % app)


@task
def shutdown_archives():
    run("%(archives_repo)s/bin/poundctl stop" % app)
    run("%(archives_repo)s/bin/zope-instance-0 stop" % app)
    run("sleep 0.5")
    run("%(archives_repo)s/bin/zeoserver stop" % app)


@task
def start_forum():
    run("%(forum_repo)s/bin/zeoserver start" % app)
    run("%(forum_repo)s/bin/zope-instance-0 start" % app)
    run("sleep 0.5")
    run("%(forum_repo)s/bin/zope-instance-1 start" % app)
    run("sleep 0.5")
    run("%(forum_repo)s/bin/zope-instance-2 start" % app)
    run("sleep 0.5")
    run("%(forum_repo)s/bin/zope-instance-3 start" % app)
    run("sleep 0.5")
    run("%(forum_repo)s/bin/poundctl start" % app)


@task
def start_projects():
    run("%(projects_repo)s/bin/zeoserver start" % app)
    run("%(projects_repo)s/bin/zope-instance-0 start" % app)
    run("sleep 0.5")
    run("%(projects_repo)s/bin/zope-instance-1 start" % app)
    run("sleep 0.5")
    run("%(projects_repo)s/bin/poundctl start" % app)


@task
def start_archives():
    run("%(archives_repo)s/bin/zeoserver start" % app)
    run("%(archives_repo)s/bin/zope-instance-0 start" % app)
    run("sleep 0.5")
    run("%(archives_repo)s/bin/poundctl start" % app)
