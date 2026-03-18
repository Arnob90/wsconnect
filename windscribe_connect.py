import subprocess
import sys

location_list = subprocess.run(
    ["windscribe-cli", "locations"], capture_output=True, text=True
).stdout.splitlines()

non_pro_locations = [location for location in location_list if "(Pro)" not in location]
selected_location_proc = subprocess.run(
    ["fzf"], input="\n".join(non_pro_locations), capture_output=True, text=True
)
if selected_location_proc.returncode != 0:
    sys.exit(0)
selected_location = selected_location_proc.stdout.strip()
selected_nick = selected_location.split(" - ")[-1]
selected_nick_info_removed = selected_nick.removesuffix("(10 Gbps)").strip()

subprocess.run(
    ["windscribe-cli", "connect", selected_nick_info_removed],
    stdout=sys.stdout,
    stderr=sys.stderr,
)
