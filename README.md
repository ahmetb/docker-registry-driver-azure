docker-registry-driver-azure
============================

Microsoft Azure Blob Storage Driver for [docker-registry][docker-registry].

This project is built on [Docker Global Hack Day #2][hackday].

Usage:

    docker run -p 5000:5000 \
    	-e AZURE_STORAGE_ACCOUNT_NAME="<my acct>" \
    	-e AZURE_STORAGE_ACCOUNT_KEY="<my key>" \
    	-e AZURE_STORAGE_CONTAINER=<container name e.g. registry> \
    	ahmetalpbalkan/registry-azure

Detailed instructions can be found on Azure Blog:
[Deploying Your Own Private Docker Registry on Azure](azure-tutorial).


License
=======

Copyright 2014 Ahmet Alp Balkan

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

[docker-registry]: https://github.com/docker/docker-registry
[hackday]: https://blog.docker.com/2014/10/announcing-docker-global-hack-day-2/
[azure-tutorial]: http://azure.microsoft.com/blog/2014/11/11/deploying-your-own-private-docker-registry-on-azure/
