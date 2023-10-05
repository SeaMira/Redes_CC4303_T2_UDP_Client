import subprocess

# Define los valores para las pruebas
pack_sz_values = [1000, 3000, 5000, 7500, 9999]
timeout_values = [20, 50, 80, 100]
loss_values = [5, 20, 30, 50]

tries = 3

# Ruta al script principal
script_path = "bwc_sw.py"

# Itera sobre todas las combinaciones de valores
for pack_sz in pack_sz_values:
    for timeout in timeout_values:
        for loss_value in loss_values:
            print("---------------------------------------")
            print("pack size:", pack_sz, "loss_value:",
                  loss_value, "timeout:", timeout)
            print("---------------------------------------")
            for i in range(tries):
                # Ejecuta el script con los parámetros actuales
                cmd = ["python3", script_path, str(pack_sz), "1000000", str(
                    timeout), str(loss_value), "out", "anakena.dcc.uchile.cl", "1819"]
                subprocess.run(cmd)
