---
name: test-coverage-audit
description: >-
  Adversarial test coverage audit. Analyzes the specification and
  existing test suite to find untested features, then generates
  adversarial test cases to expose the gaps. Optionally reads
  implementation source for deeper whitebox analysis.
use_for: >-
  Auditing test suite completeness, finding untested features, or
  generating adversarial test cases.
dont_use_for: >-
  Writing the initial test suite, stress testing, or opaque-box test design.
---

# Test Coverage Audit Playbook

Adversarial audit of a test suite's feature coverage. Your job is to find what
the tests **don't** test — then write tests that expose those gaps.

## Audit Modes

This playbook operates in two modes depending on available inputs:

-   **Opaque-box** (spec + tests only): Audit coverage against the
    specification. Use when implementation source is not available or when
    testing must be requirement-driven.
-   **Whitebox** (spec + tests + source): Additionally analyze implementation
    code to find untested code paths and potential bugs. Use when you have
    access to the implementation source.

## Prerequisites

You need access to:

1.  **Specification** — `ORIGINAL_REQUEST.md`, `PROJECT.md`, or any document
    listing what the product must do
2.  **Existing test suite** — the tests you are auditing
3.  **Implementation source code** (whitebox mode only) — the product being
    tested. Enables Source B analysis in Phase 1.
4.  **Reference implementation** (if available) — an oracle to verify your
    adversarial tests produce the correct output

## Audit Procedure

### Phase 1: Feature Matrix Extraction
Build a comprehensive checklist of every feature the product supports using Source A (Spec), Source B (Implementation), and Source C (Existing test suite).

### Phase 2: Feature-to-Test Mapping
For each feature in the matrix, find whether the existing test suite exercises it.

### Phase 3: Gap Report
For each uncovered feature, assess Severity (High, Medium, Low) and Why it matters.

### Phase 4: Adversarial Test Generation
For each gap (prioritized by severity), write a targeted, adversarial, self-verifying test case (`adv_*`).

### Phase 5: Validation
Run every adversarial test against the product under test and record pass/fail.
