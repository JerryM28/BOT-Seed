import requests
import time
import sys
import os
import datetime
import pytz
from colorama import init, Fore, Style

init(autoreset=True)

# URL endpoint
url_claim = 'https://elb.seeddao.org/api/v1/seed/claim'
url_balance = 'https://elb.seeddao.org/api/v1/profile/balance'
url_checkin = 'https://elb.seeddao.org/api/v1/login-bonuses'
url_upgrade_storage = 'https://elb.seeddao.org/api/v1/seed/storage-size/upgrade'
url_upgrade_mining = 'https://elb.seeddao.org/api/v1/seed/mining-speed/upgrade'
url_upgrade_holy = 'https://elb.seeddao.org/api/v1/upgrades/holy-water'
url_get_profile = 'https://elb.seeddao.org/api/v1/profile'

# Headers yang diperlukan untuk request
headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'en-ID,en-US;q=0.9,en;q=0.8,id;q=0.7',
    'content-length': '0',
    'dnt': '1',
    'origin': 'https://cf.seeddao.org',
    'priority': 'u=1, i',
    'referer': 'https://cf.seeddao.org/',
    'sec-ch-ua': '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'telegram-data': 'tokens',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
}

# Variabel global untuk menyimpan hasil konfirmasi
confirm_storage = ''
confirm_mining = ''
confirm_holy = ''
confirm_task = ''

def print_welcome_message():
    print(f"{Fore.GREEN + Style.BRIGHT}AI Seed BOT")
    print(f"{Fore.GREEN + Style.DIM}JerryM")
    print(f"{Fore.GREEN + Style.DIM}-------------------------------------------")

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def load_credentials():
    try:
        with open('query.txt', 'r') as file:
            tokens = file.read().strip().split('\n')
        return tokens
    except FileNotFoundError:
        print(f"{Fore.RED + Style.BRIGHT}File 'query.txt' not found.")
        return []
    except Exception as e:
        print(f"{Fore.RED + Style.BRIGHT}Error loading tokens: {str(e)}")
        return []

