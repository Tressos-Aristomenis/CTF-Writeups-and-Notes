# babyRSA - [TSJ CTF 2022]

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
          <td style="border: 1px solid grey; text-align: center; color: orange">Medium</td>
        </tr>
        <tr>
          <td style="border: 1px solid grey; text-align: center"><b>CTF</b></td>
          <td style="border: 1px solid grey; text-align: center"><a href="https://ctftime.org/event/1547/" target="_blank">TSJ CTF</a></td>
        </tr>
        <tr>
          <td style="border: 1px solid grey; text-align: center"><b>Year</b></td>
          <td style="border: 1px solid grey; text-align: center">2022</td>
        </tr>
      </tbody>
    </table>
  </body>
</html>

# Description

![](meme.png)

# Synopsis

The point $C$ belongs to the curve so we create two multivariate polynomials, eliminate one variable using resultants and run `small_roots()` to obtain $q$. Having factored $N$, construct the curve in the composite ring $\mathbb{Z}/n\mathbb{Z}$ and find the base point by calculating $C$ with the inverse of $e$ modulo the curve's order.

# Source files

1. [challenge.sage](src/challenge.sage)
2. [output.txt](src/output.txt)

# Overview

Let's first analyze the main script of the challenge; that is `challenge.sage`.

```python
from Crypto.Util.number import *
import os

proof.arithmetic(False)  # to make sage faster

flag = b"TSJ{not_real_flag}"

p = getPrime(1024)
q = getPrime(512)
n = p * q
e = 65537
E = EllipticCurve(Zmod(n), [p, q])

while True:
    x = ZZ(bytes_to_long(flag + os.urandom(192 - len(flag))))
    try:
        yp = ZZ(E.change_ring(GF(p)).lift_x(x).xy()[1])
        yq = ZZ(E.change_ring(GF(q)).lift_x(x).xy()[1])
        y = crt([yp, yq], [p, q])
        break
    except:
        pass

C = e * E(x, y)
print(n)
print(C.xy())
```

At first glance, we see there is a standard RSA key generation, i.e. the secret primes $\{p,\ q\}$ and the public key $\{N=pq,\ e\}$. Then, an elliptic curve $\mathbb{E}$ is defined over the composite ring $\mathbb{Z}/n\mathbb{Z}$ with parameters $a = p$ and $b = q$.

We can describe this curve with the following algebraic relationship:

$$
y^2 \equiv x^3 + px + q \pmod N
$$

The flag is randomly padded and stored in the variable $x$. After that, two points with the $x$-coordinate are calculated:

- $(x,\ y_p)$

  This is a point of the curve that is defined over $GF(p)$; say $\mathbb{E}_p$.
  
  $$y_p^2 = x^3 + q \pmod {p}$$

  Note that $px$ is a multiple of $p$ so it is eliminated $\pmod p$.
- $(x,\ y_q)$

  This is a point of the curve that is defined over $GF(q)$; say $\mathbb{E}_q$.
  
  $$y_q^2 = x^3 + px \pmod {q}$$

  Note that $q$ is eliminated $\pmod q$.

*What the function `E.change_ring()` basically does is changing the ring in which the curve* $\mathbb{E}$ *is defined*.

Then, $y_p$ and $y_q$ are combined with the Chinese Remainder Theorem to get the $y$-coordinate that belongs to $\mathbb{E_n}$. 

To summarize, this loop does the same job as the Sage method `E.lift_x(x)`. The reason we can't use this method now is due to $\mathbb{E}_n$ being defined over a composite ring and `lift_x` would try to factor $N$ to lift the point in $\mathbb{E}_p$ and $\mathbb{E}_q$, which is a very hard problem since the prime generation is secure. Therefore we conclude that the flag is randomly padded until the point $(x,\ y)$ is on $\mathbb{E}_n$, where $x$ is the padded flag.

Finally, the encryption is similar to that of RSA but in the additive group:

- $C$ is the ciphertext point
- $e$ is the scalar
- $G = E(x,y)$ is the point of $\mathbb{E}_n$ that we want to retrieve

# Idea on how to recover the base point and the problem that lies

How does decryption work in RSA?
One raises the ciphertext to the multiplicative inverse of $e$ modulo the order of the multiplicative group $\mathbb{Z}/n\mathbb{Z}$; that is $\phi(n)$.

