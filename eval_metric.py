# !pip install https://github.com/schmiph2/pysepm/archive/master.zip --quiet
# !pip install git+https://github.com/aliutkus/speechmetrics#egg=speechmetrics[cpu] --quiet

# # Noisy (DNS dataset)
# python eval_metric.py \
# --save_name noisy \
# --save_dir ./ \
# --clean_dir test/nrm_clean/ \
# --noisy_dir test/nrm_noisy/

# # Low (t-DNS dataset)
# python eval_metric.py \
# --save_name low \
# --save_dir ./ \
# --clean_dir test/nrm_clean/ \
# --noisy_dir test/nrm_zm_phone_relay_low/

# # Auto (Industry / don't normalize!)
# python eval_metric.py \
# --save_name auto \
# --save_dir ./ \
# --clean_dir test/nrm_clean/ \
# --noisy_dir test/src_zm_phone_relay_auto/

import argparse
import os
import re
import sys
import librosa
import pandas as pd
import numpy as np
from tqdm import tqdm
from rich import print

import pysepm
import speechmetrics

sr = 16000

FW_SNR_SEG = pysepm.fwSNRseg
PESQ = speechmetrics.relative.pesq.load(window=None)
STOI = speechmetrics.relative.stoi.load(window=None)

def calc_metric(clean, noisy):
    fwsnrseg = FW_SNR_SEG(clean, noisy, sr)
    pesq = PESQ.test_window((noisy, clean), sr)['pesq']
    stoi = STOI.test_window((noisy, clean), sr)['stoi']
    
    return [fwsnrseg, pesq, stoi]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="metric evaluation")
    parser.add_argument("--save_name", required=True, type=str)
    parser.add_argument("--save_dir", required=True, type=str)
    parser.add_argument("--clean_dir", required=True, type=str)
    parser.add_argument("--noisy_dir", required=True, type=str)
    args = parser.parse_args()
    
    print(f"Evaluate files in {args.noisy_dir} ...")

    clean_files = sorted(os.listdir(args.clean_dir))
    noisy_files = sorted(os.listdir(args.noisy_dir))
    assert len(clean_files) == len(noisy_files)

    results = []

    for i, clean_fname in enumerate(tqdm(clean_files)):
        clean_fileid = re.findall("fileid_\d+", clean_fname)[0] # fileid_xxx
        clean_fileid = clean_fileid.split("_") # xxx

        for noisy_fname in noisy_files:
            noisy_fileid = re.findall("fileid_\d+", noisy_fname)[0] # fileid_xxx
            noisy_fileid = noisy_fileid.split("_") # xxx
            if clean_fileid == noisy_fileid:
                break

        clean_wav = librosa.load(os.path.join(args.clean_dir, clean_fname), sr=sr)[0]
        noisy_wav = librosa.load(os.path.join(args.noisy_dir, noisy_fname), sr=sr)[0]

        evals = calc_metric(clean_wav, noisy_wav)
        results.append(evals)

    results = np.array(results)
    results = results.mean(axis=0).reshape((1,-1))
    columns = ['fwSNRseg', 'PESQ', 'STOI']
    
    print(columns)
    print(f"[{results}]")
    
    df = pd.DataFrame(data=results, columns=columns)
    save_path = os.path.join(args.save_dir, f"{args.save_name}.csv")
    df.to_csv(save_path)
    print(f"Saved [{save_path}]")