def check_worm():
    try:
        response = requests.get('https://elb.seeddao.org/api/v1/worms', headers=headers)
        if response.status_code == 200:
            worm_data = response.json()['data']
            next_refresh = worm_data['next_refresh']
            is_caught = worm_data['is_caught']

            next_refresh_dt = datetime.datetime.fromisoformat(next_refresh[:-1] + '+00:00')
            now_utc = datetime.datetime.now(pytz.utc)
            time_diff_seconds = (next_refresh_dt - now_utc).total_seconds()
            hours = int(time_diff_seconds // 3600)
            minutes = int((time_diff_seconds % 3600) // 60)

            print(f"{Fore.WHITE + Style.BRIGHT}[Worms    🪱 ]:{Fore.WHITE + Style.BRIGHT} Next in {hours} hours {minutes} minutes")

            return worm_data
        else:
            print(f"{Fore.WHITE + Style.BRIGHT}[Worms    🪱 ]:{Fore.RED + Style.DIM} Failed to get data. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"{Fore.RED + Style.DIM}Exception in check_worm: {str(e)}")
        return None

def catch_worm():
    try:
        worm_data = check_worm()
        if worm_data and not worm_data['is_caught']:
            response = requests.post('https://elb.seeddao.org/api/v1/worms/catch', headers=headers)
            if response.status_code == 200:
                print(f"{Fore.WHITE + Style.BRIGHT}[Worms    🪱 ]:{Fore.GREEN + Style.BRIGHT} Successfully")
            elif response.status_code == 400:
                print(f"{Fore.WHITE + Style.BRIGHT}[Worms    🪱 ]:{Fore.GREEN + Style.BRIGHT} Already")
            elif response.status_code == 404:
                print(f"{Fore.WHITE + Style.BRIGHT}[Worms    🪱 ]:{Fore.RED + Style.DIM} Not found.")
            else:
                print(f"{Fore.WHITE + Style.BRIGHT}[Worms    🪱 ]:{Fore.RED + Style.DIM} Failed Status code: {response.status_code}")
        else:
            print(f"{Fore.WHITE + Style.BRIGHT}[Worms    🪱 ]:{Fore.RED + Style.DIM} Worm not available")
    except Exception as e:
        print(f"{Fore.RED + Style.BRIGHT}Exception in catch_worm: {str(e)}")

def get_profile():
    response = requests.get(url_get_profile, headers=headers)
    if response.status_code == 200:
        profile_data = response.json()
        name = profile_data['data']['name']
        print(f"{Fore.CYAN + Style.BRIGHT}{name}")
        upgrades = {}
        for upgrade in profile_data['data']['upgrades']:
            upgrade_type = upgrade['upgrade_type']
            upgrade_level = upgrade['upgrade_level']
            if upgrade_type in upgrades:
                if upgrade_level > upgrades[upgrade_type]:
                    upgrades[upgrade_type] = upgrade_level
            else:
                upgrades[upgrade_type] = upgrade_level
        for upgrade_type, level in upgrades.items():
            print(f"{Fore.BLUE + Style.DIM}[ {upgrade_type.capitalize()} Level ]: {level + 1}")
        return profile_data
    else:
        print(f"{Fore.RED + Style.BRIGHT}Gagal mendapatkan data, status code: {response.status_code}")
        return None

def check_balance():
    response = requests.get(url_balance, headers=headers)
    if response.status_code == 200:
        balance_data = response.json()
        print(f"{Fore.WHITE + Style.BRIGHT}[Balance  💰 ]:{Fore.YELLOW + Style.BRIGHT} {balance_data['data'] / 1000000000}")
        return True
    else:
        print(f"{Fore.WHITE + Style.BRIGHT}[Balance 💰 ]:{Fore.RED + Style.DIM} Gagal | {response.status_code}")
        return False

def cekin_daily():
    response = requests.post(url_checkin, headers=headers)
    if response.status_code == 200:
        data = response.json()
        day = data.get('data', {}).get('no', '')
        print(f"{Fore.WHITE + Style.BRIGHT}[Check-in ✅ ]:{Fore.GREEN + Style.BRIGHT} Check-in berhasil | Day {day}")
    else:
        data = response.json()
        if data.get('message') == 'already claimed for today':
            print(f"{Fore.WHITE + Style.BRIGHT}[Check-in ✅ ]:{Fore.GREEN + Style.BRIGHT} Sudah check-in")
        else:
            print(f"{Fore.WHITE + Style.BRIGHT}[Check-in ❌ ]:{Fore.RED + Style.DIM} Gagal | {data}")

def upgrade_storage():
    if confirm_storage.lower() == 'y':
        response = requests.post(url_upgrade_storage, headers=headers)
        if response.status_code == 200:
            return f"{Fore.WHITE + Style.BRIGHT}[Upgrade storage 🗃  ]:{Fore.GREEN + Style.BRIGHT} Berhasil"
        else:
            return f"{Fore.WHITE + Style.BRIGHT}[Upgrade storage 🗃  ]:{Fore.RED + Style.DIM} 💰 Tidak cukup"
    else:
        return None

def upgrade_mining():
    if confirm_mining.lower() == 'y':
        response = requests.post(url_upgrade_mining, headers=headers)
        if response.status_code == 200:
            return f"{Fore.WHITE + Style.BRIGHT}[Upgrade mining  ⛏  ]:{Fore.GREEN + Style.BRIGHT} Berhasil"
        else:
            return f"{Fore.WHITE + Style.BRIGHT}[Upgrade mining  ⛏  ]:{Fore.RED + Style.DIM} 💰 Tidak cukup"
    else:
        return None

def upgrade_holy():
    if confirm_holy.lower() == 'y':
        response = requests.post(url_upgrade_holy, headers=headers)
        if response.status_code == 200:
            return f"{Fore.WHITE + Style.BRIGHT}[Upgrade holy    💧 ]:{Fore.GREEN + Style.BRIGHT} Berhasil"
        else:
            return f"{Fore.WHITE + Style.BRIGHT}[Upgrade holy    💧 ]:{Fore.RED + Style.DIM} ❌ Gagal"
    else:
        return None

def get_tasks():
    response = requests.get('https://elb.seeddao.org/api/v1/tasks/progresses', headers=headers)
    tasks = response.json()['data']
    for task in tasks:
        if task['task_user'] is None or not task['task_user']['completed']:
            complete_task(task['id'], task['name'])

def complete_task(task_id, task_name):
    response = requests.post(f'https://elb.seeddao.org/api/v1/tasks/{task_id}', headers=headers)
    if response.status_code == 200:
        print(f"{Fore.GREEN + Style.BRIGHT}[Tasks ]:{Fore.GREEN + Style.DIM} Tugas {task_name} ✅")
    else:
        print(f"{Fore.RED + Style.DIM}[Tasks ]:{Fore.GREEN + Style.DIM} ❌ {task_name}, status code: {response.status_code}")

def main():
    global confirm_storage, confirm_mining, confirm_holy, confirm_task

    print_welcome_message()

    while True:
        try:
            tokens = load_credentials()  # Memuat ulang daftar token dari file query.txt

            # Meminta konfirmasi upgrade sekali saja sebelum loop
            if not confirm_storage or not confirm_mining or not confirm_holy or not confirm_task:
                default_confirm = 'y'  # Nilai default untuk konfirmasi
                confirm_storage = input(f"{Fore.YELLOW + Style.BRIGHT}Upgrade storage? (y/n): ").strip().lower() or default_confirm
                confirm_storage = confirm_storage if confirm_storage in ['y', 'n'] else default_confirm
                
                confirm_mining = input(f"{Fore.YELLOW + Style.BRIGHT}Upgrade mining?  (y/n): ").strip().lower() or default_confirm
                confirm_mining = confirm_mining if confirm_mining in ['y', 'n'] else default_confirm
                
                confirm_holy = input(f"{Fore.YELLOW + Style.BRIGHT}Upgrade holy?    (y/n): ").strip().lower() or default_confirm
                confirm_holy = confirm_holy if confirm_holy in ['y', 'n'] else default_confirm
                
                confirm_task = input(f"{Fore.YELLOW + Style.BRIGHT}Clear Task?      (y/n): ").strip().lower() or default_confirm
                confirm_task = confirm_task if confirm_task in ['y', 'n'] else default_confirm

            for index, token in enumerate(tokens):
                headers['telegram-data'] = token
                info = get_profile()
                if info:
                    hasil_upgrade = upgrade_storage() if confirm_storage == 'y' else None
                    hasil_upgrade1 = upgrade_mining() if confirm_mining == 'y' else None
                    hasil_upgrade2 = upgrade_holy() if confirm_holy == 'y' else None

                    if hasil_upgrade:
                        print(hasil_upgrade)
                        time.sleep(1)  # Menunggu 1 detik sebelum melanjutkan
                    if hasil_upgrade1:
                        print(hasil_upgrade1)
                        time.sleep(1)  # Menunggu 1 detik sebelum melanjutkan
                    if hasil_upgrade2:
                        print(hasil_upgrade2)
                        time.sleep(1)  # Menunggu 1 detik sebelum melanjutkan

                    if check_balance():
                        cekin_daily()
                        response = requests.post(url_claim, headers=headers)
                        if response.status_code == 200:
                            print(f"{Fore.WHITE + Style.BRIGHT}[Claim    🎁 ]:{Fore.GREEN + Style.BRIGHT} Claim ✅")
                        elif response.status_code == 400:
                            response_data = response.json()
                            print(f"{Fore.WHITE + Style.BRIGHT}[Claim    🎁 ]:{Fore.RED + Style.DIM} Belum waktunya")
                        else:
                            print(f"Terjadi kesalahan, status code: {response.status_code}")

                        catch_worm()
                        if confirm_task == 'y':
                            get_tasks()

            # Delay sebelum memulai kembali
            countdown_seconds = 1800
            for i in range(countdown_seconds, 0, -1):
                minutes = i // 60
                seconds = i % 60
                sys.stdout.write(f"\r{' ' * 30}")  # Menghapus baris sebelumnya
                sys.stdout.write(f"\r{Fore.YELLOW + Style.DIM}Tunggu {minutes} menit {seconds} detik..")
                sys.stdout.flush()
                time.sleep(1)

            # Membersihkan konsol setelah hitungan mundur
            sys.stdout.write(f"\r{''* (len('Tunggu {countdown_seconds} detik..') + 10)}\r")
            clear_console()

        except Exception as e:
            print(f"{Fore.RED + Style.BRIGHT}Exception in main loop: {str(e)}")
            continue

if __name__ == "__main__":
    main()
