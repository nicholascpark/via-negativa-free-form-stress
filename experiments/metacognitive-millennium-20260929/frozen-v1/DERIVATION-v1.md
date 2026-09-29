# Derivation v1: interaction order versus representation cost

## Transformation B1 — exact visibility threshold

Parent: SHARED-AFFINE-SETUP.md. Changed representation: replace the scalar satisfying-assignment count by the complete collection of joint distributions of constraint violation bits. The assignments remain uniformly distributed and the original equations remain fixed. This is an exact derived observable, but using only that observable is an explicitly lossy restriction on an algorithm's input access.

Let A in F_2^(m×n), let X be uniform in F_2^n, and let V_b=AX+b in F_2^m. Coordinate i of V_b is 1 exactly when equation i is violated. For 0≤k≤m, define S_k(A,b) to be the indexed list of distributions Law((V_b)_J) for *all* subsets J of [m] with |J|≤k. This includes arbitrary nonlinear functions of each such marginal, all their atom probabilities, and all mixed moments of up to k distinct violation bits. No numerical approximation is involved.

Set D=ker(A^T), δ=b+b', and

    d_A(δ) = min {|z| : z in D, z·δ=1},

with min(empty)=infinity. Then

    S_k(A,b)=S_k(A,b')  iff  k<d_A(δ).                 (1)

Proof. For any z in F_2^m,

    E[(-1)^(z·V_b)] = (-1)^(z·b) E[(-1)^((A^Tz)·X)]
                     = (-1)^(z·b) if z in D, and 0 otherwise.

The last expectation cancels in pairs when A^Tz≠0. The Fourier characters supported on J form a basis for all real functions on F_2^J, so two J-marginals agree iff these expectations agree for every z supported on J. They disagree exactly when some such z lies in D and has z·δ=1. Taking every |J|≤k proves (1). At k=d_A(δ)<infinity a minimum-weight z yields a stronger statement: its parity is deterministic and opposite under the two distributions. The corresponding marginal distributions have disjoint supports, so total variation distance is 1.

For b'=0, d_A(b) is also the minimum number of equations in an inconsistent subsystem: a subsystem is inconsistent iff it admits a dual vector supported on its rows with odd dot product with b. This uses the dual criterion from the shared setup. Thus the visibility threshold is an exact invariant of this interface, not a guess that a chosen fixed number of moments happens to be insufficient.

Boundary cases: d=1 handles an inconsistent zero row; d=infinity means δ belongs to im(A) and all joint distributions agree. k=0 yields only the empty marginal and never distinguishes. None of these statements lower-bounds unrestricted computation on A and b.

## Transformation B2 — sparse graph realization and actual 3-CNF

Parent: B1. Change: impose a concrete bounded-arity incidence structure, retaining the full threshold definition. Let G=(V,E) be a finite connected simple graph, m=|V|, n=|E|, and let A be its vertex-edge incidence matrix over F_2. Each edge column has exactly two 1s. A vector z satisfies A^Tz=0 iff its values agree at both endpoints of every edge. Connectivity implies

    D={0,1_V}, rank(A)=m-1.

Take b_even=0 and b_odd equal to the indicator of one vertex. Then d_A(b_even+b_odd)=m. Equation (1) says *all proper-subset joint violation distributions are identical*. More specifically every proper row subset is independent, hence its marginal is exactly uniform. Yet the even instance has 2^(n-m+1) solutions and the odd instance has none. Summing all equations already decides which case holds.

For unbounded instances with constraints of arity exactly three, use the prism graphs C_l square K_2 for l≥3: m=2l, n=3l, every vertex has degree 3. At a vertex with incident edge variables a,b,c and prescribed charge q, forbid each of the four assignments α in F_2^3 with α_a+α_b+α_c≠q. The clause forbidding α has literal x for α_x=0 and literal not-x for α_x=1. The conjunction of these four 3-clauses is equivalent to the parity equation. Hence the graph system is a 3-CNF with 4m clauses, no auxiliary variables, and every edge variable occurs in exactly eight clauses.

For each assignment, an unsatisfied parity equation violates exactly one of its four clauses; a satisfied equation violates none. Therefore the *total number of violated CNF clauses* is exactly U_b=sum_i (V_b)_i. This fact transfers the energy conclusions below to standard 3-CNF. The theorem about all proper-subset marginals is about the m labeled parity blocks, not every individual CNF clause marginal. That stronger clause-level statement is neither asserted nor used.

## Transformation B3 — global correction and exact generating function

Parent: B2 (and general B1). Change: replace enumerated local interactions by the dual space D, which has a basis with at most m vectors. This representation exposes a global operation: take linear combinations of rows and test their right hand sides. For consistency, a basis of D suffices; one need not enumerate its 2^dim(D) elements. This is the polynomial-time repair of the local-summary failure for affine systems.

The full energy generating polynomial is

    Z_b(t)=sum_{x in F_2^n} t^|Ax+b|
          =2^(n-m) sum_{z in D} (-1)^(z·b)
                       (1+t)^(m-|z|) (1-t)^|z|.     (2)

Proof: for v∈{0,1}, t^v=((1+t)+(1-t)(-1)^v)/2. Multiply across coordinates and use the character expectation in B1, then multiply by 2^n. All statements are polynomial identities, including t=0 or t=1.

For a connected graph, let s=(-1)^sum_i b_i. Then

    Z_s(t)=2^(n-m)[(1+t)^m+s(1-t)^m].               (3)

Equivalently the number of assignments with U=j is 2^(n-m+1) binom(m,j) when j has the same parity as sum b_i, and zero otherwise.

Consequences:

1. The satisfiable and unsatisfiable instances have identical E[p(U)] for every real polynomial p of degree less than m. Indeed Z_+(t)-Z_-(t)=2^(n-m+1)(1-t)^m has a zero of order m at t=1, so all factorial moments of orders 0,...,m-1 agree. The same is true of ordinary moments because these are linear combinations of factorial moments.
2. For 0<t<1 define the relative contrast around the mean partition function by

       R_m(t)=(Z_+(t)-Z_-(t))/(Z_+(t)+Z_-(t))
             =((1-t)/(1+t))^m.

   At fixed t this contrast is exponentially small. With t=exp(-β), it is tanh(β/2)^m. To have R_m≥c for fixed 0<c<1 requires exactly

       β ≥ log((1+c^(1/m))/(1-c^(1/m))).            (4)

   This is log m + log(2/(-log c)) + o(1). The interpretation is sensitivity of this particular thermal observable, not a runtime or numerical impossibility theorem. Exact symbolic evaluation of (3) distinguishes the cases immediately.
3. The first missed observable is itself cheap: product_i (-1)^(V_i)=s, a degree-m character describable and evaluable using O(m) operations. High interaction order does not imply high computation cost.

## General-SAT return audit

Why use these summaries? For any Boolean constraint system, if I_i is its satisfaction indicator, then #SAT=2^n E[product_i I_i]. Expanding I_i=1-V_i gives inclusion-exclusion in joint violation moments. Keeping interactions of bounded order is therefore an explicit truncation of an exact counting identity, not an unrelated statistic. Energy/partition-function formulations similarly encode #SAT as Z(0). The examples test those proposals with exact summaries of every proper subset; the amount of supplied local data may itself be exponential.

What is proved: no decision rule whose only instance-dependent input is S_(m-1) (with the common A and dimensions allowed) can distinguish these opposite answers. A randomized rule also has the same output distribution on the pair, so it cannot succeed with probability greater than 1/2 on each member. This is an information restriction, not a time lower bound.

What it teaches about full complexity: a representation-based attempt must account for the *cost of constructing and updating* a global invariant, not just its degree, number of interactions, or order of detection. A general lower-bound route based solely on delayed local visibility is defeated by this polynomial-time affine class. A general algorithmic route must show that a compact invariant survives non-affine constraints.

Exact obstruction to carrying the repair to a clause: the satisfying set of x OR y OR z has seven points, whereas a nonempty affine subspace has a power-of-two cardinality. Thus a single affine coset cannot even represent one ordinary 3-clause exactly. Replacing it with a union of cosets or a richer algebra is possible, but a bound on the number/size of components under conjunction and existential projection has not been proved. Assuming polynomial-size effective closure would insert the desired algorithm into the hypothesis.

The general lower-bound transfer is absent, and a blanket claim that all polynomial-time algorithms factor through S_(m-1) is false on the construction itself. No P-versus-NP separation, algorithm for general SAT, novel proof-system lower bound, or formal proof-assistant verification is claimed.
