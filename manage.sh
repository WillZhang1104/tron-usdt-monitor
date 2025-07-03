#!/bin/bash

# Tron监控服务管理脚本
# 使用方法: ./manage.sh {start|stop|restart|status|logs|update}

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$PROJECT_DIR/monitor.log"
PID_FILE="$PROJECT_DIR/monitor.pid"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_debug() {
    echo -e "${BLUE}[DEBUG]${NC} $1"
}

# 检查服务是否运行
is_running() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            return 0
        else
            rm -f "$PID_FILE"
        fi
    fi
    return 1
}

# 获取进程ID
get_pid() {
    pgrep -f "python3.*main.py"
}

# 启动服务
start_service() {
    log_info "启动Tron监控服务..."
    
    if is_running; then
        log_warn "服务已在运行中，PID: $(get_pid)"
        return 1
    fi
    
    # 检查Python和依赖
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 未安装"
        return 1
    fi
    
    # 检查.env文件
    if [ ! -f ".env" ]; then
        log_error ".env 文件不存在，请先配置环境变量"
        return 1
    fi
    
    # 启动服务
    cd "$PROJECT_DIR"
    nohup python3 main.py > "$LOG_FILE" 2>&1 &
    local pid=$!
    
    # 保存PID
    echo "$pid" > "$PID_FILE"
    
    # 等待服务启动
    sleep 2
    
    if is_running; then
        log_info "服务启动成功，PID: $pid"
        log_info "日志文件: $LOG_FILE"
        return 0
    else
        log_error "服务启动失败，请检查日志"
        return 1
    fi
}

# 停止服务
stop_service() {
    log_info "停止Tron监控服务..."
    
    if ! is_running; then
        log_warn "服务未运行"
        return 0
    fi
    
    local pid=$(get_pid)
    if [ -n "$pid" ]; then
        kill "$pid"
        sleep 2
        
        # 检查是否停止成功
        if ps -p "$pid" > /dev/null 2>&1; then
            log_warn "服务未正常停止，强制终止..."
            kill -9 "$pid"
        fi
        
        rm -f "$PID_FILE"
        log_info "服务已停止"
    else
        log_warn "未找到服务进程"
    fi
}

# 重启服务
restart_service() {
    log_info "重启Tron监控服务..."
    stop_service
    sleep 2
    start_service
}

# 查看服务状态
show_status() {
    log_info "Tron监控服务状态:"
    
    if is_running; then
        local pid=$(get_pid)
        log_info "✅ 服务正在运行"
        log_info "PID: $pid"
        log_info "日志文件: $LOG_FILE"
        
        # 显示最近日志
        if [ -f "$LOG_FILE" ]; then
            log_info "最近日志:"
            tail -n 5 "$LOG_FILE" | while read line; do
                echo "  $line"
            done
        fi
    else
        log_warn "❌ 服务未运行"
    fi
}

# 查看日志
show_logs() {
    if [ -f "$LOG_FILE" ]; then
        log_info "查看实时日志 (按 Ctrl+C 退出):"
        tail -f "$LOG_FILE"
    else
        log_error "日志文件不存在: $LOG_FILE"
    fi
}

# 更新服务
update_service() {
    log_info "更新Tron监控服务..."
    
    # 备份配置
    if [ -f ".env" ]; then
        cp .env .env.backup
        log_info "配置已备份到 .env.backup"
    fi
    
    # 下载最新文件
    log_info "下载最新文件..."
    
    # 检查wget是否可用
    if command -v wget &> /dev/null; then
        wget -O address_manager.py https://raw.githubusercontent.com/WillZhang1104/tron-usdt-monitor/master/address_manager.py
        wget -O telegram_bot.py https://raw.githubusercontent.com/WillZhang1104/tron-usdt-monitor/master/telegram_bot.py
        wget -O main.py https://raw.githubusercontent.com/WillZhang1104/tron-usdt-monitor/master/main.py
    elif command -v curl &> /dev/null; then
        curl -o address_manager.py https://raw.githubusercontent.com/WillZhang1104/tron-usdt-monitor/master/address_manager.py
        curl -o telegram_bot.py https://raw.githubusercontent.com/WillZhang1104/tron-usdt-monitor/master/telegram_bot.py
        curl -o main.py https://raw.githubusercontent.com/WillZhang1104/tron-usdt-monitor/master/main.py
    else
        log_error "wget 和 curl 都不可用，无法下载文件"
        return 1
    fi
    
    log_info "文件下载完成"
    
    # 重启服务
    restart_service
}

# 显示帮助
show_help() {
    echo "Tron监控服务管理脚本"
    echo ""
    echo "使用方法: $0 {start|stop|restart|status|logs|update|help}"
    echo ""
    echo "命令说明:"
    echo "  start   - 启动服务"
    echo "  stop    - 停止服务"
    echo "  restart - 重启服务"
    echo "  status  - 查看服务状态"
    echo "  logs    - 查看实时日志"
    echo "  update  - 更新服务文件"
    echo "  help    - 显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 start    # 启动服务"
    echo "  $0 status   # 查看状态"
    echo "  $0 logs     # 查看日志"
    echo "  $0 update   # 更新服务"
}

# 主函数
main() {
    case "$1" in
        start)
            start_service
            ;;
        stop)
            stop_service
            ;;
        restart)
            restart_service
            ;;
        status)
            show_status
            ;;
        logs)
            show_logs
            ;;
        update)
            update_service
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            log_error "未知命令: $1"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@" 