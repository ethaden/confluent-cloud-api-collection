import argparse
import json
import yaml


def extract_tag_groups(yaml_data):
    tag_to_group = {}
    group_names = []
    tag_groups = yaml_data.get("x-tagGroups", [])
    for group in tag_groups:
        group_name = group.get("name")
        group_names.append(group_name)
        tags = group.get("tags", [])
        for tag in tags:
            tag_to_group[tag] = group_name
    return tag_to_group, group_names

def update_host_base_url(grouped_structure):
    groups = grouped_structure.get("item", [])
    for group in groups:
        group_name = group.get("name")
        api_sub_groups = group.get("item")
        for api_sub_group in api_sub_groups:
          api_sub_group_items = api_sub_group.get("item")
          for api_sub_group_item in api_sub_group_items:
            request = api_sub_group_item.get("request")
            request_url = request.get("url")
            request_url["host"] = [get_host_base_url(group_name)]

def get_host_base_url(group_name: str):
    if group_name=="Kafka API (v3)":
        return "{{CONFLUENT_CLOUD_CLUSTER_API_ENDPOINT}}"
    if group_name=="Metrics API (v2)":
        return "{{CONFLUENT_CLOUD_METRICS_API_ENDPOINT}}"
    if group_name=="Schema Registry API (v1)" or group_name=="Catalog API":
        return "{{CONFLUENT_CLOUD_STREAM_GOVERNANCE_API_ENDPOINT}}"
    if group_name=="SQL API (v1)":
        return "{{CONFLUENT_CLOUD_FLINK_API_ENDPOINT}}"
    return "{{CONFLUENT_CLOUD_BASE_URL}}"

def generate_basic_auth_json(username: str, password: str):
    auth_dict = {}
    auth_dict["type"] = "basic"
    auth_dict["basic"] = [
      {
				"key": "password",
				"value": f"{password}",
				"type": "string"
			},
			{
				"key": "username",
				"value": f"{username}",
				"type": "string"
			}
    ]
    return auth_dict

def remove_key (sub_dict: {}, key: str):
    if key in sub_dict:
      sub_dict.pop(key)
    if "request" in sub_dict:
        sub_dict.get("request").pop(key)
    for item in sub_dict.get("item", []):
        remove_key(item, key)
    

def add_basic_auth_json(grouped_structure):
    # remove auth everywhere
    remove_key(grouped_structure, "auth")
    grouped_structure["auth"] = generate_basic_auth_json(username="{{CONFLUENT_CLOUD_API_KEY}}", password="{{CONFLUENT_CLOUD_API_SECRET}}")
    for group in grouped_structure.get("item", []):
        group_name = group.get("name")
        if group_name=="Kafka API (v3)":
            group["auth"] = generate_basic_auth_json(username="{{CONFLUENT_CLOUD_CLUSTER_API_KEY}}", password="{{CONFLUENT_CLOUD_CLUSTER_API_SECRET}}")
        elif group_name=="Schema Registry API (v1)" or group_name=="Catalog API":
          group["auth"] = generate_basic_auth_json(username="{{CONFLUENT_CLOUD_STREAM_GOVERNANCE_API_KEY}}", password="{{CONFLUENT_CLOUD_STREAM_GOVERNANCE_API_SECRET}}")
        elif group_name=="SQL API (v1)":
          group["auth"] = generate_basic_auth_json(username="{{CONFLUENT_CLOUD_FLINK_API_KEY}}", password="{{CONFLUENT_CLOUD_FLINK_API_SECRET}}")
        elif group_name=="Security Token Service (v1)":
          group["auth"] = { "type": "noauth" }
    
def disable_query_parameters(grouped_structure):
    groups = grouped_structure.get("item", [])
    for group in groups:
        api_sub_groups = group.get("item")
        for api_sub_group in api_sub_groups:
          api_sub_group_items = api_sub_group.get("item")
          for api_sub_group_item in api_sub_group_items:
            request = api_sub_group_item.get("request")
            request_url = request.get("url")
            query_params = request_url.get("query")
            for query_param in query_params:
                if "disabled" in query_param:
                    query_param["disabled"] = True
                    if "description" in query_param:
                      description=query_param.get("description")
                      if "content" in description:
                          content = description.get("content")
                          if "(Required)" in content:
                              query_param["disabled"] = False
                    

