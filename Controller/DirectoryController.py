import  os,re
from flask import jsonify

ENV_FILE_PATH = 'directory.env'
# ENV_FILE_PATH = 'directory1.env'

class DirectoryController():

    # 🔁 Reusable helper to get latest ROOT_DIR path
    @staticmethod
    def get_latest_directory():
        if not os.path.exists(ENV_FILE_PATH):
            return None

        latest_path = None
        latest_index = 0
        root_dir_pattern = re.compile(r'^ROOT_DIR(\d+)=(.*)')

        with open(ENV_FILE_PATH, 'r') as file:
            for line in file:
                match = root_dir_pattern.match(line.strip())
                if match:
                    index = int(match.group(1))
                    path = match.group(2)
                    if index > latest_index:
                        latest_index = index
                        latest_path = path
        return latest_path
       
        
    
    @staticmethod
    def add_directory_path(new_path):

        if not new_path:
            return jsonify({"error": "Missing 'path' in request body"}), 400

        # Ensure .env exists
        if not os.path.exists(ENV_FILE_PATH):
            open(ENV_FILE_PATH, 'w').close()

        # Read existing lines
        with open(ENV_FILE_PATH, 'r') as file:
            lines = file.readlines()

        # Find the last ROOT_DIRX key
        root_dir_pattern = re.compile(r'^ROOT_DIR(\d+)=')
        max_index = 0
        for line in lines:
            match = root_dir_pattern.match(line)
            if match:
                index = int(match.group(1))
                max_index = max(max_index, index)

        new_key = f"ROOT_DIR{max_index + 1}"
        with open(ENV_FILE_PATH, 'a') as file:
            normalized_root_dir = new_path.replace("\\", "/")
            file.write(f"{new_key}={normalized_root_dir}\n")
        
        return jsonify({"message": "Path added successfully", "key": new_key}), 200