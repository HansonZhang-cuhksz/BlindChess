from modelscope import AutoModelForCausalLM, AutoTokenizer
from transformers import BitsAndBytesConfig
import torch

model_name = "./Qwen3-4B-Thinking-2507"

# Configure 4-bit quantization
quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4"
)

# load the tokenizer and the model
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    quantization_config=quantization_config,
    device_map="auto"
)

prompt = """

"""
messages = [
    {"role": "system", "content": prompt}
]

def query(msg):
    messages.append({"role": "user", "content": msg})
    # prepare the model input
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
    )
    model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

    # conduct text completion
    generated_ids = model.generate(
        **model_inputs,
        max_new_tokens=32768
    )
    output_ids = generated_ids[0][len(model_inputs.input_ids[0]):].tolist() 

    # parsing thinking content
    try:
        # rindex finding 151668 (</think>)
        index = len(output_ids) - output_ids[::-1].index(151668)
    except ValueError:
        index = 0

    thinking_content = tokenizer.decode(output_ids[:index], skip_special_tokens=True).strip("\n")
    content = tokenizer.decode(output_ids[index:], skip_special_tokens=True).strip("\n")
    messages.append({"role": "assistant", "content": content})
    return thinking_content, content

if __name__ == "__main__":
    while True:
        msg = "What is the capital of France?"
        thinking, answer = query(msg)
        print("Thinking:\n", thinking)
        print("Answer:\n", answer)