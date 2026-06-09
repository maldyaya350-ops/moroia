import os
import sys
import time
import socket
import shutil
import subprocess
import requests
import threading
import gc
import json
import platform
from datetime import datetime, timedelta
from collections import deque
from typing import Dict, List, Optional, Tuple, Any

try:
    import psutil
except ImportError:
    psutil = None

try:
    from tabulate import tabulate
except ImportError:
    tabulate = None

# MAJOR RELEASE VERSION
VERSION = "3.6.0"
BUILD_DATE = "2026-06-09"

# ANSI Color Codes
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    HIDE_CURSOR = '\033[?25l'
    SHOW_CURSOR = '\033[?25h'
    CLEAR_SCREEN = '\033[2J\033[H'

class PerformanceMonitor:
    def __init__(self, max_history=60):
        self.cpu_history = deque(maxlen=max_history)
        self.ram_history = deque(maxlen=max_history)
        self.start_time = time.time()
        
    def update(self):
        if psutil:
            self.cpu_history.append(psutil.cpu_percent(interval=None))
            self.ram_history.append(psutil.virtual_memory().percent)
    
    def get_uptime_seconds(self):
        return int(time.time() - self.start_time)
    
    def get_uptime_string(self):
        uptime = self.get_uptime_seconds()
        hours = uptime // 3600
        minutes = (uptime % 3600) // 60
        seconds = uptime % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

