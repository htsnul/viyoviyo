import random
import re

FIELD = {
    "WIDTH": 6,
    "HEIGHT": 13
}

PIECE_KINDS = 4

def sub_position(pos, angle_id):
    if angle_id == 0: return [pos[0] + 0, pos[1] - 1]
    if angle_id == 1: return [pos[0] + 1, pos[1] + 0]
    if angle_id == 2: return [pos[0] + 0, pos[1] + 1]
    if angle_id == 3: return [pos[0] - 1, pos[1] + 0]

def piece_id_to_characer(id):
    return chr(ord("A") + id)

def cell_id_from_piece_id(id):
    return id + 1

def cell_id_to_piece_id(id):
    return id - 1

def cell_id_to_character(id):
    if id == 0: return " ";
    return piece_id_to_characer(cell_id_to_piece_id(id))

def erase_united_pieces(field):
    def count_recursively(field, list, pos, id):
        if not position_is_in_field(field, pos):
            return
        if field[pos[1]][pos[0]] != id:
            return
        if len([p for p in list if p[0] == pos[0] and p[1] == pos[1]]) == 1:
            return
        list += [pos]
        count_recursively(field, list, [pos[0] + 0, pos[1] - 1], id)
        count_recursively(field, list, [pos[0] + 1, pos[1] + 0], id)
        count_recursively(field, list, [pos[0] + 0, pos[1] + 1], id)
        count_recursively(field, list, [pos[0] - 1, pos[1] + 0], id)

    has_erased = False
    try_again = True
    while try_again:
        try_again = False
        for y in range(0, FIELD["HEIGHT"]):
            for x in range(0, FIELD["WIDTH"]):
                if field[y][x] == 0: continue
                id = field[y][x]
                pos = [x, y]
                list = []
                count_recursively(field, list, pos, id)
                if len(list) >= 4:
                    for pos in list:
                        field[pos[1]][pos[0]] = 0
                    try_again = True
                    has_erased = True
    return has_erased

def fall_pieces(field):
    pieces = []
    has_falled = False
    for x in range(FIELD["WIDTH"]):
        field_ids = []
        for y in range(FIELD["HEIGHT"]-1, -1, -1):
            field_ids += [field[y][x]]
        has_gap = False
        for i in range(len(field_ids) - 1):
            if field_ids[i] == 0 and field_ids[i + 1] != 0:
                has_gap = True
                break
        if not has_gap:
            continue
        field_ids = [i for i in field_ids if i > 0]
        for y in range(FIELD["HEIGHT"]):
            field[FIELD["HEIGHT"] - y - 1][x] = field_ids[y] if y < len(field_ids) else 0
        has_falled = True
    return has_falled

def print_field(field, target):
    if target != None:
        pos = target["position"]
        sub_pos = sub_position(pos, target["angle_id"])
    print("#" * (2 + FIELD["WIDTH"]))
    for y in range(0, FIELD["HEIGHT"]):
        s = ""
        for x in range(0, FIELD["WIDTH"]):
            c = cell_id_to_character(field[y][x])
            if target != None:
                if pos[1] == y and pos[0] == x:
                    c = piece_id_to_characer(target["kind_ids"][0])
                if sub_pos[1] == y and sub_pos[0] == x:
                    c = piece_id_to_characer(target["kind_ids"][1])
            s += c
        print("#" + s + "#")
    print("#" * (2 + FIELD["WIDTH"]))

def print_state(state):
    print_field(state["field"], state["target"])
    for i in reversed(range(2)):
        chars = []
        for next_kind_ids in state["next_kind_ids_list"]:
            chars.append(piece_id_to_characer(next_kind_ids[i]))
        print(" ".join(chars))
    if state["combo"] > 0:
        print("Combo: " + str(state["combo"]))
    elif state["target"] == None:
        print("!")
    else:
        print("?")

def position_is_in_field(field, pos):
    if pos[0] < 0: return False
    if pos[1] < 0: return False
    if pos[0] >= FIELD["WIDTH"]: return False
    if pos[1] >= FIELD["HEIGHT"]: return False
    return True

def position_hits_field(field, pos):
    if not position_is_in_field(field, pos): return True
    if field[pos[1]][pos[0]] != 0: return True
    return False

def provisional_position_by_action(pos, action):
    if action == "h": return [pos[0] - 1, pos[1] + 0]
    if action == "j": return [pos[0] + 0, pos[1] + 1]
    if action == "l": return [pos[0] + 1, pos[1] + 0]
    return pos

def update_position_by_action(pos, angle_id, field, action):
    provisional_pos = provisional_position_by_action(pos, action)
    provisional_sub_pos = sub_position(provisional_pos, angle_id)
    if position_hits_field(field, provisional_pos):
        return True
    if position_hits_field(field, provisional_sub_pos):
        return True
    pos[:] = provisional_pos
    return False

def next_angle_id_by_action(angle_id, action):
    if action == "w": return (angle_id + 0 + 1) % 4
    if action == "b": return (angle_id + 4 - 1) % 4
    return angle_id

def put_target_on_field(field, target):
    pos = target["position"]
    sub_pos = sub_position(pos, target["angle_id"])
    field[pos[1]][pos[0]] = cell_id_from_piece_id(target["kind_ids"][0])
    field[sub_pos[1]][sub_pos[0]] = cell_id_from_piece_id(target["kind_ids"][1])

def update_target_to_next(target, next_kind_ids_list):
    target["position"] = [2, 1]
    target["angle_id"] = 0
    target["kind_ids"] = next_kind_ids_list.pop(0);
    next_kind_ids_list.append([int(PIECE_KINDS * random.random()), int(PIECE_KINDS * random.random())])

def update_state_by_action(state, action):
    field = state["field"]
    is_hit = update_position_by_action(state["target"]["position"], state["target"]["angle_id"], field, action)
    state["target"]["angle_id"] = next_angle_id_by_action(state["target"]["angle_id"], action)
    if action == "j" and is_hit:
        put_target_on_field(field, state["target"])
        state["target"] = None

def create_initial_state():
    return {
        "target": {},
        "field": [[0 for x in range(0, FIELD["WIDTH"])] for y in range(0, FIELD["HEIGHT"])],
        "next_kind_ids_list": [[2, 3], [0, 0]],
        "combo": 0,
    }

state = create_initial_state()
update_target_to_next(state["target"], state["next_kind_ids_list"])

while True:
    print_state(state)
    s = input()
    if fall_pieces(state["field"]):
        continue
    if erase_united_pieces(state["field"]):
        state["combo"] += 1
        continue
    if state["target"] == None:
        state["target"] = {}
        update_target_to_next(state["target"], state["next_kind_ids_list"])
        state["combo"] = 0
        continue
    while state["target"] != None:
        result = re.search("^[0-9]+", s)
        count = 1
        if result != None:
            s = s[len(result[0]):]
            count = int(result[0])
        result = re.search("^[hjlwb]", s)
        if result == None:
            break
        action = result[0]
        s = s[len(result[0]):]
        for i in range(count):
            update_state_by_action(state, action)
            if state["target"] == None:
                break

