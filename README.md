# מנהרת ביטוח 
### AloniSoft HarBit Proxy API

#### Supported pages
* [ביטוח תכולה](https://dira.cma.gov.il/Home/FillParameters?InsuranceType=Content)
* [ביטוח מבנה](https://dira.cma.gov.il/Home/FillParameters?InsuranceType=Structure)
* [מבנה ותכולה](https://dira.cma.gov.il/Home/FillParameters?InsuranceType=StructureAndContent)
* [ביטוח חיים](https://life.cma.gov.il/RiskParameters/RiskParameters?id=84300001)
* [ביטוח משכנתה](https://life.cma.gov.il/RiskParameters/RiskParameters?id=84300003)

#### Usage 
* [Current IP](http://18.221.172.87)
* [Current FQDN](ec2-18-221-172-87.us-east-2.compute.amazonaws.com)
* See [harbit.http](harbit.http) for API endpoints and their parameters

#### Deployment
* [AWS](https://console.aws.amazon.com)
    
    * Create EC2 instance from Ubuntu Server 16.04 LTS (HVM),EBS General Purpose (SSD) Volume Type.
    
    * Save received .pem key to app folder  
    
    * Create Elastic IP and assign it to instance
    
    * Check SSH connection to instance 
        * ($ ssh -i your_key.pem ubuntu@<your.elastic.ip.address>)
            > Last login: Thu Mar  5 07:40:21 2020 from 82.81.223.240
            > ubuntu@ip-172-31-24-131:~$ 


* [Deploy code](https://gitlab.com/leon.kladnitsky/_aloni_harbit)
    
    * Clone from repo
        * $ git clone https://gitlab.com/leon.kladnitsky/_aloni_harbit


* [Chrome](https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb)
    
    * Download corresponding version or use [setup folder](/setup/80/google-chrome-stable_current_amd64.deb)
    
    * Install it with dpkg
        * ($ dpkg -i google-chrome-stable_current_amd64.deb) 
            > It will probably fail
    * Install missing packages
        * ($ sudo apt-get install --fix-broken)
        
    * Install Chrome again 
        * ($ dpkg -i google-chrome-stable_current_amd64.deb)
            > Should be successful now
                                                                 > 
    * Check version 
        * ($ google-chrome --version) 
            > Google Chrome 80.0.3987.132


* [Chromedriver](https://chromedriver.chromium.org/downloads)
    
    * Download corresponding version or use [setup folder](/setup/80/chromedriver_v80.zip)
    
    * Unpack it to application root folder and make it executable 
        * $ chmod a+x ./chromedriver
    
    * Check version 
        * $ ./chromedriver --version
            > ChromeDriver 80.0.3987.106 (f68069574609230cf9b635cd784cfb1bf81bb53a-refs/branch-heads/3987@{#882})"

    * Install as system service
        * $ sudo cp ./chromedriver /usr/bin/
        * $ sudo nano /etc/systemd/system/chromedriver.service
            >   [Unit]
                Description=ChromeDriver service
                Wants=network.target
                After=syslog.target network-online.target
                [Service]
                User=ubuntu 
                Group=ubuntu
                Type=simple
                ExecStart=/usr/bin/chromedriver --port=5780 --log-path=/home/ubuntu/dev/tunbit/logs/chrmdrv.log --append-log --readable-timestamp
                Restart=always
                RestartSec=1
                KillMode=process
                [Install]
                WantedBy=multi-user.target
        * $ sudo systemctl daemon-reload
        * $ sudo systemctl enable chromedriver.service
            > Created symlink from /etc/systemd/system/multi-user.target.wants/chromedriver.service to /etc/systemd/system/chromedriver.service.
        * $ sudo systemctl start chromedriver.service
        * $ sudo systemctl status chromedriver.service
            > ● chromedriver.service - ChromeDriver service
              Loaded: loaded (/etc/systemd/system/chromedriver.service; enabled; vendor preset: enabled)
              Active: active (running) since Tue 2020-03-10 16:43:42 UTC; 5s ago
            Main PID: 30391 (chromedriver)
               Tasks: 44
              Memory: 55.5M
                 CPU: 4ms
              CGroup: /system.slice/chromedriver.service
                      ├─30137 /usr/bin/google-chrome --disable-background-networking --disable-client-side-phishing-detection --disable-default-apps --disable-hang-monitor --disable-popup-blocking --disable-prompt-on-
                      ├─30142 cat
                      ├─30143 cat
                      ├─30146 /opt/google/chrome/chrome --type=zygote --enable-logging --headless --log-level=0 --headless --enable-crash-reporter
                      ├─30148 /opt/google/chrome/chrome --type=zygote --enable-logging --headless --log-level=0 --headless --enable-crash-reporter
                      ├─30164 /opt/google/chrome/chrome --type=gpu-process --field-trial-handle=15415683116874597251,7491830997132768872,131072 --enable-logging --headless --log-level=0 --headless --enable-crash-repor
                      ├─30165 /opt/google/chrome/chrome --type=utility --field-trial-handle=15415683116874597251,7491830997132768872,131072 --lang=en-US --service-sandbox-type=network --enable-logging --log-level=0 --
                      ├─30168 /opt/google/chrome/chrome --type=renderer --allow-pre-commit-input --enable-automation --enable-logging --log-level=0 --remote-debugging-port=0 --test-type=webdriver --use-gl=swiftshader-
                      ├─30186 /opt/google/chrome/chrome --type=broker                                                                                                                                                    
                      └─30391 /usr/bin/chromedriver --port=5780 --log-path=/home/ubuntu/dev/tunbit/logs/chrmdrv.log --append-log --readable-timestamp


* [mod_wsgi](https://github.com/GrahamDumpleton/mod_wsgi/)
    
    * Check [this guide](https://medium.com/@prspr/django-deployment-on-amazon-ec2-running-apache-and-mod-wsgi-32481742115f), which refers to this [SO post]().
    
    * Install python3.7
        * $ sudo add-apt-repository ppa:deadsnakes/ppa 
        * $ sudo apt update
        * $ sudo apt install python3.7 python3.7-dev 
                
    * Make python3 default system-wide
        * $ update-alternatives --list python
            > /usr/bin/python2.7
            > /usr/bin/python3.5
            > /usr/bin/python3.7
        * $ sudo update-alternatives --config python
            > There are 3 choices for the alternative python (providing /usr/bin/python).
                * 0            /usr/bin/python3.7   2         auto mode
                  1            /usr/bin/python2.7   0         manual mode
                  2            /usr/bin/python3.5   1         manual mode
                  3            /usr/bin/python3.7   2         manual mode
        * Select python3.7 in auto mode
    
    * Install dev packages 
        * $ sudo apt-get install python3-pip python3-dev
    
    * Install [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/install.html)
        * $ pip install virtualenvwrapper --user
    
    * Find virtualenvwrapper script
        * $ which virtualenvwrapper.sh
            > /home/ubuntu/.local/bin/virtualenvwrapper.sh
    
    * Add environment vars to .bash_rc
        * $ nano /home/ubuntu/.bash_rc
            > export VIRTUALENVWRAPPER_SCRIPT=/home/ubuntu/.local/bin/virtualenvwrapper.sh
            > export WORKON_HOME=$HOME/.virtualenvs
            > export PROJECT_HOME=$HOME
            > source /home/ubuntu/.local/bin/virtualenvwrapper.sh
    
    * Create virtual environment for app 
        * $ mkvirtualenv -a /home/ubuntu/tunbit -r requirements.txt tunbit
    
    * Check python path and installed packages
        * $ lsvirtualenv
            > tunbit
        * $ workon tunbit
        * (tunbit) $ which python
            > /home/ubuntu/.virtualenvs/tunbit/bin/python
        * (tunbit) $ python -m pip list
            > Package           Version
            > ----------------- -------
            > Django            2.2.9  
            > pip               20.0.2 
            > pytz              2019.3 
            > selenium          3.141.0
            > setuptools        45.2.0 
            > sqlparse          0.3.1  
            > urllib3           1.25.8 
            > wheel             0.34.2
    
    * Prepare static files
        * (tunbit) $ python manage.py collectstatic 
            > 15 static files copied to '/home/ubuntu/dev/tunbit/collectstatic'.

    * Download [mod_wsgi](https://github.com/GrahamDumpleton/mod_wsgi/archive/4.7.1.tar.gz) or use [4.7.1](/setup/mod_wsgi-4.7.1.tar.gz)
    
    * Unpack and build
        * $ tar -xf mod_wsgi-4.7.1.tar.gz
        * $ cd mod_wsgi-4.7.1
        * $ ./configure --with-python=/home/ubuntu/.virtualenvs/tunbit/bin/python
        * $ make
        * $ sudo make install


* [Apache](http://httpd.apache.org/)
    * Install Apache2 
        * $ sudo apt-get install apache2 apache2-dev
    * Add ubuntu user to www-data group
        * $ sudo usermod -a -G ubuntu www-data
    * Fix permissions on /home/ubuntu folder
        * $ sudo chmod 710 /home/ubuntu
    * Change app ownergroup to www-data
        * $ sudo chown :www-data ~/tunbit
    * Add your virtual host section to apache
        * $ sudo nano /etc/apache2/sites-available/000-default.conf
            > <VirtualHost *:80>
                ServerAdmin webmaster@example.com
                DocumentRoot /home/ubuntu/tunbit
                ErrorLog ${APACHE_LOG_DIR}/error.log
                CustomLog ${APACHE_LOG_DIR}/access.log combined
                Alias /static /home/ubuntu/tunbit/collectstatic
                <Directory /home/ubuntu/tunbit/collectstatic>
                    Require all granted
                </Directory>
                <Directory /home/ubuntu/tunbit>
                    <Files wsgi.py>
                        Require all granted
                    </Files>
                </Directory>
                WSGIDaemonProcess tunbit python-path=/home/ubuntu/tunbit python-home=/home/ubuntu/.virtualenvs/tunbit
                WSGIProcessGroup tunbit
                WSGIScriptAlias / /home/ubuntu/tunbit/wsgi.py
            </VirtualHost>
    * Restart apache
        * $ sudo apache2ctl configtest
            > Syntax OK
        * $ sudo apache2ctl restart


* [Crombie killer](misc/kill_old.sh)  
    * Make scripts executable
        * $ chmod a+x misc/*.sh
    *  Add script to crontab
        * $ crontab -e
            > @hourly /home/ubuntu/dev/tunbit/misc/kill_old.sh 

#### TODO
* HTTPS
* Other Har Bituach services
