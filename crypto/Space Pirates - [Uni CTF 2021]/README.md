# Space Pirates - [Uni CTF 2021]

<html>
  <body>
    <table style="border: 1px solid grey; text-align: center">
      <tbody>
        <tr>
          <td style="border: 1px solid grey; text-align: center"><b>Category</b></td>
          <td style="border: 1px solid grey; text-align: center">Crypto</td>
        </tr>
        <tr>
          <td style="border: 1px solid grey; text-align: center"><b>Difficulty</b></td>
          <td style="border: 1px solid grey; text-align: center; color: 'green'">Easy</td>
        </tr>
        <tr>
          <td style="border: 1px solid grey; text-align: center"><b>CTF</b></td>
          <td style="border: 1px solid grey; text-align: center"><a href="https://ctftime.org/event/1511/" target="_blank">Uni CTF</a></td>
        </tr>
        <tr>
          <td style="border: 1px solid grey; text-align: center"><b>Year</b></td>
          <td style="border: 1px solid grey; text-align: center">2021</td>
        </tr>
      </tbody>
    </table>
  </body>
</html>

# Description

Jones and his crew have started a long journey to discover the legendary treasure left by the guardians of time in the early beginnings of the universe. Mr Jones, though, is wanted by the government for his crimes as a pirate. Our agents entered his base and discovered digital evidence about the way captain Jones contacts with his closest friends back home. We managed to get his last message, sent to his best friend. Could you help us decrypt it?

# Synopsis

This challenge was an introduction to the Shamir Secret Sharing (SSS). The vulnerability lies in the fact that each polynomial coefficient $a_i$ results from MD5-hashing the previous coefficient $a_{i-1}$, for $1 \leq i \leq 18$. Also, we are given $a_1$ which makes it easy to calculate the rest coefficients and eventually $s = a_0$ which is the secret value. Once we know $s$, we can generate the 128-bit AES key and decrypt the encrypted flag.

# Source files

1. [chall.py](src/chall.py)
2. [msg.enc](src/msg.enc)

# Overview

