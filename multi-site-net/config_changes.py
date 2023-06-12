import os
import yaml

def modify_config_file(file_path, changes):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    for change in changes.get('append', []):
        lines.append(change + '\n')

    for change in changes.get('replace', []):
        line_to_replace = change.get('line')
        new_line = change.get('new_line')
        lines = [new_line + '\n' if line.strip() == line_to_replace.strip() else line for line in lines]

    with open(file_path, 'w') as file:
        file.writelines(lines)

def find_config_file(node_type, asn, node_name, file_name):
    directory = f'output/{node_type}_{asn}_{node_name}'
    dockerfile_path = os.path.join(directory, 'Dockerfile')
    with open(dockerfile_path, 'r') as dockerfile:
        for line in dockerfile:
            if file_name in line:
                config_file = line.split()[1]
                return os.path.join(directory, config_file)

def main():
    config_file = 'config_changes.yaml'

    with open(config_file, 'r') as f:
        config_changes = yaml.safe_load(f)

    for change in config_changes:
        file_name = change.get('file')
        node_name = change.get('node_name')
        asn = change.get('asn')
        node_type = change.get('node_type')

        if node_type.lower() not in ['router', 'host']:
            print(f"Invalid node type '{node_type}' specified for node '{node_name}'.")
            continue

        node_type = f"rnode" if node_type.lower() == 'router' else f"hnode"
        config_file_path = find_config_file(node_type, asn, node_name, file_name)

        if config_file_path:
            modify_config_file(config_file_path, change)
            print(f"Config file '{file_name}' for node '{node_name}' modified successfully.")
        else:
            print(f"Config file '{file_name}' for node '{node_name}' not found.")

if __name__ == '__main__':
    main()
