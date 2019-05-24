---
layout: default
title: Status
---

## Project Summary

In the first working implementation of StevesFightClub, the agent will only use a sword to fight at most two zombies at a time. The agent can attack, strafe left/right, walk forwards/backwards, and turn around. The agent currently takes into consideration nearby enemies, but future implementations could consider the type and health of the enemy.


## Approach



## Evaluation



## Remaining Goals and Challenges

A wider variety of enemies, a baseline to compare performance, and more weapons such as bows, arrows, and shields

One of the challenges encountered was when the agent backed itself into the corner of the arena and was surrounded by enemies. The agent does not have anyway of knowing the surrounding blocks, and this situation usually led to the agent's death. 
A solution could be to increase the arena size, but this may result in the agent running away to avoid damage/death. We could implement a way for the agent to find out about its surroundings so when it retreats, the agent will learn that retreating into a corner can lead to a bad reward.

## Resources Used

Malmo Python examples: the tutorials, tabular_q_learning.py, hit_test.py, and mob_fun.py
