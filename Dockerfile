FROM tparkerusgs/avopytroll:release-2.0.0

RUN apt-get update && apt-get install -y \
  nginx

WORKDIR /var/www/html

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR avoviirstools
COPY setup.py .
COPY setup.cfg .
COPY avoviirstools avoviirstools
RUN python setup.py install
RUN pip freeze > requirements.txt

COPY files/uwsgi.ini uwsgi.ini
COPY files/supervisord.conf /etc/supervisor/supervisord.conf
COPY files/main.config /etc/nginx/sites-enabled/main.config
CMD ["supervisord"]
