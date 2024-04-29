import os
import json
import re
import glob
from os.path import join
from utils.format import extract_all_names_in_src
from copy import deepcopy

def read_wiki_special(
    special_json_fp: str = 'magireco-translate-data/special-translate-text-info.json',
)-> dict:
    with open(special_json_fp) as f:
        content = json.loads(f.read())["story"]["group_1"][0]["narration"]
    special = json.loads(content)
    # print(special)
    return special

def build_special(
    source_root = 'magireco-source',
    wiki_special_fp = 'magireco-translate-data/special-translate-text-info.json',
    output_fp = 'output/special.json'
):
    src_fps =  [filepath for filepath in glob.glob(join(source_root, '*.json'))]
    names = set()
    for src_fp in src_fps:
        with open(src_fp) as f:
            src = json.loads(f.read())
        names.update(extract_all_names_in_src(src))
    special = {name: name for name in names}
    special_old = read_wiki_special(wiki_special_fp)
    special.update(special_old)
    
    # filter out some
    to_filt = ['＆', '&', '?', '？', 'の声', 'の父', 'の母', 'の祖父', 'の妹', 'の姉', 'たち', 'の弟', 'の兄', 'の叔母', 'の従兄弟']
    special_filt = deepcopy(special)
    for key in special.keys():
        for filt in to_filt:
            if filt in key:
                del special_filt[key]
                break

    if output_fp:
        with open(output_fp, 'w') as f:
            f.write(json.dumps(special_filt, ensure_ascii=False, indent=4))
    return special_filt


def convert_special_to_text(
    special_fp: str = 'output/special_manual_sort.json'
):
    with open(special_fp) as f:
        special = json.loads(f.read())
    return '\n'.join(f'{src}->{tgt}' for (src, tgt) in special.items())

def find_special_in_src(
    src: dict,
    special: dict
):

    special = []
    


if __name__ == '__main__':
    read_wiki_special()
