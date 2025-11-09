import subprocess
import sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

try:
    import psutil
except ImportError:
    print("[*] psutil 모듈이 없어 설치를 진행합니다...")
    install("psutil")
    import psutil

import shutil
import os
from uuid import uuid4
import time
import ctypes

def find_latest_roblox_player():
    base_dir = r"C:\Program Files (x86)\Roblox\Versions"
    if not os.path.exists(base_dir):
        print(f"[!] 폴더가 존재하지 않음: {base_dir}")
        return None

    latest_folder = None
    latest_time = 0

    for folder in os.listdir(base_dir):
        folder_path = os.path.join(base_dir, folder)
        if os.path.isdir(folder_path) and folder.startswith("version-"):
            exe_path = os.path.join(folder_path, "RobloxPlayerBeta.exe")
            if os.path.exists(exe_path):
                modified_time = os.path.getmtime(exe_path)
                if modified_time > latest_time:
                    latest_time = modified_time
                    latest_folder = folder_path

    if latest_folder:
        print(f"[+] 최신 Roblox 버전 경로 탐색 성공: {latest_folder}")
        return latest_folder
    else:
        print("[!] RobloxPlayerBeta.exe를 찾을 수 없습니다.")
        return None

def is_process_running(exe_name):
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'] and proc.info['name'].lower() == exe_name.lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return False

def kill_process_by_name(exe_name):
    killed = False
    for proc in psutil.process_iter(['name', 'pid']):
        try:
            if proc.info['name'] and proc.info['name'].lower() == exe_name.lower():
                proc.kill()
                killed = True
                print(f"[i] {exe_name} 프로세스 (PID {proc.pid}) 강제 종료 시도")
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            print(f"[!] 프로세스 종료 오류: {e}")
    return killed

def wait_for_process_exit(exe_name, timeout=20, check_interval=2):
    start = time.time()
    while is_process_running(exe_name):
        elapsed = time.time() - start
        if elapsed > timeout:
            print(f"[!] {exe_name} 프로세스 종료 대기 시간({timeout}s) 초과")
            return False
        print(f"[i] {exe_name} 프로세스 종료 대기 중...({int(elapsed)}s 경과)")
        time.sleep(check_interval)
    return True

def try_remove_file(path, retry=3, delay=1):
    for i in range(retry):
        try:
            if os.path.exists(path):
                os.remove(path)
                print(f"[+] 파일 삭제 성공: {path}")
                return True
            else:
                print(f"[!] 파일이 존재하지 않습니다: {path}")
                return True
        except Exception as e:
            print(f"[!] 파일 삭제 실패({i+1}/{retry}): {e}")
            time.sleep(delay)
    return False

def try_copy_file(src, dst, retry=3, delay=1):
    for i in range(retry):
        try:
            shutil.copyfile(src, dst)
            print(f"[+] 파일 복사 성공: {dst}")
            return True
        except Exception as e:
            print(f"[!] 파일 복사 실패({i+1}/{retry}): {e}")
            time.sleep(delay)
    return False

def try_remove_dir(path, retry=3, delay=1):
    for i in range(retry):
        try:
            if os.path.exists(path):
                shutil.rmtree(path, ignore_errors=False)
                print(f"[+] 폴더 삭제 성공: {path}")
                return True
            else:
                print(f"[!] 폴더가 존재하지 않습니다: {path}")
                return True
        except Exception as e:
            print(f"[!] 폴더 삭제 실패({i+1}/{retry}): {e}")
            time.sleep(delay)
    return False

def main():
    target_exe_name = "RobloxPlayerBeta.exe"
    original_dir = find_latest_roblox_player()

    if not original_dir:
        print("[!] Roblox 실행 파일을 찾을 수 없어 종료합니다.")
        return

    if is_process_running(target_exe_name):
        print(f"[!] {target_exe_name} 프로세스 실행 중입니다. 종료를 기다립니다...")
        if not wait_for_process_exit(target_exe_name):
            print("[!] 종료 대기 실패. 강제 종료 시도합니다.")
            if kill_process_by_name(target_exe_name):
                if not wait_for_process_exit(target_exe_name, timeout=10):
                    print("[!] 강제 종료 후에도 프로세스가 남아 있습니다. 종료 후 다시 시도하세요.")
                    return
            else:
                print("[!] 프로세스 종료 실패. 프로그램을 종료합니다.")
                return

    temp_dir = os.path.join(os.environ.get("TEMP", "C:\\Windows\\Temp"), "MicrosoftUpdater_" + uuid4().hex[:8])

    if not try_remove_dir(temp_dir):
        print("[!] 임시 폴더 삭제 실패. 계속 진행할 경우 문제가 생길 수 있습니다.")

    try:
        shutil.copytree(original_dir, temp_dir)
        print(f"[+] 원본 폴더 복사 완료: {temp_dir}")
    except Exception as e:
        print(f"[!] 폴더 복사 실패: {e}")
        try_remove_dir(temp_dir)
        return

    original_exe_in_temp = os.path.join(temp_dir, target_exe_name)
    fake_exe = original_exe_in_temp

    if not try_remove_file(original_exe_in_temp):
        print("[!] 임시 폴더 내 원본 실행 파일 삭제 실패. 계속 진행할 경우 문제가 발생할 수 있습니다.")

    if not try_copy_file(os.path.join(original_dir, target_exe_name), fake_exe):
        print("[!] 페이크 실행 파일 복사 실패. 작업을 종료합니다.")
        try_remove_dir(temp_dir)
        return

    vbs_path = os.path.join(temp_dir, "run.vbs")
    try:
        with open(vbs_path, "w", encoding="utf-8") as f:
            f.write('Set WshShell = CreateObject("WScript.Shell")\n')
            f.write(f'WshShell.Run """{fake_exe}""", 0, False\n')
        print(f"[+] VBScript 작성 완료: {vbs_path}")
    except Exception as e:
        print(f"[!] VBScript 작성 실패: {e}")
        try_remove_dir(temp_dir)
        return

    try:
        subprocess.Popen(["wscript", vbs_path], shell=False)
        print("[*] 백그라운드 실행 완료")
    except Exception as e:
        print(f"[!] VBScript 실행 실패: {e}")

if __name__ == "__main__":
    main()
