import os
import pathlib
import sys
import time

from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import Chrome
from selenium.common.exceptions import TimeoutException
from art import text2art

from app.config import config


SLEEP_STEP_SLENIUM = 2
SLEEP_AIT = 1
STEP_TIMEOUT = 10
TIMEOUT_SHOW_ELEMENT = 2
DEFAULT_RETRY_SHOW_ELEMENT = 0
MAX_RETRY_SHOW_ELEMENT = 5
COMPRESS_TIMEOUT = 900
UPLOAD_TIMEOUT = 1800

DCIM_FOLDER = config.DCIM_FOLDER
FOTO_FOLDER = config.FOTO_FOLDER
SUB_FOTO_FOLDER = config.SUB_FOTO_FOLDER
FOLDER_DONE = config.FOLDER_DONE

ROOT_DIR = config.ROOT_DIR
UPLOAD_IMAGE_DIR = config.UPLOAD_IMAGE_DIR


def print_with_delay(text, delay):
    for char in text:
        print(char, end="")
        time.sleep(delay)
        sys.stdout.flush()
    time.sleep(0.3)


def starting_text():

    text = "Created By: ArdiYP"
    Art=text2art("Auto Upload","big")
    print(Art)
    print_with_delay(text,0.1)
    print()
    print()


def load_config():
    with open("config.txt", "r") as f:
        for line in f.readlines():
            text = line.split("=")
            var = text[0]
            value = text[1]
            os.environ[var] = value


def action_input(
        driver:Chrome, 
        element_value:str,
        input_value:str, 
        sleep=SLEEP_STEP_SLENIUM,
        element_type:str=By.XPATH,
        step_timeout=STEP_TIMEOUT
        ):
    time.sleep(SLEEP_STEP_SLENIUM)
    try:
        WebDriverWait(driver, step_timeout).until(EC.visibility_of_element_located((element_type, element_value)))
        element = find_element(driver, element_type, element_value)
        element.clear()
        element.send_keys(input_value)
    except Exception as err:
        msg = f"Gagal input value ke element: {element_value}"
        print(msg)
        print(f"Error: {err}", type(err))
        raise Exception(msg)


def action_click(
        driver:Chrome, 
        element_value:str,
        sleep=SLEEP_STEP_SLENIUM,
        element_type:str=By.XPATH,
        step_timeout=STEP_TIMEOUT
        ):
    time.sleep(SLEEP_STEP_SLENIUM)
    try:
        WebDriverWait(driver, step_timeout).until(EC.visibility_of_element_located((element_type, element_value)))
        element = find_element(driver, element_type, element_value)    
        element.click()
    except Exception as err:
        msg=f"Gagal klik element: {element_value}"
        print(msg)
        print(f"Error: {err}")
        raise Exception(msg)


def find_element(
    driver:Chrome, 
    by_type:By, 
    element_value:str, 
    is_list:bool=False,
    ):
    
    if is_list:
        element = driver.find_elements(
            by=by_type, 
            value=element_value
            )
    else:
        element = driver.find_element(
            by=by_type, 
            value=element_value
            )

    return element


def show_element(
    driver:Chrome, 
    element_value:str, 
    element_type:str=By.XPATH,
    step_timeout=STEP_TIMEOUT,
    retry=DEFAULT_RETRY_SHOW_ELEMENT
    ):

    element = driver.find_element(
        by=element_type, 
        value=element_value
        )
    driver.execute_script("arguments[0].style.display = 'block';", element)     

    try:
        WebDriverWait(driver, step_timeout).until(EC.visibility_of_element_located((element_type, element_value)))
    except TimeoutException:
        
        if retry == MAX_RETRY_SHOW_ELEMENT:
            raise TimeoutException
        
        retry += 1
        show_element(
            driver=driver, 
            element_value=element_value, 
            element_type=element_type,
            retry=retry
            )

    return element


def convert_seconds_to_time(seconds):
  """
  Mengubah format detik menjadi jam dengan format hh:mm:ss

  Args:
    seconds: Jumlah detik

  Returns:
    String yang berisi waktu dengan format hh:mm:ss
  """

  hours = seconds // 3600
  minutes = (seconds % 3600) // 60
  seconds = seconds % 60

  time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

  return time_str


def create_sub_folder_target(folder, sub_folder_number:int=1):
    folder_path = os.path.join(folder, SUB_FOTO_FOLDER + "_" + str(sub_folder_number))
    
    if os.path.exists(folder_path):
        folder_path = create_sub_folder_target(folder, sub_folder_number=sub_folder_number + 1)
    else:
        os.mkdir(folder_path)

    return folder_path


def create_folder_target(folder_number:int=0):
    folder_path = os.path.join(UPLOAD_IMAGE_DIR, FOTO_FOLDER + "_" + str(folder_number))
    
    if os.path.exists(folder_path) or os.path.exists(folder_path + FOLDER_DONE):
        folder_path = create_folder_target(folder_number=folder_number + 1)
    else:
        os.mkdir(folder_path)
        
    return folder_path


def rename_folder(folder_name, status=""):
    
    if status:
        rename_folder_name = folder_name + status
    else:
        rename_folder_name = folder_name + FOLDER_DONE
    
    os.rename(folder_name, rename_folder_name)
    print()
    print("============== Rename folder FOTO ==============")
    print(f"Rename folder: {folder_name}")
    print(f"menjadi folder: {rename_folder_name}")
    print("============== Rename folder FOTO ==============")
    print()
    
    return rename_folder_name


def action_input_many(
        driver:Chrome, 
        element_value:str,
        input_value:list, 
        sleep=SLEEP_STEP_SLENIUM,
        element_type:str=By.XPATH,
        step_timeout=STEP_TIMEOUT
    ):
    
    WebDriverWait(driver, step_timeout).until(EC.visibility_of_element_located((element_type, element_value)))
    element = find_element(
        driver=driver, 
        by_type=element_type,
        element_value=element_value
        )
    # for input in input_value:
    files = " \n ".join(input_value)
    print("==============================")
    print(files)
    print("==============================")
    element.send_keys(files)
    
    print(f"Sukses input many value ke element: {element_value}")
    

def get_list_foto(image_folder):
    
    image_folder = pathlib.Path(image_folder)    
    semua_foto = list(image_folder.rglob("*.JPG"))
    
    if not semua_foto:
        raise Exception (f"Tidak ada foto di {image_folder}")
    
    semua_foto_str = [str(path) for path in semua_foto]
    return semua_foto_str