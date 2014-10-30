FROM registry

RUN pip install azure

ENV DOCKER_REGISTRY_CONFIG /azure-driver/config/config_sample.yml

ENV SETTINGS_FLAVOR azureblob

COPY . /azure-driver

RUN cd /azure-driver && python ./setup.py install
