import re
import subprocess


def run(cmd):
    try:
        return subprocess.check_output(
            cmd, text=True, encoding="utf-8", errors="ignore", stderr=subprocess.DEVNULL
        )
    except Exception:
        return ""


def get_current_ssid():
    match = re.search(r"^\s*SSID\s*:\s*(.+)$", run(["netsh", "wlan", "show", "interfaces"]), re.M)
    return match.group(1).strip() if match else None


def get_all_wifi_passwords():
    profiles = re.findall(r"All User Profile\s*:\s*(.+)", run(["netsh", "wlan", "show", "profiles"]))
    passwords = {}
    for ssid in (s.strip() for s in profiles):
        details = run(["netsh", "wlan", "show", "profile", f"name={ssid}", "key=clear"])
        pwd_match = re.search(r"Key Content\s*:\s*(.+)", details)
        passwords[ssid] = pwd_match.group(1).strip() if pwd_match else None
    return passwords


if __name__ == "__main__":
    current_ssid = get_current_ssid()
    passwords = get_all_wifi_passwords()
    current_password = passwords.get(current_ssid)

    CYAN, GREEN, RED, RESET = "\033[96m", "\033[92m", "\033[91m", "\033[0m"

    print(f"\n{CYAN}  Sparade WIFI-nätverk{RESET}\n" + "─" * 44)
    print(f"{CYAN}  {'SSID':<28} Lösenord{RESET}\n" + "─" * 44)

    for network, pwd in sorted(passwords.items()):
        marker = f"{RED} * {RESET}" if network == current_ssid else ""
        print(f"  {network:<28} {pwd or '(inget lösenord)'}{marker}")

    print("─" * 44)
    if current_ssid:
        print(f"{GREEN}  {'Nuvarande nätverk':<28} {current_ssid}{RESET}")
        status_color = GREEN if current_password else RED
        print(f"{status_color}  {'Lösenord':<28} {current_password or '(inget lösenord)'}{RESET}")
    else:
        print(f"{RED}  Inget anslutet Wi-Fi-nätverk hittades.{RESET}")
