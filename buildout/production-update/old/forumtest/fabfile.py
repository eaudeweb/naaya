from fabric.api import *
from fabric.api import env
from fabric.contrib.files import *
from path import path as ppath

app = env.app = {
    'buildout_repo':
        'https://github.com/eaudeweb/naaya.buildout.groupware.git',
    'naaya_repo':
        'https://github.com/eaudeweb/naaya.git',
}

env.hosts = ['edw@nautilus.eea.europa.eu']

app['repo'] = ppath('/var/local/groupware/gw-test')

app.update({
    'buildout_var': app['repo']/'src/buildout',
    'naaya_var': app['repo']/'src/naaya',
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
def _update_forumtest():
    _git_repo(app['buildout_var'], app['buildout_repo'], update=True)
    _git_repo(app['naaya_var'], app['naaya_repo'], update=True)


@task
def restart_forumtest():
    execute('shutdown_forumtest')
    execute('start_forumtest')


@task
def update_forumtest():
    execute('_update_forumtest')
    execute('shutdown_forumtest')
    run("%(repo)s/bin/buildout -c %(repo)s/buildout.cfg" % app)
    execute('start_forumtest')


@task
def shutdown_forumtest():
    run("%(repo)s/bin/zope-instance-0 stop" % app)
    run("sleep 0.5")
    run("%(repo)s/bin/zeoserver stop" % app)


@task
def start_forumtest():
    run("%(repo)s/bin/zeoserver start" % app)
    run("%(repo)s/bin/zope-instance-0 start" % app)
