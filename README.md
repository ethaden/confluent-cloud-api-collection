# Confluent Cloud API Collection for VS Code Thunder Client

This is a Confluent Cloud API collection for the extension `Thunder Client` for Visual Studio Code.
It is based on the OpenAPI specification released by Confluent, see https://docs.confluent.io/cloud/current.

CAUTION: Everything contained in this repository is not supported by Confluent.

DISCLAIMER AND WARNING: You use this code at your own risk! Please do not use it for production systems. The author may not be held responsible for any harm caused by this code!

## How to use
Install Visual Studio Code and the Thunder Client extension.

In the "Thunder Client" extension view, open the `Env`tab and create a new environment, e.g. named `ConfluentCloud`. Point it to the file `env` found in this repository.
Adapt the `env` file to your needs (e.g. add all required API keys and the particular endpoints).

Then go to `Collections` and open its side menu. Import the file `thunder-collection_Confluent Cloud APIs.json`. Open `Settings` and choose your new environment.

Have fun with the API.