class MoroiaEngine:
    def __init__(self):
        self.monitor = PerformanceMonitor()
        self.optimization_log = []
        self.cache_dir = os.path.join(os.environ.get('APPDATA', os.path.expanduser('~')), '.moroia')
        self.cache_file = os.path.join(self.cache_dir, 'update_cache.json')
        
    def check_for_updates(self):
        """Check for updates every 10 minutes"""
        now = datetime.now()
        should_check = False
        
        if not os.path.exists(self.cache_dir):
            try: os.makedirs(self.cache_dir)
            except: pass
            
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    data = json.load(f)
                    last_check_str = data.get('last_check', '')
                    if last_check_str:
                        last_check = datetime.strptime(last_check_str, "%Y-%m-%d %H:%M:%S")
                        if now - last_check > timedelta(minutes=10):
                            should_check = True
                    else:
                        should_check = True
            except:
                should_check = True
        else:
            should_check = True

        if not should_check:
            return

        try:
            with open(self.cache_file, 'w') as f:
                json.dump({'last_check': now.strftime("%Y-%m-%d %H:%M:%S")}, f)
        except:
            pass

        try:
            response = requests.get("https://pypi.org/pypi/moroia/json", timeout=2.0)
            if response.status_code == 200:
                res_json = response.json()
                latest_version = res_json["info"]["version"]
                
                if latest_version != VERSION:
                    print(f"\n{Colors.WARNING}⚠️ New version available: v{latest_version} (Current: v{VERSION}){Colors.ENDC}")
                    print(f"{Colors.CYAN}Run: pip install --upgrade moroia{Colors.ENDC}\n")
        except:
            pass

    @staticmethod
    def get_hardware_status():
        if not psutil: 
            return {"error": "psutil missing"}
        
        cpu_usage = psutil.cpu_percent(interval=0.1)
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        heavy_apps = []
        try:
            procs = []
            for p in psutil.process_iter(['name', 'memory_percent', 'cpu_percent']):
                try:
                    p_info = p.info
                    if p_info['name'] and not p_info['name'].startswith('['):
                        procs.append(p_info)
                except: continue
            procs.sort(key=lambda x: x.get('memory_percent', 0) or 0, reverse=True)
            for p in procs[:3]:
                mem_pct = p.get('memory_percent', 0) or 0
                if mem_pct > 0.1:
                    heavy_apps.append(f"{p['name']} ({mem_pct:.1f}%)")
        except: pass
        
        gpu_name = "Unknown"
        try:
            if platform.system() == "Windows":
                cmd = "wmic path win32_VideoController get name"
                gpu_out = subprocess.check_output(cmd, shell=True, text=True, timeout=2).split('\n')
                if len(gpu_out) > 1 and gpu_out[1].strip():
                    gpu_name = gpu_out[1].strip()[:30]
        except: pass
        
        return {
            "cpu_usage_pct": cpu_usage,
            "ram_total_gb": round(ram.total / (1024**3), 2),
            "ram_usage_pct": ram.percent,
            "ram_available_gb": round(ram.available / (1024**3), 2),
            "ram_used_gb": round((ram.total - ram.available) / (1024**3), 2),
            "disk_usage_pct": disk.percent,
            "disk_free_gb": round(disk.free / (1024**3), 2),
            "disk_total_gb": round(disk.total / (1024**3), 2),
            "gpu": gpu_name,
            "heavy_apps": heavy_apps
        }

    @staticmethod
    def spy_hunter_scan() -> List[Dict[str, Any]]:
        suspicious = []
        if not psutil: return suspicious
        try:
            connections = psutil.net_connections(kind='inet')
            for conn in connections:
                if conn.status == 'ESTABLISHED' and conn.raddr:
                    remote_ip = conn.raddr[0]
                    if remote_ip not in ['127.0.0.1', '::1', '0.0.0.0']:
                        pid = conn.pid
                        proc_name = "Unknown"
                        if pid:
                            try: proc_name = psutil.Process(pid).name()
                            except: continue
                        suspicious.append({"pid": pid, "process": proc_name[:20], "remote": f"{remote_ip}:{conn.raddr[1]}"})
        except: pass
        return suspicious[:5]

    @staticmethod
    def get_network_info():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
        except:
            local_ip = "127.0.0.1"
        
        public_ip = "Unknown"
        try:
            public_ip = requests.get("https://api.ipify.org", timeout=2).text.strip()
        except:
            pass
        
        return {"local": local_ip, "public": public_ip}

    @staticmethod
    def get_battery():
        if not psutil or not hasattr(psutil, "sensors_battery"):
            return None
        battery = psutil.sensors_battery()
        if battery:
            return {"percent": battery.percent, "plugged": battery.power_plugged}
        return None

    @staticmethod
    def get_startup_apps():
        """Get Windows startup applications"""
        startup_apps = []
        if platform.system() != 'Windows':
            return startup_apps
        
        startup_folder = os.path.join(os.environ.get('APPDATA', ''), r"Microsoft\Windows\Start Menu\Programs\Startup")
        if os.path.exists(startup_folder):
            for item in os.listdir(startup_folder):
                if os.path.isfile(os.path.join(startup_folder, item)):
                    startup_apps.append({"name": item, "type": "Folder"})
        return startup_apps

    @staticmethod
    def disable_startup_app(app_name: str) -> Tuple[bool, str]:
        """Disable a startup application"""
        if platform.system() != 'Windows':
            return False, "Not supported on this OS"
        
        startup_folder = os.path.join(os.environ.get('APPDATA', ''), r"Microsoft\Windows\Start Menu\Programs\Startup")
        file_path = os.path.join(startup_folder, app_name)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                return True, f"Removed {app_name} from startup"
            except Exception as e:
                return False, str(e)
        return False, "App not found"

    @staticmethod
    def clear_temp_files(safe_mode: bool = True) -> Dict[str, float]:
        """Clear temporary files"""
        if platform.system() != 'Windows':
            return {"freed_mb": 0, "files_deleted": 0}
        
        temp_paths = [os.environ.get('TEMP', ''), os.path.join(os.environ.get('SystemRoot', 'C:\\Windows'), 'Temp')]
        freed_bytes = 0
        files_deleted = 0
        
        for path in temp_paths:
            if not path or not os.path.exists(path):
                continue
            for filename in os.listdir(path):
                file_path = os.path.join(path, filename)
                try:
                    if safe_mode and time.time() - os.path.getmtime(file_path) < 3600:
                        continue
                    if os.path.isfile(file_path):
                        freed_bytes += os.path.getsize(file_path)
                        os.unlink(file_path)
                        files_deleted += 1
                except:
                    continue
        
        return {"freed_mb": round(freed_bytes / (1024**2), 2), "files_deleted": files_deleted}

    @staticmethod
    def clear_developer_cache() -> Dict[str, float]:
        """Clear developer caches (pip, npm, etc.)"""
        freed_bytes = 0
        if platform.system() == 'Windows':
            path = os.path.expanduser(r"~\AppData\Local\pip\cache")
        else:
            path = os.path.expanduser("~/.cache/pip")
        
        if os.path.exists(path):
            try:
                for root, dirs, files in os.walk(path):
                    for f in files:
                        try:
                            freed_bytes += os.path.getsize(os.path.join(root, f))
                        except:
                            pass
                shutil.rmtree(path, ignore_errors=True)
            except:
                pass
        
        return {"freed_mb": round(freed_bytes / (1024**2), 2)}