def reorganize_by_groups(json_data, tag_to_group, group_names):
    grouped_structure = {"item": []}

    for group_name in group_names:
        group_item = {
            "name": group_name,
            "item": []
        }
        grouped_structure["item"].append(group_item)

    original_items = json_data.get("item", [])
    for item in original_items:
        item_name = item.get("name")
        if item_name in tag_to_group:
            target_group = tag_to_group[item_name]
            for group_item in grouped_structure["item"]:
                if group_item["name"] == target_group:
                    group_item["item"].append(item)
                    break

    if "event" in json_data:
        grouped_structure["event"] = json_data["event"]

    new_variables = []
    new_variables.append({"key": "CONFLUENT_CLOUD_BASE_URL", "value": "https://api.confluent.cloud"})
    new_variables.append({"key": "CONFLUENT_CLOUD_API_KEY", "value": ""})
    new_variables.append({"key": "CONFLUENT_CLOUD_CLUSTER_API_ENDPOINT", "value": ""})
    new_variables.append({"key": "CONFLUENT_CLOUD_CLUSTER_API_KEY", "value": ""})
    new_variables.append({"key": "CONFLUENT_CLOUD_CLUSTER_API_SECRET", "value": ""})
    new_variables.append({"key": "CONFLUENT_CLOUD_STREAM_GOVERNANCE_API_ENDPOINT", "value": ""})
    new_variables.append({"key": "CONFLUENT_CLOUD_STREAM_GOVERNANCE_API_KEY", "value": ""})
    new_variables.append({"key": "CONFLUENT_CLOUD_STREAM_GOVERNANCE_API_SECRET", "value": ""})
    new_variables.append({"key": "CONFLUENT_CLOUD_FLINK_API_ENDPOINT", "value": ""})
    new_variables.append({"key": "CONFLUENT_CLOUD_FLINK_API_KEY", "value": ""})
    new_variables.append({"key": "CONFLUENT_CLOUD_FLINK_API_SECRET", "value": ""})
    new_variables.append({"key": "CONFLUENT_CLOUD_METRICS_API_ENDPOINT", "value": "https://api.telemetry.confluent.cloud"})
    new_variables.append({"key": "id", "value": "<string>"})
    grouped_structure["variable"] = new_variables

    if "info" in json_data:
        grouped_structure["info"] = json_data["info"]
    
    update_host_base_url(grouped_structure)
    add_basic_auth_json(grouped_structure)
    disable_query_parameters(grouped_structure)

    return grouped_structure


def main():
    parser = argparse.ArgumentParser(description="Parse OpenAPI YAML and Postman collection JSON files")
    parser.add_argument(
        "yaml_file",
        default="openapi.yaml",
        help="Path to the OpenAPI YAML file (default: openapi.yaml)"
    )
    parser.add_argument(
        "json_file",
        default="collection.json",
        help="Path to the Postman collection JSON file (default: collection.json)"
    )
    parser.add_argument(
        "output_file",
        default="grouped_collection.json",
        help="Path to the final grouped Postman collection JSON file (default: grouped_collection.json)"
    )
    args = parser.parse_args()

    try:
        with open(args.yaml_file, "r") as f:
            yaml_data = yaml.safe_load(f)
        print(f"Successfully parsed YAML file: {args.yaml_file}")
    except FileNotFoundError:
        print(f"Error: YAML file not found: {args.yaml_file}")
        return
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file: {e}")
        return

    try:
        with open(args.json_file, "r") as f:
            json_data = json.load(f)
        print(f"Successfully parsed JSON file: {args.json_file}")
    except FileNotFoundError:
        print(f"Error: JSON file not found: {args.json_file}")
        return
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON file: {e}")
        return

    tag_to_group, group_names = extract_tag_groups(yaml_data)
    print(f"Extracted {len(tag_to_group)} tag-to-group mappings")
    print(f"Found {len(group_names)} groups: {group_names}")

    grouped_data = reorganize_by_groups(json_data, tag_to_group, group_names)
    print(f"Reorganized JSON into {len(grouped_data['item'])} groups")

    output_file = "grouped_collection.json"
    with open(args.output_file, "w") as f:
        json.dump(grouped_data, f, indent=2)
    print(f"Saved reorganized collection to {output_file}")


if __name__ == "__main__":
    main()
