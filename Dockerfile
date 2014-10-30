FROM registry

COPY . /azure-driver

RUN cd /azure-driver && python ./setup.py install

ENV DOCKER_REGISTRY_CONFIG /azure-driver/config/config_sample.yml

ENV SETTINGS_FLAVOR azure

EXPOSE 5000

CMD ["docker-registry"]

