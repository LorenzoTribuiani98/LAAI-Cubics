"""
@ Lorenzo Tribuiani - lorenzo.tribuiani@studio.unibo.it
"""

import numpy as np
import h5py
from tqdm import tqdm
import multiprocessing as mp
import os


# _________________GLOBALS_________________________
# -------------------------------------------------

ROW_N = 3             # Number of row considered
COL_N = 10            # number of columns
POSSIBLE_BLOCKS = 9   # Number of different shaped blocks
LR = .9               # Learning Rate
Y = .9

# block mapping: shape -> int
BLOCK_MAP = {
    (1,1) : 0,
    (1,2) : 1,
    (1,3) : 2,
    (2,1) : 3,
    (2,2) : 4,
    (2,3) : 5,
    (3,1) : 6,
    (3,2) : 7,
    (3,3) : 8,
}

# possible actions mapping: int -> (block code, rotation)
ACTION_MAP = {
    0 : (0,0),
    1 : (1,0),
    2 : (2,0),
    3 : (3,0),
    4 : (4,0),
    5 : (5,0),
    6 : (6,0),
    7 : (7,0),
    8 : (8,0),
    9 : (9,0),
    10: (0,1),
    11: (1,1),
    12: (2,1),
    13: (3,1),
    14: (4,1),
    15: (5,1),
    16: (6,1),
    17: (7,1),
    18: (8,1),
    19: (9,1),
}

# representations
SIZES = {
    "observation_n" : ((ROW_N+1) ** COL_N)* POSSIBLE_BLOCKS,
    "field_n" : ((ROW_N+1) ** COL_N),
    "block_n" : POSSIBLE_BLOCKS,
    "action_n" : 20
}

__Q_TABLE = np.zeros([((ROW_N+1) ** COL_N),POSSIBLE_BLOCKS,20]) 




# _________________FUNCTIONS_______________________
# -------------------------------------------------

def indexing(array: list, n:int=4, k:int=10) -> int:
    """
    Assign for each observation the corresponding index in the q-table (base 4 converion)
    
    Parameters
    ----------------

    - array: The observation description
    - n: number of rows +1
    - k: number of columns

    Returns
    ----------------

    - index: the q-table index
    """
    index = 0
    for i in range(k):
        index += array[i] * n**(k-(i+1))
    return index


def deindexing(number):  
    """
    Given the q_table index construct the field observation

    Parameters:
    ------------

    - number: the q_table index
    """  
    base10_digits = []
    resto = number
    while resto != 0:
        base10_digits.append(resto%4)
        resto = resto//4

    while len(base10_digits) <10:
        base10_digits.append(0)        
    
    base10_digits.reverse()
    return base10_digits


def create_observation(field, block_shape):
    """ create the full state description (a list of observations)
    
    Parameters:
    -------------

    - field: the current field
    - block_shape: the shape of the current block

    Returns:

    - observation: a tuple containing (field_observation(list), block_code(int))
    """
    block_code = BLOCK_MAP[block_shape]
    observation = []
    observations = []
    i = 20
    while i != 0:
        print(i)
        for col in field.T:
          el = np.count_nonzero(col[i-3:i])
          observation.append(el)
        
        if sum(observation) == 0:
            if len(observations) == 0:
                observations.append(observation)
                break
            else:
                break
        observations.append(observation)
        observation= []
        i -= 3
    print(observations)    
    return (observations, block_code)


def q_table_greedy(return_storing: dict, field_obs: list, block_code: int, noise: float):
    """
    Choose an action given the currest state observation by greedy saerch with a selected noise

    Parameters:
    -------------

    - return storing: dictionary storing the return values (action, current observation and block code)
    - field_obs: the observation of the field
    - block_code: the integer value of the current block
    - noise: multiplicative weight for the randomness
    - representation: the representation used (std)
    """
    
    a = np.argmax(__Q_TABLE[indexing(field_obs), block_code, :] + (np.random.randn(1,SIZES["action_n"]) * noise))
    return_storing["action"] = ACTION_MAP[a]
    return_storing["obs"] = field_obs
    return_storing["block_code"] = block_code


