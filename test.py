import retro

def main():
    env = retro.make(game='SuperMarioBros-Nes')
    obs = env.reset()
    while True:
        obs, rew, done, info = env.step(env.action_space.sample())
        sample = env.action_space.sample()
        print(env.get_action_meaning(sample))
        print(env.action_to_array(sample))
        print(info)
        env.render()
        exit()
        if done:
            obs = env.reset()
    env.close()


if __name__ == "__main__":
    main()