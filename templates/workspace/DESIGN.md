---
# The product's design system, in the DESIGN.md format (github.com/google-labs-code/design.md).
# Tokens here are normative: prototypes use them as they are. Setup fills this file from the
# design source (Figma variables, the app's CSS or theme files, a brand guide). Delete these
# comment lines once it is filled. Check it with: python3 .pm-harness/pm_check.py design DESIGN.md
name: <Product name>
description: <one-line description of the visual system>
colors:
  primary: "<#hex>"
  on-primary: "<#hex>"
  surface: "<#hex>"
  on-surface: "<#hex>"
  muted: "<#hex>"
  border: "<#hex>"
  success: "<#hex>"
  warning: "<#hex>"
  error: "<#hex>"
typography:
  title:
    fontFamily: "<family, fallback>"
    fontSize: "<rem>"
    fontWeight: 600
    lineHeight: 1.25
  body:
    fontFamily: "<family, fallback>"
    fontSize: "<rem>"
    fontWeight: 400
    lineHeight: 1.5
  label:
    fontFamily: "<family, fallback>"
    fontSize: "<rem>"
    fontWeight: 500
    lineHeight: 1.3
rounded:
  sm: "<px>"
  md: "<px>"
spacing:
  sm: "<px>"
  md: "<px>"
  lg: "<px>"
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
    rounded: "{rounded.md}"
---

# Design System: <Product name>

## Overview
<!-- Two or three sentences: the personality, density and feel of the product's screens. -->

## Colors
<!-- Each colour token: where it is used and where it is not. Dark mode, if the app has one. -->

## Typography
<!-- The families, the scale (title, body, label…) and where each size is used. -->

## Layout
<!-- Grid, screen margins, spacing rhythm, how screens adapt from phone to desktop. -->

## Elevation & Depth
<!-- Shadows or tonal layers, and when each is used. Say so if the system is flat. -->

## Shapes
<!-- Corner radii, borders, icon style (stroke weight, filled or outline). -->

## Components
<!-- Buttons, inputs, lists, cards, sheets, banners: shape, colours and every state. -->

## Do's and Don'ts
<!-- Concrete rules from the real product, e.g. "Don't use the accent on inactive states." -->
