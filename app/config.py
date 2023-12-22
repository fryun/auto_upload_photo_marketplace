import os
import pathlib

CONSTANTA_INT = ["HARGA_FOTO", "BANYAK_BROWSER"]
            
class Config:
    ROOT_DIR = str(pathlib.Path(__file__).parent.parent.absolute())
    UPLOAD_IMAGE_DIR = os.path.join(ROOT_DIR, "upload_file")
    DRIVER_PATH = os.path.join(ROOT_DIR, "chromedriver", "chromedriver")
    LOCAL_IMG_SRC_DIR = os.path.join(ROOT_DIR,"image")
    FOLDER_DONE = "_upload_selesai"
    
    SUMBER_FOTO:str
    USERNAME:str
    PASSWORD:str
    FOTO_TREE:str
    HARGA_FOTO:int
    BANYAK_BROWSER:int
    DESKRIPSI:str
    TESTING:str
    
    DCIM_FOLDER = "DCIM"
    FOTO_FOLDER = "FOTO"
    SUB_FOTO_FOLDER = "SUB_FOTO"
    FOTOYU_PROFILE:str = "https://www.fotoyu.com/profile/"

    def __init__(self) -> None:

        with open("config.txt", "r") as f:
            for line in f.readlines():
                text = line.split("=")
                var = text[0]
                value = text[1].replace("\n","")
                
                if var in CONSTANTA_INT:
                    self.__setattr__(var, int(value))
                else:
                    self.__setattr__(var, value)
                    

config = Config()

