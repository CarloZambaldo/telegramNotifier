import os


def _cpu_temp(self) -> str:
    """Return the CPU temperature if available."""

    try:
        with open("/sys/class/thermal/thermal_zone0/temp") as fh:
            return f"{int(fh.read()) / 1000:.1f}°C"
    except Exception:
        temp = os.popen("vcgencmd measure_temp").read().strip()
        return temp.replace("temp=", "") if temp else "N/A"
