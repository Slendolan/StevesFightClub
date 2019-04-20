---
layout: default
title: Proposal
---

## Summary of the Project
The main goal of our project is to build an agent that can fight against all sorts of mobs in Minecraft. Armed with fighting equipment, the agent should find the optimal way to defeat enemies by taking into consideration the type of enemy, distance from enemy, terrain, and health. The agent will output controls that are available to a human player, such as moving, jumping, attacking, etc. 

## AI/ML Algorithms
We plan to implement reinforcement learning in our project. This will enable the agent to learn from its mistakes and experiences and do better in the next trial. 

## Evaluation Plan
We can measure and evaluate the agent by time taken, damage taken, damage dealt, and types of enemies defeated. The baseline will be for the agent to defeat a zombie without dying. At the end of our project, we aim for the agent to defeat fifty zombies without taking damage. An initial evaluation of the data can be -1 for each second taken, -10 for each point of damage taken, +10 for each point of damage dealt, and +100 for a defeated enemy. These values can be changed as the project progresses to help improve the agent. 

To verify that our project works, the sanity cases will be to place the agent in an arena with an enemy mob. The types of mobs can be changed, and our agent should be able to defeat the enemy without dying. The moonshot case of our project is for the agent to win against boss mobs, such as an ender dragon. 

## Appointment
9:45am - 10:00am on April 29, 2019
