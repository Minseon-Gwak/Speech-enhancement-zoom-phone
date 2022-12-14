# Prerequisite
Run cells in `Demucs_Denooiser_Training_Example.ipynb` and `FullSubNet_Denoiser_Training_Example.ipynb` to get the baseline codes (Demucs and FullSubNet) and pre-trained eGeMAPS estimator.

# DATASET
mkdir train
mkdir test

## Clean
### Train data (1/3)
wget -q https://cmu.box.com/shared/static/2c8wabvnh10j4izz4t5jv4ewt9xmotxd --content-disposition --show-progress
unzip -q src_clean.zip  -d train/
### Test data 
wget -q https://cmu.box.com/shared/static/z6f1iz3nic2d31zxnix3bn4ge7lz69p1 --content-disposition --show-progress
unzip -q src_clean.zip.1  -d test/

## Low denoising (denoising OFF)
### Train data (1/3)
wget -q https://cmu.box.com/shared/static/dve4yqo2cdfnn8lpp6mo8vddkxac3x2z --content-disposition --show-progress
unzip -q src_zm_phone_relay_low.zip  -d train/
### Test data 
wget -q https://cmu.box.com/shared/static/w45x9viyn6ugif32qa7vjvzi99onjhe1 --content-disposition --show-progress
unzip -q src_zm_phone_relay_low.zip.1  -d test/

## Auto denoising (denoising ON)
### Train data (1/3)
wget -q https://cmu.box.com/shared/static/65seuub7gwbhlphkdphk8b44sugojqa8 --content-disposition --show-progress
unzip -q src_zm_phone_relay_auto.zip  -d train/
### Test data 
wget -q https://cmu.box.com/shared/static/m05ovewmx0hdcpx5uzsorn8f8ec74br2 --content-disposition --show-progress
unzip -q src_zm_phone_relay_auto.zip.1  -d test/


## Data 
unzip -q 400-800-clean-noisy.zip -d new_data/
unzip -q 400-800-zpa.zip -d new_data/
unzip -q 400-800-zpl.zip -d new_data/

unzip -q 800-1200-zpa.zip -d new_data/
unzip -q 800-1200-zpl.zip -d new_data/
unzip -q 800-1200.zip  -d new_data/


## Data normalization

mkdir -p train/nrm_clean train/nrm_zm_phone_relay_low
mkdir -p test/nrm_clean test/nrm_zm_phone_relay_low

python normalize.py new_data/train/src_clean new_data/train/nrm_clean
python normalize.py new_data/train/src_noisy new_data/train/nrm_noisy
python normalize.py new_data/train/src_zp_low new_data/train/nrm_zp_low
python normalize.py new_data/train/src_zp_auto new_data/train/nrm_zp_auto

python normalize.py test/src_clean test/nrm_clean
python normalize.py test/src_zm_phone_relay_auto test/nrm_zm_phone_relay_auto
python normalize.py test/src_zm_phone_relay_low test/nrm_zm_phone_relay_low


## Validation dataset
rm -rf test/no_reverb/clean test/no_reverb/noisy
mkdir -p test/no_reverb/clean test/no_reverb/noisy
cd test/
cp -r nrm_clean/ clean/
cp -r nrm_zm_phone_relay_low/ noisy/
mv clean/ no_reverb/
mv noisy/ no_reverb/



# Evaluate BASELINE !!!
mkdir -p result/fullsubnet/nrm/baseline/low/
mkdir -p result/fullsubnet/nrm/baseline/auto/

python /content/TAPLoss-master/FullSubNet/recipes/dns_interspeech_2020/inference.py \
  -C /content/TAPLoss-master/FullSubNet/recipes/dns_interspeech_2020/fullsubnet/test_low.toml \
  -M /content/fullsubnet_best_model_58epochs.tar \
  -O result/fullsubnet/nrm/baseline/low/
  
python /content/TAPLoss-master/FullSubNet/recipes/dns_interspeech_2020/inference.py \
  -C /content/TAPLoss-master/FullSubNet/recipes/dns_interspeech_2020/fullsubnet/test_auto.toml \
  -M /content/fullsubnet_best_model_58epochs.tar \
  -O result/fullsubnet/nrm/baseline/auto/
  

