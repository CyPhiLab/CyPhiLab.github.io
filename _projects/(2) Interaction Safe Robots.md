---
name: Interaction Safe Robots
# tools: [nothing, important]
image: impedance_new.gif
description: You have no problem bumping the world with your elbow. Neither should robots.
# external_url: https://www.google.com
category: bio
---

# Integrated multi-material robots

We are developing robot systems that can leverage complex material and sensing architectures to improve task performance. The end goal is to create robots that, like humans, are not afraid of bumping into the world in unexpected ways. Ongoing work centers around the design and development of manufacturing approaches to tightly integrate sensing with traditional engineering materials and materials to more closely mimic soft tissue. Most robots shown on this website exhibit this paradigm in some fashion. 

# Custom Whole Body Skins

Perhaps the most promising way that we can have an impact (pun intended) in this area is to develop viable whole body skins for standard commercial robot systems. The idea is to mitigate contact passively (through soft material deformation instead of rigid collision) and actively (by sensorizing the skins). This would be truly revolutionary from a robot motion planning perspective. If you don't believe me, just check out Russ Tedrake's fantastic online [textbook](https://manipulation.mit.edu/) from his course on robot manipulation and note just how essential collision avoidance is for Chapter 6. Robots should be allowed to bump into the world, just as humans do.

As far as I can tell, this concept has been around for about as long as robots have. So why don't we have the skins? My answer is rather unique: prior attempts (of which there are countless) are fundamentally limited by the *manufacturability* of the skin. Using typical fabrication approaches, prior whole body sensory skins that have been developed are far too labor intensive to allow for wide replication let alone mass production. Therefore, we are developing skins allow for rapid manufacturing in the lab (and eventually in the factory). This not only has great benefits for robotic functionality, but it also does wonders for the mental health of graduate students working on it. This avenue imposes an entirely new set of constraints and design choices, but we are confident that this will unlock the potential for a new generation of *physically* safe robots. We're dealing with the hardware and low level control first, because that is the bottleneck, but eventually we will also move towards generating motion plans that *embrace* contact as a probable outcome rather than avoiding it like the plague. 

<div class="figure-row" style="max-width: 260px">
  <figure>
    <video src="skin_demo.mp4" autoplay muted loop playsinline></video>
    <figcaption>CBF-based safety limits deployed on custom skins.</figcaption>
  </figure>
</div>


<!-- ![preview](hitting_2.gif) -->

## Publications
- Z. J. Patterson, E. Sologuren, C. Della Santina, and D. Rus, “Design and Control of Modular Soft-Rigid Hybrid Manipulators with Self-Contact,” arXiv: arXiv:2408.09275. [Link](https://arxiv.org/abs/2408.09275)
- Z. J. Patterson, C. D. Santina, and D. Rus, “Modeling and Control of Intrinsically Elasticity Coupled Soft-Rigid Robots,” ICRA, May 2024. [Link](https://arxiv.org/abs/2311.05362)
