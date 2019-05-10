FROM tparkerusgs/avopytroll:release-1.9.0

WORKDIR /app
WORKDIR passplotter
COPY pass_plotter.py .

CMD ["/app/passplotter.py"]
