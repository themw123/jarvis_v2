import glob
import os
import platform
import shutil
import subprocess
import sys
import time
import requests
import zipfile

class Extracter:
    
    def __init__(self, config):
        self.config = config
        self.sha = None
        self.extension = os.path.splitext(sys.argv[0])[1]
        self.os_type = platform.system()
        self.cuda_archive_name = "cuda_dlls.zip"
        self.current_dir = os.path.dirname(os.path.realpath(__file__))
        self.torch_lib_dir = os.path.abspath(os.path.join(self.current_dir, "..", "torch", "lib"))
        
    def run(self):
        if self.os_type not in ['Windows']:
            print("\n- unsupported os. Only Windows and Linux are supported. Leaving updater...")
            return
        if self.extension == ".py":
            print("\n- you are in dev mode. Leaving extracter...")
            return
        
        available = self.exist_cuda_dlls()
        if not available:
            print("\n- did not found cuda dll's in lib/torch/lib, start downloading ...")
            path = self.download_cuda_archive()
            
            print("\n- start extracting ...")
            self.extract_cuda_archive(path)
        
    def exist_cuda_dlls(self):
        cuda_files = os.path.join(self.torch_lib_dir , "cudnn*")
        
        matching_files = glob.glob(cuda_files)
        
        return len(matching_files) > 0
    
    def download_cuda_archive(self):
        url = "https://drive.usercontent.google.com/download?id=1SQbeWv7NzbPlxfBHqHyL-2thIIHXeseQ&confirm=xxx"
        rar_filename = os.path.join(self.torch_lib_dir, self.cuda_archive_name)

        response = requests.get(url, stream=True)
        total_size = int(response.headers.get('content-length', 0))
        chunk_size = 1024
        downloaded_size = 0
        print("")
        with open(rar_filename, 'wb') as f:
            for data in response.iter_content(chunk_size=chunk_size):
                downloaded_size += len(data)
                f.write(data)
                progress = (downloaded_size / total_size) * 100
                print(f"- progress: {progress:.2f}%", end='\r')
        print("\n\n- download complete")
        
        return rar_filename
    
    def extract_cuda_archive(self, path):
        with zipfile.ZipFile(path, 'r') as zip_ref:
            zip_ref.extractall(self.torch_lib_dir)
        os.remove(path)
        
        cuda_dll_path = os.path.join(self.torch_lib_dir, "cuda_dlls")
        for file_name in os.listdir(cuda_dll_path):
            full_file_name = os.path.join(cuda_dll_path, file_name)
            if os.path.isfile(full_file_name):
                shutil.move(full_file_name, self.torch_lib_dir)
        os.rmdir(cuda_dll_path)
        print("\n- extraction complete, restarting ...")
            
        updated_client = os.path.abspath(os.path.join(self.current_dir, "..", "..", 'assisstant.exe'))
        subprocess.Popen([updated_client], creationflags=subprocess.CREATE_NEW_CONSOLE)
        sys.exit()
        