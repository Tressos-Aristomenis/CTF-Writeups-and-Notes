- $p_i, A_i \simeq 2^{2048}$
- $s_i \simeq 2^{256}$

- Task : Recover $s_i$

$$
A = s_0 \cdot h_0 + s_1 \cdot h_1 + s_2 \cdot h_2 + s_3 \cdot h_3 + s_4 \cdot h_5 + s_5 \cdot h_5 \pmod {p}\\
$$

# SVP Approach

$$
s_0
\begin{pmatrix}
1\\
0\\
0\\
0\\
0\\
0\\
0\\
h_0\\
\end{pmatrix}
+
s_1
\begin{pmatrix}
0\\
1\\
0\\
0\\
0\\
0\\
0\\
h_1\\
\end{pmatrix}
+
s_2
\begin{pmatrix}
0\\
0\\
1\\
0\\
0\\
0\\
0\\
h_2\\
\end{pmatrix}
+
s_3
\begin{pmatrix}
0\\
0\\
0\\
1\\
0\\
0\\
0\\
h_3\\
\end{pmatrix}
+
s_4
\begin{pmatrix}
0\\
0\\
0\\
0\\
1\\
0\\
0\\
h_4\\
\end{pmatrix}
+
s_5
\begin{pmatrix}
0\\
0\\
0\\
0\\
0\\
1\\
0\\
h_5\\
\end{pmatrix}
+
k
\cdot
\begin{pmatrix}
0\\
0\\
0\\
0\\
0\\
0\\
1\\
p\\
\end{pmatrix}
+
1
\begin{pmatrix}
0\\
0\\
0\\
0\\
0\\
0\\
0\\
-A\\
\end{pmatrix}
=
\begin{pmatrix}
s_0\\
s_1\\
s_2\\
s_3\\
s_4\\
s_5\\
k\\
0\\
\end{pmatrix}
$$

### Why?

$$
\begin{pmatrix}
s_0 & s_1 & s_2 & s_3 & s_4 & s_5 & k & 1
\end{pmatrix}
\cdot
\begin{bmatrix}
1 & 0 & 0 & 0 & 0 & 0 & 0 & h_0\\
0 & 1 & 0 & 0 & 0 & 0 & 0 & h_1\\
0 & 0 & 1 & 0 & 0 & 0 & 0 & h_2\\
0 & 0 & 0 & 1 & 0 & 0 & 0 & h_3\\
0 & 0 & 0 & 0 & 1 & 0 & 0 & h_4\\
0 & 0 & 0 & 0 & 0 & 1 & 0 & h_5\\
0 & 0 & 0 & 0 & 0 & 0 & 1 & p\\
0 & 0 & 0 & 0 & 0 & 0 & 0 & -A\\
\end{bmatrix}
=
\begin{pmatrix}
s_0 & s_1 & s_2 & s_3 & s_4 & s_5 & k & 0
\end{pmatrix}
$$

Unfortunately, works 7/10 times.

### Alternatively

$$
\begin{pmatrix}
s_0 & s_1 & s_2 & s_3 & s_4 & s_5 & k & 1
\end{pmatrix}
\cdot
\begin{bmatrix}
1 & 0 & 0 & 0 & 0 & 0 & 0 & h_0\\
0 & 1 & 0 & 0 & 0 & 0 & 0 & h_1\\
0 & 0 & 1 & 0 & 0 & 0 & 0 & h_2\\
0 & 0 & 0 & 1 & 0 & 0 & 0 & h_3\\
0 & 0 & 0 & 0 & 1 & 0 & 0 & h_4\\
0 & 0 & 0 & 0 & 0 & 1 & 0 & h_5\\
0 & 0 & 0 & 0 & 0 & 0 & B & -A\\
0 & 0 & 0 & 0 & 0 & 0 & 0 & p\\
\end{bmatrix}
=
\begin{pmatrix}
s_0 & s_1 & s_2 & s_3 & s_4 & s_5 & B & 0
\end{pmatrix}
$$

