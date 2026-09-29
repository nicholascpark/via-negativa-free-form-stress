# Shared affine setup v1

This setup is independent of the pending research-direction choice.

Let A be an m by n matrix over F_2 and b in F_2^m. A Boolean assignment x satisfies the affine constraint system exactly when Ax=b. Row operations on the augmented matrix [A|b] preserve its solution set. Row reduction therefore either produces an equation 0=1 (inconsistency) or identifies r=rank(A) pivot coordinates and n-r free coordinates. Consequently:

- the system is satisfiable iff rank(A)=rank([A|b]);
- if it is satisfiable, it has exactly 2^(n-r) solutions;
- elimination uses O(m n min(m,n)) individual field operations with a simple rectangular implementation, hence is polynomial in the explicit input length.

This is an elementary derivation, not a claim of a new algorithm. Its role is to provide an exact comparison class where a representation can be exponentially large although deciding existence is polynomial.

A dual form makes the global obstructions explicit. Write D=ker(A^T), using the standard bilinear dot product over F_2. Since im(A) is contained in D-perp and both have dimension r, they are equal. Thus Ax=b is consistent iff z·b=0 for every z in D. A vector z with A^T z=0 and z·b=1 is a certificate of inconsistency: adding the selected equations gives 0=1.

The same dual form yields an exact counting identity. For a in F_2, 1[a=0]=(1+(-1)^a)/2. Expanding the product of row indicators and summing over x gives

    # {x:Ax=b} = 2^(n-m) sum_{z in D} (-1)^(z·b).

The character sum is |D| if b is orthogonal to D, and zero otherwise (pair each z with z+z0 for any z0·b=1). This recovers the rank count above. The possibly negative exponent n-m causes no problem: the displayed expression is a rational identity whose value is the integer count.

Dependencies: finite-dimensional vector-space dimension identities and elementary character orthogonality over F_2. No assumption about P≠NP, randomness, average-case inputs, or oracle access.

Obligation before any general-SAT transfer: arbitrary disjunctions are not affine equations, and general constraint composition need not preserve a polynomial-size linear subspace representation.