def q_table_solve(return_storing: dict, field_obs: list, block_code: int):
    """
    Find the best action given the current state observation and the q_values of the table (no update is compited)

    Parameters:
    --------------

    - return_storing: a dictionary to store return values (for threading)
    - field_obs: the observation of the current state (a list of observation or a single observation)
    - block_code: the current block
    """
    q_values = []
    actions = []
    for observation in field_obs:
        a = np.argmax(__Q_TABLE[indexing(observation), block_code, :])
        actions.append(a)
        q_values.append(__Q_TABLE[indexing(observation), block_code, a])
    

    a = actions[np.argmax(q_values)]


    return_storing["action"] = ACTION_MAP[a]
    return_storing["obs"] = field_obs
    return_storing["block_code"] = block_code


def update_q_table(current_state: list, current_block: int, previous_state: list, previous_block: int, action: int, reward: int):
    """
    Update the q-values inside the table accoding to the Bellman equation
    
    Parameters:
    -------------
    - current_state: the new state description
    - current block: the new block choosen
    - previous_state: the state on which the action is computed
    - previous_block: the block code of the state in which the action is computed
    - action: the action computed
    - reward: the reward value

    """
    
    action = [i for i in ACTION_MAP if ACTION_MAP[i]==action][0]
    actual_value = __Q_TABLE[indexing(previous_state),previous_block, action] 
    #Q_TABLE[indexing(previous_state), previous_block, action] = 
    return actual_value + LR*(reward + Y*np.max(__Q_TABLE[indexing(current_state),current_block, :]) - actual_value)


def save_table(path="", name="Q_table"):
    """
    save the table to a h5 file
    
    Parameters:
    ------------

    - path: the path to store the file (file name excluded)
    - name: the name of the file (without extension)
    """
    final_path = os.path.join(path, name + ".h5")
    h5f = h5py.File(final_path, "w")
    h5f.create_dataset("Q_table", data=__Q_TABLE)
    h5f.close()



def load_table(path="", name="Q_table"):
    """
    save the table to a h5 file
    
    Parameters:
    ------------

    - path: the path to store the file (file name excluded)
    - name: the name of the file (without extension)
    """
    try:
        final_path = os.path.join(path, name + ".h5")
        h5f = h5py.File(final_path, "r")
        global __Q_TABLE
        __Q_TABLE = h5f["Q_table"][:]
    except:
        print("no table found, random assignment")


def compute_reward(return_dict: dict, field: np.ndarray, bad_placing: bool) -> int:
    """
    Compute the reward for the current state-action
    
    Parameters:
    -------------
    
    - return_dict: a dictionary storing previous informations about the observation
    - game: the current game state
    - bad_placing: positioning of the block
    
    Returns:
    -------------
    
    - reward: the reward value
    """

    completed_lines = 0
    consecutive_rows = []
    longest_row = 0
    for row in field[-ROW_N:]:
        if np.all(row):
            completed_lines += 1

        if row[0] != 0:
            consecutive_rows.append(row)
            consecutive_len = 0
            for i in range(COL_N):
                if row[i] != 0:
                    consecutive_len += 1
                if row[i] == 0:
                    if consecutive_len > longest_row:
                        longest_row = consecutive_len
                    break
            
    max_height = 0
    unreachable = 0
    for col in field.T:
        try:
            temp = 20 - np.min(np.nonzero(col)) 
        except:
            temp = 0
        if temp > max_height:
            max_height = temp 
        
        flag = False        
        for i in range(20-ROW_N, 20):
            if col[i] != 0:
                flag = True
                continue
            if flag and col[i] == 0:
                unreachable += 1
            if flag and col[i] != 0:
                flag = False
                continue
    
    reward = completed_lines*100 + \
             return_dict["longest"] + (longest_row - return_dict["longest"])*10 - \
             return_dict["unreachable"] - (unreachable - return_dict["unreachable"])*30
    
    if max_height > return_dict["height"]:
        reward -= max_height
    if bad_placing:
        reward = -200

    return_dict["height"] = max_height
    return_dict["longest"] = 0 if longest_row == 10 else longest_row 
    return_dict["consecutives"] = len(consecutive_rows)
    return_dict["unreachable"] = unreachable
    
    return reward


