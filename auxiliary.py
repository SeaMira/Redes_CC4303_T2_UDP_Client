import random
import socket
import sys
import time

loss_rate = 0

# Env´ıa un paquete con loss_rate porcentaje de p´erdida
# si loss_rate = 5, implica un 5% de p´erdida


class Loss(Exception):
    def __init__(self, mensaje):
        super().__init__(mensaje)


def send_loss(s, data):
    global loss_rate
    if random.random() * 100 > loss_rate:
        s.send(data)
    else:
        print("[send_loss]")

# Recibe un paquete con loss_rate porcentaje de pérdida
# Si decide perderlo, vuelve al recv y no retorna aun
# Retorna None si hay timeout o error


def recv_loss(s, size):
    global loss_rate
    try:
        while True:
            data = s.recv(size)
            if random.random() * 100 <= loss_rate:
                print("[recv_loss]")
            else:
                break
    except socket.timeout:
        print('timeout', file=sys.stderr)
        data = None
    except socket.error:
        print('recv err', file=sys.stderr)
        data = None
    return data


def encode_package_time(package_size, time_ms):
    # Asegúrate de que los valores estén en el rango permitido
    if package_size < 0 or package_size > 9999 or time_ms < 0 or time_ms > 9999:
        raise ValueError(
            "Los valores de tamaño de paquete y tiempo deben estar entre 0 y 9999")

    # Convierte los valores en cadenas de 4 dígitos con ceros a la izquierda si es necesario
    package_str = str(package_size).zfill(4)
    # print("package siz:", package_str)
    time_str = str(time_ms).zfill(4)
    # print("time ms:", time_str)

    # Concatena las cadenas y agrega el carácter 'C' al principio
    encoded_str = f'C{package_str}{time_str}'

    # Convierte la cadena codificada en un bytearray de números
    encoded_bytes = bytearray(encoded_str, encoding='utf-8')

    return (package_str, encoded_bytes)


def belongs_to_(i, code):
    assert type(i) == type(code) == int

    if i >= 50:
        lim_0 = (i + 50) % 100
        if (i <= code <= 99) or (0 <= code < lim_0):
            return True
        return False
    else:
        if (i <= code < i + 50):
            return True
        return False


assert not belongs_to_(50, 0)
assert belongs_to_(50, 99)
assert not belongs_to_(23, 73)
assert belongs_to_(23, 72)


def new_list(size):
    assert type(size) == int
    assert size > 0
    l = []
    for i in range(size):
        l += [[0, None]]
    return l


def write_pending_data(aw_nmb, fileout, closet):
    while (closet[aw_nmb][0] == "a" or closet[aw_nmb][0] == "A"):
        data = closet[aw_nmb][1]
        fileout.write(data)
        closet[aw_nmb][0] = "f"
        closet[aw_nmb][1] = None
        aw_nmb = (aw_nmb+1) % 100
    return aw_nmb, closet


def pack_rec(s, fileout, pack_sz, nbytes):
    total_bytes = 0
    closet = new_list(100)
    actual_code = ""
    aw_nmb = 0
    last_code = "00"
    errores = 0

    start = time.time()
    while True:
        s.settimeout(3)
        rcv_data = recv_loss(s, pack_sz + 3)

        if rcv_data == None:
            print("[Error none]")
            break
        else:
            actual_code = rcv_data.decode('utf-8')[0:3]
            if not belongs_to_(aw_nmb, int(actual_code[1:3])):
                print("[Error]")
                cde = "A"+last_code
                send_loss(s, cde.encode('UTF-8'))
                errores += 1
            else:
                if int(actual_code[1:3]) == aw_nmb:
                    if actual_code[0] == "E" and total_bytes == nbytes:
                        print("[End]")
                        cde = f"A{aw_nmb}"
                        send_loss(s, cde.encode('UTF-8'))
                        break

                    if actual_code[0] == "D":
                        try:
                            data_r_s = len(rcv_data[3:])
                            if data_r_s != pack_sz and data_r_s != (nbytes % pack_sz):
                                raise Loss("[recv_loss]")
                            send_loss(s, "A".encode('UTF-8') + rcv_data[1:3])
                            last_code = actual_code[1:3]
                            closet[aw_nmb][0], closet[aw_nmb][1] = 'A', rcv_data[3:]
                            new_aw_nmb, new_closet = write_pending_data(
                                aw_nmb, fileout, closet)
                            aw_nmb = new_aw_nmb
                            closet = new_closet
                        except Loss:
                            print("[Error len]")
                            cde = "A"+last_code
                            send_loss(s, cde.encode('UTF-8'))
                            errores += 1
                    else:
                        print("[Error]")
                        cde = "A"+last_code
                        send_loss(s, cde.encode('UTF-8'))
                        errores += 1
                else:
                    this_code = int(actual_code[1:3])
                    if actual_code[0] == "E":
                        print("[End]")
                        cde = f"a{this_code}"
                        send_loss(s, cde.encode('UTF-8'))

                    if actual_code[0] == "D":
                        try:
                            data_r_s = len(rcv_data[3:])
                            if data_r_s != pack_sz and data_r_s != (nbytes % pack_sz):
                                raise Loss("[recv_loss]")
                            send_loss(s, "a".encode('UTF-8') + rcv_data[1:3])
                            closet[this_code][0] = "a"
                            closet[this_code][1] = rcv_data[1:3]

                        except Loss:
                            print("[Error len]")
                            cde = "A"+last_code
                            send_loss(s, cde.encode('UTF-8'))
                            errores += 1
                    else:
                        print("[Error]")
                        cde = "A"+last_code
                        send_loss(s, cde.encode('UTF-8'))
                        errores += 1
    end = time.time()
    return (total_bytes, errores, start, end)
