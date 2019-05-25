---
layout: default
title: Status
---

## Project Summary

In the first working implementation of StevesFightClub, the agent will only use a sword to fight at most two zombies at a time. The agent can attack, strafe left/right, walk forwards/backwards, and turn around. The agent currently takes into consideration nearby enemies, but future implementations could consider the type and health of the enemy.


## Approach

We started by building a world as a 13x13 enclosed arena. We spawned two zombies near the agent. Using the hit_test.py and tutorial files, the agent was able to aim at the zombies and attack. At this time, our agent was only able to attack. It was not able to move and therefore would repeated attacked as he stood still and fought back. 

The next version of our agent include a simple Q table approach. Our current Q table update is as follows:

	`old_q = q_table[prev_s][prev_a]
        new_q = old_q + alpha * (reward + gamma * max(q_table[current_state]) - old_q)`

The state contains the agent’s position. 
This version includes the following actions:
	- attack
	- move forward
	- move left
	- move right
	- move back
The rewards include:
	- -1000 for agent death
	- 100 for damaging an enemy
	- -1 for any action

The agent has a 0.3 chance of choosing a random action and a 0.70 chance of choosing an action from the Q table. We reduce the epsilon over time. As it approaches 200 episodes, the epsilon will reduce to 0. Below shows the output of the random and q table actions chosen.

We are currently experimenting with rewarding the agent more for completing tasks faster. For example, we can include a 1000 reward if the agent defeats all the enemies and completes the mission early and -5 if the agent runs out of mission time. We need more testing in order to evaluate this approach.


## Evaluation

Before the inclusion of Q table, the agent would repeated attack with sword even when the enemies were not in range. However, with the Q table, the agent was strategically attacking when the enemies were in attackable range. The agent was quickly able to learn this after a couple iterations. The agent would also prioritize on attack the closest enemy. The agent would choose the option to attack when there is an opportunity, so prioritizing the closest enemy would most likely provide it with the reward of damaging the enemy. The movement of the agent is still quite sporadic. Hopefully, this will be improved with by taking in more state information.


## Remaining Goals and Challenges

A wider variety of enemies, a baseline to compare performance, and more weapons such as bows, arrows, and shields

One of the challenges encountered was when the agent backed itself into the corner of the arena and was surrounded by enemies. The agent does not have anyway of knowing the surrounding blocks, and this situation usually led to the agent's death. 
A solution could be to increase the arena size, but this may result in the agent running away to avoid damage/death. We could implement a way for the agent to find out about its surroundings so when it retreats, the agent will learn that retreating into a corner can lead to a bad reward.

## Resources Used

Malmo Python examples: the tutorials, tabular_q_learning.py, hit_test.py, and mob_fun.py
