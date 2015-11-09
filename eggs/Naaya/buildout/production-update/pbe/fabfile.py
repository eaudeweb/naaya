from fabric.api import *
from fabric.api import env
from fabric.contrib.files import *
from path import path as ppath

app = env.app = {
    'buildout_repo':
        'https://github.com/eaudeweb/naaya.buildout.groupware.git',
    'bundle_repo':
        'https://github.com/eaudeweb/naaya.bundles.NaayaBundles-PBE.git',
}

env.hosts = ['zope@sepia.eea.europa.eu']

app['repo'] = ppath('/var/local/groupware')

app.update({
    'buildout_var': app['repo']/'src/buildout',
    'bundle_var': app['repo']/'src/NaayaBundles-PBE',
})


@task
def ssh():
    open_shell("cd '%(repo)s'" % app)


def _git_repo(repo_path, origin_url, update=True):
    if not exists(repo_path/'.git'):
        run("mkdir -p '%s'" % repo_path)
        with cd(repo_path):
            run("git clone '%s' ." % origin_url)

    elif update:
        with cd(repo_path):
            run("git pull")


@task
def _update_pbe():
    _git_repo(app['buildout_var'], app['buildout_repo'], update=True)
    _git_repo(app['bundle_var'], app['bundle_repo'], update=True)


@task
def restart_pbe():
    execute('shutdown_pbe')
    execute('start_pbe')


@task
def update_pbe():
    execute('_update_pbe')
    execute('shutdown_pbe')
    run("%(repo)s/bin/buildout -c %(repo)s/buildout.cfg" % app)
    execute('start_pbe')


@task
def shutdown_pbe():
    run("%(repo)s/bin/poundctl stop" % app)
    run("%(repo)s/bin/zope-instance-0 stop" % app)
    run("sleep 0.5")
    run("%(repo)s/bin/zope-instance-1 stop" % app)
    run("sleep 0.5")
    run("%(repo)s/bin/zope-instance-2 stop" % app)
    run("sleep 0.5")
    run("%(repo)s/bin/zope-instance-3 stop" % app)
    run("sleep 0.5")
    run("%(repo)s/bin/zeoserver stop" % app)


@task
def start_pbe():
    run("%(repo)s/bin/zeoserver start" % app)
    run("%(repo)s/bin/zope-instance-0 start" % app)
    run("sleep 0.5")
    run("%(repo)s/bin/zope-instance-1 start" % app)
    run("sleep 0.5")
    run("%(repo)s/bin/zope-instance-2 start" % app)
    run("sleep 0.5")
    run("%(repo)s/bin/zope-instance-3 start" % app)
    run("sleep 0.5")
    run("%(repo)s/bin/poundctl start" % app)
