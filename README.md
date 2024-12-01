# FullStack Bench: Evaluating LLMs as Full Stack Coders

## Usage

Start the [sandbox server](https://bytedance.github.io/SandboxFusion/):

```bash
docker run -d --rm -p 8080:8080 volcengine/sandbox-fusion:server-20241202
```

Then, run the benchmark:

```bash
git clone https://github.com/bytedance/FullStackBench.git
cd FullStackBench
pip install -r requirements.txt
# modify the model configs in src/main.py
python src/main.py
```
