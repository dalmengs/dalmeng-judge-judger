docker run -itd -p 8004:8004 \
    -e JUDGE_SERVER_PORT=8004 \
    -e LOG_DIRECTORY=./log \
    -e CHUNK_SIZE=6 \
    -e DEFAULT_TIME_LIMIT=5.0 \
    -e DEFAULT_MEMORY_LIMIT=128 \
    --name dalmeng_judge_server \
    -v ./log:/usr/src/app/log \
    dalmeng/judge_server:1.0.0