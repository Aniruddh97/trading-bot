Build Image
```
docker build -t tradingbot -f ./Dockerfile .
```


Run image
```
docker run --network host -v ~/Workspace/trading-bot/jupyter:/app tradingbot:latest jupyter notebook --NotebookApp.token='' --NotebookApp.password=''
```