where $B = 2^{256}$ and works as a scaling factor.

#### Why?

$$
s_0
\begin{pmatrix}
1\\
0\\
0\\
0\\
0\\
0\\
0\\
h_0\\
\end{pmatrix}
+
s_1
\begin{pmatrix}
0\\
1\\
0\\
0\\
0\\
0\\
0\\
h_1\\
\end{pmatrix}
+
s_2
\begin{pmatrix}
0\\
0\\
1\\
0\\
0\\
0\\
0\\
h_2\\
\end{pmatrix}
+
s_3
\begin{pmatrix}
0\\
0\\
0\\
1\\
0\\
0\\
0\\
h_3\\
\end{pmatrix}
+
s_4
\begin{pmatrix}
0\\
0\\
0\\
0\\
1\\
0\\
0\\
h_4\\
\end{pmatrix}
+
s_5
\begin{pmatrix}
0\\
0\\
0\\
0\\
0\\
1\\
0\\
h_5\\
\end{pmatrix}
+
1
\begin{pmatrix}
0\\
0\\
0\\
0\\
0\\
0\\
B\\
-A\\
\end{pmatrix}
+
k
\cdot
\begin{pmatrix}
0\\
0\\
0\\
0\\
0\\
0\\
0\\
p\\
\end{pmatrix}
=
\begin{pmatrix}
s_0\\
s_1\\
s_2\\
s_3\\
s_4\\
s_5\\
B\\
0\\
\end{pmatrix}
$$

We add $B$ cause we want to weight it as much as the other columns. In reality, what happens is that the column with $-A$ is interpreted as:

$$
\cdots
+
B
\begin{pmatrix}
0\\
0\\
0\\
0\\
0\\
0\\
1\\
-A\\
\end{pmatrix}
$$

We essentially weight the columns that we want them to play an important role in the final result. Indeed, $-A$ cannot be omitted as it plays significant role in making the entire equation $= 0$. By multiplying with $B$, we force it to appear in the reduced matrix.


# CVP Approach

$$
s_0
\begin{pmatrix}
1\\
0\\
0\\
0\\
0\\
0\\
h_0\\
\end{pmatrix}
+
s_1
\begin{pmatrix}
0\\
1\\
0\\
0\\
0\\
0\\
h_1\\
\end{pmatrix}
+
s_2
\begin{pmatrix}
0\\
0\\
1\\
0\\
0\\
0\\
h_2\\
\end{pmatrix}
+
s_3
\begin{pmatrix}
0\\
0\\
0\\
1\\
0\\
0\\
h_3\\
\end{pmatrix}
+
s_4
\begin{pmatrix}
0\\
0\\
0\\
0\\
1\\
0\\
h_4\\
\end{pmatrix}
+
s_5
\begin{pmatrix}
0\\
0\\
0\\
0\\
0\\
1\\
h_5\\
\end{pmatrix}
+
k
\cdot
\begin{pmatrix}
0\\
0\\
0\\
0\\
0\\
0\\
p\\
\end{pmatrix}
$$

$$
\begin{pmatrix}
s_0 &
s_1 &
s_2 &
s_3 &
s_4 &
s_5 &
k
\end{pmatrix}
\cdot
\begin{bmatrix}
1 & 0 & 0 & 0 & 0 & 0 & h_0\\
0 & 1 & 0 & 0 & 0 & 0 & h_1\\
0 & 0 & 1 & 0 & 0 & 0 & h_2\\
0 & 0 & 0 & 1 & 0 & 0 & h_3\\
0 & 0 & 0 & 0 & 1 & 0 & h_4\\
0 & 0 & 0 & 0 & 0 & 1 & h_5\\
0 & 0 & 0 & 0 & 0 & 0 & p\\
\end{bmatrix}
\simeq
\begin{pmatrix}
2^{256} & 2^{128} & 2^{224} & 2^{256} & 2^{224} & 2^{256} & A
\end{pmatrix}
$$