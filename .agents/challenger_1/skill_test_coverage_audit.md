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
- **Opaque-box** (spec + tests only)
- **Whitebox** (spec + tests + source)

## Audit Procedure
1. **Phase 1: Feature Matrix Extraction** (Source A Spec, Source B Implementation, Source C Existing tests)
2. **Phase 2: Feature-to-Test Mapping**
3. **Phase 3: Gap Report**
4. **Phase 4: Adversarial Test Generation** (`adv_*` naming convention)
5. **Phase 5: Validation**
