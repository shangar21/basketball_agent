from environment import BasketballEnvironment
from agent import DQN
import torch
from assets.assets import Action

def select_action(state, policy_net):
    with torch.no_grad():
        return policy_net(state).max(1)[1].view(1,1)


env = BasketballEnvironment()
model = DQN(n_observations=len(env.start()), n_actions=10)
model.load_state_dict(torch.load('./target_net.pth'))
model.eval()

num_eps = 100_000

for i in range(num_eps):
    state = env.start()
    state = torch.tensor(state, dtype=torch.float32).unsqueeze(0)
    episode_going = env.is_in_play
    while episode_going:
        action = select_action(state, model)
        # Do something with state and best action (collect and do some visuals after or something)
        observed_reward = env.step(Action(int(action[0][0])))
        observation = env.get_state()
        episode_going = env.is_in_play
        if not episode_going:
            next_state = None
        else:
            next_state = observation
            state = torch.tensor(next_state, dtype=torch.float32).unsqueeze(0)


