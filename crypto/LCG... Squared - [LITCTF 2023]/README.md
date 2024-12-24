# LCG... Squared? - [LITCTF 2023]

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
          <td style="border: 1px solid grey; text-align: center; color: 'green'">Medium</td>
        </tr>
        <tr>
          <td style="border: 1px solid grey; text-align: center"><b>CTF</b></td>
          <td style="border: 1px solid grey; text-align: center"><a href="https://ctftime.org/event/2052/" target="_blank">LITCTF</a></td>
        </tr>
        <tr>
          <td style="border: 1px solid grey; text-align: center"><b>Year</b></td>
          <td style="border: 1px solid grey; text-align: center">2023</td>
        </tr>
        <tr>
          <td style="border: 1px solid grey; text-align: center"><b>Solves</b></td>
          <td style="border: 1px solid grey; text-align: center">14</td>
        </tr>
        <tr>
          <td style="border: 1px solid grey; text-align: center"><b>Author</b></td>
          <td style="border: 1px solid grey; text-align: center">quasar0147</td>
        </tr>
      </tbody>
    </table>
  </body>
</html>

# Description

Apparently lcgs are weak...... but my lcgs have doubled their power since they last met!

# Synopsis

This challenge is about two related LCGs. Knowning five outputs of the second LCG, we are able to get five equations for the five unknowns and use Groebner basis to retrieve equivalent equations but with fewer variables. One of these equations is quadratic so we have two possible values for $b_2$. For each candidate $b_2$, we initialize the lcg with each solution of the system $x_0, y_0, a_1, b_1, b_2$ and try decrypting the ciphertext until we find the flag.

# Source files

1. [rng.py](src/rng.py)
2. [out.txt](src/out.txt)

# Overview

Luckily, the source code is relatively short so it is easy to understand how the flag is encrypted. At a quick glance we see the two LCG classes that are defined which are mathematically connected.

Before diving into the analysis of the two RNGs, let's get a better idea of the entire cryptosystem.

- First, a 64-bit prime $p$ is generated, which will be used as the modulo for both RNGs.
- We get 5 consecutive outputs of the `lcg2` RNG along with the prime $p$. We will see later that the number of the known outputs is what makes the challenge solveable. If we knew less states, the following solution wouldn't work!
```py
lcg = lcg2()
print(p)
for x in range(5):
    print(lcg.next())
```
- The next output of the RNG (i.e. the sixth one) is used as the AES key that finally encrypts the flag.

```py
from Crypto.Cipher import AES
from Crypto.Util.number import long_to_bytes as l2b
from Crypto.Util.Padding import pad
from os import urandom
r = lcg.next()
k = pad(l2b(r**2), 16)
iv = urandom(16)
cipher = AES.new(k, AES.MODE_CBC, iv=iv)
print(iv.hex())
f = open("flag.txt",'rb').read().strip()
enc = cipher.encrypt(pad(f,16))
print(enc.hex())
```

Assuming AES is secure, the only way to decrypt the ciphertext is to retrieve the encryption key, which means we have to recover $r$ - the sixth output of the RNG. As we don't have many information, we should probably focus on these five outputs.

## Analyzing the LCG classes

```py
class lcg1:
    def __init__(self, n=64):
        self.a = random.randint(1, 2**n)
        self.b = random.randint(1, 2**n)
        self.x = random.randint(1, 2**n)
        self.m = p
    def next(self):
        ret = self.x
        self.x = (self.a * self.x + self.b) % self.m
        return ret

class lcg2:
    def __init__(self, n=64):
        self.lcg = lcg1(n)
        self.x = random.randint(1, 2**n)
        self.b = random.randint(1, 2**n)
        self.m = p
    def next(self):
        self.x = (self.lcg.next() * self.x + self.b) % self.m
        return self.x
```

The constructor of the `lcg2` class creates an object of the `lcg1` class passing the modulo's bit length as an argument.

In the constructor of `lcg1`, three random 64-bit numbers are generated:

- $a_1$ is used as the LCG multiplier.
- $b_1$ as the increment and
- $x_0$ as the seed.

Similarly, in the constructor of `lcg2`:

- The multiplier is the output of the first lcg.
- $b_2$ as the increment and
- $y_0$ as the seed.

As one can notice, we are not given neither the LCG parameters $a_1, b_1, b_2$ nor the seeds $x_0, y_0$. However, to compute the sixth output, we need to recover all these values.


# Solution

Let's first write two outputs of `lcg2`.

