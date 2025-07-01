
# Train on Runpod h100 On-demand
### And OS deeps

```bash
apt update && apt install -y git curl unzip zip libgl1 portaudio19-dev
```

ssh root@69.48.159.14 -p 12345 -i ~/.ssh/id_ed25519

### Transfer Github Keys
On your local machine
```bash
# Note, make sure to update the IP address and port with your actual
scp -P {port} -i ~/.ssh/id_ed25519 ~/.ssh/id_ed25519 root@{ip}:/root/.ssh/
scp -P {port} -i ~/.ssh/id_ed25519 ~/.ssh/id_ed25519.pub root@{ip}:/root/.ssh/
```
On your remote instance
```bash
chmod 700 ~/.ssh
chmod 600 ~/.ssh/id_ed25519
chmod 644 ~/.ssh/id_ed25519.pub
chmod 600 /root/.ssh/id_ed25519
eval "$(ssh-agent -s)"
ssh-add /root/.ssh/id_ed25519
ssh -T git@github.com # to verify
```

### HuggingFace Tokens
Either copy/paste your env HF_TOKEN or get a new token from [HuggingFace](https://huggingface.co/settings/tokens)
> Note, when it asks about github, say `n`
```bash
huggingface-cli login
```

### Transfer data to pod
On local machine. Note these instructions assume you're in the folder with the .zip file (and you'll have to update IP with your actual IP)
```bash
scp -P {port} -i ~/.ssh/id_ed25519 {file} root@{ip}:/root/rachel/data/
```

On remote/pod
```bash
mkdir -p data/training
unzip -q data.zip -d data/training
cd ~/rachel/data/training
mv DATA/* .
rmdir DATA
```

### Start Training
Note: use `--resume` to resume from crash (checkpoints are enabled)
```bash
# Start fresh
PYTHONPATH=src accelerate launch -m training.train_hf --path /root/rachel/data/DATA

# Force resume
PYTHONPATH=src accelerate launch -m training.train_hf --path /root/rachel/data/DATA --resume

```

### Save results
```bash
scp -i ~/.ssh/id_ed25519 -P {port} -r root@{ip}:/root/rachel/data/outputs data/outputs

```