def print_banner():
    """Display Moroia banner"""
    banner = f"""
{Colors.CYAN}================================================================={Colors.ENDC}
{Colors.BOLD}{Colors.HEADER}      __  __  ____  _____   ____  _____  _      /\   {Colors.ENDC}
{Colors.BOLD}{Colors.HEADER}     |  \/  |/ __ \|  __ \ / __ \|_   _|| |    /  \  {Colors.ENDC}
{Colors.BOLD}{Colors.HEADER}     | \  / | |  | | |__) | |  | | | |  | |   /    \ {Colors.ENDC}
{Colors.BOLD}{Colors.HEADER}     | |\/| | |  | |  _  /| |  | | | |  | |  /  /\  \{Colors.ENDC}
{Colors.BOLD}{Colors.HEADER}     | |  | | |__| | | \ \| |__| |_| |_ | |_/ ____  \{Colors.ENDC}
{Colors.BOLD}{Colors.HEADER}     |_|  |_|\____/|_|  \_\\____/|_____||_/_/    \_\ {Colors.ENDC}
{Colors.BOLD}{Colors.CYAN}             🔥 MOROIA SECURITY & SYSTEMS v{VERSION} 🔥{Colors.ENDC}
{Colors.CYAN}================================================================={Colors.ENDC}
"""
    print(banner)

def print_dashboard(hw, network, battery, uptime_str, refresh_count, time_left):
    """Print dashboard with static display"""
    
    cpu_pct = hw['cpu_usage_pct']
    cpu_color = Colors.GREEN if cpu_pct < 60 else Colors.WARNING if cpu_pct < 80 else Colors.FAIL
    cpu_bar_length = int(cpu_pct / 2)
    cpu_bar = "█" * min(cpu_bar_length, 50) + "░" * (50 - min(cpu_bar_length, 50))
    
    ram_pct = hw['ram_usage_pct']
    ram_color = Colors.GREEN if ram_pct < 60 else Colors.WARNING if ram_pct < 80 else Colors.FAIL
    ram_bar_length = int(ram_pct / 2)
    ram_bar = "█" * min(ram_bar_length, 50) + "░" * (50 - min(ram_bar_length, 50))
    
    print(f"\n{Colors.BOLD}{Colors.CYAN}📊 SYSTEM MONITOR DASHBOARD{Colors.ENDC}")
    print(f"   Uptime: {Colors.GREEN}{uptime_str}{Colors.ENDC} | Auto-exit: {Colors.FAIL}{time_left}:00{Colors.ENDC}")
    print()
    
    print(f"   {Colors.BOLD}💻 CPU:{Colors.ENDC} {cpu_color}{cpu_pct}%{Colors.ENDC}  {cpu_bar}")
    print(f"   {Colors.BOLD}🧠 RAM:{Colors.ENDC} {ram_color}{ram_pct}%{Colors.ENDC}  {ram_bar}")
    print(f"   {Colors.BOLD}💾 RAM Details:{Colors.ENDC} {hw['ram_used_gb']} GB / {hw['ram_total_gb']} GB used ({hw['ram_available_gb']} GB free)")
    print(f"   {Colors.BOLD}💿 Disk:{Colors.ENDC} {hw['disk_usage_pct']}% used ({hw['disk_free_gb']} GB free of {hw['disk_total_gb']} GB)")
    print(f"   {Colors.BOLD}🎮 GPU:{Colors.ENDC} {hw['gpu']}")
    
    print(f"\n{Colors.BOLD}{Colors.CYAN}🌐 NETWORK{Colors.ENDC}")
    print(f"   Local IP: {Colors.GREEN}{network['local']}{Colors.ENDC}")
    print(f"   Public IP: {Colors.WARNING}{network['public']}{Colors.ENDC}")
    
    if battery:
        battery_color = Colors.GREEN if battery['percent'] > 50 else Colors.WARNING if battery['percent'] > 20 else Colors.FAIL
        status = "🔌 Charging" if battery['plugged'] else "🔋 Discharging"
        print(f"\n{Colors.BOLD}{Colors.CYAN}🔋 BATTERY{Colors.ENDC}")
        print(f"   {battery_color}{battery['percent']}%{Colors.ENDC} - {status}")
    
    if hw['heavy_apps']:
        print(f"\n{Colors.BOLD}{Colors.CYAN}🔥 TOP PROCESSES{Colors.ENDC}")
        for i, app in enumerate(hw['heavy_apps'][:3], 1):
            print(f"   {i}. {app}")
    
    spies = MoroiaEngine.spy_hunter_scan()
    if spies:
        print(f"\n{Colors.BOLD}{Colors.CYAN}🛡️ ACTIVE CONNECTIONS{Colors.ENDC}")
        for conn in spies[:3]:
            print(f"   {conn['process']} → {conn['remote']}")
    
    print(f"\n{Colors.CYAN}─────────────────────────────────────────────────────────────────{Colors.ENDC}")
    print(f"{Colors.WARNING}💡 Press Ctrl+C to open optimization menu{Colors.ENDC}")

