from vllm import SamplingParams
from typing import Optional

def build_chat_input(messages: list[dict]):
    prompt = "<s>"
    for msg in messages:
        role = msg["role"]
        message = msg["content"]
        if message is None :
            continue
        if role == "user":
            prompt += "Human: " + message + "\nAssistant: "
        if role == "assistant":
            prompt += message + "</s>"

    # input_tokens = tokenizer.encode(prompt)
    return prompt

def vllm_chat_with(model, messages: list[dict], sampling_params: Optional[SamplingParams|None]):
    prompt = build_chat_input(messages)
    # input_ids = torch.LongTensor([input_tokens]).to(model.device)
    if not sampling_params:
        sampling_params = SamplingParams()
    vllm_output = model.generate(prompt, sampling_params)
    response = vllm_output[0].outputs[0].text
    # response = tokenizer.decode(outputs[0][len(input_ids[0]):], skip_special_tokens=True)
    return response
