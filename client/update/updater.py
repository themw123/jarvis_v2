import json
import os
import platform
import shutil
import subprocess
import sys
import time
import zipfile
import requests


class Updater:
    
    def __init__(self, config):
        self.config = config
        self.sha = None

    def run(self):
        if len(sys.argv) > 1:
            print("\n- deleting old version...")
            old_dir = sys.argv[1]
            shutil.rmtree(old_dir)
            return
            
        update_url = self.check_for_update()
        if update_url:
            user_input = input("\n- do you want to install the update? (yes/no): ")
            if user_input.lower() == 'yes':
                self.download_update(update_url)
                
    def check_for_update(self):
        api_url = "https://api.github.com/repos/themw123/jarvis_v2/releases/latest"
        try:
            response = requests.get(api_url)
            latest_release = response.json()
            self.sha = latest_release['id']
            if self.sha != self.config["version"]:
                print(f"\n- update available with sha: {self.sha}")
                return latest_release['assets'][0]['browser_download_url']
            else:
                return None
        except Exception as e:
            print(f"Error in checking for updates: {e}")
            return None

    def download_update(self, download_url):
        os_type = platform.system()
        name = "exe.linux-x86_64-3.11_" + str(self.sha)
        current_dir = os.path.dirname(os.path.realpath(__file__))
        
        #testing on linux only
        old_dir = "/home/marvin/code/private/jarvis_v2/client/build/test"
        
        current_dir = os.path.abspath(os.path.join(current_dir, ".."))
        
        program_name = sys.argv[0]
        extension = os.path.splitext(program_name)[1]

        if extension != ".py":
            old_dir = os.path.basename(os.path.dirname(os.path.dirname(current_dir)))
            current_dir = os.path.abspath(os.path.join(current_dir, "..", ".."))
        else:
            current_dir = os.path.abspath(os.path.join(current_dir, "build", name))
        os.makedirs(current_dir, exist_ok=True)
        
        #delete everything to be sure
        shutil.rmtree(current_dir); os.makedirs(current_dir, exist_ok=True)
        
        update_file = os.path.join(current_dir, 'update.zip')
        print("\n- downloading update...")
        response = requests.get(download_url, stream=True)
        
        total_size = int(response.headers.get('content-length', 0))
        chunk_size = 1024
        downloaded_size = 0

        print("")
        with open(update_file, 'wb') as f:
            for data in response.iter_content(chunk_size=chunk_size):
                downloaded_size += len(data)
                f.write(data)
                progress = (downloaded_size / total_size) * 100
                print(f"- progress: {progress:.2f}%", end='\r')
        print("\n\n- download complete")
    
        print("\n- extracting update...")
        
        with zipfile.ZipFile(update_file, 'r') as zip_ref:
            zip_ref.extractall(current_dir)
        print("\n- update extracted")       
        
        
        print("\n- cleaning up...") 
        os.remove(update_file)
        subdirs = [d for d in os.listdir(current_dir) if os.path.isdir(os.path.join(current_dir, d))]
        subdir_path = os.path.join(current_dir, subdirs[0])

        for item in os.listdir(subdir_path):
            item_path = os.path.join(subdir_path, item)
            shutil.move(item_path, current_dir)

        if os_type == "Linux":
            assisstant_path_linux = os.path.join(current_dir, 'assisstant')
            os.chmod(assisstant_path_linux, 0o755)
        

        os.rmdir(subdir_path)        
        os.rename(os.path.join(current_dir, "example.config.json"), os.path.join(current_dir, "config.json"))
        
        self.config["version"] = str(self.sha)
        with open(os.path.join(current_dir, "config.json"), "w", encoding="utf-8") as file:
            json.dump(self.config, file, indent=4, ensure_ascii=False)      
       
        
        print("\n- update complete.")
        time.sleep(2)

        
        #if extension == ".py":
        #    sys.exit() 
            
        print("\n- restarting with new version ...")
        time.sleep(2)
        if os_type == "Windows":
            updated_client = os.path.join(update_file, 'assisstant.exe')
            subprocess.Popen([updated_client, old_dir], creationflags=subprocess.CREATE_NEW_CONSOLE)
            sys.exit()
        elif os_type == "Linux":
            #updated_client = os.path.join(current_dir, 'assisstant')
            updated_client = os.path.join(os.path.dirname(current_dir), 'new', 'assisstant')
            #subprocess.Popen(["gnome-terminal", "--", "python3", updated_client], cwd=old_dir)
            emulators = "gnome-terminal"
            cmd = [emulators, "--", updated_client, old_dir]
            subprocess.Popen(cmd)
            
            sys.exit()
        else:
            print("\n- unsupported os")
            sys.exit()
        
        
            
          
    
        
