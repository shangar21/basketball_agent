from environment import BasketballEnvironment
from agent import DQN
import torch

def select_action(state, policy_net):
    with torch.no_grad():
        return policy_net(state).max(1)[1].view(1,1)



model = DQN()
model.load_state_dict(torch.load('./target_net.pth'))
model.eval()

env = BasketballEnvironment()

num_eps = 100_000

for i in num_eps:
    state = env.start()
    state = torch.tensor(state, dtype=torch.float32).unsqueeze(0)
    episode_going = env.is_in_play
    while episode_going:
        action = select_action(state, eps)
        observed_reward = env.step(Action(int(action[0][0])))
        observation = env.get_state()
        episode_going = env.is_in_play
        if not episode_going:
            next_state = None
        else:
            next_state = observation

        # Store state, action

        state = next_state

