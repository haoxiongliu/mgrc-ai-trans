import fire
import json
from os.path import join
from copy import deepcopy
from dataclasses import dataclass
import re

KEYS_RETAIN = [
    'textLeft', 'textCenter', 'textRight',
    'nameLeft', 'nameCenter', 'nameRight',
    'nameNarration', 'narration', 'progressNarration'
]

KEYS_NAME = [
    'nameLeft', 'nameCenter', 'nameRight', 'nameNarration'
]

KEYS_CONTENT= [
    'textLeft', 'textCenter', 'textRight', 'narration', 'progressNarration'
]

CONTENT2NAME = {
    'textLeft': 'nameLeft',
    'textCenter': 'nameCenter',
    'textRight': 'nameRight',
    'narration': 'nameNarration',
    'progressNarration': 'nameNarration'
}


def extract_all_names_in_src(
    src: dict
):
    names = set()
    story = src['story']
    if type(story) == dict:
        grps = story
    elif type(story) == list:
        grps = {'dummy_grp_key': story}
    
    for grp in grps.values():
        for item in grp:
            for name_key in KEYS_NAME:
                if name_key in item.keys() and item[name_key]:
                    names.add(item[name_key])
    return names                   

@dataclass
class Block:
    grp_key: str = None # 'group_1'
    content_key: str = None # in KEYS_CONTENT
    name_key: str = None
    name: str = None
    members: list[int] = None
    text: int = None

class MagirecoJSON:
    
    # to make the memory cost smaller
    def __init__(self, src: dict, special: dict = {}) -> None:
        self.src = src
        self.tgt = deepcopy(src)
        # 其实可以不用维护这个表，只需要维护一个mgrc_name_trans就行了
        self.blocks: list[Block] = []
        # 关键在于怎么从tgt_txt里面还原出tgt，其实简单
        self.grouped = True    
        self.special_in_src: set[str] = set()
        self._process_src(special)  # special_in_src and names in tgt build

    def tgt_text2tgt(self, tgt_text: str, add_line_number=False, space2at=True) -> dict:
        if not tgt_text:
            return None
        tgt_text_list = tgt_text.strip().split('\n')
        if len(tgt_text_list) != len(self.blocks):
            if not add_line_number:
                print(f'tgt_text lines not matching number of blocks, return None')
                return None
            else:
                print(f'tgt_text lines not matching number of blocks, find line number')
                old_list = tgt_text_list
                tgt_text_list = ['']*len(self.blocks)
                for tgt_text_line in old_list:
                    m = re.match(r'(\[|^)(?P<line>\d+).*', tgt_text_line)
                    if m:
                        index = int(m.group('line')) - 1
                        if index < len(self.blocks):
                            tgt_text_list[index] = tgt_text_line
                if ''.join(tgt_text_list) == '':
                    print('No line number found. return None.')
                    return None
            # if len(tgt_text_list) < len(self.blocks):
            #     tgt_text_list += ['']* (len(self.blocks) - len(tgt_text_list))
            # else:
            #     tgt_text_list = tgt_text_list[:len(self.blocks)]
        for tgt_text, block in zip(tgt_text_list, self.blocks):
            content = tgt_text.split('：')[-1]
            mem_contents = content.split('@')
            for mem_ind, mem_content in zip(block.members, mem_contents):
                # substitute 孤立的空格为 @
                if space2at:
                    mem_content = re.sub(r'(?<!\S) (?!\S)', '@', mem_content)
                if self.grouped:
                    item = self.tgt['story'][block.grp_key][mem_ind] # type: dict
                else:
                    item = self.tgt['story'][mem_ind]
                item[block.content_key] = mem_content
        return self.tgt


    def get_src_text(self, add_line_number=False) -> str:
        src_text = ''
        for i, block in enumerate(self.blocks):
            prefix = f'[{i+1}]' if add_line_number else ''
            src_text += prefix + block.text + '\n'
        src_text = src_text.strip()
        # src_text = '\n'.join([f'2 {i} 3' + block.text for i, block in enumerate(self.blocks)])
        return src_text

    def _process_src(self, special: dict):
        src = self.src
        story = src['story']
        if type(story) == dict:
            grps = story
        elif type(story) == list:
            grps = {'dummy_grp_key': story}
            self.grouped = False
        blocks = [] # list[Block]
        not_in_src = set(special.keys())
        for grp_key, grp in grps.items():
            # grp = src["story"][grp_key]
            
            current_names = {}
            block = None
            
            for item_ind, item in enumerate(grp):

                content_key =  None
                for key in item.keys():
                    if key in KEYS_NAME:
                        name = item[key]
                        for special_word in special.keys():
                            if special_word in name:
                                not_in_src.discard(special_word)
                                self.special_in_src.add(special_word)
                            if special_word == name:
                                if self.grouped:
                                    self.tgt['story'][grp_key][item_ind][key] = special[name]
                                else:
                                    self.tgt['story'][item_ind][key] = special[name]
                        current_names[key] = name
                        del name    # a guarantee
                    if key in KEYS_CONTENT:
                        assert not content_key, f'multiple texts at pos {item_ind} in {grp_key}'
                        content_key = key
                        occurs = set()
                        for special_word in not_in_src:
                            if special_word in item[key]:
                                occurs.add(special_word)
                        self.special_in_src.update(occurs)
                        not_in_src.difference_update(occurs)

                if content_key:
                    # confirm if we need a new block
                    name_key = CONTENT2NAME[content_key]
                    try:
                        name = current_names[name_key]  # current_name
                    except:
                        print(f'find no corresponding name to key {content_key} in {src}')
                        name = ''
                    content = item[content_key]
                    # 将所有跟随在"、"后的"@"替换为""，否则将"@"替换为" "
                    content = re.sub(r'、@', '、', content)  # Replace "、@" with "、"
                    content = re.sub(r'(?<!、)@', ' ', content)  # Replace "@" with " " if not preceded by "、"
                    if not block or block.content_key != content_key or block.name != name:
                        if block:
                            blocks.append(block)
                        block = Block(grp_key=grp_key, 
                                      content_key=content_key, 
                                      name_key=name_key,
                                      name=name,
                                      members=[item_ind])
                        block.text = f"{name}：{content}" if name else content
                    elif block.content_key == content_key:
                        block.members.append(item_ind)
                        block.text += f'@{content}'
                    elif block.content_key != content_key:
                        blocks.append(block)
                        block = None
            if block:
                blocks.append(block)
        self.blocks = blocks



