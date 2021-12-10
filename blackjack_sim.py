import os
import itertools as it
import numpy as np
import pandas as pd
import multiprocessing as mp
import random
import shutil
import time
from tqdm.auto import tqdm
from game_state import GameState
from blackjack import blackjack_train_agent, blackjack_test_agent


def run_blackjack_exp(ndecks, ntrials, eps, eta, gamma, num_exp, out_dir):
    state = GameState(ndecks, 2)
    blackjack_train_agent(state, ndecks, ntrials, eps, eta, gamma, out_dir)
    
    with cnt.get_lock():
        cnt.value += 1
        print(f"Progress: {cnt.value} / {num_exp} ({(cnt.value) / num_exp * 100:.2f} %)", end='\r', flush=True)
        
        
def run_blackjack_exp_imap(args):
    print(args)
    ndecks, ntrials, eps, eta, gamma, num_exp, out_path = args
    state = GameState(ndecks, 2)
    blackjack_train_agent(state, ndecks, ntrials, eps, eta, gamma, out_path)
    
    with cnt.get_lock():
        cnt.value += 1
        print(f"Progress: {cnt.value} / {num_exp} ({(cnt.value) / num_exp * 100:.2f} %)", end='\r', flush=True)


def init_globals(counter):
    global cnt
    cnt = counter
    
    
if __name__ == '__main__':
    #os.system("taskset -p 0xff %d" % os.getpid())
    serial = True
    #trials = [10000, 50000, 100000, 250000, 500000, 1000000]
    trials = [10000]
    decks = range(1, 7)
    etas = [np.round(i, 2) for i in np.arange(0.1, 0.9, 0.1)]
    gammas = [np.round(i, 2) for i in np.arange(0.2, 1.0, 0.1)]
    epss = [np.round(i, 2) for i in np.arange(0.1, 0.6, 0.1)]
    
    
    if serial is True:
        param_iter = it.product(decks, trials, epss, etas, gammas)
        num_experiments = len(list(param_iter))
        # Need to reinitialize
        param_iter = it.product(decks, trials, epss, etas, gammas)

        exp_data = []
        for ndecks, ntrials, eps, eta, gamma in tqdm(param_iter, total=num_experiments):
            #print(ndecks, ntrials, eps, eta, gamma)
            state = GameState(ndecks, 2)
            agent, data = blackjack_train_agent(state, ndecks, ntrials, eps, eta, gamma, out_dir=None)
            exp_data.extend(data)
        rdf = pd.DataFrame(exp_data)
        rdf.to_csv('training_10k_episodes4.csv.gz', index=False)
    else:
        '''
        n = 10
        data_file = 'training_results.csv'
        if os.path.exists(data_file):
            os.remove(data_file)
        param_iter = (t for t, _ in zip(range(n), it.product(decks, trials, epss, etas, gammas)))
        num_exp = len(list(param_iter))
        param_iter = (t for _, t in zip(range(n), it.product(decks, trials, epss, etas, gammas, [num_exp], [data_file])))
        '''

        data_dir = '/stash/tlab/jc2/rl_training_results'
        if os.path.exists(data_dir):
            shutil.rmtree(data_dir)
        os.mkdir(data_dir)
        param_iter = it.product(decks, trials, epss, etas, gammas)
        num_exp = len(list(param_iter))
        param_iter = list(it.product(decks, trials, epss, etas, gammas, [num_exp], [data_dir]))
        random.shuffle(param_iter)

        print(f"Starting sims")
        cnt = mp.Value('i', 0)
        exp_data = []
        start = time.time()
        with mp.Pool(mp.cpu_count(), initializer=init_globals, initargs=(cnt,)) as pool:
        #with mp.Pool(mp.cpu_count() * 2) as pool:
            pool.starmap(run_blackjack_exp, param_iter)
            #pool.imap(run_blackjack_exp_imap, param_iter)

        '''
        rout = list(it.chain.from_iterable(results))
        rdf = pd.DataFrame(rout)
        print(f"Writing to file")
        rdf.to_csv('sim_data_test.csv', index=False)
        '''
        end = time.time()
        print(flush=True)
        print(f"Took {(end - start) / 60} mins")
    
    
    


