import json
import os
import platform
import shutil
import subprocess
import sys
import time
import zipfile
import requests
import zipfile
#Do not remove this import, it is needed for cx_freeze to work correctly
import encodings.cp437 

class Updater:
    
    def __init__(self, config):
        self.config = config
        self.sha = None
        self.extension = os.path.splitext(sys.argv[0])[1]
        self.os_type = platform.system()
    def run(self):
        if self.os_type not in ['Windows', 'Linux']:
            print("\n- unsupported os. Only Windows and Linux are supported. Leaving updater...")
            return
        if self.extension == ".py":
            print("\n- You are in dev mode. Leaving updater...")
            return
        if len(sys.argv) > 1:
            try:
                print("\n- deleting old version...")
                old_dir = sys.argv[1]
                shutil.rmtree(old_dir)
            except Exception as e:
                print("\n- Could not delete folder of old version, because the terminal of the previous version is still open. Delete it by yourself.")
                return
            return
        else:
            print("\n- checking for updates...")
            
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
            self.sha = latest_release['tag_name'].replace("Release-", "")
            if self.sha != self.config["version"]:
                print(f"\n- update available with sha: {self.sha}")
                
                if self.os_type == "Windows":
                    client = "windows-client.zip"
                elif self.os_type == "Linux":
                    client = "linux-client.zip"
                
                for asset in latest_release['assets']:
                    if asset['name'] == client:
                        return asset['browser_download_url']
                print("\n- Could not find a release. Leaving updater...")
                return
            else:
                return None
        except Exception as e:
            print(f"Error in checking for updates: {e}")
            return None

    def download_update(self, download_url):
        if self.os_type == "Windows":
            name = "exe.win-amd64-3.11_" + str(self.sha)
        elif self.os_type == "Linux":
            name = "exe.linux-x86_64-3.11_" + str(self.sha)
            
        current_dir = os.path.dirname(os.path.realpath(__file__))
        
        #current_dir = os.path.abspath(os.path.join(current_dir, ".."))
        

        if self.extension != ".py":
            old_dir = os.path.abspath(os.path.join(current_dir, "..", ".."))
            current_dir = os.path.abspath(os.path.join(current_dir, "..", "..", "..", name))
        else:
            current_dir = os.path.abspath(os.path.join(current_dir, "..", "build", name))
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
            for file in zip_ref.namelist():
                zip_ref.extract(file, path=current_dir)
        print("\n- update extracted")       
        
        
        print("\n- cleaning up...") 
        os.remove(update_file)
        subdirs = [d for d in os.listdir(current_dir) if os.path.isdir(os.path.join(current_dir, d))]
        subdir_path = os.path.join(current_dir, subdirs[0])

        for item in os.listdir(subdir_path):
            item_path = os.path.join(subdir_path, item)
            shutil.move(item_path, current_dir)

        if self.os_type == "Linux":
            assisstant_path_linux = os.path.join(current_dir, 'assisstant')
            os.chmod(assisstant_path_linux, 0o755)
        

        os.rmdir(subdir_path)        
        os.rename(os.path.join(current_dir, "example.config.json"), os.path.join(current_dir, "config.json"))
        
        self.config["version"] = str(self.sha)
        with open(os.path.join(current_dir, "config.json"), "w", encoding="utf-8") as file:
            json.dump(self.config, file, indent=4, ensure_ascii=False)      
       
        
        print("\n- update complete.")
        time.sleep(2)
            
        print("\n- restarting with new version ...")
        time.sleep(2)
        if self.os_type == "Windows":
            updated_client = os.path.join(current_dir, 'assisstant.exe')
            print(old_dir)
            subprocess.Popen([updated_client, old_dir], creationflags=subprocess.CREATE_NEW_CONSOLE)
            sys.exit()
        elif self.os_type == "Linux":
            updated_client = os.path.join(current_dir, 'assisstant')
            emulators = "gnome-terminal"
            cmd = [emulators, "--", updated_client, old_dir]
            subprocess.Popen(cmd)
            sys.exit()

        
        
            
          
    
        
