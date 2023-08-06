How to run
```
docker-compose up
```

Or

Build Image
```
docker build -t tradingbot -f ./Dockerfile .
```


Run image
a) Jupyter Notebook
```
docker run --network host -v ~/Workspace/trading-bot/jupyter:/app tradingbot:latest jupyter notebook --NotebookApp.token='' --NotebookApp.password='' --NotebookApp.iopub_data_rate_limit=1.0e10
```

b) Streamlit web app
```
docker run --network host -v ~/Workspace/trading-bot/jupyter:/app tradingbot:latest streamlit run app.py
```