python eval_metric.py --save_name denoised_fsnet_baseline_nrm_low --save_dir ./ --clean_dir test/nrm_clean/ --noisy_dir result/fullsubnet/nrm/baseline/low/
python eval_metric.py --save_name denoised_fsnet_baseline_nrm_auto --save_dir ./ --clean_dir test/nrm_clean/ --noisy_dir result/fullsubnet/nrm/baseline/auto/





# Run fine-tuning ()
## Set Configuration
python set_fsnet_finetune_train_cfg.py
## Train
torchrun --standalone --nnodes=1 --nproc_per_node=1 /content/TAPLoss-master/FullSubNet/recipes/dns_interspeech_2020/train.py -C /content/TAPLoss-master/FullSubNet/recipes/dns_interspeech_2020/fullsubnet/finetune_newdata_lr00001.toml -P /content/fullsubnet_best_model_58epochs.tar

## Validation (Choose the best model using tensorboard)
zip -q logs_finetune.zip -r /home/yunyangz/Documents/FullSubNet/code/FullSubNet/EXPs/finetune_newdata_lr00001/logs/*
tensorboard --logdir logs

python /content/TAPLoss-master/FullSubNet/recipes/dns_interspeech_2020/inference.py \
  -C /content/TAPLoss-master/FullSubNet/recipes/dns_interspeech_2020/fullsubnet/test_low.toml \
  -M [?] \
  -O result/fullsubnet/nrm/finetune/


## Test (low)
### Set Configuration
python set_fsnet_test_cfg.py

### Inference (One GPU is used by default)
mkdir -p result/fullsubnet/nrm/finetune/

python /content/TAPLoss-master/FullSubNet/recipes/dns_interspeech_2020/inference.py \
  -C /content/TAPLoss-master/FullSubNet/recipes/dns_interspeech_2020/fullsubnet/test_low.toml \
  -M [?] \
  -O result/fullsubnet/nrm/finetune/

### save results
cd result/fullsubnet/nrm/finetune/
zip -q denoised_fsnet_finetune_nrm_low.zip enhanced_0000/*



# Run fine-tuning (TapLoss)
## Set Configuration
python set_fsnet_taploss_train_cfg.py
## Train 
torchrun --standalone --nnodes=1 --nproc_per_node=1 /content/TAPLoss-master/FullSubNet/recipes/dns_interspeech_2020/train.py -C /content/TAPLoss-master/FullSubNet/recipes/dns_interspeech_2020/fullsubnet/taploss_newdata_005_lr00001.toml -P /content/fullsubnet_best_model_58epochs.tar

## Validation (Choose the best model using tensorboard)
zip logs_taploss_newdata_01_lr00001.zip -r /home/yunyangz/Documents/FullSubNet/code/FullSubNet/EXPs/taploss_newdata_05_lr00001/logs/*

tensorboard --logdir logs

## Test (low)
### Set Configuration
python set_fsnet_test_low_cfg.py

### Inference (One GPU is used by default)
mkdir -p result/fullsubnet/nrm/taploss/low/

python /content/TAPLoss-master/FullSubNet/recipes/dns_interspeech_2020/inference.py \
  -C /content/TAPLoss-master/FullSubNet/recipes/dns_interspeech_2020/fullsubnet/test_low.toml \
  -M /home/yunyangz/Documents/FullSubNet/code/FullSubNet/EXPs/taploss_train_003/checkpoints/model_0100.pth \
  -O result/fullsubnet/nrm/taploss/low/

### save results
cd result/fullsubnet/nrm/taploss/low/
zip -q /home/GMS/02_IDL-project/denoised_fsnet_taploss_nrm_low.zip enhanced_0000/*


## Test (auto)
### Set Configuration
python set_fsnet_test_auto_cfg.py

### Inference (One GPU is used by default)
mkdir -p result/fullsubnet/nrm/taploss/auto/

python /content/TAPLoss-master/FullSubNet/recipes/dns_interspeech_2020/inference.py \
  -C /content/TAPLoss-master/FullSubNet/recipes/dns_interspeech_2020/fullsubnet/test_auto.toml \
  -M /home/yunyangz/Documents/FullSubNet/code/FullSubNet/EXPs/custom_train/checkpoints/model_0030.pth \
  -O result/fullsubnet/nrm/taploss/auto/

### save results
cd result/fullsubnet/nrm/taploss/auto/
zip -q /home/GMS/02_IDL-project/denoised_fsnet_taploss_nrm_auto.zip enhanced_0000/*
