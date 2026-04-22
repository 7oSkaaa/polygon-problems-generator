# Statement Writing Guide

Sources:
- https://polygon.codeforces.com/docs/statements-tex-manual
- https://quangloc99.github.io/posts/polygon-codeforces-tutorial/

---

## Structure

Every statement has these sections in Polygon:

| Section | Purpose |
|---|---|
| **Legend** | Problem description / story |
| **Input** | Input format with all constraints |
| **Output** | Expected output format |
| **Notes** | Explanations for examples, edge case clarifications |

Example tests are pulled directly from the actual test cases — mark them with "Use in statements" in the Tests page.

---

## TeX Formatting

### Text Styles

```latex
\textbf{bold text}          % or \bf{bold}
\textit{italic text}        % or \it{italic}
\texttt{monospace text}     % or \tt{mono}  ← use for variable names, code
\emph{emphasized}
\underline{underlined}
\sout{strikethrough}
\textsc{Small Caps}
```

### Text Sizes

```latex
\tiny  \scriptsize  \small  \normalsize
\large  \Large  \LARGE  \huge  \Huge
```

### Math

Problems created after June 1, 2021 use MathJax — full LaTeX math is supported.

```latex
% Inline math
$a_i$, $n \leq 10^9$, $1 \leq k \leq n$

% Display math (centered, separate line)
$$\sum_{i=1}^{n} a_i \leq 10^6$$
```

- **All variables must be in math mode** — never write plain `n`, always `$n$`
- Use `\times` for multiplication — never `x` or `\cdot` unless semantically correct
- Use `\leq`, `\geq`, `\neq` — not `<=`, `>=`, `!=`
- Use `\ldots` for sequences: `$a_1, a_2, \ldots, a_n$`

### Lists

```latex
\begin{itemize}
    \item First bullet
    \item Second bullet
\end{itemize}

\begin{enumerate}
    \item First numbered item
    \item Second numbered item
\end{enumerate}
```

### Images

1. Upload image via **Statement Resource Files** (bottom of Statements page)
2. Use only **black and white** images (color only if necessary)
3. Always include a bounding box:

```latex
\begin{center}
    \includegraphics[bb=0 0 1080 424, scale=0.5]{image.png}
\end{center}
```

### Code Listings

```latex
\begin{lstlisting}
int main() {
    return 0;
}
\end{lstlisting}
```

### Tables

```latex
\begin{tabular}{|c|c|c|}
    \hline
    Col1 & Col2 & Col3 \\
    \hline
    a & b & c \\
    \hline
\end{tabular}
```

Supports: `\hline`, `\cline{i-j}`, `\multicolumn{n}{align}{text}`, `\multirow{n}{width}{text}`

### Center & Links

```latex
\begin{center}
    Centered content
\end{center}

\url{https://example.com}
\href{https://example.com}{link text}
```

---

## Math Symbols Reference

> Source: `symbols.pdf` (LaTeX Mathematical Symbols)
> Unusual symbols require `\usepackage{amssymb}` — already included in Polygon by default.

### Greek Letters

| Symbol | Command | Symbol | Command | Symbol | Command |
|---|---|---|---|---|---|
| α | `\alpha` | β | `\beta` | γ | `\gamma` |
| δ | `\delta` | ε | `\epsilon` | ζ | `\zeta` |
| η | `\eta` | θ | `\theta` | ι | `\iota` |
| κ | `\kappa` | λ | `\lambda` | µ | `\mu` |
| ν | `\nu` | ξ | `\xi` | π | `\pi` |
| ρ | `\rho` | σ | `\sigma` | τ | `\tau` |
| υ | `\upsilon` | φ | `\phi` | χ | `\chi` |
| ψ | `\psi` | ω | `\omega` | | |
| ε | `\varepsilon` | ϑ | `\vartheta` | κ | `\varkappa` |
| ϕ | `\varphi` | ς | `\varsigma` | ρ | `\varrho` |
| Γ | `\Gamma` | Δ | `\Delta` | Θ | `\Theta` |
| Λ | `\Lambda` | Ξ | `\Xi` | Π | `\Pi` |
| Σ | `\Sigma` | Υ | `\Upsilon` | Φ | `\Phi` |
| Ψ | `\Psi` | Ω | `\Omega` | ℵ | `\aleph` |

