---
layout: default
title: Final Report
---

## Video


## Project Summary

The goal of StevesFightClub is to create an agent that is able to fight and defeat all sorts of Minecraft mobs. 


## Approaches

In our first approach, our agent only knew how to attack while looking at the nearest enemy. 
This would be the baseline for our project. 

Later, we implemented tabular Q-learning for our agent because it would help our agent to improve and get better rewards. 
It could take actions such as attacking, moving forwards/backwards, and strafing left/right. 

For our final approach, we kept the use of Q-tables and changed what kind of states were stored in the table. 
In our initial states, we stored x and z coordinates, but we decided that it would be better to store positions, such as being near the wall or the corner of the arena. 
Our agent had no information about the arena boundaries, so when it backed itself into a corner, it would not be able to retreat anymore and not know the reason for dying. 


## Evaluation


## References