$$
\begin{aligned}
y_1 &= x_0y_0 + b_2\\
y_2 &= x_1y_1 + b_2 = (a_1x_0 + b_1)(x_0y_0 + b_2) + b_2 =\\
&= a_1y_0x_0^2 + a_1b_2x_0 + b_1y_0x_0 + b_1b_2 + b_2
\end{aligned}
$$

In total, we get 5 relations with 5 unknowns which means that this non-linear system must have a unique solution. But how can we define the system relations and the unknowns?

## Simulating the LCGs symbolically

We could do the algebra by hand but we are too lazy so let's write a SageMath script that creates five variables and runs the LCGs symbolically, instead of running it with actual integers. First, we have to define five variables over $\mathbb{F}(p)$ which can be done as:

```python
PR.<x0,y0,a1,b1,b2> = PolynomialRing(GF(p))
```

Next, we slightly modify the classes so that no random numbers are generated in the constructors, but instead, the five variables are passed as arguments.

```python
class lcg1:
    def __init__(self, x, a, b1):
        self.a = a
        self.b = b1
        self.x = x
        self.m = p
    def next(self):
        ret = self.x
        self.x = (self.a * self.x + self.b) % self.m
        return ret

class lcg2:
    def __init__(self, x, y, a, b1, b2):
        self.lcg = lcg1(x, a, b1)
        self.x = y
        self.b = b2
        self.m = p
    def next(self):
        self.x = (self.lcg.next() * self.x + self.b) % self.m
        return self.x

lcg = lcg2(x0, y0, a1, b1, b2)
for i in range(5):
    print(lcg.next())
```

By running this, we get the following output which is redacted for the sake of brevity.

```python
x0*y0 + b2
x0^2*y0*a1 + x0*y0*b1 + x0*a1*b2 + b1*b2 + b2
.
.
.
```

We can verify that the outputs are the same as the ones we calculated by hand above.

## Setting up the equations

Okay, what does it all mean? Why did we do that? Well, we have the following system of equations:

$$
\begin{aligned}
y_1 &= f_1(x_0,y_0,a_1,b_1,b_2) = x_0y_0 + b_2\\
y_2 &= f_2(x_0,y_0,a_1,b_1,b_2) = ...\\
y_3 &= f_3(x_0,y_0,a_1,b_1,b_2) = ...\\
y_4 &= f_4(x_0,y_0,a_1,b_1,b_2) = ...\\
y_5 &= f_5(x_0,y_0,a_1,b_1,b_2) = ...
\end{aligned}
$$

This system is non-linear and extremely complex to solve by hand since most of $f_i$ depend on all 5 variables and this is where SageMath comes to save the day!

There are two tricks to use to solve such systems.

### Resultant and Polynomial GCD

Suppose you have two equations and two unknowns which you want to compute. Resultant is basically a variable elimination function which you feed it these polynomials, it eliminates one variable, leaving just one variable which you can compute easily even by manual rearrangement. For more complex systems, resultant is combined with polynomial GCD which can be used to figure out common factors of polynomials and cancel them out, therefore eliminating variables.

However, in our case, each $f_i$ contains all five unknowns so we would have to apply resultant and GCD several times to minimize the number of variables, which would take a lot of time. What if there was a method that applies these techniques (along with some others too) until the number of variables per equation is minimized? Fortunately, there is such a method and it's called ***Groebner Basis***.

### Groebner Basis

Without getting into technical details, what Groebner basis does at a high level is get some multivariate equations, perform clever rearrangements and variable elimination and eventually end up with some equivalent equations that have fewer variables. We will use this challenge as an example.

Using Groebner basis sounds like a good plan so let's get back to forming the equations that we will feed it.

Moving $f_i$ to the other side we get $y_i -f_i(x_0, y_0, a_1, b_1, b_2) = 0$.

What Groebner basis will do is find different equations, with fewer variables, that still result in 0. It saves us a lot of time from doing all of this by hand.

## Retrieving the unknowns

We will use the following script to generate the equations.

```python
lcg = lcg2(x0, y0, a1, b1, b2)
eqs = []
for i in range(5):
    sym_out = lcg.next()
    eqs.append(states[i] - sym_out)
```
where,

- `lcg2` the symbolic version of the LCG.
- `states` the array that stores the 5 outputs of the RNG.

Let's run Groebner basis. We will use the following code. For now, we will treat ideals as black-box.

```python
I = Ideal(eqs)
G = I.groebner_basis()
print(G)
```

