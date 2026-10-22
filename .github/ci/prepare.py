"""Write local.cfg and secret.cfg for testing a pip site against this checkout.

Usage: prepare.py SITE_DIR NAAYA_DIR
"""
import glob
import os
import re
import sys

# Test tools, on top of the eggs of the site
TEST_EGGS = ['zope.testrunner', 'twill', 'WebOb']


def main(site_dir, naaya_dir):
    naaya_dir = os.path.abspath(naaya_dir)
    # Every package of the checkout; naaya_pip.py installs only those the site eggs need
    develop = sorted(os.path.dirname(path) for pattern in ('eggs/*/setup.py', 'bundles/*/setup.py')
                     for path in glob.glob(os.path.join(naaya_dir, pattern)))
    site_cfg = open(os.path.join(site_dir, 'site.cfg'), encoding='utf-8').read()
    # Empty secrets: naaya_pip.py leaves out environment variables without a value
    secrets = sorted(set(re.findall(r'\$\{secrets:([\w-]+)\}', site_cfg)))
    # be.ldapadmin opens its log files there at startup and fails if it is missing
    for path in re.findall(r'LDAP_DISK_STORAGE\s+\$\{directory\}/(\S+)', site_cfg):
        os.makedirs(os.path.join(site_dir, path), exist_ok=True)
    with open(os.path.join(site_dir, 'secret.cfg'), 'w', encoding='utf-8') as f:
        f.write('[secrets]\n' + ''.join('%s =\n' % name for name in secrets))
    with open(os.path.join(site_dir, 'local.cfg'), 'w', encoding='utf-8') as f:
        f.write('[site]\ndevelop =\n')
        f.write(''.join('    %s\n' % path for path in develop))
        f.write('\n[instance:ci]\n'
                'http-address = 127.0.0.1:8080\n'
                'storage = file\n'
                'temporary-storage = local\n'
                'eggs =\n')
        f.write(''.join('    %s\n' % egg for egg in TEST_EGGS))
    sys.stdout.write('Wrote local.cfg (%d develop packages) and secret.cfg (%d secrets)\n'
                     % (len(develop), len(secrets)))


if __name__ == '__main__':
    main(*sys.argv[1:3])