Similarly, from [here](https://crypto.stackexchange.com/questions/86663/how-to-find-the-base-point-given-public-and-private-key-and-ec-parameters-except/86670#86670), we know that to solve for $G$ we need to multiply $C$ by the multiplicative inverse of $e$ modulo the order of $\mathbb{E}_n$.

$$
\begin{aligned}
G = Ce^{-1} \pmod {O_n}\quad\quad\quad\quad(1)
\end{aligned}
$$

where $O_n$ is the order of the curve $\mathbb{E}_n$.

Pretty straightforward right? ... Hmm, not at all.

As aforementioned, $\mathbb{E}_n$ is defined over a composite ring so knowning its order is as hard as factoring $N$.

$N$ is more than 1500 bits long so without a quantum computer, we have no luck here.

# Solution

## q is half the bit length of p

The key to factor $N$ is notice that $q$ is half the bit length of $p$. That's about $\frac{1}{3}$ the bit length of $N$.

$\dfrac{1}{3}$? Where did this come from?

That's because $N$ can be written as the product of three `512`-bit integers, say $a,b,c$.

$$N = a * b * c$$

Since $q$ is 512 bits, we are certain that one (1) of these three (3) variables must be $q$. This makes $q$ about $\frac{1}{3}$ of $N$.

## Playing with the curve's formula

Since $G$ belongs to $\mathbb{E}_n$, so does $C$.

We know that any point $(x,\ y)$ of $\mathbb{E}_n$ satisfies the following formula:

$$y^2 = x^3 + px + q \pmod N$$

Then substituting with $C = (C_x, C_y)$ coordinates we get:

$$C_y^2 = C_x^3 + p*C_x + q \pmod N$$

Let's rewrite the relation above as follows:

$$C_y^2 - C_x^3 - p*C_x - q = 0 \pmod N$$

We know everything apart from $p$ and $q$ but we can't solve for them because we have one relation and two unknowns. Do we know something else about $p,q$? Well, from the RSA part we know that $N = p * q$ and $N$ is known. That's great! Two equations and two unknowns so there is a unique solution.

## Constructing the polynomials

Let's define the following polynomials over $\mathbb{Z}/n\mathbb{Z}$.

$$
\begin{aligned}
f(x,\ y) &= n - x \ast y\\
g(x,\ y) &= C_y^2 - C_x^3 - x \ast C_x - y
\end{aligned}
$$

Notice that $p, q$ are both roots of these polynomials:

$$
\begin{aligned}
f(p,\ q) &= n - p \ast q = 0\\
g(p,\ q) &= C_y^2 - C_x^3 - p \ast C_x - q = 0
\end{aligned}
$$

They are multivariate polynomials but maybe we could eliminate one variable? For example, we could substitute $p = \dfrac{N}{q}$ in the $g$ polynomial. One could substitute with pencil and paper and come up with a univariate polynomial in terms of $q$ but that's a lot of work (*however, it is recommended as an exercise for beginners!*).

We could use our beloved resultant that basically does the same thing. You can find more about resultants from [1](https://www.imo.universite-paris-saclay.fr/~meliot/algebra/resultant.pdf), [2](http://buzzard.ups.edu/courses/2016spring/projects/woody-resultants-ups-434-2016.pdf) and some cool Joseph [writeups](https://jsur.in/posts/2021-10-03-tsg-ctf-2021-crypto-writeups).

Let's use Sage to find the resultant of these polynomials. We will basically find a univariate polynomial in terms of $q$ only.

```py
P.<x,y> = PolynomialRing(Zmod(n))

f = n - x*y
g = Cy^2 - Cx^3 - x*Cx - y

def resultant(f1, f2, var):
  return Matrix.determinant(f1.sylvester_matrix(f2, var))

h = resultant(f, g, x)  # eliminating x is equivalent to eliminating p

print(h)
```

The output is:
```
y^2 + 11913771694063495132568425582147978387779218009404951491138444355803251420750777828581495229803905485508710200822306270492779460893035511452060758726696972877404214806553422280705330092204004616281420566339823476408647786409010040145494297930530259483781466478416269629186356995544407404915722209121439224567698019474188565402069644492370517495662654444038623713130993722823437453577026376201959720791194856979494885237541302217843842247547112767879217639883793*y
```

We have the polynomial:

$$
h(y) = y^2 + Ay \pmod N
$$

where $A$ is the large integer.

For the correct value of $q$ it holds that:

$$
h(q) = 0 \pmod N
$$

But what can we do now? This polynomial is defined in $\mathbb{Z}/n\mathbb{Z}$ so we can't apply standard techniques that work in the integers $\mathbb{Z}$.

Recall that $q$ is half $p$'s bit length. This means that $q$ is a *small root* of this polynomial, compared to the size of $N$. It turns out we can use Coppersmith's algorithm to find the roots of the polynomial above. These roots are also known as `small roots`.

## Coppersmith's algortihm

It might be a bit complex to describe how the algorithm works but the intuition behind is that when we are looking for something *small* defined over something *big*, then Coppersmith's algorithm should do the trick.

This is why we cared about $q$ being the half $p$'s bit length.

Let's get *a bit* more technical now. Coppersmith's method will return the small roots of our polynomial modulo a factor of $N$, say $p$, without having to factor $N$ at all. Pretty instance, right? That's lattices for you!

Why is this so important?

While the equations are defined modulo $N$, Coppersmith's small roots algorithm finds a small root modulo *a factor of* $N$ and in our case *modulo* $p$.

Sage's `small_roots()` function is an implementation of Coppersmith's algorithm. However, it requires some parameters:

- $X$

  That's an upper bound for the small root we are looking for. In our case, $q$ is at most $2^{512}$ so $X = 2^{512}$.

- `beta` (or $\beta$)

  That's a value such that $p \geq N^\beta$, where $p$ is a factor of $N$. We know that $p \approx n^{\frac{2}{3}}$ or equivalently $p \geq n^{\frac{2}{3}}$ so:
  
  $$\beta = \dfrac{2}{3} = 0.666\dots$$

You can check [here](https://doc.sagemath.org/html/en/reference/polynomial_rings/sage/rings/polynomial/polynomial_modn_dense_ntl.html#sage.rings.polynomial.polynomial_modn_dense_ntl.small_roots) for more information.

## Factoring $N$

Now it's time to factor $N$. Let's run the following code:

```py
roots = h.small_roots(X=2^512, beta=0.66)
print(roots)
```

```py
[0, 7560550953987228717927043411195097606178780260722416435854220484370855427179572047127883844297336386784419855728350626032040641635456814848906770345908561]
```

The second root looks like a candidate for $q$.

```py
print(N % q == 0)
```

```py
True
```

Boom! We have factored $N$.

```py
q = int(h.small_roots(X=2^512, beta=0.66)[1])
p = N // q
assert N == p * q
print(f'p = {p}')
print(f'q = {q}')
```

```py
p = 143466851392554970695990704123817779733897135669358867616227016983904822448652872447294618655211767603232776070689066195417250663712048624942911364907905504389182987025672966027320571640054927174423881068214579019052804849273855736938414398455136976371108924577231955088915205951155616111863602559370112932349
q = 7560550953987228717927043411195097606178780260722416435854220484370855427179572047127883844297336386784419855728350626032040641635456814848906770345908561
```

Now we have to find $O_n$. Since $\mathbb{E}_n$ is defined over a composite ring, it holds that:

$$
O_n = O_p * O_q
$$

where $O_p$ the order of the curve $\mathbb{E}_p$ and $O_q$ the order of the curve $\mathbb{E}_q$.

Knowning $O_n$, we can compute $G$ as shown in $(1)$.

# Full solve script
```py
from sage.matrix.matrix2 import Matrix
from Crypto.Util.number import long_to_bytes

def resultant(f1, f2, var):
  return Matrix.determinant(f1.sylvester_matrix(f2, var))

Cx = 1079311510414830031139310538989364057627185699077021276018232243092942690870213059161389825534830969580365943449482350229248945906866520819967957236255440270989833744079711900768144840591483525815244585394421988274792758875782239418100536145352175259508289748680619234207733291893262219468921233103016818320457126934347062355978211746913204921678806713434052571635091703300179193823668800062505275903102987517403501907477305095029634601150501028521316347448735695
Cy = 950119069222078086234887613499964523979451201727533569872219684563725731563439980545934017421736344519710579407356386725248959120187745206708940002584577645674737496282710258024067317510208074379116954056479277393224317887065763453906737739693144134777069382325155341867799398498938089764441925428778931400322389280512595265528512337796182736811112959040864126090875929813217718688941914085732678521954674134000433727451972397192521253852342394169735042490836886
N = 1084688440161525456565761297723021343753253859795834242323030221791996428064155741632924019882056914573754134213933081812831553364457966850480783858044755351020146309359045120079375683828540222710035876926280456195986410270835982861232693029200103036191096111928833090012465092747472907628385292492824489792241681880212163064150211815610372913101079146216940331740232522884290993565482822803814551730856710106385508489039042473394392081462669609250933566332939789
e = 65537

P.<p,q> = PolynomialRing(Zmod(N))

f = N - p*q
g = Cy^2 - Cx^3 - p*Cx - q
h = resultant(f, g, p).univariate_polynomial()

q = int(h.small_roots(X=2^512, beta=0.66)[1])
p = N // q

assert N == p * q

E = EllipticCurve(Zmod(N), [p,q])
Ep = EllipticCurve(GF(p), [p,q])
Eq = EllipticCurve(GF(q), [p,q])

On = Ep.order() * Eq.order()

C = E(Cx, Cy)
G = int(pow(e, -1, On)) * C
flag = long_to_bytes(int(G[0]))

print(flag)
```

## Output
```
b"TSJ{i_don't_know_how_to_come_up_with_a_good_flag_sorry}S+V\xd8-\x9cQ9\x07\xb0\xdb\xd4h\x1d\x08\xa9=\xc4\x97\xa1\xd1\xa8\x9e\x82\xf5\x85iq\xc4\x03\x9a\xa55\xcb\xc4\x18I\xc5so\xafhHPk\x1cZ\xdf\x00P\xfc9X\xdep\xb1\xe6\x85\xdd\xb6\x07%\xbb!\xbc\xf2M\xf8\x1b\xdd\xf3\xed\x06\xf8\xe3-\xa53NWb\xc5\xa2\xd6;o\xc9\x0fMtI\xf3\xa2\x8bU\xa4>\x15~\xb1\xc2\xbc\x85\x8dM\x06\xdc>\xd1\xa2\xa2\xb9cwN\xa5)\x0c=\xacF\xe0[\xb9\xbdgcIYk\xbd\xfe\xde\xd1\xe0\xb7\xfe"
```

# Flag

```
TSJ{i_don't_know_how_to_come_up_with_a_good_flag_sorry}
```