def train(num_workers=8, saving_step= 100000):

    """
    Train the complete q table by creating observation of the given element
    """
    
    pool = mp.Pool(processes=num_workers)
    inputs = range(SIZES["field_n"])
    for (index, sub_table) in tqdm(pool.imap(__train_single, inputs), total=SIZES["field_n"]):
        __Q_TABLE[index] = sub_table
        if (index+1) % saving_step == 0:
            save_table()
        #pass
    pool.close()

    print("Saving table")
    save_table()




# ___________________PRIVATE_FUNCTIONS_________________
# ----------------------------------------------------


def __train_single(i):
    """
    Given the q_table index creates the respective observations (for all blocks and actions) and compute or update the q_values

    Parameters:
    ------------

    - i: the q_table index
    """

    field_obs = deindexing(i) 
    reward_dict = {
        "height" : 0,
        "longest" : 0,
        "consecutives" : 0,
        "unreachable" : 0
    }

    return_sub_table = np.zeros([SIZES["block_n"],SIZES["action_n"]])

    for j in range(SIZES["block_n"]):
        for k in range(SIZES["action_n"]):
            if __Q_TABLE[i, j, k] == 0.:
                field = __create_field(field_obs)                         # create the field based on the osservation
                __create_reward_dict(field, reward_dict)                  # create reward for the current state

                block_shape = [index for index in BLOCK_MAP if BLOCK_MAP[index]==j][0]
                action = ACTION_MAP[k]

                # rotation
                if action[1]:
                    block_shape = (block_shape[1], block_shape[0])

                bad_placing = False                                     # if bad placed a random x is assigned
                if not(0 <= action[0] < 10 - block_shape[0] + 1):
                    bad_placing=True
                    x = np.random.randint(0,10 - block_shape[0] + 1)
                else:
                    x = action[0]

                nonzero = np.nonzero(field.T[x:x+block_shape[0]])[1]
                if len(nonzero) > 0:
                    y = min(nonzero)
                else:
                    y = 20
                y = y - block_shape[1]
                field[y:y+block_shape[1], x:x+block_shape[0]] = 1

                reward = compute_reward(reward_dict, field, bad_placing)
                new_obs = __create_single_observation(field, (np.random.randint(1,4), np.random.randint(1,4)))
                return_sub_table[j,k] = update_q_table(new_obs[0], new_obs[1], field_obs, j, action, reward)            

    return (i,return_sub_table)


def __create_field(field_obs):
    """
    given the current observation creates the respective field
    """
    field = np.zeros((20,10))
    for i in range(len(field_obs)):
        for j in range(field_obs[i]):
            field.T[i][19-j] = 1

    return field


def __create_reward_dict(field, return_dict):

    """
    Given the current state returns the dictionary used by the compute reward function (only for develop)"""

    completed_lines = 0
    consecutive_rows = []
    longest_row = 0
    for row in field[-ROW_N:]:
        if np.all(row):
            completed_lines += 1

        if row[0] != 0:
            consecutive_rows.append(row)
            consecutive_len = 0
            for i in range(COL_N):
                if row[i] != 0:
                    consecutive_len += 1
                if row[i] == 0:
                    if consecutive_len > longest_row:
                        longest_row = consecutive_len
                    break
            
    max_height = 0
    unreachable = 0
    for col in field.T:
        try:
            temp = 20 - np.min(np.nonzero(col)) 
        except:
            temp = 0
        if temp > max_height:
            max_height = temp 
        
        flag = False        
        for i in range(20-ROW_N, 20):
            if col[i] != 0:
                flag = True
                continue
            if flag and col[i] == 0:
                unreachable += 1
            if flag and col[i] != 0:
                flag = False
                continue

    return_dict["height"] = max_height
    return_dict["longest"] = 0 if longest_row == 10 else longest_row 
    return_dict["consecutives"] = len(consecutive_rows)
    return_dict["unreachable"] = unreachable


def __create_single_observation(field: np.ndarray, block_shape: tuple) -> tuple:
    """
    Create the observation of the current state

    Parameters:
    -------------

    - game: the current state of the game

    Return:
    -------------

    - observation: tuple consisting of (field observation, block code)
    """

    block_code = BLOCK_MAP[block_shape]
    field_obs = []
    for col in field.T:
        el = np.count_nonzero(col[-ROW_N:])
        field_obs.append(el)
    
    return (field_obs, block_code)


    
