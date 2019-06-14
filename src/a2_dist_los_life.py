'''
StevesFightClub Version 2
The agent can move and will attack anything that gets close.
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
import logging

RECORDING = False
RECORDING_ITERATIONS = 10 #slow down a segment every x segments
TICKS = 10 #how many ms each game tick is
RECORDING_TICKS = 80 #slows down the game time if we need to record a slower segment
SLEEP =  TICKS * 0.005 #Time between actions; dependent on game speed
RECORDING_SLEEP = RECORDING_TICKS * 0.005
NEAR = 2 #arbitrary number to be adjusted
NEAR *= NEAR #distance is kept as the square of the true distance, no sqrt() calc

recording_directory = "records/"

if sys.version_info[0] == 2:
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)  # flush print output immediately
else:
    import functools
    print = functools.partial(print, flush=True)

missionBaseXML =  '''<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
            <Mission xmlns="http://ProjectMalmo.microsoft.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            
              <About>
                <Summary>Hello world!</Summary>
              </About>
              <ModSettings>
              <MsPerTick>{tick}</MsPerTick>
              </ModSettings>
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
                        <DrawCuboid x1="-20" y1="10" z1="-20" x2="20" y2="10" z2="10" type="glowstone"/>
                        <DrawCuboid x1="-6" y1="4" z1="-6" x2="6" y2="7" z2="6" type="air"/>
                        
                        <DrawEntity x="0" y="7" z="3" type="Zombie"/>
                        <DrawEntity x="0" y="7" z="3" type="Zombie"/>
                        <DrawEntity x="2" y="7" z="3" type="Zombie"/>
                    </DrawingDecorator>
                  
                  <ServerQuitFromTimeUp timeLimitMs="50000"/>
                  <ServerQuitWhenAnyAgentFinishes/>
                </ServerHandlers>
              </ServerSection>
              
              <AgentSection mode="Survival">
                <Name>Berserker</Name>
                <AgentStart>
                    <Placement x="0" y="7" z="0" pitch="10"/>
                    <Inventory>
                        <InventoryItem slot="0" type="stone_sword"/>
                    </Inventory>
                </AgentStart>
                
                <AgentHandlers>
                    <ObservationFromGrid>
                      <Grid name="floorAll">
                        <min x="-10" y="-1" z="-10"/>
                        <max x="10" y="-1" z="10"/>
                      </Grid>
                    </ObservationFromGrid>
                    <ObservationFromRay/>
                    <RewardForDamagingEntity>
                        <Mob type="Zombie" reward="200"/>
                    </RewardForDamagingEntity>
                    <RewardForSendingCommand reward="-1"/>
                    <MissionQuitCommands quitDescription="no enemies left"/>
                    <RewardForMissionEnd rewardForDeath="-1000">
                        <Reward description="out_of_time" reward="-5" />
                        <Reward description="quit" reward="1000" />
                    </RewardForMissionEnd>
                    {video}
                    
                    
                    <ObservationFromNearbyEntities>
                        <Range name="entities" xrange="50" yrange="2" zrange="50" update_frequency="1"/>
                    </ObservationFromNearbyEntities>
                  <ObservationFromFullStats/>
                  <ContinuousMovementCommands turnSpeedDegs="720"/>
                </AgentHandlers>
              </AgentSection>
            </Mission>'''
missionXML = missionBaseXML.format(tick=TICKS, video='')
recordingXML = missionBaseXML.format(tick=RECORDING_TICKS, video='<VideoProducer><Width>1200</Width><Height>720</Height></VideoProducer>')


class Agent(object):
    def __init__(self, actions=[], epsilon=0.3, alpha=0.3, gamma=1.0, iterations=200):
        self.epsilon = epsilon
        self.alpha = alpha
        self.gamma = gamma
        self.delta_eps = epsilon / iterations # goes from high chance of random action -> 0 chance as time progresses
        #self.training = True
        
        self.logger = logging.getLogger(__name__)
        if False: # True if you want to see more information
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)
        self.logger.handlers = []
        self.logger.addHandler(logging.StreamHandler(sys.stdout))
        
        self.actions = ["attack 1", "move -0.5", "move 0.5", "strafe -0.5", "strafe 0.5"]
        self.q_table = {}
        self.canvas = None
        self.root = None
        self.entity_id = None
    
    def updateQTable( self, reward, current_state ):
        old_q = self.q_table[self.prev_s][self.prev_a]
        new_q = old_q + self.alpha * (reward + self.gamma * max(self.q_table[current_state]) - old_q)

        self.q_table[self.prev_s][self.prev_a] = new_q
    
    def updateQTableFromTerminatingState( self, reward ):
        old_q = self.q_table[self.prev_s][self.prev_a]
        new_q = old_q + self.alpha * (reward + self.gamma * max(self.q_table[self.prev_s]) - old_q)
        self.q_table[self.prev_s][self.prev_a] = new_q
    
    def look(self, ob):
        '''
        # Use the line-of-sight observation to determine when to hit:
        if u'LineOfSight' in ob:
            los = ob[u'LineOfSight']
            if los["type"] in mobs:
                agent_host.sendCommand("attack 1")
        '''
        
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
            ob["nearest_mob"] = 100000
            for e in entities:
                i += 1
                if e["name"] in mobs:
                    dist = max(0.0001, (e["x"] - self_x) * (e["x"] - self_x) + (e["z"] - self_z) * (e["z"] - self_z))
                    x_pull += (e["x"] - self_x)/dist
                    z_pull += (e["z"] - self_z)/dist
                    #Attaching nearest mob calculation to the look calculation for simplicity
                    ob["nearest_mob"] = min(ob["nearest_mob"], dist)
            # Determine the direction we need to turn:
            yaw = -180 * math.atan2(x_pull, z_pull) / math.pi
            difference = yaw - current_yaw;
            while difference < -180:
                difference += 360;
            while difference > 180:
                difference -= 360;
            difference /= 180.0;
            agent_host.sendCommand("turn " + str(difference))
    
    def alone(self, obs):
        # Check for enemies
        y = 0
        if u'entities' in obs:
            for x in obs["entities"]:
                if x in mobs:
                    y += 1
            if y == 0:    
                agent_host.sendCommand("quit")

    def adjust_dist_granularity(self, dist):
        #if the nearest mob is closer than some arbitrary distance, log that as one state, otherwise use another state
        if dist < NEAR:
            return 0
        else:
             return 1
         
    def distance_of_points(self, x1, z1, x2, z2):
        return math.sqrt(math.pow(x1 - x2, 2) + math.pow(z1 - z2, 2))
        
    def get_nearest_entity(self, xPos, zPos, obs):
        '''
        for entity in obs["entities"]:
            if entity["id"] == self.entity_id:
                return self.distance_of_points(xPos, zPos, entity["x"], entity["z"])
        '''
        
        for entity in sorted(obs["entities"], key = lambda e: self.distance_of_points(xPos, zPos, e["x"], e["z"])):
            if entity["name"] != "Berserker":
                self.entity_id = entity["id"]
                return self.distance_of_points(xPos, zPos, entity["x"], entity["z"])
        return None

    def calc_state(self, obs):
        line_of_sight = False
        #nearest = 10000
        xPos = int(obs[u'XPos'])
        zPos = int(obs[u'ZPos'])
        distance = self.get_nearest_entity(xPos, zPos, obs)
        if distance != None:
            distance = self.adjust_dist_granularity(distance)
        if distance != None and u'LineOfSight' in obs and obs[u'LineOfSight']["type"] in mobs:
            line_of_sight = obs[u'LineOfSight']["inRange"]
        life = 2
        if obs[u'Life'] < 10:
            life = 1
        return (distance, line_of_sight, life)
        '''
        if "nearest_mob" in obs.keys():
            nearest = self.adjust_dist_granularity(obs["nearest_mob"])
    #return "{}:{}:{}".format(xPos, zPos, nearest)
    '''
        #return "{}".format(nearest)
    
    def act(self, world_state, agent_host, current_r ):
        """take 1 action in response to the current world state"""
        obs_text = world_state.observations[-1].text
        obs = json.loads(obs_text) # most recent observation
        self.logger.debug(obs)
        
        current_s = self.calc_state(obs)
        info_str = "State: {}   ".format(current_s)
        self.logger.debug("State: %s (x = %.2f, z = %.2f)" % (current_s, float(obs[u'XPos']), float(obs[u'ZPos'])))
        if current_s not in self.q_table:
            self.q_table[current_s] = ([0] * len(self.actions))
        
        # Update Q values
        if self.prev_s is not None and self.prev_a is not None:
            self.updateQTable( current_r, current_s )
        
        #self.drawQ( curr_x = int(obs[u'XPos']), curr_y = int(obs[u'ZPos']) )
        # Select the next action
        self.look(obs)
        action = self.actions
        
        rnd = random.random()
        if rnd < self.epsilon:
            a = random.randint(0, len(self.actions) - 1)
            self.logger.info("Random action: %s" % self.actions[a])
        else:
            m = max(self.q_table[current_s])
            self.logger.debug("Current values: %s" % ",".join(str(x) for x in self.q_table[current_s]))
            l = list()
            for x in range(0, len(self.actions)):
                if self.q_table[current_s][x] == m:
                    l.append(x)
            y = random.randint(0, len(l)-1)
            a = l[y]
            
            info_str += "Taking q action: %s" % self.actions[a]
            self.logger.info(info_str)
        
        
        # Try to send the selected action, only update prev_s if this succeeds
        try:
            agent_host.sendCommand(self.actions[a])
            self.prev_s = current_s
            self.prev_a = a
        except RuntimeError as e:
            self.logger.error("Failed to send command: %s" % e)
        
        return current_r
    
    def run(self, agent_host):
        """Run the agent on the world"""
        total_reward = 0
        self.prev_s = None
        self.prev_a = None
        is_first_action = True
        self.epsilon -= self.delta_eps
        agent_sleep = RECORDING_SLEEP if self.recording else SLEEP
        
        # Main loop:
        world_state = agent_host.getWorldState()
        while world_state.is_mission_running:
            current_r = 0
            if is_first_action:
                # Wait until have received a valid observation
                while True:
                    time.sleep(agent_sleep)
                    world_state = agent_host.getWorldState()
                    for error in world_state.errors:
                        self.logger.error("Error: %s" % error.text)
                    for reward in world_state.rewards:
                        current_r += reward.getValue()
                    if world_state.is_mission_running and len(world_state.observations)>0 and not world_state.observations[-1].text=="{}":
                        total_reward += self.act(world_state, agent_host, current_r)
                        break
                    if not world_state.is_mission_running:
                        break
                is_first_action = False
            else:
                # Wait for non-zero reward
                while world_state.is_mission_running and current_r == 0:
                    time.sleep(agent_sleep)
                    world_state = agent_host.getWorldState()
                    for error in world_state.errors:
                        self.logger.error("Error: %s" % error.text)
                    for reward in world_state.rewards:
                        current_r += reward.getValue()
                # Allow time to stabilise after action
                while True:
                    time.sleep(agent_sleep)
                    world_state = agent_host.getWorldState()
                    for error in world_state.errors:
                        self.logger.error("Error: %s" % error.text)
                    for reward in world_state.rewards:
                        print(reward)
                        current_r += reward.getValue()
                    if world_state.is_mission_running and len(world_state.observations)>0 and not world_state.observations[-1].text=="{}":
                        total_reward += self.act(world_state, agent_host, current_r)
                        break
                    if not world_state.is_mission_running:
                        break
        
        # Process final reward
        self.logger.debug("Final reward: %d" % current_r)
        total_reward += current_r
        
        # Update Q values
        if self.prev_s is not None and self.prev_a is not None:
            self.updateQTableFromTerminatingState( current_r )
        
        #self.drawQ()
        return total_reward


if __name__ == '__main__':
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

    n = 1
    num_repeats = 200
    agent = Agent(iterations = num_repeats)
    my_mission = MalmoPython.MissionSpec(missionXML, True)
    my_recording_mission = MalmoPython.MissionSpec(recordingXML, True)

    # Attempt to start a mission:
    max_retries = 3
    
    cumulative_rewards = []
    for i in range(num_repeats):

        
        for retry in range(max_retries):
            try:
                if RECORDING and (i % RECORDING_ITERATIONS == 0):
                    my_mission_record = MalmoPython.MissionRecordSpec("recording_" + str(i) + ".tgz")
                    my_mission_record.recordMP4(60, 8000000)
                    agent.recording = True
                    agent_host.startMission( my_recording_mission, my_mission_record )
                else:
                    agent.recording = False
                    my_mission_record = MalmoPython.MissionRecordSpec()
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
        mobs = ["Zombie", "Pig", "Cow"]
        health_lost = 0
        damage_dealt = 0
        
        # Run the agent in the world
        cumulative_reward = agent.run(agent_host)
        print('Cumulative reward: %d' % cumulative_reward)
        cumulative_rewards += [ cumulative_reward ]
        
        # Clean up
        time.sleep(0.5) # (let the Mod reset)
    
    print()
    print("Mission ended")
    print(cumulative_rewards)
    # Mission has ended.

