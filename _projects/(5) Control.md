---
name: Safe Control
# tools: [nothing, important]
image: flipper.gif
description: We are thinking about how to control soft-rigid systems to ensure safety in unknown environments.
# external_url: https://www.google.com
category: srh
---

# Control of Robots in Uncertain Environments

How should robots imbued with structural flexibility be controlled in order to maximize safety and robustness while also allowing precision? This question motivates by current focus within control, and my lab explores it through a variety of different approaches. While traditional approaches (e.g. impedance control) get us pretty far, we have recently begun to incorporate optimization-based control which can encode the unique physical attributes of our new classes of soft-rigid hybrid robots, allowing us to solve more complex control problems and directly encode notions of safety.

A major motivator for my current work is the apparent contradiction between precision of traditional feedback control and the closed loop compliance of a robotic system. Essentially, as we turn up our proportional control knob to decrease the control error, we reduce the compliance of the system, as seen in the following simple demo.
![preview](highk.gif)
Had I not removed my finger, the robot would have either crushed my finger or the motors would have burnt out. This means that our cuddly, "safe" soft robot is not so safe when operated with pure feedback control. Thus, for this work we are seeking alternatives.

## Control Barrier Functions for Soft Robots
![preview](cbf_gif_new.gif)

## Sensorless Fofce Control
![preview](flipper.gif)

## Impedance Control
![preview](impedance_new.gif)

## Safe Control with Actuator Saturation
![preview](sma.gif)


## Publications
