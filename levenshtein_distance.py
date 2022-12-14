from dataclasses import dataclass


@dataclass
class OpsCosts:
    onset_cost: int = 0
    match_cost: int = 0
    ins_cost: int = 1
    rep_cost: int = 1
    del_cost: int = 1

    def create_costs_dict(self) -> dict[str, int]:
        ops_costs_dict = {
            "onset": self.onset_cost,
            "match": self.match_cost,
            "insert": self.ins_cost,
            "replace": self.rep_cost,
            "delete": self.del_cost,
        }
        return ops_costs_dict

    def __post_init__(self):
        self.ops_costs_dict = self.create_costs_dict()


@dataclass
class LevenshteinData:
    distance: int
    seq_arr: list


@dataclass
class SeqOp:
    seq_arr: list
    seq_dict: dict
    seq1_len: int
    seq2_len: int


class Levenshtein:
    def __init__(
                self, seq1: str, seq2: str,
                ins_cost: int = 1,
                rep_cost: int = 1,
                del_cost: int = 1):
        self.seq1 = seq1
        self.seq2 = seq2

        self.ins_cost = ins_cost
        self.rep_cost = rep_cost
        self.del_cost = del_cost

        ops_costs = OpsCosts(
            ins_cost=self.ins_cost, rep_cost=self.rep_cost, del_cost=self.del_cost)

        self.lev_data: LevenshteinData = levenshtein_distance(
            self.seq1, self.seq2, ops_costs)

    def distance(self) -> int:
        return self.lev_data.distance

    def ratio(self) -> float:
        total_lens = len(self.seq1) + len(self.seq2)
        dist_val = self.lev_data.distance
        ratio_calc = (total_lens - dist_val) / total_lens
        return ratio_calc

    def sequence_array(self) -> list:
        return self.lev_data.seq_arr


def levenshtein_distance(seq1: str, seq2: str, ops_costs: OpsCosts) -> LevenshteinData:
    seq_op = create_sequence_data(seq1, seq2)
    seq1_len = seq_op.seq1_len
    seq2_len = seq_op.seq2_len

    for x in range(seq1_len):
        for y in range(seq2_len):
            op_values = dynamic_operations(x, y, seq_op)
            op_value = op_values["val"]
            op_key = op_values["key"]
            op_cost = ops_costs.ops_costs_dict[op_key]
            seq_op.seq_arr[y][x] = op_value + op_cost

    seq_arr = seq_op.seq_arr
    dist_val = int(seq_arr[seq2_len - 1][seq1_len - 1])
    lev_data = LevenshteinData(distance=dist_val, seq_arr=seq_arr)
    return lev_data


def create_sequence_data(seq1: str, seq2: str) -> SeqOp:
    seq_dict = {}

    seq1_l, seq2_l = insert_null_onset([*seq1], [*seq2])
    seq1_len, seq2_len = len(seq1_l), len(seq2_l)

    seq_arr = [[0 for _ in range(seq1_len)] for _ in range(seq2_len)]

    for s_index, seq in enumerate([seq1_l, seq2_l]):
        sequence_str = f"seq{s_index+1}"
        for l_index, letter in enumerate(seq):
            if sequence_str not in seq_dict:
                seq_dict.update({sequence_str: {}})
            seq_dict[sequence_str].update({l_index: letter})

    seq_op = SeqOp(
                   seq_arr=seq_arr,
                   seq_dict=seq_dict,
                   seq1_len=seq1_len,
                   seq2_len=seq2_len)
    return seq_op


def insert_null_onset(seq1: list, seq2: list) -> tuple[list, list]:
    seq1.insert(0, None)
    seq2.insert(0, None)
    return seq1, seq2


def min_ops(ops_list) -> dict:
    min_ops = {"x": None, "y": None, "val": None, "key": "invalid"}

    for op in ops_list:
        op_x, op_y = op["x"], op["y"]
        if op_x >= 0 and op_y >= 0:
            min_ops = op if min_ops["val"] is None else min_ops
            if op["val"] < min_ops["val"]:
                min_ops = op

    return min_ops


def dynamic_operations(x: int, y: int, seq_op: SeqOp) -> dict:
    x_dict = seq_op.seq_dict["seq1"][x]
    y_dict = seq_op.seq_dict["seq2"][y]

    x_ins, y_ins = (x, y - 1) if seq_op.seq1_len < seq_op.seq2_len else (x - 1, y)
    x_rep, y_rep = (x - 1, y - 1)
    x_del, y_del = (x - 1, y) if seq_op.seq1_len < seq_op.seq2_len else (x, y - 1)

    ins_val = seq_op.seq_arr[y_ins][x_ins]
    rep_val = seq_op.seq_arr[y_rep][x_rep]
    del_val = seq_op.seq_arr[y_del][x_del]

    onset_state = x_rep + y_rep == -2
    match_state = x_dict == y_dict

    if onset_state:
        op_dict = {"x": 0, "y": 0, "val": 0, "key": "onset"}

    elif match_state:
        op_dict = {"x": x_rep, "y": y_rep, "val": rep_val, "key": "match"}

    else:
        ops_list = [
            {"x": x_ins, "y": y_ins, "val": ins_val, "key": "insert"},
            {"x": x_rep, "y": y_rep, "val": rep_val, "key": "replace"},
            {"x": x_del, "y": y_del, "val": del_val, "key": "delete"},
        ]

        min_op_dict = min_ops(ops_list)
        op_dict = min_op_dict

    return op_dict
