Project Overview

This project explores the Jane Street Real-Time Market Data Forecasting dataset with a focus on understanding its underlying structure and extracting meaningful predictive signals. I performed a detailed feature analysis to identify the most important feature vectors and uncover relationships between different variables.

Multiple machine learning models were evaluated on the dataset, and after extensive experimentation, CatBoost was selected as the final model due to its strong performance and robustness to noisy, high-dimensional data.

Because financial datasets typically exhibit high noise and weak generalization patterns, many models struggle to produce stable results. In such cases, conventional loss metrics do not necessarily indicate poor model design—they often reflect the inherent nature of the dataset itself. This project highlights these challenges and demonstrates an approach that balances interpretability, performance, and resilience to noise.

Dataset:
you can download from kaggle Jane Street Real-Time Market Data Forecasting official website.
Or download it partially:
!kaggle competitions download -c jane-street-real-time-market-data-forecasting -f train.parquet/partition_id=3/part-0.parquet