---

### Math Constructs

```latex
\frac{a}{b}               % fraction
\sqrt{x}                  % square root
\sqrt[n]{x}               % n-th root
\overline{abc}            % overline
\underline{abc}           % underline
\overrightarrow{abc}      % right arrow over
\overleftarrow{abc}       % left arrow over
\widehat{abc}             % wide hat
\widetilde{abc}           % wide tilde
\overbrace{abc}           % brace above
\underbrace{abc}          % brace below
f'                        % derivative (prime)
```

---

### Delimiters

```latex
(  )   [  ]   \{  \}
|  \vert   \|  \Vert
\langle  \rangle
\lfloor  \rfloor
\lceil   \rceil

% Auto-size to content height:
\left( expr \right)
\left\{ expr \right\}
\left| expr \right|
\left\lfloor expr \right\rfloor
\left. expr \right|        % one-sided
```

---

### Variable-Sized Symbols

| Symbol | Command | Symbol | Command |
|---|---|---|---|
| ∑ | `\sum` | ∏ | `\prod` |
| ∫ | `\int` | ∮ | `\oint` |
| ∬ | `\iint` | ∭ | `\iiint` |
| ⋃ | `\bigcup` | ⋂ | `\bigcap` |
| ⊕ | `\bigoplus` | ⊗ | `\bigotimes` |
| ⊙ | `\bigodot` | ⊔ | `\bigsqcup` |
| ∨ | `\bigvee` | ∧ | `\bigwedge` |

```latex
% With limits:
$\sum_{i=1}^{n}$     $\prod_{i=1}^{n}$     $\int_{0}^{\infty}$
```

---

### Standard Functions

Always use these — they render in Roman (upright), not italic:

```latex
\arccos  \arcsin  \arctan  \arg
\cos     \cosh    \cot     \coth
\csc     \deg     \det     \dim
\exp     \gcd     \hom     \inf
\ker     \lg      \lim     \liminf  \limsup
\ln      \log     \max     \min
\Pr      \sec     \sin     \sinh
\sup     \tan     \tanh
```

```latex
% Correct usage:
$\sin(x)$,  $\log_2 n$,  $\gcd(a, b)$,  $\lim_{n \to \infty}$
```

---

### Comparison & Relation Symbols

| Symbol | Command | Symbol | Command |
|---|---|---|---|
| ≤ | `\leq` | ≥ | `\geq` |
| ≠ | `\neq` | ≡ | `\equiv` |
| ≈ | `\approx` | ∼ | `\sim` |
| ≅ | `\cong` | ≃ | `\simeq` |
| ≪ | `\ll` | ≫ | `\gg` |
| ⊂ | `\subset` | ⊃ | `\supset` |
| ⊆ | `\subseteq` | ⊇ | `\supseteq` |
| ∈ | `\in` | ∉ | `\notin` |
| ∋ | `\ni` | ⊥ | `\perp` |
| ∣ | `\mid` | ∥ | `\parallel` |
| ∝ | `\propto` | ⊨ | `\models` |
| ≺ | `\prec` | ≻ | `\succ` |
| ⊴ | `\trianglelefteq` | ⊵ | `\trianglerighteq` |

---

### Binary Operations

| Symbol | Command | Symbol | Command |
|---|---|---|---|
| × | `\times` | ÷ | `\div` |
| ± | `\pm` | ∓ | `\mp` |
| · | `\cdot` | ∘ | `\circ` |
| ∩ | `\cap` | ∪ | `\cup` |
| ∧ | `\wedge` | ∨ | `\vee` |
| ⊕ | `\oplus` | ⊗ | `\otimes` |
| ⊖ | `\ominus` | ⊙ | `\odot` |
| ⊓ | `\sqcap` | ⊔ | `\sqcup` |
| † | `\dagger` | ‡ | `\ddagger` |
| ∖ | `\setminus` | ⊎ | `\uplus` |

---

### Arrows

