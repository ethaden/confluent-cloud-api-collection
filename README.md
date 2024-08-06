# Confluent Cloud API Collection for VS Code Postman

This is a Confluent Cloud API collection for the extension `Postman` for Visual Studio Code.
It is based on the OpenAPI specification released by Confluent, see https://docs.confluent.io/cloud/current.

CAUTION: Everything contained in this repository is not supported by Confluent.

DISCLAIMER AND WARNING: You use this code at your own risk! Please do not use it for production systems. The author may not be held responsible for any harm caused by this code!

## How to use
Install Visual Studio Code and the `Postman`` extension.

Log in to Postman with your account and choose a workspace.

Have fun with the API.

## How to update (full update)

* Export OpenAPI spec from Confluent Website.
* Import the spec into Postman as new collection. Set switches to always inherit authentication and to import based on tags instead of pathes.
* Delete old entries from existing collection one by one
* Copy new entries to the folders
* Replace basUrl everywhere (can be done with the Postman desktop client, left lower corner: `Find and replace`):
  * CONFLUENT_CLOUD_BASE_URL (in all cases except for the following ones. Suggestion: Start by running search and replace on this one, then fix all the ones listed below manually)
  * CONFLUENT_CLOUD_CLUSTER_API_ENDPOINT: In Kafka API (v3)
  * CONFLUENT_CLOUD_STREAM_GOVERNANCE_API_ENDPOINT: In Schema Registry API (v1) + Catalog API
  * CONFLUENT_CLOUD_FLINK_API_ENDPOINT: Only in SQL API (NOT in Compute Pool API!)

## How to update (internal, not recommended)

Download the latest OpenAPI spec from Confluent Cloud and save it as e.g. `openapi.json`.

Use the method described [here](https://blog.postman.com/creating-an-openapi-definition-from-a-collection-with-the-postman-api) to translate the current collection to OpenAPI.
First, set some environment variables:

```shell
export POSTMAN_APIKEY="<Put Postman API key here>"
export POSTMAN_COLLECTION="<Put Collection ID here>"
```

Then export to openapi format:

```shell
curl --location --request GET "https://api.getpostman.com/collections/${POSTMAN_COLLECTION}/transformations" \
--header "Content-Type: application/json" \
--header "x-api-key: ${POSTMAN_APIKEY}" | jq -r ".output | fromjson" > openapi-export.json
```

For identifying any calls not yet present in the postman collection, get all paths, sort them and compare them with each other.

```shell
cat openapi-export.json | jq -r ".paths | keys" > openapi-export-keys-sorted.json
cat openapi.json | jq -r ".paths | keys" > openapi-keys-sorted.json
```

Compare the result files `temp/openapi-export-keys-sorted.json` and `temp/openapi-keys-sorted.json` with each other to find the differences.

Then, create a new temporary collection in Postman and import the new openapi specification. Copy the missing API calls to the existing collection and delete the temporary collection.
