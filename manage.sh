#!/bin/bash

# Tron监控服务管理脚本
# 用法: ./manage.sh {start|stop|restart|status|logs}

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$PROJECT_DIR/monitor.log"
PID_FILE="$PROJECT_DIR/monitor.pid"

start() {
    if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then
        echo "[INFO] 服务已在运行 (PID: $(cat $PID_FILE))"
        exit 0
    fi
    echo "[INFO] 启动Tron监控服务..."
    nohup python3 main.py > "$LOG_FILE" 2>&1 &
    echo $! > "$PID_FILE"
    echo "[INFO] 服务启动成功, PID: $(cat $PID_FILE)"
    echo "[INFO] 日志文件: $LOG_FILE"
}

stop() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 $PID 2>/dev/null; then
            echo "[INFO] 停止Tron监控服务..."
            kill $PID
            rm -f "$PID_FILE"
            echo "[INFO] 服务已停止"
        else
            echo "[WARN] 服务未运行"
            rm -f "$PID_FILE"
        fi
    else
        echo "[WARN] 未找到PID文件，服务可能未运行"
    fi
}

status() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 $PID 2>/dev/null; then
            echo "[INFO] 服务正在运行 (PID: $PID)"
        else
            echo "[WARN] 服务未运行，但PID文件存在"
        fi
    else
        echo "[INFO] 服务未运行"
    fi
}

logs() {
    echo "[INFO] 查看实时日志 (按 Ctrl+C 退出):"
    tail -f "$LOG_FILE"
}

case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        stop
        start
        ;;
    status)
        status
        ;;
    logs)
        logs
        ;;
    *)
        echo "用法: $0 {start|stop|restart|status|logs}"
        exit 1
        ;;
esac
