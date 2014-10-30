# Copyright Ahmet Alp Balkan <ahmetalpbalkan@gmail.com>

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

FROM registry
MAINTAINER Ahmet Alp Balkan <ahmetalpbalkan at gmail.com>

ENV SETTINGS_FLAVOR azureblob

# Install Azure Python SDK
RUN pip install azure

# This should remain until config_sample.yml in docker/docker-registry
# gets the 'azure' section 'registry' image on Docker Hub is updated
# with the change.
ENV DOCKER_REGISTRY_CONFIG /azure-driver/config/config_sample.yml

COPY . /azure-driver

WORKDIR /azure-driver
RUN python ./setup.py install
