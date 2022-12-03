# the-next-java
Data Mapping and Validation for Project sample_project

### Front Door API

The Front Door API is a Python-based API that handles interaction with the user interface to an Azure Storage account backend. The API features the following routes:

* Upload File - Upload a file to the Azure Storage account
* Get File - Retrieve a file from the Azure Storage account
* Probability - Run data processing on your uploaded data to gain a probability on which fields from your data match up to org Payment Integrity data
* Mapping - After specifying which fields match the org Payment Integrity (OPI) fields, map your provided data to OPI's fields
* Validation -  After mapping the data to org Payment Integrity (OPI) fields, run validation against a rules engine to verify the data matches with OPI's fields

### Route Syntax for Front Door API

* Upload - upload (**NOTE**: Uses an xhr request to send form data)
* Get File - file/YourFileName
* Probability - probability?filename=YourFileName.xlsx
* Mapping - mapping?filename=YourFileName.xlsx
* Validation - validation?filename=mapped_data.xlsx

Please see [FlaskProvider.py](https://github.com/project-sample_project/the-next-java/blob/dev/FlaskProvider.py) for source code on routes.

### Building the Front Door API Using Docker

To build the Front Door API, a Docker image was produced in that runs `FlaskProvider.py`. Using this code requires an Azure Storage account and a blob storage container. After creating your Azure Storage account and container, the Docker image can be built with the following command in the repo directory:

`docker build --build-arg PASSWORD=<Enter Encryption Password> --build-arg STORAGE_KEY=<Azure Storage Key Here> -t frontdoorapi:latest .`

**Note**: The PASSWORD parameter can be anything you choose. It is used to encrypt and decrypt your Azure Storage account key while stored in the Docker container.

Next, you can run the image locally with the following command:

`docker run -p 5000:5000 frontdoorapi:latest`

You should now have the Front Door API running locally at port 5000 and it should be configured with your Azure Storage account.

### Azure Deployment

This documentation assumes you have created an [Azure Container Registry](https://azure.microsoft.com/en-us/services/container-registry/), have installed the [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli?view=azure-cli-latest), have installed the [Kubernetes CLI](https://kubernetes.io/docs/tasks/tools/install-kubectl/), and have created an [Azure service principal](https://docs.microsoft.com/en-us/azure/azure-resource-manager/resource-group-create-service-principal-portal).

The Front Door API can be deployed to an Azure Kubernetes cluster using the following steps:

1. Build the docker image locally with the docker build command shown above under Building the Front Door API Using Docker section
2. Tag your image locally:
  `docker tag frontdoorapi:latest <Your Container Registry>.azurecr.io/<Your Registry Name>`
3. Push the image to the Azure Container Registry:
  `docker push <Your Container Registry>.azurecr.io/<Your Registry Name>`
4. Create a resource group using the Azure CLI:
  `az group create --name FrontDoorAPI --location eastus`
5. Create a Kubernetes cluster:
  `az aks create --resource-group FrontDoorAPI  --name frontdoorapicluster --node-count 1 --generate-ssh-keys --service-principal <Enter App ID for Service Principal> --client-secret <Enter Client Secret for Service Principal> --admin-username k8fduser --kubernetes-version 1.8.7`
6. Get the cluster credentials:
  `az aks get-credentials --resource-group FrontDoorAPI --name frontdoorapicluster`
7. Create Docker registry secret using Kubernetes CLI:
  `kubectl create secret docker-registry regsecret --docker-server=apicatalogcontainerregistry.azurecr.io --docker-username=<Enter Azure Container Registry Username> --docker-password=<Enter Azure Container Registry Password> --docker-email=x`
8. Create static ip and dns name for Front Door API:
  `az network public-ip create -g MC_FrontDoorAPI_frontdoorapicluster_eastus -n MyIpName --dns-name frontdoorapicluster --allocation-method Static`
9. Enter the static ip returned by the previous command into the `application.yml` file in this repo and deploy the Front Door API Docker container to the cluster:
  `kubectl create -f application.yml`

The Front Door API should now be deployed to a Kubernetes cluster in Azure and can be accessed at frontdoorapicluster.eastus.cloudapp.azure.com.
