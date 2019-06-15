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


#### States


In our initial states, we stored x and z coordinates, but we decided that it would be better to store positions, such as being near the wall or the corner of the arena. This turned out to not be enough, because the agent had no information about the direction it was facing in relation to the wall or corner.  So if it would learn a certain response to being near a wall, say to move left away from the wall, if it encountered a wall to the left in another instance and needs to move right to get away and fails, it would quickly unlearn that response.  We had two options for a solution. One was to introduce wall states as additions to the current position states of {wall, corner, nothing}.  The wall states would be something like: wall_left, wall_right, wall_front, wall_back.  Additionally, there would be corner states; only two would be needed: corner_left ( where there's a wall on the left and a wall behind) and corner_right.  We would only need two because our line of sight function takes care of turning and the agent is usually backed into a corner while the zombies are closer to the center, and a situation where the agent is in a corner and somehow has zombies between it and the walls is exceedingly rare and nearly impossible.  Overall this would add 6 total options to the position state, increasing it from 3 to 9; this would increase the total state space by a factor of 3.
The other option was the introduce an entirely new state to the state representation, keeping the position state at 3 options.  The new state would be based on the angle the agent is facing.  Using the yaw of the agent returned by observations, we could make say 4 different options of the state based on the cardinal directions: north, south, east, and west.  This would increase the total number of states by a factor of 4, which is greater than the factor of 3 of the first option.
In the end we chose to go with the first option, the reasoning being that not only does it increase the state space less overall, it also doesn't in our opinion waste states for positions where no walls are around.
We also found that the line of sight update function was tied to our agent action tick rate.  What this resulted in was that sometimes the agent would not be facing a zombie and would still choose to attack. Rather than changing our line of sight function to work outside of the agent tick rate, we instead opted to make the agent more complex by introducing another state based on whether a zombie was in range to attack or not. Since this was based on the ray observations from Malmo's API, we could easily make a function to calculate the state and be confident in the results.  Thus the aim is to have the agent not attack if enemies are not in range. 
Our agent had no information about the arena boundaries, so when it backed itself into a corner, it would not be able to retreat anymore and not know the reason for dying. 


## Evaluation


## References

