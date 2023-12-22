import datetime
import os
import pathlib
import shutil
import time
from concurrent.futures import ProcessPoolExecutor
import random

import ait
import psutil
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import Chrome
from selenium.webdriver.common.action_chains import ActionChains 
from selenium.common.exceptions import NoSuchElementException

from app import utility as ut
from app.config import config

IMAGE_SRC = config.SUMBER_FOTO
ROOT_DIR = config.ROOT_DIR
UPLOAD_IMAGE_DIR = config.UPLOAD_IMAGE_DIR
DRIVER_PATH = config.DRIVER_PATH
LOCAL_IMG_SRC_DIR = config.LOCAL_IMG_SRC_DIR
FOLDER_DONE = config.FOLDER_DONE

MAX_PROCESS = config.BANYAK_BROWSER

FOTOYU_PROFILE = config.FOTOYU_PROFILE

USERNAME  = config.USERNAME
PASSWORD  = config.PASSWORD
FOTO_TREE = config.FOTO_TREE
HARGA_FOTO = config.HARGA_FOTO
DESKRIPSI = config.DESKRIPSI

DCIM_FOLDER = "DCIM"
FOTO_FOLDER = "FOTO"
SUB_FOTO_FOLDER = "SUB_FOTO"
DEFAULT_NUMBER = 0

SLEEP_STEP_SLENIUM = 2
SLEEP_AIT = 1
STEP_TIMEOUT = 10
COMPRESS_TIMEOUT = 900
UPLOAD_TIMEOUT = 1800



def get_images(image_src:str="local"):
    print("====================== START ======================")

    if image_src == "local":
        image_src_path = LOCAL_IMG_SRC_DIR
    
    if image_src == "sdcard":   
        sd_card = None
        
        #* Baca semua partisi yang ada di laptop
        partitions = psutil.disk_partitions()
        #* Cek partisi yang memiliki folder DCIM, sebagai tanda itu SD Card Kamera
        
        for partition in partitions:
            disk_usage = psutil.disk_usage(partition.mountpoint)
            folders = os.listdir(partition.mountpoint)
        
            if DCIM_FOLDER in folders:            
                print()
                print(f"Nama disk: {partition.mountpoint}")
                print(f"Ukuran disk: {format(disk_usage.total / 1024**3,'.2f')} GB")
                print(f"Penggunaan disk: {format(disk_usage.used / 1024**3,'.2f')} GB")
                print(f"Free space: {format(disk_usage.free / 1024**3,'.2f')} GB")
                print()
                sd_card = partition.mountpoint
    
        if not sd_card:
            raise Exception("sd card tidak ditemukan")
        image_src_path = pathlib.Path(os.path.join(sd_card, DCIM_FOLDER))
        
    print()
    print(f"Start memindahkan file dari {image_src_path} ke {UPLOAD_IMAGE_DIR}")
    
    image_folder = pathlib.Path(image_src_path)
    #* memberikan hak akses ke partisi sd card, untuk dapat memindahkan semua file
    os.chmod(image_folder, 0o755)
    
    #*folder target path
    target_folder = ut.create_folder_target()

    print(f"Proses pindah file")
    print(f"dari {image_folder}")
    print(f"ke {target_folder}")
    
    semua_foto = list(image_folder.rglob("*.JPG"))
    if not semua_foto:
        raise Exception (f"Tidak ada foto di {image_src_path}")
    
    total_foto = len(semua_foto)
    max_file_per_folder = round(total_foto/MAX_PROCESS)
    list_sub_foto_folder = []
    print()
    print(f"Total semua foto: {total_foto}")
    print(f"Akan dibagi ke: {MAX_PROCESS} folder")
    print(f"Tiap folder memiliki max foto: {max_file_per_folder}")
    print()
    
    for n in range(0, MAX_PROCESS):
        #* ambil sisa foto di dcim folder
        semua_foto = list(image_folder.rglob("*.JPG"))
        
        total_foto_yang_dimove = 0
        target_sub_folder = ut.create_sub_folder_target(target_folder)
        list_sub_foto_folder.append(target_sub_folder)

        print(f"Proses pindah foto ke sub folder")
        print(target_sub_folder)
        #* Proses move foto ke sub folder
        for foto in semua_foto:
            shutil.move(foto, target_sub_folder)
            if total_foto_yang_dimove == max_file_per_folder:
                break
            total_foto_yang_dimove += 1
        
        print(f"Total foto yang dimove: {total_foto_yang_dimove}")
        print(f"Sisa foto di sd card: {len(semua_foto)}")
        print()

    print("Proses pindah file sukses!")
    print()
    print("====================== END ======================")
    print()
    return target_folder, list_sub_foto_folder


