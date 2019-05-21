'''
StevesFightClub Version 1
The agent cannot move and will attack anything that gets close.
Malmo Python examples used: tutorial_2.py, hit_test.py
'''

from __future__ import print_function

from builtins import range
import MalmoPython
import os
import sys
import time
import json

import random
import math

if sys.version_info[0] == 2:
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)  # flush print output immediately
else:
    import functools
    print = functools.partial(print, flush=True)

missionXML='''<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
            <Mission xmlns="http://ProjectMalmo.microsoft.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            
              <About>
                <Summary>Hello world!</Summary>
              </About>
              
              <ServerSection>
                <ServerInitialConditions>
                    <Time>
                        <StartTime>18000</StartTime>
                        <AllowPassageOfTime>false</AllowPassageOfTime>
                    </Time>
                <AllowSpawning> false </AllowSpawning>
                </ServerInitialConditions>

                <ServerHandlers>
                  <FlatWorldGenerator generatorString="3;7,3*1;1;,biome_1"/>
                    <DrawingDecorator>
                        <DrawCuboid x1="-10" y1="4" z1="-10" x2="10" y2="6" z2="10" type="glowstone"/>
                        <DrawCuboid x1="-20" y1="20" z1="-20" x2="20" y2="20" z2="10" type="glowstone"/>
                        <DrawCuboid x1="-5" y1="4" z1="-5" x2="5" y2="7" z2="5" type="air"/>
                        <DrawCuboid x1="-5" y1="4" z1="-5" x2="5" y2="4" z2="5" type="torch"/>
                        
                        <DrawEntity x="0" y="7" z="3" type="Zombie"/>
                        <DrawEntity x="2" y="7" z="5" type="Zombie"/>
                        <DrawEntity x="-5" y="8" z="10" type="Zombie"/>
                    </DrawingDecorator>
                  
                  <ServerQuitFromTimeUp timeLimitMs="20000"/>
                  <ServerQuitWhenAnyAgentFinishes/>
                </ServerHandlers>
              </ServerSection>
              
              <AgentSection mode="Survival">
                <Name>Berserker</Name>
                <AgentStart>
                    <Placement x="0" y="7" z="0"/>
                    <Inventory>
                        <InventoryItem slot="0" type="diamond_sword"/>
                    </Inventory>
                </AgentStart>
                
                <AgentHandlers>
                    <ObservationFromRay/>
                    <RewardForDamagingEntity>
                        <Mob type="Zombie" reward="1"/>
                    </RewardForDamagingEntity>
                
                    <ObservationFromNearbyEntities>
                        <Range name="entities" xrange="100" yrange="2" zrange="100" update_frequency="1"/>
                    </ObservationFromNearbyEntities>
                  <ObservationFromFullStats/>
                  <ContinuousMovementCommands turnSpeedDegs="720"/>
                </AgentHandlers>
              </AgentSection>
            </Mission>'''

# Create default Malmo objects:
agent_host = MalmoPython.AgentHost()
try:
    agent_host.parse( sys.argv )
except RuntimeError as e:
    print('ERROR:',e)
    print(agent_host.getUsage())
    exit(1)
if agent_host.receivedArgument("help"):
    print(agent_host.getUsage())
    exit(0)

my_mission = MalmoPython.MissionSpec(missionXML, True)
my_mission_record = MalmoPython.MissionRecordSpec()

# Attempt to start a mission:
max_retries = 3
for retry in range(max_retries):
    try:
        agent_host.startMission( my_mission, my_mission_record )
        break
    except RuntimeError as e:
        if retry == max_retries - 1:
            print("Error starting mission:",e)
            exit(1)
        else:
            time.sleep(2)

# Loop until mission starts:
print("Waiting for the mission to start ", end=' ')
world_state = agent_host.getWorldState()
while not world_state.has_mission_begun:
    print(".", end="")
    time.sleep(0.1)
    world_state = agent_host.getWorldState()
    for error in world_state.errors:
        print("Error:",error.text)

print()
print("Mission running ", end=' ')

# List of mobs to attack
mobs = ["Zombie"]
health_lost = 0
damage_dealt = 0

# Loop until mission ends:
while world_state.is_mission_running:
    world_state = agent_host.getWorldState()
    
    if world_state.number_of_observations_since_last_state > 0:
        msg = world_state.observations[-1].text
        ob = json.loads(msg)
        
        # Use the line-of-sight observation to determine when to hit:
        if u'LineOfSight' in ob:
            los = ob[u'LineOfSight']
            type1=los["type"]
            if type1 in mobs:
                agent_host.sendCommand("attack 1")
                #agent_host.sendCommand("attack 0")
        
        # Get our position/orientation:
        if u'Yaw' in ob:
            current_yaw = ob[u'Yaw']
        if u'XPos' in ob:
            self_x = ob[u'XPos']
        if u'ZPos' in ob:
            self_z = ob[u'ZPos']
        
        # Use the nearby-entities observation to decide which way to move:
        if u'entities' in ob:
            entities = ob["entities"]
            x_pull = 0
            z_pull = 0
            i = 0
            for e in entities:
                i += 1
                if e["name"] in mobs:
                    dist = max(0.0001, (e["x"] - self_x) * (e["x"] - self_x) + (e["z"] - self_z) * (e["z"] - self_z))
                    x_pull += (e["x"] - self_x)/dist
                    z_pull += (e["z"] - self_z)/dist
                #elif e["name"] == "Pig":
                    #pass
            # Determine the direction we need to turn:
            yaw = -180 * math.atan2(x_pull, z_pull) / math.pi
            difference = yaw - current_yaw;
            while difference < -180:
                difference += 360;
            while difference > 180:
                difference -= 360;
            difference /= 180.0;
            agent_host.sendCommand("turn " + str(difference))
            #move_speed = 1.0 if abs(difference) < 0.5 else 0
            #agent_host.sendCommand("move " + str(move_speed))
    
    for error in world_state.errors:
        print("Error:",error.text)
    
print()
print("Mission ended")
# Mission has ended.
