from fabric.api import *
from fabric.api import env
from fabric.contrib.files import *
from path import path as ppath

app = env.app = {
    'buildout_repo': 'https://github.com/eaudeweb/naaya.buildout.destinet.git',
    'bundle_repo':
        'https://github.com/eaudeweb/naaya.bundles.NaayaBundles-DESTINET.git',
}

env.hosts = ['edw@destinet.eu']

app['repo'] = ppath('/var/local/destinet/buildout')

app.update({
    'buildout_var': app['repo']/'src/buildout-destinet',
    'bundle_var': app['repo']/'src/NaayaBundles-DESTINET',
})


@task
def ssh():
    open_shell("cd '%(repo)s'" % app)


def _git_repo(repo_path, origin_url, update=True):
    if not exists(repo_path/'.git'):
        run("mkdir -p '%s'" % repo_path)
        with cd(repo_path):
            run("git clone '%s' buildout-destinet" % origin_url)

    elif update:
        with cd(repo_path):
            run("git pull")


@task
def _update_repos():
    _git_repo(app['buildout_var'], app['buildout_repo'], update=True)
    _git_repo(app['bundle_var'], app['bundle_repo'], update=True)


@task
def restart_destinet():
    run("%(repo)s/bin/buildout -c %(repo)s/buildout.cfg" % app)
    run("%(repo)s/bin/zope-instance-0 stop" % app)
    run("sleep 0.5")
    run("%(repo)s/bin/zope-instance-0 start" % app)
    run("sleep 5")
    run("%(repo)s/bin/zope-instance-1 stop" % app)
    run("sleep 0.5")
    run("%(repo)s/bin/zope-instance-1 start" % app)
    run("sleep 5")
    run("%(repo)s/bin/zope-instance-2 stop" % app)
    run("sleep 0.5")
    run("%(repo)s/bin/zope-instance-2 start" % app)
    run("sleep 5")
    run("%(repo)s/bin/zope-instance-3 stop" % app)
    run("sleep 0.5")
    run("%(repo)s/bin/zope-instance-3 start" % app)
    run("sleep 5")
    run("%(repo)s/bin/zope-instance-translations-test stop" % app)
    run("sleep 0.5")
    run("%(repo)s/bin/zope-instance-translations-test start" % app)


@task
def update_destinet():
    execute('_update_repos')
    execute('restart_destinet')


@task
def shutdown_destinet():
    run("%(repo)s/bin/poundctl stop" % app)
    run("%(repo)s/bin/zope-instance-0 stop" % app)
    run("sleep 0.5")
    run("%(repo)s/bin/zope-instance-1 stop" % app)
    run("sleep 0.5")
    run("%(repo)s/bin/zope-instance-2 stop" % app)
    run("sleep 0.5")
    run("%(repo)s/bin/zope-instance-3 stop" % app)
    run("sleep 0.5")
    run("%(repo)s/bin/zeo-server stop" % app)
    run("sleep 0.5")
    run("%(repo)s/bin/zope-instance-translations-test stop" % app)


@task
def start_destinet():
    run("%(repo)s/bin/zeo-server start" % app)
    run("%(repo)s/bin/zope-instance-0 start" % app)
    run("sleep 0.5")
    run("%(repo)s/bin/zope-instance-1 start" % app)
    run("sleep 0.5")
    run("%(repo)s/bin/zope-instance-2 start" % app)
    run("sleep 0.5")
    run("%(repo)s/bin/zope-instance-3 start" % app)
    run("sleep 0.5")
    run("%(repo)s/bin/poundctl start" % app)
    run("sleep 0.5")
    run("%(repo)s/bin/zope-instance-translations-test start" % app)
