import fire
import json
from os.path import join
from vllm import LLM, SamplingParams
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import os
from utils.format import MagirecoJSON, MagirecoJSON_0427, extract_all_names_in_src
from utils.orion_util import vllm_chat_with
from utils.assistant import Assistant
from utils.misc import read_wiki_special
import glob
from copy import deepcopy
from functools import partial
import multiprocessing
from tqdm import tqdm
import re

def trans_glob(
    src_root: str = 'magireco-source',
    fn_pattern: str = '5167(10-2|10-9|20-6|20-7)_.*.json',
    num_worker: int = 4,
    api_key: str = "api-1703564783321-YtWSxoHawe",
    model: str = 'gpt-4-0125-preview',
    tgt_root: str = 'output',
    log_root: str = 'log',
    prompt_root: str = 'prompts',
    prompt_name: str = 'sakura_v8.md',
    temperature: float = 0.0,
    special_fp: str = 'output/special_manual_v1.json',
    max_tokens = 4096
):
    src_fps = []
    for fn in os.listdir(src_root):
        if re.match(fn_pattern, fn):
            src_fps.append(join(src_root, fn))
    print(sorted(src_fps))
    
    _trans_single = partial(trans_single_openai, api_key=api_key, model=model, tgt_root=tgt_root, log_root=log_root, prompt_root=prompt_root, prompt_name=prompt_name, special_fp=special_fp, max_tokens=max_tokens, temperature=temperature)

    # if len(src_fps) > 1 and num_worker > 1:
    results = []
    with multiprocessing.Pool(num_worker) as pool:
        for res in tqdm(pool.imap_unordered(_trans_single, src_fps)):
            results.append(res)
    # print(results)
    print(f'\n{set(src_fps).difference(set(results))} \nfailed out of \n{src_fps}')    
    # else:
    #     for src_fp in src_fps:
    #         trans_single_openai(src_fp=src_fp, api_key=api_key, model=model, tgt_root=tgt_root, log_root=log_root, prompt_root=prompt_root, prompt_name=prompt_name, special_fp=special_fp, max_tokens=max_tokens, temperature=temperature)

def _trans_single_legacy(src_fp):
    res = trans_single_openai(src_fp)
    return res

# 反正连不上内网的人用不了
def trans_single_openai(
    src_fp: str = 'magireco-source/102204-9_yV4hL.json',
    api_key: str = "api-1703564783321-YtWSxoHawe",
    model: str = 'gpt-4-0125-preview',
    tgt_root: str = 'output',
    log_root: str = 'log',
    prompt_root: str = 'prompts',
    prompt_name: str = 'sakura_v8.md',
    special_fp: str = 'output/special_manual_v1.json',
    temperature: float = 0.0,
    max_tokens = 4096,
):
    prompt_fp = join(prompt_root, prompt_name)
    with open(src_fp, encoding='utf-8') as f:
        src = json.loads(f.read()) # type: dict
    with open(special_fp) as f:
        special = json.loads(f.read())
    
    JSONmeta = MagirecoJSON(src, special)
    special_text = '\n'.join(f'{src}->{special[src]}' for src in JSONmeta.special_in_src)
    with open(prompt_fp, encoding='utf-8') as f:
        # prompt_msg = json.loads(f.read()) < v7
        prompt = f.read().strip().format(special_text=special_text)
    prompt_msg = [{"role": "system", "content": prompt}]

    src_text = JSONmeta.get_src_text()
    msg = prompt_msg + [{"role": "user", "content": src_text}]
    assistant = Assistant(api_key)
    assistant.set_request_parameters(max_tokens=max_tokens, model=model, temperature=temperature)
    assistant.substitute_msg(msg)
    tgt_text = assistant.send_request()

    print(f'\nResults of {src_fp}:\n{src_text}\n\n{tgt_text}')
    src_name = os.path.basename(src_fp)

    log_fp = join(log_root, model, os.path.splitext(prompt_name)[0], os.path.splitext(src_name)[0]+'.log')
    os.makedirs(os.path.dirname(log_fp), exist_ok=True)
    with open(log_fp, 'w', encoding='utf-8') as f:
        f.write(f'{src_text}\n\n{tgt_text}')

    tgt = JSONmeta.tgt_text2tgt(tgt_text)
    if not tgt:
        return None
    else:
        tgt_fp = join(tgt_root, model, os.path.splitext(prompt_name)[0], src_name)
        os.makedirs(os.path.dirname(tgt_fp), exist_ok=True)
        with open(tgt_fp, 'w', encoding='utf-8') as f:
            f.write(json.dumps(tgt, ensure_ascii=False, indent=4))
        return src_fp



def main(task, **kwargs):
    globals()[task](**kwargs)

if __name__ == "__main__":
    fire.Fire(main)