FROM centos:7

RUN yum -y install wget
RUN wget http://pkgs.repoforge.org/rpmforge-release/rpmforge-release-0.5.3-1.el6.rf.x86_64.rpm && \
    rpm --import http://apt.sw.be/RPM-GPG-KEY.dag.txt && \
    rpm -i rpmforge-release-0.5.3-1.el6.rf.*.rpm && \
    rm -r rpmforge-release-0.5.3-1.el6.rf.x86_64.rpm
RUN wget http://dl.fedoraproject.org/pub/epel/7/x86_64/e/epel-release-7-5.noarch.rpm
RUN rpm -ivh epel-release-7-5.noarch.rpm

# Install libraries
RUN \
  yum -y install \
    cryptopp-devel \
    curl-devel \
    cyrus-sasl-devel \
    freetype-devel \
    glibc-devel \
    glib2-devel \
    gvfs-devel \
    libjpeg-turbo-devel \
    libxml2-devel \
    libxslt-devel \
    libyaml-devel \
    mysql-libs \
    openldap-devel \
    openssl-devel \
    python-devel \
    readline-devel \
    sqlite-devel \
    zlib-devel

#RUN yum groupinstall -y 'Development Tools'

# Install packages
RUN \
  yum -y updateinfo && \
  yum -y install \
    gcc \
    gcc-c++ \
    git \
    make \
    mc \
    patch \
    python-virtualenv \
    subversion \
    tar \
    which \
    yasm

# Install lame
RUN wget -O lame-3.99.5.tar.gz http://sourceforge.net/projects/lame/files/lame/3.99/lame-3.99.5.tar.gz/download && \
    tar xvfz lame-3.99.5.tar.gz && \
    cd lame-3.99.5 && ./configure && make && make install && ldconfig && \
    cd .. && \
    rm -r lame-3.99.5 lame-3.99.5.tar.gz

# Install ffmpeg 0.7.x
RUN wget http://www.ffmpeg.org/releases/ffmpeg-0.7.17.tar.gz && \
   tar xvfz ffmpeg-0.7.17.tar.gz && cd ffmpeg-0.7.17 && \
   ./configure --enable-gpl --enable-libmp3lame --enable-nonfree \
       --enable-version3 --enable-x11grab && \
   make && make install && \
   cd .. && \
   rm -r ffmpeg-0.7.17 ffmpeg-0.7.17.tar.gz

# Install Python 2.6.x
RUN wget http://eggshop.eaudeweb.ro/Python-2.6.8-edw1.tgz && \
    tar xvfz Python-2.6.8-edw1.tgz && cd Python-2.6.8-edw1 && \
    ./configure --prefix=/var/local/python/python26 --enable-unicode=ucs4 && \
    make && make install && \
    cd .. && \
    rm -r Python-2.6.8-edw1 Python-2.6.8-edw1.tgz

# Install setuptools
RUN wget https://pypi.python.org/packages/source/s/setuptools/setuptools-0.6c11.tar.gz && \
    tar xvfz setuptools-0.6c11.tar.gz && cd setuptools-0.6c11 && \
    /var/local/python/python26/bin/python setup.py install && \
    cd .. && \
    rm -r setuptools-0.6c11 setuptools-0.6c11.tar.gz

# Install pip
RUN /var/local/python/python26/bin/easy_install pip

# Install pdb++
RUN /var/local/python/python26/bin/pip install pdbpp

#Install postgresql
RUN yum -y install uuid
RUN rpm -iUvh http://yum.postgresql.org/9.3/redhat/rhel-7-x86_64/pgdg-centos93-9.3-1.noarch.rpm
RUN yum -y updateinfo && \
    yum -y install postgresql93 postgresql93-server postgresql93-contrib postgresql93-libs --disablerepo=* --enablerepo=pgdg93
RUN systemctl enable postgresql-9.3

RUN yum clean all

RUN mkdir /var/local/forum
RUN mkdir /var/local/forum/var
#VOLUME /var/local/forum/var
COPY bootstrap.py /var/local/forum/
COPY buildout.cfg /var/local/forum/
COPY secret.cfg /var/local/forum/
COPY versions.cfg /var/local/forum/
COPY zope-2.12.28-versions.cfg /var/local/forum/

WORKDIR /var/local/forum
RUN /var/local/python/python26/bin/python ./bootstrap.py --version=1.4.4
RUN bin/buildout
CMD bin/forum start