First thing we notice is that the python script implements a custom Shamir Secret Sharing Scheme (SSSS) [[1]](https://en.wikipedia.org/wiki/Shamir%27s_secret_sharing#Mathematical_principle) with the class `Shamir`. It is initialized with the parameters $p = 92434467187580489687$, $k = 10$, $n = 18$.

Then, the Shamir polynomial is generated with the first coefficient $s$ being a secret value.

$$
P(x) = s + a_1x + a_2x^2 +\ \dots\ + a_{n-1}x^{n-1} \pmod{p}
$$

Formulating it mathematically, it holds that:

$$
a_i = \left\\{
\begin{array}{ll}
s & i = 0 \\
H(a_{i-1}) & 1 \leq i \leq 18\\
\end{array} 
\right.
$$

where $H$ is the MD5 hash function.

```python
def next_coeff(self, val):
  return int(md5(val.to_bytes(32, byteorder="big")).hexdigest(),16)

def calc_coeffs(self):
  for i in range(1,self.n+1):
    self.coeffs.append(self.next_coeff(self.coeffs[i-1]))
```

Since the threshold of this scheme is $k$, the scheme keeps only the first $k = 10$ coefficients out of the total $n = 18$.

```python
self.coeffs = self.coeffs[:self.k]
```

Keep in mind that $n$ refers to the number of users in the SSS and each user should have a unique share, thus 18 shares in total. Recall that a share is nothing more than a point $(x_i,\ P(x_i))$ owned by the $i$-th user. The loop below computes these shares.

```python
for i in range(self.n):
  x = randint(1,self.p-1)
  self.x_vals.append(x)
  self.y_vals.append(self.calc_y(x))
```

The secret value $s$ is later used as seed to generate the random AES key and encrypt the flag. Assuming AES is secure, there are no known vulnerabilities so it's impossible to recover the key by exploiting the cipher. Therefore our solution path is probably:

- Recover the constant polynomial term $a_0$.
- Set $a_0$ as the seed of the `random` module.
- Generate the AES key that encrypted the flag and decrypt it.

# Solution

It's time to take a look at what values we are provided at `msg.enc`.

```python
f = open('msg.enc', 'w')
f.write('share: ' + str(share) + '\n')
f.write('coefficient: ' + str(sss.coeffs[1]) + '\n')
f.write('secret message: ' + str(enc_FLAG) + '\n')
f.close()
```

We are given the following:

- A single share $(x_i,\ P(x_i))$.
- The second coefficient $a_1$.
- The AES encrypted flag.

## Recovering the coefficients

Recall how the coefficients are computed:

$$
a_i = \left\\{
\begin{array}{ll}
      s & i = 0 \\
      H(a_{i-1}) & 1 \leq i \leq 18\\
\end{array} 
\right.
$$

We are given $a_1$ which means that we can compute $a_2 = H(a_1)$, $a_3 = H(a_2)$ and then repeat the same for all $k$ coefficients.

```python
a1 = 93526756371754197321930622219489764824
coeffs = [a1]

for i in range(k-2):
  coeffs.append(next_coeff(coeffs[i]))

print(coeffs)
```

Output:

```python
[93526756371754197321930622219489764824, 240113147373490959044275841696533066373, 277069233924763976763702126953224703576, 251923626603331727108061512131337433905, 303281427114437576729827368985540159120, 289448658221112884763612901705137265192, 175064288864358835607895152573142106157, 28168790495986486687119360052973747333, 320025932402566911430256919284757559396]
```

## Recovering the secret $s$

We have now recovered $a_1, a_2,\ \dots,\ a_{9}$. We still have to compute $s$. Recall the general form of the polynomial.

$$
P(x) = s + a_1x + a_2x^2 +\ \dots\ + a_9x^9 \pmod p
$$

Moreover, we are given a single share which turns out to be enough to recover our only unknown $s$. Therefore let's substitute the given share $(x_i,\ P(x_i))$ to the polynomial and solve for $s$.

$$
s = (P(x_i) - a_9x^9_i - a_8x^8_i -\ \dots\ - a_1x_i) \pmod{p}
$$

```python
def calculate_rhs(x, coeffs):
  rhs = 0
  for i in range(len(coeffs)):
    rhs += coeffs[i] * x**(i+1)
  return rhs % p

(x, y) = (21202245407317581090, 11086299714260406068) # share
s = (y - calculate_rhs(x, coeffs)) % p
print(f'[+] seed = {s}')
```

Output:

```py
[+] seed = 64070762944634914441
```

Now we can set this value as the RNG seed, recover the AES key and decrypt the flag.

# Full solve script

```py
from hashlib import md5
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from random import randbytes, seed

def next_coeff(val):
  return int(md5(val.to_bytes(32, byteorder="big")).hexdigest(), 16)

def calculate_rhs(x, coeffs):
  rhs = 0
  for i in range(len(coeffs)):
    rhs += coeffs[i] * x**(i+1)
  return rhs % p

p, k, n = 92434467187580489687, 10, 18
a1 = 93526756371754197321930622219489764824
(x, y) = (21202245407317581090, 11086299714260406068) # share
ct = bytes.fromhex('<REDACTED>')

coeffs = [a1]
for i in range(k-2):
  coeffs.append(next_coeff(coeffs[i]))

s = (y - calculate_rhs(x, coeffs)) % p

seed(s)
key = randbytes(16)
cipher = AES.new(key, AES.MODE_ECB)
flag = cipher.decrypt(ct)

print(unpad(flag, 16).decode())
```

Output:

```
The treasure is located at galaxy VS-708.
Our team needs 3 light years to reach it.
Our solar cruise has its steam canons ready to fire in case we encounter enemies.
Next time you will hear from us brother, everyone is going to be rich!
HTB{1_d1dnt_kn0w_0n3_sh4r3_w45_3n0u9h!1337}
```

# Flag

```
HTB{1_d1dnt_kn0w_0n3_sh4r3_w45_3n0u9h!1337}
```