```
b2^2 + 8860549604559953614*b2 + 6081691856514156794
x0 + 4298251801134044542*b2 + 6949343071462624409
y0 + 5768326408389828509*b2 + 4968572571594503118
a1 + 5411030611284425018*b2 + 80950332416582054
b1 + 9662372171659581811*b2 + 10180096875606879244
```

### Finding the polynomial roots

We notice that we got five much cleaner equivalent equations back for which is trivial to find their roots. The first equation is quadratic so there will be two solutions for $b_2$.

For each of the $b_2$ candidates, we substitute into the rest polynomials and find their roots. For the time being, we don't have any way to identify the correct solution for $b_2$ so we will create two LCGs - one for each value of $b_2$.

```python
def get_lcgs(G):
    rb2 = G[0].univariate_polynomial().roots(multiplicities=False)
    lcgs = []

    for b2 in rb2:
        x0  = G[1](b2=b2).univariate_polynomial().roots(multiplicities=False)[0]
        y0  = G[2](b2=b2).univariate_polynomial().roots(multiplicities=False)[0]
        a1  = G[3](b2=b2).univariate_polynomial().roots(multiplicities=False)[0]
        b1 = G[4](b2=b2).univariate_polynomial().roots(multiplicities=False)[0]
        
        lcg = lcg2(x0, y0, a1, b1, b2)
        for _ in range(5):
            assert states[_] == lcg.next()  # sync with chall's lcg
        lcgs.append(lcg)
    
    return lcgs
```

Note that by calling `next()` five times, we have synced with the challenge's lcg which ran five times to print each output.

## Recovering the sixth output

We have two candidates for the right LCG so we try to decrypt the ciphertext for each of them until we get the flag.

```python
LCGs = get_lcgs(G)

for lcg in LCGs:
    r = int(lcg.next())
    key = pad(l2b(r**2), 16)
    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    flag = cipher.decrypt(ct)
    try:
        print(f'{r = }')
        print(unpad(flag, 16).decode())
    except:
        pass
```


# Full solve script

```python
from Crypto.Cipher import AES
from Crypto.Util.number import long_to_bytes as l2b
from Crypto.Util.Padding import pad, unpad

class lcg1:
    def __init__(self, x, a, b1):
        self.a = a
        self.b = b1
        self.x = x
        self.m = p
    def next(self):
        ret = self.x
        self.x = (self.a * self.x + self.b) % self.m
        return ret

class lcg2:
    def __init__(self, x, y, a, b1, b2):
        self.lcg = lcg1(x, a, b1)
        self.x = y
        self.b = b2
        self.m = p
    def next(self):
        self.x = (self.lcg.next() * self.x + self.b) % self.m
        return self.x

def get_lcgs(G):
    rb2 = G[0].univariate_polynomial().roots(multiplicities=False)
    lcgs = []

    for b2 in rb2:
        x0  = G[1](b2=b2).univariate_polynomial().roots(multiplicities=False)[0]
        y0  = G[2](b2=b2).univariate_polynomial().roots(multiplicities=False)[0]
        a1  = G[3](b2=b2).univariate_polynomial().roots(multiplicities=False)[0]
        b1 = G[4](b2=b2).univariate_polynomial().roots(multiplicities=False)[0]
        
        lcg = lcg2(x0, y0, a1, b1, b2)
        for _ in range(5):
            assert states[_] == lcg.next()
        lcgs.append(lcg)
    
    return lcgs

with open('out.txt') as f:
    p = int(f.readline())
    states = []
    for _ in range(5):
        states.append(int(f.readline()))
    iv = bytes.fromhex(f.readline())
    ct = bytes.fromhex(f.readline())

PR.<x0,y0,a1,b1,b2> = PolynomialRing(GF(p))

lcg = lcg2(x0, y0, a1, b1, b2)

eqs = []
for i in range(5):
    sym_out = lcg.next()
    eqs.append(states[i] - sym_out)

I = Ideal(eqs)
G = I.groebner_basis()

LCGs = get_lcgs(G)

for lcg in LCGs:
    r = int(lcg.next())
    key = pad(l2b(r**2), 16)
    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    try:
        flag = unpad(cipher.decrypt(ct), 16)
        print(f'{r = }')
        print(flag.decode())
    except:
        pass
```

Output:

```
r = 9562763730050056824
LITCTF{groebner_so_op_this_would_be_very_awkward_if_you_used_resultants}
```

# Flag

```
LITCTF{groebner_so_op_this_would_be_very_awkward_if_you_used_resultants}
```