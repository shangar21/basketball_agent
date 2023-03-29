from environment import BasketballEnvironment
from collections import namedtuple
from assets.assets import Action
import random
import math
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import numpy as np
import matplotlib.pyplot as plt
from itertools import count

Transitions = namedtuple("Transitions", ('state', 'action', 'next_state', 'reward'))

class ReplayMemory():
    def __init__(self, capacity):
        self.memory = []

    def push(self, *args):
        self.memory.append(Transitions(*args))

    def sample(self, batch_size):
        return random.sample(self.memory, batch_size)

    def __len__(self):
        return len(self.memory)

class DQN(nn.Module):
    def __init__(self, n_observations, n_actions):
        super(DQN, self).__init__()
        self.layer1 = nn.Linear(n_observations, 256)
        self.layer2 = nn.Linear(256, 256)
        self.layer3 = nn.Linear(256, 256)
        self.layer4 = nn.Linear(256, n_actions)

    def forward(self, x):
        x = F.relu(self.layer1(x))
        x = F.relu(self.layer2(x))
        x = F.relu(self.layer3(x))
        return self.layer4(x)

BATCH_SIZE = 256
GAMMA = 0.99
EPS_START = 0.9
EPS_END = 0.05
EPS_DECAY = 1000
TAU = 0.5
LR = 1e-4

n_actions = 10
env = BasketballEnvironment()
state = env.start()
n_observations = len(state)

policy_net = DQN(n_observations, n_actions)
target_net = DQN(n_observations, n_actions)
target_net.load_state_dict(policy_net.state_dict())

optimizer = optim.AdamW(policy_net.parameters(), lr=LR, amsgrad=True)
memory = ReplayMemory(10_000)

steps_done = 0

LOSS = []

def select_action(state, eps):
    global steps_done
    sample = random.random()
    eps_threshold = eps
    steps_done += 1
    if sample > eps_threshold:
        with torch.no_grad():
            return policy_net(state).max(1)[1].view(1,1)
    else:
        return torch.tensor([[np.random.randint(10)]])

def optimize_model():
    if len(memory) < BATCH_SIZE:
        return

    transitions = memory.sample(BATCH_SIZE)
    batch = Transitions(*zip(*transitions))
    non_final_mask = torch.tensor(tuple(map(lambda s : s is not None, batch.next_state)), dtype=torch.bool)
    non_final_next_states = torch.cat([s for s in batch.next_state if s is not None])
    state_batch = torch.cat(batch.state)
    action_batch = torch.cat(batch.action)
    reward_batch = torch.cat(batch.reward)
    state_action_values = policy_net(state_batch).gather(1, action_batch)
    next_state_values = torch.zeros(BATCH_SIZE)
    with torch.no_grad():
        next_state_values[non_final_mask] = target_net(non_final_next_states).max(1)[0]
    expected_state_action_values = (next_state_values * GAMMA) + reward_batch

    criterion = nn.SmoothL1Loss()
    loss = criterion(state_action_values, expected_state_action_values.unsqueeze(1))
    LOSS.append(loss.item())
    optimizer.zero_grad()
    loss.backward()
    torch.nn.utils.clip_grad_value_(policy_net.parameters(), 100)
    optimizer.step()
    torch.save(policy_net.state_dict(), './policy_net.pth')
    torch.save(target_net.state_dict(), './target_net.pth')

num_episodes = 3000

episode_rewards = []

epochs = 100

for i in range(epochs):
    EPS = 0.9
    for i_episode in range(num_episodes):
        eps = EPS - (0.1*(float(i_episode)/375))
        print(f'------------------------------------------------------ Starting new episode With Exploration {eps} ------------------------------------------------------')
        state = env.start()
        state = torch.tensor(state, dtype=torch.float32).unsqueeze(0)
        avg_r = []
        episode_going = env.is_in_play
        while episode_going:
            action = select_action(state, eps)
            observed_reward = env.step(Action(int(action[0][0])))
            reward = torch.tensor([observed_reward])
            avg_r.append(observed_reward)
            observation = env.get_state()
            done = not env.is_in_play
            episode_going = env.is_in_play
            if done:
                next_state = None
            else:
                next_state = torch.tensor(observation, dtype=torch.float32).unsqueeze(0)
            memory.push(state, action, next_state, reward)
            state = next_state
            optimize_model()
            target_net_state_dict = target_net.state_dict()
            policy_net_state_dict = policy_net.state_dict()
            for key in policy_net_state_dict:
                target_net_state_dict[key] = policy_net_state_dict[key] * TAU + target_net_state_dict[key]*(1 - TAU)
                target_net.load_state_dict(target_net_state_dict)
        episode_rewards.append(np.mean(avg_r))

import json

json.dump(episode_rewards, open('episode_rewards.json', 'r+'))

plt.plot(range(len(episode_rewards)), episode_rewards)
plt.show()

plt.plot(range(len(LOSS)), LOSS)
plt.show()