class MagirecoJSON_0427:
    
    # to make the memory cost smaller
    def __init__(self, src: dict) -> None:
        self.src = src
        self.tgt = None
        # 其实可以不用维护这个表，只需要维护一个mgrc_name_trans就行了
        self.text_index_list = None
        self.src_text_list = None
        # 关键在于怎么从tgt_txt里面还原出tgt，其实简单
        self._process_src()


    def tgt_text2tgt(self, tgt_text: str) -> dict:
        tgt_text_list = tgt_text.strip().split('\n')
        tgt = deepcopy(self.src)
        for index, text in zip(self.text_index_list, tgt_text_list):
            content = text.split('：')[-1]
            grp_key, item_ind, content_key = index
            item = tgt['story'][grp_key][item_ind] # type: dict
            item[content_key] = content
        return tgt

    def _process_src(self):
        src = self.src
        text_index_list = [] # grp_key, item_ind, content_key
        src_text_list = []
        for grp_key in src["story"].keys():
            grp = src["story"][grp_key]
            current_names = {}
            for item_ind, item in enumerate(grp):
                content_key =  None
                for key in item.keys():
                    if key in KEYS_NAME:
                        current_names[key] = item[key]
                    if key in KEYS_CONTENT:
                        assert not content_key, f'multiple texts at pos {item_ind} in {grp_key}'
                        content_key = key
                if content_key:
                    name_key = CONTENT2NAME[content_key]
                    text = f'{current_names[name_key]}：{item[content_key]}'
                    src_text_list.append(text)
                    text_index_list.append((grp_key, item_ind, content_key))
        self.text_index_list = text_index_list
        self.src_text_list = src_text_list




def main(task, **kwargs):
    globals()[task](**kwargs)

if __name__ == "__main__":
    fire.Fire(main)