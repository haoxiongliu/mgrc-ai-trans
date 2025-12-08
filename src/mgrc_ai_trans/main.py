import fire
import json
from os.path import join
import os
from importlib.resources import files, as_file
from mgrc_ai_trans.utils.format import MagirecoJSON
from mgrc_ai_trans.utils.assistant import post_request
from mgrc_ai_trans.utils.misc import load_json, read_json, jsonl2dps
from concurrent.futures import ThreadPoolExecutor
import re


def build_train_ds(
    src_root: str = 'magireco-source',
    trans_root: str = 'magireco-translate-data',
    output_fp: str = 'datasets/debug.jsonl',
    fn_pattern: str = '5167(10-2|10-9|20-6|20-7)_.*.json',
    special_fp: str = 'output/special_latest.json',
    sys_prompt_fp: str = None,
    add_line_number: bool = False
):
    fns = [fn for fn in os.listdir(trans_root) if re.match(fn_pattern, fn)]
    special = load_json(special_fp)
    
    # 如果没有提供系统提示文件路径，使用包内的默认路径
    if sys_prompt_fp is None:
        prompt_path = files('mgrc_ai_trans.prompts').joinpath('sakura_ft_v0.md')
        with open(prompt_path) as f:
            sys_prompt = f.read()
    else:
        with open(sys_prompt_fp) as f:
            sys_prompt = f.read()
    sys_msg = [{'role': 'system', 'content': sys_prompt}]
    msgs = []
    for fn in fns:
        src = load_json(join(src_root, fn))
        tgt = load_json(join(trans_root, fn))
        src_meta = MagirecoJSON(src, special)
        tgt_meta = MagirecoJSON(tgt)
        src_text = src_meta.get_src_text(add_line_number=add_line_number)
        tgt_text = tgt_meta.get_src_text(add_line_number=add_line_number)
        msg = sys_msg + [{'role': 'user', 'content': src_text}, 
                         {'role': 'assistant', 'content': tgt_text}]
        msgs.append(msg)
    raise NotImplemented
    # sys_prompt, instruction, output format
    # remember ensure_ascii=False when json.dumps
    return

def trans_glob(
    src_root: str = 'magireco-source',
    fn_pattern: str = '5167(10-2|10-9|20-6|20-7)_.*.json',
    num_worker: int = 4,
    **sub_kwargs
):
    src_fps = []
    for fn in os.listdir(src_root):
        if re.match(fn_pattern, fn):
            src_fps.append(join(src_root, fn))
    print(sorted(src_fps))
    
    # _trans_single = partial(trans_single_openai, api_key=api_key, model=model, tgt_root=tgt_root, log_root=log_root, prompt_root=prompt_root, prompt_name=prompt_name, special_fp=special_fp, max_tokens=max_tokens, temperature=temperature)
    # _trans_single = partial(trans_single_openai, **sub_kwargs)
    # if len(src_fps) > 1 and num_worker > 1:
    
    e = ThreadPoolExecutor(num_worker)
    futures = []
    for src_fp in src_fps:
        futures.append(e.submit(trans_single_openai, src_fp=src_fp, **sub_kwargs))
    # e.shutdown(wait=True)

    # with ThreadPoolExecutor(num_worker) as e:
    #     results = list(tqdm(e.map(_trans_single, src_fps)))
    # results = []
    # with multiprocessing.Pool(num_worker) as pool:
    #     for res in tqdm(pool.imap_unordered(_trans_single, src_fps)):
    #         results.append(res)
    # print(results)
    results = [f.result() for f in futures]
    print(f'\n{set(src_fps).difference(set(results))} \nfailed out of \n{src_fps}')    
    # else:
    #     for src_fp in src_fps:
    #         trans_single_openai(src_fp=src_fp, api_key=api_key, model=model, tgt_root=tgt_root, log_root=log_root, prompt_root=prompt_root, prompt_name=prompt_name, special_fp=special_fp, max_tokens=max_tokens, temperature=temperature)


def trans_single_openai(
    src_fp: str = 'magireco-source/103002-2_km1wv.json',
    api_key: str = "REMOVED_API_KEY",
    base_url: str = "REMOVED_BASE_URL",
    model: str = 'deepseek-chat',
    tgt_root: str = 'output',
    log_root: str = 'log',
    prompt_root: str = None,
    prompt_name: str = 'sakura_v8.4.md',
    special_fp: str = 'output/special_latest.json',
    temperature: float = 0.1,
    top_p: float = 0.95,
    max_tokens = 8192,
    add_line_number = True,
    prompt_in_user = False,
):
    # 如果没有提供提示根目录，使用包内的prompts目录
    if prompt_root is None:
        prompt_path = files('mgrc_ai_trans.prompts').joinpath(prompt_name)
    else:
        prompt_path = join(prompt_root, prompt_name)
    
    prompt_fp = str(prompt_path)
    src_name = os.path.basename(src_fp)
    tgt_fp = join(tgt_root, model, os.path.splitext(prompt_name)[0], src_name)
    if os.path.exists(tgt_fp):
        print(f'{tgt_fp} already exists. Jump over.')
        return src_fp
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

    src_text = JSONmeta.get_src_text(add_line_number=add_line_number)
    msg = prompt_msg + [{"role": "user", "content": src_text}]
    

    print(f'Now send to {base_url} using {model=} for translating {src_fp}:\n{prompt}\n\n{src_text}')
    response = post_request(
        msg, base_url=base_url, api_key=api_key, 
        model=model, max_tokens=max_tokens, temperature=temperature, top_p=top_p,
        prompt_in_user=prompt_in_user, return_type='response')
    choice = response.choices[0]
    tgt_text = choice.message.content # if chat else choice.text
    if model == 'deepseek-reasoner':
        reasoning_content = choice.message.reasoning_content
    # assistant = Assistant(api_key, base_url)
    # assistant.set_request_parameters(max_tokens=max_tokens, model=model, temperature=temperature, top_p=top_p)
    # assistant.substitute_msg(msg)
    # tgt_text = assistant.send_request()
    print(f'Translated text:\n{tgt_text}')
    
    log_fp = join(log_root, model, os.path.splitext(prompt_name)[0], os.path.splitext(src_name)[0]+'.log')
    os.makedirs(os.path.dirname(log_fp), exist_ok=True)
    with open(log_fp, 'w', encoding='utf-8') as f:
        f.write(f'{prompt}\n\n')
        f.write(f'{src_text}\n\n{tgt_text}')
        if model == 'deepseek-reasoner':
            f.write(f'\n\n{reasoning_content=}')

    tgt = JSONmeta.tgt_text2tgt(tgt_text, add_line_number=add_line_number)
    if not tgt:
        print('None returned, not writing the tgt')
        return None
    else:
        os.makedirs(os.path.dirname(tgt_fp), exist_ok=True)
        with open(tgt_fp, 'w', encoding='utf-8') as f:
            f.write(json.dumps(tgt, ensure_ascii=False, indent=4))
        return src_fp

if __name__ == "__main__":
    fire.Fire()
