import fire
import json
from os.path import join

KEYS_RETAIN = [
    'textLeft', 'textCenter', 'textRight',
    'nameLeft', 'nameCenter', 'nameRight',
    'nameNarration', 'narration', 'progressNarration'
]
# we do not consider story.grp_key.select and resulted multiple groups


def test_compact(
    src_root: str = 'magireco-source',
    src_name: str = '102601-1_Hfpep.json'
):
    src_fp = join(src_root, src_name)
    with open(src_fp, encoding='utf-8') as f:
        src = json.loads(f.read())
    return compact_json(src)

def compact_json(
    src: dict, # has to be an object
    keys_retain = KEYS_RETAIN
):
    # for narration there might be no name
    src_cmpt = [] # {key1: content1, key2, content2}
    cmpt_index = [] # grp_key, item_ind, 
    for grp_key in src["story"].keys():
        grp = src["story"][grp_key]
        for item_ind, item in enumerate(grp):
            item_cmpt = {key: value for key, value in item.items() if key in keys_retain}
            if item_cmpt != {}:
                src_cmpt.append(item_cmpt)
                cmpt_index.append([grp_key, item_ind])

    return (src_cmpt, cmpt_index)

def translate_single(
    src_root: str = 'magireco-source',
    src_name: str = '102601-1_Hfpep.json'
):
    pass


def main(task, **kwargs):
    globals()[task](**kwargs)

if __name__ == "__main__":
    fire.Fire(main)