---
name: "Tentacles: what is the point?"
# tools: [Node JS, JavaScript, HTML, CSS]
image: floating_goal.gif
description: Octopuses, elephant trunks, giraffe tongues, and ... brittle stars? We are developing techniques to harness the power of bending.
category: srh
# external_url: https://github.com/YoussefRaafatNasry
---

# We Like Tentacles

Why are soft roboticists obsessed with producing robots that look like tentacles? I guess we would need a psychologist to answer that question. However, we at CyPhiLab are as guilty as anyone in seeing the innate promise in this concept. Tentacle-like robots have immense potential in medical research, disaster response, and just plain old pick-and-place. But we as a field have spent 15 years chasing this hunch. So what is the point and when will we get to it? 

To me, one of the major reasons that tentacle-like robots have not entered the mainstream is that we treat them like standard Cobots (such as the Franka FR3). What I mean is that we tend to treat the arm of the manipulator as a vehicle to get the end effector to where it needs to go. Then, when the end effector gets there, we grasp the object and move to the next waypoint. However, Cobots are already widely used in industry for solving this class of problems, and the applications where a soft robot would have a more favorable performance profile are quite limited. Instead, we are working on whole-body manipulation and control for soft continuum robots. These days, we are developing advanced control for systems such as the wonderful [Spirob](https://www.sciencedirect.com/science/article/pii/S2666998624006033):

<div class="figure-row" style="max-width: 420px">
  <figure>
    <video src="spirob_grasp.mp4" autoplay muted loop playsinline></video>
    <figcaption>RL-Trained Grasping Policy.</figcaption>
  </figure>
</div>

# Brittle Star Research

The goal of this research project was to produce a state-of-the-art soft robot inspired by the brittle star, a curious order of echinoderms that is suprisingly mobile. The following Youtube video contains a nice overview of this interesting species:
{% include elements/video.html id="50fSuNqq-JQ" %}

In early 2020, we developed what was at the time (and maybe still is) perhaps the most sophisticated untethered soft robot ever created. The device has a suite of sensors and 20 shape memory alloy actuators, which allow for very tight system integration as long as you are OK sacrificing efficiency. Here is a video from our initial paper:
{% include elements/video.html id="j18NgpCnn3c" %}

We used the robot to make fundamental contributions in soft robot control and manufacturing, along with making contributions to the physics of underwater walking (this work is still in preparation but a preliminary form can be found in Zach Patterson's thesis).

## Publications
- Pham, H., & Patterson, Z. J. (2026). Control Lyapunov Functions for Underactuated Soft Robots. arXiv preprint arXiv:2603.05638. [Link](https://arxiv.org/abs/2603.05638)
- Z. J. Patterson, A. P. Sabelhaus, K. Chin, T. Hellebrekers, and C. Majidi, “An Untethered Brittle Star-Inspired Soft Robot for Closed-Loop Underwater Locomotion,” IROS, Oct. 2020. [Link](https://arxiv.org/abs/2003.13529)
- Z. J. Patterson, A. P. Sabelhaus, and C. Majidi, “Robust Control of a Multi-Axis Shape Memory Alloy-Driven Soft Manipulator,” IEEE Robotics and Automation Letters, Apr. 2022. [Link](https://arxiv.org/abs/2110.10022)` `  
- Z. J. Patterson, D. K. Patel, S. Bergbreiter, L. Yao, and C. Majidi, “A Method for 3D Printing and Rapid Prototyping of Fieldable Untethered Soft Robots,” Soft Robotics, Apr. 2023. [Link](https://par.nsf.gov/servlets/purl/10348585)` `  
- X. Huang, M. Ford, Z. J. Patterson, M. Zarepoor, C. Pan, and C. Majidi, “Shape memory materials for electrically-powered soft machines,” J. Mater. Chem. B, Jun. 2020. [Link](https://pubs.rsc.org/en/content/getauthorversionpdf/d0tb00392a)
