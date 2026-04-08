import subprocess


def run(cmd):
    return subprocess.check_output(
        cmd, text=True, encoding="utf-8",
        errors="ignore", stderr=subprocess.DEVNULL
    )


def get_current_ssid():
    try:
        ssid = run([
            "powershell", "-NoProfile", "-NonInteractive",
            "-Command", "(Get-NetConnectionProfile).Name"
        ]).strip()
        return ssid or None
    except Exception:
        pass

    try:
        for line in run(["netsh", "wlan", "show", "interfaces"]).splitlines():
            if "SSID" in line and "BSSID" not in line:
                return line.split(":", 1)[1].strip()
    except Exception:
        pass

    return None


def get_all_wifi_passwords():
    passwords = {}
    try:
        output = run(["netsh", "wlan", "show", "profiles"])
        for line in output.splitlines():
            if "All User Profile" in line:
                ssid = line.split(":", 1)[1].strip()
                try:
                    pwd_output = run([
                        "netsh", "wlan", "show", "profile",
                        f"name={ssid}", "key=clear"
                    ])
                    for pwd_line in pwd_output.splitlines():
                        if "Key Content" in pwd_line:
                            password = pwd_line.split(":", 1)[1].strip()
                            passwords[ssid] = password
                            break
                    else:
                        passwords[ssid] = None
                except Exception:
                    passwords[ssid] = None
    except Exception:
        pass

    return passwords

def find_password_for_ssid(ssid, passwords):
    if ssid is None:
        return None
    if ssid in passwords:
        return passwords[ssid]
    return None


if __name__ == "__main__":
    current_ssid = get_current_ssid()
    passwords = get_all_wifi_passwords()
    current_password = find_password_for_ssid(current_ssid, passwords)

    GREEN = "\033[92m"
    RED = "\033[91m"
    CYAN = "\033[96m"
    RESET = "\033[0m"
    
    
    print("\n")
    print(CYAN + f"  {'Sparade WIFI-nätverk'}" + RESET)
    print("─" * 44)
    print(CYAN + f"  {'SSID':<28} Lösenord" + RESET)
    print("─" * 44)

    for network, pwd in sorted(passwords.items()):
        marker = RED + " * " + RESET  if network == current_ssid else ""
        print(f"  {network:<28} {pwd or '(inget lösenord)'}{marker}")

    print("─" * 44)
    if current_ssid:
        print(GREEN + f"  {'Nuvarande nätverk':<28} {current_ssid}" + RESET)
        if current_password:
            print(GREEN + f"  {'Lösenord':<28} {current_password}" + RESET)
        else:
            print(RED + f"  {'Lösenord':<28} (inget lösenord)" + RESET)
    else:
        print(RED + "  Ingen ansluten Wi-Fi-nätverk hittades." + RESET)