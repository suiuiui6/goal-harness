# Checklists

## Bootstrap Checklist (Layer 0-6)

### Layer 0

- [ ] Capability statements are explicit and evidence-based.
- [ ] Non-capability list is explicit.
- [ ] Boundary records are persisted.

### Layer 1

- [ ] Each component uses isolated runtime.
- [ ] Secret files are ignored; secret template exists.
- [ ] Minimal MVP script runs end-to-end per component.
- [ ] Execution artifacts are preserved.
- [ ] Component spec is derived from measured output.

### Layer 2

- [ ] Integration topology spec references all upstream component specs.
- [ ] Every stage has explicit input/output schema.
- [ ] Stage-by-stage verification has been performed.
- [ ] Cache/replay mode exists for downstream debugging.

### Layer 3

- [ ] Optional external tooling (if used) passes connectivity checks.
- [ ] Technical architecture document exists with ADR rationale.
- [ ] No unvalidated component enters architecture.

### Layer 4

- [ ] PRD completed first.
- [ ] Backend API spec completed second.
- [ ] Frontend system spec completed third.
- [ ] Cross-document consistency has been checked.
- [ ] Feature priorities and implementation route are explicit.

### Layer 5

- [ ] Engineering rules document is complete and discoverable.
- [ ] Runtime isolation and dependency lock rules are explicit.
- [ ] Secret handling and logging safety rules are explicit.
- [ ] Integration tests are required on real dependencies.
- [ ] Collaboration roles and review/debug loops are explicit.
- [ ] Product Contract includes version declaration.
- [ ] Product Contract includes boundary definition.
- [ ] Product Contract includes change log.
- [ ] Product Contract includes acceptance criteria.
- [ ] Layer 5 is not marked passed if any Product Contract field is missing.

### Layer 6

- [ ] Frontend and backend run independently.
- [ ] Backend endpoint integration tests pass.
- [ ] Integration workflow works end-to-end.
- [ ] Runtime bug root-cause/fix loop is closed.
- [ ] Static review issue list is closed.
- [ ] Production-readiness checklist passes.

## Production-Readiness Checklist

- [ ] Dependency vulnerability scan has no blocking severity.
- [ ] Logs contain no secrets.
- [ ] External calls define timeout and failure behavior.
- [ ] Required environment keys are listed in secret template.
- [ ] Documentation matches current behavior.
- [ ] Runtime isolation controls are defined (permissions/hooks/sandbox model).

## Maintenance Iteration Checklist

- [ ] Change impact layer is identified.
- [ ] Rollback scope is minimal and explicit.
- [ ] Affected specs are updated.
- [ ] Tests for affected contracts are executed.
- [ ] New findings are written back to relevant docs.

## Anti-Pattern Spot Check

- [ ] No capability assumptions without evidence.
- [ ] No integration before per-component MVP pass.
- [ ] No blueprint skip before implementation.
- [ ] No docs-code drift left unresolved.
- [ ] No review or readiness bypass before release.