def main():
    engine = MoroiaEngine()
    
    # Check updates
    engine.check_for_updates()
    
    # Clear screen and hide cursor
    print(f"{Colors.CLEAR_SCREEN}{Colors.HIDE_CURSOR}", end="")
    
    # Record start time (15 minutes auto-shutdown)
    start_time = time.time()
    
    print_banner()
    
    try:
        while True:
            current_time = time.time()
            
            # Auto-shutdown after 15 minutes
            elapsed_minutes = (current_time - start_time) / 60
            if elapsed_minutes >= 15:
                print(f"{Colors.CLEAR_SCREEN}")
                print(f"{Colors.GREEN}{Colors.BOLD}✅ Auto-shutdown completed after 15 minutes{Colors.ENDC}")
                print(f"{Colors.CYAN}Moroia System Suite - Session ended{Colors.ENDC}")
                break
            
            time_left = int(15 - elapsed_minutes)
            
            # Get fresh data
            hw = engine.get_hardware_status()
            if "error" in hw:
                print(f"{Colors.FAIL}Error: {hw['error']}{Colors.ENDC}")
                break
                
            network = MoroiaEngine.get_network_info()
            battery = MoroiaEngine.get_battery()
            uptime_str = engine.monitor.get_uptime_string()
            
            # Update monitor
            engine.monitor.update()
            
            # Move cursor to top and redraw
            print(f"\033[H", end="")
            print_banner()
            print_dashboard(hw, network, battery, uptime_str, 0, time_left)
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        print(f"{Colors.SHOW_CURSOR}", end="")
        print(f"\n\n{Colors.CLEAR_SCREEN}")
        print_banner()
        
        # Interactive menu
        print(f"\n{Colors.BOLD}{Colors.CYAN}═══════════════════════════════════════════════════════════{Colors.ENDC}")
        print(f"{Colors.BOLD}🛠️  OPTIMIZATION MENU{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.CYAN}═══════════════════════════════════════════════════════════{Colors.ENDC}")
        
        startup_apps = MoroiaEngine.get_startup_apps()
        
        print("[1] Clear System Temp Files")
        print("[2] Clear Developer Cache (PIP)")
        print("[3] Flush DNS Cache")
        print("[4] FULL AUTO-OPTIMIZATION")
        if startup_apps:
            print(f"[5] Manage Startup Apps ({len(startup_apps)} found)")
        print("[6] Exit")
        
        try:
            choice = input(f"\n{Colors.BOLD}Select (1-6): {Colors.ENDC}").strip()
            
            if choice == '1':
                result = MoroiaEngine.clear_temp_files(safe_mode=False)
                print(f"\n{Colors.GREEN}✅ Cleaned {result['freed_mb']} MB from {result['files_deleted']} files{Colors.ENDC}")
                
            elif choice == '2':
                result = MoroiaEngine.clear_developer_cache()
                print(f"\n{Colors.GREEN}✅ Cleaned {result['freed_mb']} MB from caches{Colors.ENDC}")
                
            elif choice == '3' and platform.system() == 'Windows':
                subprocess.run("ipconfig /flushdns", shell=True, capture_output=True)
                print(f"\n{Colors.GREEN}✅ DNS Cache Flushed{Colors.ENDC}")
                
            elif choice == '4':
                print(f"\n{Colors.CYAN}Running full optimization...{Colors.ENDC}")
                temp_res = MoroiaEngine.clear_temp_files(safe_mode=False)
                dev_res = MoroiaEngine.clear_developer_cache()
                if platform.system() == 'Windows':
                    subprocess.run("ipconfig /flushdns", shell=True, capture_output=True)
                print(f"{Colors.GREEN}✅ Complete! Freed {temp_res['freed_mb'] + dev_res['freed_mb']} MB{Colors.ENDC}")
                
            elif choice == '5' and startup_apps:
                print(f"\nSelect app to disable:")
                for idx, app in enumerate(startup_apps):
                    print(f"   [{idx+1}] {app['name']}")
                app_choice = input("Number (0 to skip): ").strip()
                if app_choice.isdigit() and 1 <= int(app_choice) <= len(startup_apps):
                    target = startup_apps[int(app_choice)-1]
                    success, msg = MoroiaEngine.disable_startup_app(target['name'])
                    print(f"\n{Colors.GREEN if success else Colors.FAIL}{msg}{Colors.ENDC}")
            
            print(f"\n{Colors.CYAN}Press Enter to exit...{Colors.ENDC}")
            input()
            
        except:
            pass
    
    finally:
        print(f"{Colors.SHOW_CURSOR}{Colors.CLEAR_SCREEN}", end="")
        print(f"{Colors.GREEN}{Colors.BOLD}✅ Moroia Session Complete{Colors.ENDC}")

if __name__ == '__main__':
    main()