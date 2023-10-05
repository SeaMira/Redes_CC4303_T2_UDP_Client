#!/usr/bin/python3
# Echo client program
# Version con dos threads: uno lee de stdin hacia el socket y el otro al revés
import jsockets
import sys
from csv import writer
import auxiliary as aux


def stopAndWaitUDP(s, pack_sz, nbytes, timeout, loss, fileout):
    print("Starting UDP")

    aux.loss_rate = float(loss)

    s_msg, en_msg = aux.encode_package_time(pack_sz, timeout)

    i = 0
    while i < 100:
        try:
            s.send(en_msg)
            s.settimeout(3)
            print("propuse paquete:", s_msg)
            act_pack_sz = s.recv(10).decode('utf-8')
            break
        except s.timeout:
            i += 1
    if i >= 100:
        sys.exit("Stop UDP")

    print("recibo paquete:", act_pack_sz[1:])
    s.send(bytearray("N" + str(nbytes), encoding='utf-8'))
    print("recibiendo", nbytes, "nbytes")

    # Recepcion de paquetes
    total_bytes, errores, start, end = aux.pack_rec(
        s, fileout, int(act_pack_sz[1:]), nbytes)

    with open('results3.csv', 'a') as f_object:

        writer_object = writer(f_object)
        writer_object.writerow(
            [int(act_pack_sz[1:]), timeout, loss, total_bytes, end-start, total_bytes/((end-start)*1024*1024), errores])
        f_object.close()

    print("bytes recibidos =", total_bytes, ", time =", end-start,
          " , bw = ", total_bytes/((end-start)*1024*1024), " , errores = ", errores)


# Program start: asking for parameters and creating a link
if len(sys.argv) != 8:
    print('Use: '+sys.argv[0]+' pack_sz nbytes timeout loss fileout host port')
    sys.exit(1)

s = jsockets.socket_udp_connect(sys.argv[6], sys.argv[7])


if s is None:
    print('could not open socket')
    sys.exit(1)


fileout = open(sys.argv[5], 'wb')


stopAndWaitUDP(s, int(sys.argv[1]), int(
    sys.argv[2]), int(sys.argv[3]), sys.argv[4], fileout)

print("Message sent")
s.close()
fileout.close()
