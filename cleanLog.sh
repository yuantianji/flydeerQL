#!/bin/bash
#0 0 * * 0 cleanLog.sh
#new Env('清理日志');

echo "开始清理日志"
pwd
# ls ../log
find ../log -mtime +10 -name "*.log"
find ../log -mtime +10 -name "*.log" -exec rm -rf {} \;
echo "清理日志完成"
