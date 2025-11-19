import argparse
import os
import pandas as pd
import numpy as np
import joblib
import polars as pl
from catboost import CatBoostRegressor, Pool
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--target", type=str, default="responder_6")
    p.add_argument("--model-out", type=str, default="artifacts/model.cbm")
    p.add_argument("--num-iter", type=int, default=2000)
    p.add_argument("--val-size", type=float, default=0.2)
    p.add_argument("--random-seed", type=int, default=42)
    return p.parse_args()

# Paths and constants
input_path = 'data'
def read_selected_data(input_path):
    # Define the directory containing your data files

    # List three specific Parquet files you want to read
    selected_files = [f"partition_id={i}/part-0.parquet" for i in range(1)]
    # Load and filter the data from only the selected Parquet files
    dfs = []
    for file_name in selected_files:
        file_path = f'{input_path}/train.parquet/{file_name}'
        lazy_df = pl.scan_parquet(file_path)
        df = lazy_df.collect()
        dfs.append(df)

    # Concatenate all dataframes into a single dataframe
    full_df = pl.concat(dfs)

    return full_df
def main():
    args = parse_args()
    os.makedirs(os.path.dirname(args.model_out), exist_ok=True)

    print("Loading data...")
    df = read_selected_data(input_path)
    df = df.fill_null(strategy='forward')

    # Prepare feature names
    feature_names = [f"feature_{i:02d}" for i in range(79)]

    # Prepare training and validation data
    num_valid_dates = 100
    dates = df['date_id'].unique().to_numpy()
    valid_dates = dates[-num_valid_dates:]
    train_dates = dates[:-num_valid_dates]

    # Extract features, target, and weights for validation and training sets
    X_valid = df.filter(pl.col('date_id').is_in(valid_dates)).select(feature_names).fill_null(0).to_numpy()
    y_valid = df.filter(pl.col('date_id').is_in(valid_dates)).select('responder_6').fill_null(0).to_numpy().ravel()
    w_valid = df.filter(pl.col('date_id').is_in(valid_dates)).select('weight').fill_null(0).to_numpy().ravel()

    X_train = df.filter(pl.col('date_id').is_in(train_dates)).select(feature_names).fill_null(0).to_numpy()
    y_train = df.filter(pl.col('date_id').is_in(train_dates)).select('responder_6').fill_null(0).to_numpy().ravel()
    w_train = df.filter(pl.col('date_id').is_in(train_dates)).select('weight').fill_null(0).to_numpy().ravel()

    from catboost import CatBoostRegressor

    model = CatBoostRegressor(
        loss_function="RMSE",
        learning_rate=0.03,
        depth=8,
        iterations=4000,
        l2_leaf_reg=5,
        bootstrap_type="Bernoulli",
        subsample=0.8,
        random_strength=1,
        leaf_estimation_iterations=4,
        verbose=200,
    )

    model.fit(
        X_train, y_train,
        eval_set=(X_valid, y_valid),
        use_best_model=True
    )

    # 保存模型 + scaler + feature list
    print(f"Saving model to {args.model_out}")
    model.save_model(args.model_out)

    # 保存 scaler & feature list for inference
    import joblib
    joblib.dump({"features": feature_names}, os.path.join(os.path.dirname(args.model_out), "preprocess.pkl"))
    print("Saved preprocessing artifacts.")

if __name__ == "__main__":
    main()