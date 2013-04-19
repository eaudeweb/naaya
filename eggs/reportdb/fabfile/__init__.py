from fabric.api import *
from fabric.contrib.files import *
from path import path as ppath

app = env.app = {
    'reportdb_svn': 'https://svn.eionet.europa.eu/repositories/Naaya/trunk/eggs/reportdb',
    'localrepo': ppath(__file__).abspath().parent.parent,
}

try: from localcfg import *
except: pass

app.update({
    'instance_var_reportdb': app['reportdb_repo']/'instance',
    'sandbox_reportdb': app['reportdb_repo']/'sandbox',
    'instance_var_seris': app['seris_repo']/'instance',
    'sandbox_seris': app['seris_repo']/'sandbox',
    'user': 'edw',
})


@task
def ssh():
    open_shell("cd '%(seris_repo)s'" % app)


def _install_random_key(remote_path, key_length=20, mode=0600):
    import random
    import string
    from StringIO import StringIO
    vocabulary = string.ascii_letters + string.digits
    key = ''.join(random.choice(vocabulary) for c in xrange(key_length))
    put(StringIO(key), remote_path, mode=mode)


def _svn_repo(repo_path, origin_url, update=True):
    if not exists(repo_path/'.svn'):
        run("mkdir -p '%s'" % repo_path)
        with cd(repo_path):
            run("svn co '%s' ." % origin_url)

    elif update:
        with cd(repo_path):
            run("svn up")

@task
def install_reportdb():
    _svn_repo(app['reportdb_repo'], app['reportdb_svn'], update=True)

    if not exists(app['sandbox_reportdb']):
        run("virtualenv "# -p python2.6 
            "--no-site-packages --distribute "
            "'%(sandbox_reportdb)s'" % app)
    run("%(sandbox_reportdb)s/bin/pip install -r %(reportdb_repo)s/requirements.txt" % app)

    if not exists(app['instance_var_reportdb']):
        run("mkdir -p '%(instance_var_reportdb)s'" % app)

    secret_key_path = app['instance_var_reportdb']/'secret_key.txt'
    if not exists(secret_key_path):
        _install_random_key(str(secret_key_path))

    put(app['localrepo']/'fabfile'/'production-settings_reportdb.py',
        str(app['instance_var_reportdb']/'settings.py'))

    upload_template(app['localrepo']/'fabfile'/'supervisord_reportdb.conf',
                    str(app['sandbox_reportdb']/'supervisord.conf'),
                    context=app, backup=False)

@task
def install_seris():
    _svn_repo(app['seris_repo'], app['reportdb_svn'], update=True)

    if not exists(app['sandbox_seris']):
        run("virtualenv "# -p python2.6 
            "--no-site-packages --distribute "
            "'%(sandbox_seris)s'" % app)
    run("%(sandbox_seris)s/bin/pip install -r %(seris_repo)s/requirements.txt" % app)

    if not exists(app['instance_var_seris']):
        run("mkdir -p '%(instance_var_seris)s'" % app)

    secret_key_path = app['instance_var_seris']/'secret_key.txt'
    if not exists(secret_key_path):
        _install_random_key(str(secret_key_path))

    put(app['localrepo']/'fabfile'/'production-settings_seris.py',
        str(app['instance_var_seris']/'settings.py'))

    upload_template(app['localrepo']/'fabfile'/'supervisord_seris.conf',
                    str(app['sandbox_seris']/'supervisord.conf'),
                    context=app, backup=False)


@task
def service_reportdb(action):
    run("'%(sandbox)s/bin/supervisorctl' %(action)s %(name)s" % {
            'sandbox': app['sandbox_reportdb'],
            'action': action,
            'name': 'reportdb',
        })

@task
def service_seris(action):
    run("'%(sandbox)s/bin/supervisorctl' %(action)s %(name)s" % {
            'sandbox': app['sandbox_seris'],
            'action': action,
            'name': 'seris',
        })


@task
def deploy_reportdb():
    execute('install_reportdb')
    execute('service_reportdb', 'restart')

@task
def deploy_seris():
    execute('install_seris')
    execute('service_seris', 'restart')
