FROM ubuntu:16.04
MAINTAINER k01 <k01@white-wing.jp>

RUN locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

RUN apt-get update -y && apt-get install -y \
    git \
    libfreetype6 \
    libfreetype6-dev \
    libjpeg8 \
    libjpeg8-dev \
    liblcms2-2 \
    liblcms2-dev \
    liblcms2-utils \
    libtiff5-dev \
    python-dev \
    python-pip \
    python-setuptools \
    unzip \
    vim \
    wget \
    zlib1g-dev && \
    rm -rf /var/lib/apt/lists/*

ENV KAKADU_URL http://kakadusoftware.com/wp-content/uploads/2014/06/KDU78_Demo_Apps_for_Linux-x86-64_160226.zip
ENV KAKADU_ARCHIVE_FOLDER_NAME KDU78_Demo_Apps_for_Linux-x86-64_160226

RUN wget -O /tmp/kakadu.zip $KAKADU_URL && \
    cd /tmp && \
    unzip kakadu.zip && \
    cd /tmp/$KAKADU_ARCHIVE_FOLDER_NAME && \
    cp libkdu_v78R.so /usr/local/lib && \
    chmod 755 /usr/local/lib/libkdu_v78R.so && \
    cp kdu_expand /usr/local/bin && \
    chmod 755 /usr/local/bin/kdu_expand && \
    cd /tmp && \
    rm -rf /tmp/$KAKADU_ARCHIVE_FOLDER_NAME && \
    rm -rf /tmp/__MACOSX && \
    rm /tmp/kakadu.zip && \
    ln -s /usr/lib/`uname -i`-linux-gnu/libfreetype.so /usr/lib/ && \
    ln -s /usr/lib/`uname -i`-linux-gnu/libjpeg.so /usr/lib/ && \
    ln -s /usr/lib/`uname -i`-linux-gnu/libz.so /usr/lib/ && \
    ln -s /usr/lib/`uname -i`-linux-gnu/liblcms2.so /usr/lib/ && \
    ln -s /usr/lib/`uname -i`-linux-gnu/libtiff.so /usr/lib/ && \
    echo '/usr/local/lib' >> /etc/ld.so.conf && \
    ldconfig

RUN pip install --upgrade pip && \
    pip2.7 install Werkzeug && \
    pip2.7 install configobj && \
    pip2.7 install Pillow && \
    pip2.7 install boto3

RUN git clone https://github.com/loris-imageserver/loris.git /opt/loris

RUN mkdir -p /var/www/loris && \
    useradd -d /var/www/loris -s /sbin/false loris && \
    chown loris.loris /var/www/loris && \
    mkdir /usr/local/share/images && \
    cp -R /opt/loris/tests/img/* /usr/local/share/images/ && \
    cd /opt/loris && \
    ./setup.py install

RUN sed -i -- 's/localhost/0.0.0.0/g' /opt/loris/loris/webapp.py && \
    sed -i 's/app = create_app(debug=True)/app = create_app(debug=False, config_file_path=conf_fp)/g' /opt/loris/loris/webapp.py && \
    sed -i 's/r.call_on_close(unlink(fp))/r.call_on_close(lambda: unlink(fp))/g' /opt/loris/loris/webapp.py

COPY src/s3resolver.py /opt/loris/loris/
COPY conf/loris2.conf /opt/loris/etc/loris2.conf

WORKDIR /opt/loris/loris
EXPOSE 5004
CMD ["python", "webapp.py"]