| Symbol | Command | Symbol | Command |
|---|---|---|---|
| → | `\rightarrow` | ← | `\leftarrow` |
| ⇒ | `\Rightarrow` | ⇐ | `\Leftarrow` |
| ↔ | `\leftrightarrow` | ⇔ | `\Leftrightarrow` |
| ↑ | `\uparrow` | ↓ | `\downarrow` |
| ⟶ | `\longrightarrow` | ⟵ | `\longleftarrow` |
| ⟹ | `\Longrightarrow` | ⟸ | `\Longleftarrow` |
| ↦ | `\mapsto` | ⟼ | `\longmapsto` |
| ↗ | `\nearrow` | ↘ | `\searrow` |
| ↙ | `\swarrow` | ↖ | `\nwarrow` |
| ↪ | `\hookrightarrow` | ↩ | `\hookleftarrow` |
| ⇝ | `\rightsquigarrow` | | |

---

### Miscellaneous Symbols

| Symbol | Command | Symbol | Command |
|---|---|---|---|
| ∞ | `\infty` | ∅ | `\emptyset` |
| ∇ | `\nabla` | ∂ | `\partial` |
| ∀ | `\forall` | ∃ | `\exists` |
| ∄ | `\nexists` | ∴ | `\therefore` |
| ∵ | `\because` | ∠ | `\angle` |
| √ | `\surd` | ℜ | `\Re` |
| ℑ | `\Im` | ℘ | `\wp` |
| ⊤ | `\top` | ⊥ | `\bot` |
| ⋯ | `\cdots` | ⋮ | `\vdots` |
| ⋱ | `\ddots` | … | `\ldots` |
| ♠ | `\spadesuit` | ♥ | `\heartsuit` |
| ♦ | `\diamondsuit` | ♣ | `\clubsuit` |

---

### Math Mode Accents

```latex
\acute{a}    % á
\bar{a}      % ā
\breve{a}    % ă
\check{a}    % ǎ
\ddot{a}     % ä
\dot{a}      % ȧ
\grave{a}    % à
\hat{a}      % â
\tilde{a}    % ã
\vec{a}      % a⃗
```

---

### Math Styles (math mode only)

```latex
$\mathcal{A}$    % Caligraphic:  𝒜ℬ𝒞 ...
$\mathbb{R}$     % Blackboard:   ℝℤℕℚℂ ...  (common for number sets)
$\mathfrak{A}$   % Fraktur:      𝔄𝔅ℭ ...
$\mathsf{A}$     % Sans-serif
$\mathbf{A}$     % Bold
```

Common blackboard bold usage:
```latex
$\mathbb{N}$   % natural numbers
$\mathbb{Z}$   % integers
$\mathbb{Q}$   % rationals
$\mathbb{R}$   % reals
$\mathbb{C}$   % complex numbers
```

---

### Arrays & Piecewise Functions

```latex
% Matrix
\left( \begin{array}{cc}
    a & b \\
    c & d
\end{array} \right)

% Augmented matrix
\left[ \begin{array}{cc|r}
    3 & 4 & 5 \\
    1 & 3 & 729
\end{array} \right]

% Piecewise function
f(x) = \left\{ \begin{array}{rcl}
    x^2  & \mbox{for} & x < 0 \\
    0    & \mbox{for} & x = 0 \\
    x    & \mbox{for} & x > 0
\end{array} \right.
```

Column alignment characters: `l` (left), `r` (right), `c` (center), `|` (vertical line)

---

### Font Sizes in Math

```latex
{\displaystyle \int f(x)\,dx}      % largest (default in $$ $$)
{\textstyle \int f(x)\,dx}         % normal inline size
{\scriptstyle \int f(x)\,dx}       % smaller
{\scriptscriptstyle \int f(x)\,dx} % smallest
```

---

## Writing Rules

- Keep the statement **short and simple** — avoid long stories (they may need to change)
- The statement must be **renderable to PDF** on Polygon — check it
- Use **GPT + Grammarly** to refine and proofread text
- Pay close attention to **LaTeX correctness** — compile to PDF and review
- Separators between values in input: `~` (non-breaking space) or regular space — be consistent

---

## Tutorial

Each problem **must** include a tutorial, also renderable to PDF:
- Either a **full explanation** of the solution
- Or a **brief summary** with a link to attached docs/slides

---

## Commit Messages

```
"Add problem statement"
"Fix LaTeX rendering in statement"
"Add tutorial"
```
