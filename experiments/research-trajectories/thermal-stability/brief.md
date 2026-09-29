# Thermal model: frozen brief

Source: the raw forward-test user task supplied to this worker on 2026-09-28.

Purpose: determine a concrete next build for a thermal model without mistaking a computational artifact for a material mechanism.

Given model: periodic rod, length 1, u_t = alpha u_xx, alpha = 0.01; central spatial differences and forward Euler. N=20 with dt=0.10 reportedly shows smooth decay; N=80 with the same dt reportedly develops ringing. Proposed team interpretation: add material resonance. These are user-reported observations and a proposal; no experimental temperature measurements or original solver files were supplied.

Given possible initial condition: u_j(0) = sin(2 pi x_j) + 0.001 (-1)^j. For the executable fixture, use N unique periodic points x_j=j/N and treat u as temperature relative to a reference. Length/time units were not specified. No inference of material properties from synthetic data is authorized.

Resources: standard-library Python, local filesystem. No network, external dependencies, external measurements, or paid tools. Work stays in /private/tmp/via-negativa-numerical-test.

First cycle: three continuing representation routes, then executable comparison and obligation-derived checks. All four team execution slots were occupied when this worker inspected them, so the routes remain locally distinct rather than launching more workers. No claim of independent human/agent validation is made.

Question v1: Is the observed ringing informative about the material, or can the stated numerical construction produce it?
Question v2 (provisional refinement, same purpose): Which spatial modes does the update amplify, and which prospective correction controls all of them without erasing the modeled physics?

Preserve alpha, periodicity, and the user objective. A proposed numerical correction is a scratch prototype. No production solver or material model is changed.
