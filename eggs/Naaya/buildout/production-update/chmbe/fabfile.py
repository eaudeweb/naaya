from fabric.api import *
from fabric.api import env
from fabric.contrib.files import *
from path import path as ppath

app = env.app = {
    'buildout_repo': 'https://github.com/eaudeweb/naaya.buildout.chm-be.git',
    'bundle_repo':
        'https://github.com/eaudeweb/naaya.bundles.NaayaBundles-CHMBE.git',
    'bundle_cop10_repo':
        'https://github.com/eaudeweb/'
        'naaya.bundles.NaayaBundles-CHMBE-cop10.git',
    'bundle_training_repo':
        'https://github.com/eaudeweb/'
        'naaya.bundles.NaayaBundles-CHMBE-training.git',
}

env.hosts = ['zope@193.190.234.37:1974']

app['repo'] = ppath('/var/local/bch')


app.update({
    'buildout_var': app['repo']/'src/buildout-chm-be',
    'bundle_var': app['repo']/'src/NaayaBundles-CHMBE',
    'bundle_cop10_var': app['repo']/'src/NaayaBundles-CHMBE',
    'bundle_training_var': app['repo']/'src/NaayaBundles-CHMBE',
})


@task
def ssh():
    open_shell("cd '%(repo)s'" % app)


def _git_repo(repo_path, origin_url, update=True):
    if not exists(repo_path/'.git'):
        run("mkdir -p '%s'" % repo_path)
        with cd(repo_path):
            run("git clone '%s' buildout-chm-be" % origin_url)

    elif update:
        with cd(repo_path):
            run("git pull")


@task
def _update_repos():
    _git_repo(app['buildout_var'], app['buildout_repo'], update=True)
    _git_repo(app['bundle_var'], app['bundle_repo'], update=True)
    _git_repo(app['bundle_var'], app['bundle_cop10_repo'], update=True)
    _git_repo(app['bundle_var'], app['bundle_training_repo'], update=True)


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
    run("%(repo)s/bin/zope-instance-biodiv-2 stop" % app)
    run("sleep 0.5")
    run("%(repo)s/bin/zope-instance-biodiv-2 start" % app)
    run("sleep 5")
    run("%(repo)s/bin/zope-instance-biodiv-3 stop" % app)
    run("sleep 0.5")
    run("%(repo)s/bin/zope-instance-biodiv-3 start" % app)
    run("sleep 5")
    run("%(repo)s/bin/zope-instance-biodiv-4 stop" % app)
    run("sleep 0.5")
    run("%(repo)s/bin/zope-instance-biodiv-4 start" % app)
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
    run("%(repo)s/bin/zope-instance-biodiv-2 stop" % app)
    run("sleep 0.5")
    run("%(repo)s/bin/zope-instance-biodiv-3 stop" % app)
    run("sleep 0.5")
    run("%(repo)s/bin/zope-instance-biodiv-4 stop" % app)
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
    run("%(repo)s/bin/zope-instance-biodiv-2 start" % app)
    run("sleep 0.5")
    run("%(repo)s/bin/zope-instance-biodiv-3 start" % app)
    run("sleep 0.5")
    run("%(repo)s/bin/zope-instance-biodiv-4 start" % app)
    run("sleep 0.5")
    run("%(repo)s/bin/poundctl start" % app)
    run("sleep 0.5")
    run("%(repo)s/bin/zope-instance-cop10 start" % app)
    run("sleep 0.5")
    run("%(repo)s/bin/zope-instance-training start" % app)
