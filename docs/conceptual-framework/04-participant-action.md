---
identifier: CON-0004
title: Participant Action
status: Canonical
version: 0.2
updated: 2026-07
milestone: OWM-0005
depends_on:
  - CON-0001
  - CON-0003
referenced_by:
  - CON-0005
  - CON-0006
  - OWCM-0001
  - OWCM-0003
---

# Participant Action

## Definition

> A Participant Action is an operation performed by a participant within an
> Operational World.

An action is an event.

It realizes, attempts, combines, resists, or invents one or more capabilities.

## Participant

A participant may be:

- a person;
- a group;
- an automated agent;
- a software process;
- a device;
- an institution;
- a nonhuman actor treated as operationally relevant.

The category is functional rather than exclusively human.

## Action and capability

```text
Capability
    makes an operation possible

Participant Action
    enacts or attempts that operation
```

The distinction matters because a capability may exist without being used, and
an attempted action may fail.

## Action states

A Participant Action may be:

- successful;
- unsuccessful;
- partial;
- repeated;
- interrupted;
- reversed;
- prohibited;
- improvised;
- unrecognized by the system;
- misinterpreted by observers.

## Action categories

Possible action categories include:

- spatial action;
- material action;
- interface action;
- communicative action;
- rule action;
- strategic action;
- collaborative action;
- competitive action;
- observational action;
- refusal or non-action.

Non-action may be analytically relevant when a participant could act but
chooses not to.

## Action sequence

Actions often occur in sequences.

```text
approach
↓
inspect
↓
select
↓
place
↓
revise
↓
submit
```

The order, timing, reversibility, and visibility of these actions may affect the
resulting mechanism.

## Action trace

An action trace is a record of what occurred.

Possible traces include:

- changed object position;
- system log;
- saved state;
- video recording;
- written note;
- participant report;
- observer annotation;
- timestamp;
- material wear.

The trace is not identical to the action.

It is evidence about the action.

## Intended and unintended action

Participants may use a capability as intended, reinterpret it, ignore it, or
act outside the represented interface.

Unintended action should not automatically be classified as misuse.

It may reveal:

- a discovered capability;
- unclear constraints;
- a competing interpretation;
- a missing interface;
- an emergent mechanism.

## Research questions

- Which capabilities become actions?
- Which remain unused?
- Which actions are repeated?
- Which actions are prohibited but attempted?
- Which sequences matter?
- Which traces remain?
- How does participant interpretation differ from system intent?

## Revision history

| Version | Milestone | Change |
|---|---|---|
| 0.2 | OWM-0005 | Established canonical definition |
