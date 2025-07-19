import platform
import subprocess

def get_gpu_info():
    """Obtiene información de la tarjeta gráfica."""
    try:
        if platform.system() == "Windows":
            import wmi
            c = wmi.WMI()
            for card in c.Win32_VideoController():
                return card.Name, card.AdapterRAM / (1024 * 1024)
        else:  # Linux, macOS (usando OpenGL)
            from OpenGL import GL
            gpu_name = GL.glGetString(GL.GL_RENDERER).decode()
            # No es posible obtener la VRAM con OpenGL de forma portable
            return gpu_name, "N/A"
    except Exception as e:
        return "N/A", "N/A"  # En caso de error

def get_cpu_name():
    """Obtiene el nombre del CPU."""
    try:
        if platform.system() == "Windows":
            import wmi
            c = wmi.WMI()
            for cpu in c.Win32_Processor():
                return cpu.Name
        else: # Linux y macOS
            with open("/proc/cpuinfo", "r") as f:
                for line in f:
                    if "model name" in line:
                        return line.split(":")[1].strip()
        return platform.processor() # Si falla todo lo anterior, usa platform.processor()
    except Exception as e:
        print(f"Error al obtener el nombre del CPU: {e}")
        return platform.processor()  # En caso de error, usar platform.processor()