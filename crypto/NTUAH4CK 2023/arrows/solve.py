from Crypto.Util.number import long_to_bytes

enc = 28159761705955253718454662360068272342440885298700051112417729041843661663258713442591709941031131886387

n = ''
for i, b in enumerate(bin(enc)[2:][:-2]):
    if i < 4:
        n += b
        continue
    n += str(int(b) ^ int(n[i-4]))

flag = long_to_bytes(int(n, 2)).decode()

print('NH4CK{'+flag+'}')