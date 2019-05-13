FROM tparkerusgs/avopytroll:release-1.10.3

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR avoviirstools
COPY setup.py .
COPY setup.cfg .
COPY avoviirstools avoviirstools
RUN python setup.py install

RUN pip freeze > requirements.txt
COPY supervisord.conf /etc/supervisor/supervisord.conf
CMD ["supervisord"]