def auto_upload(params):
    """
        upload dengan selenium ke Fotoyu
        kalau udah sukses upload rubah nama folder jadi _done_upload
    """
    sub_folder_foto, sleep_ait = params
    print(f"Start upload foto dari folder:[ait:{sleep_ait}] {sub_folder_foto}")
    
    auto_upload_start = time.perf_counter()
    
    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.get(FOTOYU_PROFILE)
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
    
    # Mencari tombol "Masuk" berdasarkan teks lengkap

    akun_saya_xpath =f"//*[contains(text(), 'Akun Saya')]"
    ut.action_click(
        driver=driver,
        element_value=akun_saya_xpath
        )
    
    masuk_xpath =f"//*[contains(@label, 'Masuk')]"
    ut.action_click(
        driver=driver,
        element_value=masuk_xpath
    )
    
    account_xpath =f"//*[contains(@name, 'account')]"
    input_account_value = USERNAME
    ut.action_input(
        driver=driver,
        element_value=account_xpath,
        input_value=input_account_value
    )

    password_xpath =f"//*[contains(@name, 'password')]"
    input_password_value = PASSWORD
    ut.action_input(
        driver=driver,
        element_value=password_xpath,
        input_value=input_password_value
    )    
    
    masuk_xpath =f"//*[contains(@label, 'Masuk')]"
    ut.action_click(
        driver=driver,
        element_value=masuk_xpath
    )
    
    akun_saya_xpath =f"//*[contains(text(), 'Akun Saya')]"
    ut.action_click(
        driver=driver,
        element_value=akun_saya_xpath
        )
    
    unggah_xpath =f"//*[contains(text(), 'Unggah')]"
    ut.action_click(
        driver=driver,
        element_value=unggah_xpath
        )

    jual_xpath =f"//*[contains(text(), 'Jual')]"
    ut.action_click(
        driver=driver,
        element_value=jual_xpath
    )
    
    # time.sleep(sleep_ait)
    mode_bulk_xpath =f"//*[contains(text(), 'Foto - Mode Bulk')]"
    ut.action_click(
        driver=driver,
        element_value=mode_bulk_xpath
    )
    
    input_xpath = "//p[contains(text(), 'Foto - Mode Bulk')]/preceding-sibling::input"
    list_foto = ut.get_list_foto(sub_folder_foto)
    print("list Foto: ", list_foto)
    
    ut.show_element(
        driver=driver, 
        element_type=By.XPATH,
        element_value=input_xpath
    )

    input_result = ut.action_input_many(
        driver=driver, 
        element_type=By.XPATH,
        element_value=input_xpath,
        input_value=list_foto
    )
    all_input = driver.execute_script("return document.querySelectorAll('input');")
    
    time.sleep(100)
    
    # print(f"Paste dir foto: {sub_folder_foto}")
    # time.sleep(SLEEP_AIT)
    # ait.write(sub_folder_foto)
    # ait.press('enter')

    # #* klik window foto
    # time.sleep(SLEEP_AIT)
    # ait.click(345, 269)

    compress_start = time.perf_counter()    
    # time.sleep(SLEEP_AIT)
    # ait.press('ctrl+a')
    # ait.press('enter')
    
    #* Update status
    time.sleep(SLEEP_AIT)
    ut.rename_folder(
        sub_folder_foto,
        status="_sedang_dikompres"
        )
    
    fototree_xpath =f"//input[@placeholder='Ketik nama FotoTree']"
    fototree_value = FOTO_TREE
    ut.action_input(
        driver=driver,
        element_value=fototree_xpath,
        input_value=fototree_value,
        step_timeout=COMPRESS_TIMEOUT
    )
    compress_end = time.perf_counter()
    #* Update status
    ut.rename_folder(
        sub_folder_foto,
        status="_kompres_selesai"
        )
    
    fototree_clik_xpath =f"//input[@value='{FOTO_TREE}']"
    ut.action_click(
        driver=driver,
        element_value=fototree_clik_xpath
        )
    
    fotoree_xpath =f"//div[contains(@class, 'ListItemSelect')]/p[contains(text(), '{FOTO_TREE}')]"
    ut.action_click(
        driver=driver,
        element_value=fotoree_xpath
        )
    
    price_xpath =f"//div[contains(@class, 'InputBase')]/input[@name='price']"
    ut.action_input(
        driver=driver,
        element_value=price_xpath,
        input_value=HARGA_FOTO
    )
    
    description_xpath =f"//textarea[@name='description']"
    ut.action_input(
        driver=driver,
        element_value=description_xpath,
        input_value=DESKRIPSI
    )
    
    #* Update status
    ut.rename_folder(
        sub_folder_foto,
        status="_sedang_diupload"
        )
        
    unggah_start = time.perf_counter()
    unggah_xpath =f"//div[@data-testid='button']/p[contains(text(),'Unggah')]"
    ut.action_click(
        driver=driver,
        element_value=unggah_xpath
        )
    
    unggah_xpath =f"//*[contains(text(), 'Sunting Profil')]"
    ut.action_click(
        driver=driver,
        element_value=unggah_xpath,
        step_timeout=UPLOAD_TIMEOUT
        )
    unggah_end = time.perf_counter()

    ut.rename_folder(sub_folder_foto)
    auto_upload_end = time.perf_counter()
    
    compress_total    = ut.convert_seconds_to_time(round(compress_end - compress_start))
    unggah_total      = ut.convert_seconds_to_time(round(unggah_end - unggah_start))
    auto_upload_total = ut.convert_seconds_to_time(round(auto_upload_end - auto_upload_start))
    
    print()
    print(f"======================= Upload Foto Selesai [{sleep_ait}] =======================")
    print(sub_folder_foto)
    print(f"Waktu Kompres Foto: {compress_total}")
    print(f"Waktu Unggah Foto: {unggah_total}")
    print(f"Waktu Auto Upload: {auto_upload_total}")
    print(f"======================= Upload Foto Selesai [{sleep_ait}] =======================")
    print()
    
    return driver


def main_upload():
    
    ut.starting_text()
    target_folder, target_sub_folder = get_images(IMAGE_SRC)
    os.chmod(target_folder, 0o755)

    if config.TESTING.lower() == "true":
        print("ini testing multiple upload local")
        param_auto_upload = (target_sub_folder[0], 15)
        auto_upload(param_auto_upload)
    else:
        print("ini multiple upload local")
        param_auto_upload = []
        ait_sleep = 2
        for sub_folder in target_sub_folder:
            param_auto_upload.append(
                (sub_folder, ait_sleep)
            )
            ait_sleep += 15
        
        print()
        print("====================== Start Upload ======================")
        with ProcessPoolExecutor(max_workers=MAX_PROCESS) as executor:
            results = executor.map(auto_upload, param_auto_upload)
        print("======================= End Upload =======================")
        print()
    
    time.sleep(10)
    ut.rename_folder(target_folder)


    
