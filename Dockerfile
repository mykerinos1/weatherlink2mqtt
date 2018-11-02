FROM seblucas/alpine-python3:latest
LABEL maintainer="Sebastien Lucas <sebastien@slucas.fr>"
LABEL Description="weatherlink2mqtt image"

COPY weatherlink2mqtt.py /usr/bin/weatherlink2mqtt.py
ADD https://gist.github.com/seblucas/0668844f2ef247993ff605f10014c1ed/raw/070321575dc656eee16ee6bfeb3f19aea56a4ac0/runCron.sh /bin/runCron.sh

RUN chmod +x /usr/bin/weatherlink2mqtt.py && \
    chmod +x /bin/runCron.sh

ENTRYPOINT ["runCron.sh"]

