import pdb

import os
import sys
sys.setrecursionlimit(10**9)

from automodeler.input_reader import ReadInput


class DuplicateChecker(ReadInput):
    def __init__(self, input_name, comb_label):
        super(DuplicateChecker, self).__init__(input_name)
        self.comb_label = comb_label

    # seen : ディレクトリを作成せずに組み合わせを列挙する時に使う
    def run(self, name_comb, seen=set()):
        self.name_comb = name_comb
        self.seen = seen

        # name_combには, X以外にもother_componentsの情報が数値やHOEの形式で含まれることがある
        # しかし, other_componentsの情報はインプットファイルであるread.comには記載されていない
        # 従って, X以外の要素はモデル分子作成に用いるname_enum_lに組み込まれない
        self.part_X_name_enum_l = self.get_name_enum(name_comb)

        self.dir_name_l = []
        self.name_comb_l = []
        self.isDuplicate_l = []

        self.dfs_enumeration([])

        if any(self.isDuplicate_l):
            inx = self.isDuplicate_l.index(True)
            c_dir_name = self.dir_name_l[inx]
            c_name_comb = self.name_comb_l[inx]
            isDuplicate = True
        else:
            c_dir_name = self.dir_name_l[0]
            c_name_comb = self.name_comb_l[0]
            isDuplicate = False

        c_name_comb = tuple(c_name_comb)

        return c_dir_name, c_name_comb, isDuplicate

    def get_name_enum(self, name_comb):
        part_X_name_enum_l = []
        for mode, X_inx in self.part_mode_X_inx_dict.values():
            name_l = []
            for each_X_inx in X_inx:
                name_l.append(name_comb[each_X_inx])

            each_part_X_name_enum_l = []
            if mode == 'P':
                each_part_X_name_enum_l.append(name_l)
            elif mode == 'B':
                each_part_X_name_enum_l.append(sorted(name_l))
            elif mode == 'C':
                for i in range(len(name_l)):
                    temp_name_l = name_l[i:] + name_l[:i]
                    if temp_name_l not in each_part_X_name_enum_l:
                        each_part_X_name_enum_l.append(temp_name_l)

            part_X_name_enum_l.append(each_part_X_name_enum_l)

        return part_X_name_enum_l

    def dfs_enumeration(self, temp_name_enum):
        if len(temp_name_enum) == len(self.part_X_name_enum_l):
            modify_name_enum = sum(temp_name_enum, [])

            new_name_comb = [''] * self.total_X_num
            for name, dir_inx in zip(modify_name_enum, self.ori_X_dir_inx_rel):
                new_name_comb[dir_inx] = name

            X_num = 1
            dir_name = ''
            while X_num <= self.total_X_num:
                dir_name += 'X' + str(X_num) + '-' + new_name_comb[X_num - 1]
                if X_num < self.total_X_num:
                    dir_name += '_'

                X_num += 1

            other_names = self.name_comb[self.total_X_num:]
            other_labels = self.comb_label[self.total_X_num:]
            if other_names:
                for name, label in zip(other_names, other_labels):
                    name = str(name)
                    if 'solvent' in label.lower():
                        dir_name += '_Sol-' + name
                    if 'temperature' in label.lower():
                        dir_name += '_Temp-' + name

            self.dir_name_l.append(dir_name)
            self.name_comb_l.append(new_name_comb)

            if dir_name in self.seen:
                self.isDuplicate_l.append(True)
            elif os.path.isdir('../' + dir_name):
                self.isDuplicate_l.append(True)
            else:
                self.isDuplicate_l.append(False)

            return

        next_inx = len(temp_name_enum)
        for name in self.part_X_name_enum_l[next_inx]:
            # temp_name_enum += [name]
            self.dfs_enumeration(temp_name_enum + [name])
