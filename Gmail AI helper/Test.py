from gpt4all import GPT4All
model = GPT4All ("Phi-3-mini-4k-instruct.Q4_0.gguf")
output = model.generate ("say only ‘Hello LLM’, without extra text" , max_tokens=10)
print(output.strip())