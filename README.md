# vyper-poc

## Local env setup

Create `conda` env
```shell
conda create -n vyper-poc python=3.11
conda activate vyper-poc
pip install -r requirements.txt
pip install --upgrade -r requirements.txt
``` 

Install Foundry
```shell
curl -L https://foundry.paradigm.xyz | bash
source ~/.bashrc
foundryup
```

Install `ape` plugins (automatic from `ape-config.yaml`)
```shell
ape plugins install .
ape plugins install vyper
ape plugins list
```

Add Alchemy key to `~/.bashrc`
```shell
export WEB3_ALCHEMY_PROJECT_ID=XXX
```