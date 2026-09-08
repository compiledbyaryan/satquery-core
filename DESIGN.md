---
name: SatQuery Field Desk
description: Editorial Earth observation interface with inspectable evidence.
colors:
  paper: "#f5f4ef"
  panel: "#fffefa"
  forest: "#12221f"
  ink: "#15251f"
  lime: "#c7df5a"
  quiet: "#59675f"
  link: "#176f68"
  divider: "#d7dcd1"
typography:
  display:
    fontFamily: "Georgia, serif"
    fontWeight: 400
  body:
    fontFamily: "Segoe UI, system-ui, sans-serif"
    fontSize: "15px"
    lineHeight: 1.5
rounded:
  control: "5px"
---

# Design System: SatQuery Field Desk

## Overview

**Creative North Star: "Field Desk"**

The implemented interface combines warm paper, forest framing and editorial headings with compact, practical controls. Synthetic observation imagery anchors the workbench; findings and source details sit beside it. The independent landing introduces the same identity through oversized typography and a contour globe explicitly labelled decorative.

**Key Characteristics:**

- Image-led investigation.
- Restrained editorial hierarchy.
- Visible distinctions between synthetic examples and recorded output.

## Colors

Lime marks primary workbench actions and active navigation against forest framing. Paper and panel neutrals support reading; ink carries primary text, quiet green secondary context, and teal links and focus. Fine dividers separate working regions. Error and unresolved states combine distinct warm colors with textual labels.

## Typography

Georgia supplies the landing headline, workspace title, question prompt, findings and recorded output. Segoe UI with system fallbacks carries controls and explanatory text; system monospace carries technical identifiers.

The workspace title is (29px); findings use (21px). The landing headline uses a responsive display scale with tight leading. Workbench body text is deliberately denser than the landing's introductory copy.

## Layout

Desktop uses a compact vertical navigation rail, flexible image column and evidence sidebar. Inputs expand beneath the toolbar. The composer follows the imagery, retaining selected-input context.

At (800px) and below, workbench evidence and recorded-run columns stack. At (480px), navigation becomes horizontal, before/after images stack and composer actions fill the available width. The landing switches its split composition to one column at (700px).

## Elevation & Depth

Tonal panels and thin borders establish most hierarchy. The inline evidence drawer adds a restrained shadow (0 10px 24px #15251f12). Depth supports inspection without obscuring the observation.

## Shapes

Controls have subtly rounded corners; the landing call-to-action uses (4px). Comparison controls form a joined segmented group. Images retain rectangular frames; circular contour geometry belongs to the landing illustration.

## Components

Buttons use compact labels, explicit selected states and restrained hover changes. Inputs use a light panel fill and visible stroke. Global focus outlines are teal (3px), with offsets.

The Inputs toggle progressively reveals asset assignments. Selecting a claim opens its matching inline evidence drawer with source, identifiers and limitations.

Investigation stages remain visible beside the imagery and explicitly say simulated workflow with no live analysis. Recorded output has its own view, a native (64px by 64px) pixelated source image, verbatim model text and the original human review.

Both applications disable animation and transitions under reduced-motion preferences. Status updates use a polite live region.

## Do's and Don'ts

- **Do** preserve evidence labels, source context and clear keyboard focus.
- **Do** keep the workbench independently buildable from the landing.
- **Don't** turn synthetic progress or recorded output into a live-execution claim.
- **Don't** enlarge the recorded source into a fabricated high-resolution image.
