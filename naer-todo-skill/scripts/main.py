#!/usr/bin/env python3
"""
TaskService CLI接口 - 为LLM设计的待办任务管理工具

这个CLI提供了简单的待办任务管理功能，适合AI通过shell调用。
所有操作都基于环境变量中的认证信息。

环境变量要求:
- DIDA_TOKEN: 滴答清单API访问令牌
- DIDA_PROJECT_ID: 项目ID

使用示例:
    # 列出当前未完成任务（今日以及过期的和未安排时间的任务）
    python main.py list-today
    
    # 列出全部未完成任务（所有时间的以及没有安排时间的任务）
    python main.py list-all
    
    # 列出所有任务（兼容命令，等同于list-today）
    python main.py list
    
    # 创建新任务
    python main.py create --title "购买 groceries" --description "牛奶、鸡蛋、面包" --date 2026-03-21 --priority MEDIUM
    
    # 获取任务详情
    python main.py get <task_id>
    
    # 完成任务
    python main.py complete <task_id>
    
    # 删除任务
    python main.py delete <task_id>
"""

import os
import sys
import argparse
from datetime import date, datetime
from typing import Optional, List

from TaskService import TaskService, Task, TaskCategory, TaskCompletedStatus

def check_env_vars() -> tuple[str, str]:
    """检查环境变量，缺失时直接报错退出"""
    token = os.environ.get('DIDA_TOKEN')
    project_id = os.environ.get('DIDA_PROJECT_ID')
    
    if not token:
        print("错误: 环境变量 DIDA_TOKEN 未设置", file=sys.stderr)
        sys.exit(1)
    if not project_id:
        print("错误: 环境变量 DIDA_PROJECT_ID 未设置", file=sys.stderr)
        sys.exit(1)
    
    return token, project_id

def format_task_for_display(task: Task) -> str:
    """将任务对象格式化为可读的字符串"""
    # 状态显示
    status_str = "COMPLETED" if isinstance(task.status, TaskCompletedStatus) else "NORMAL"
    
    # 优先级显示
    priority_map = {'NONE': '无', 'LOW': '低', 'MEDIUM': '中', 'HIGH': '高'}
    priority_str = priority_map.get(task.priority, task.priority)
    
    # 日期显示
    date_str = task.schedule_date.strftime("%Y-%m-%d") if task.schedule_date else "未安排"
    
    # 分类显示
    category_str = task.category.name if task.category else "未分组"

    repeat_str = task.repeat_flag if task.repeat_flag else ""

    # 简短的描述（截断过长的描述）
    desc_short = task.description[:30] + "..." if len(task.description) > 30 else task.description

    return f"{task.id} | {task.title} | {status_str} | {priority_str} | {date_str} | {category_str} | {repeat_str} | {desc_short}"

def format_task_detail(task: Task) -> str:
    """将任务对象格式化为详细显示"""
    # 状态显示
    status_str = "已完成" if isinstance(task.status, TaskCompletedStatus) else "未完成"
    
    # 优先级显示
    priority_map = {'NONE': '无', 'LOW': '低', 'MEDIUM': '中', 'HIGH': '高'}
    priority_str = priority_map.get(task.priority, task.priority)
    
    # 日期显示
    date_str = task.schedule_date.strftime("%Y-%m-%d") if task.schedule_date else "未安排"
    
    # 分类显示
    category_str = f"{task.category.name} ({task.category.id})" if task.category else "未分组"
    
    # 完成时间（如果已完成）
    completed_time = ""
    if isinstance(task.status, TaskCompletedStatus):
        completed_time = f"\n完成时间: {task.status.completed_at.strftime('%Y-%m-%d %H:%M:%S')}"
    
    repeat_str = f"\n重复: {task.repeat_flag}" if task.repeat_flag else ""

    return f"""任务ID: {task.id}
标题: {task.title}
描述: {task.description}
状态: {status_str}{completed_time}
优先级: {priority_str}
日期: {date_str}
分类: {category_str}{repeat_str}"""

def list_today_tasks_command(service: TaskService, args):
    """处理list-today命令：列出当前未完成任务（今日以及过期的任务）"""
    try:
        # 获取今天的日期
        today = date.today()
        
        # 获取所有未完成的任务
        tasks = service.list_tasks(status=["NORMAL"])
        
        # 过滤：今日任务、过期任务（日期小于今天）、以及没有安排日期的任务
        filtered_tasks = []
        for task in tasks:
            if not task.schedule_date:
                # 没有安排日期的任务
                filtered_tasks.append(task)
            elif task.schedule_date <= today:
                # 今日或过期的任务
                filtered_tasks.append(task)
        
        # 输出结果
        if not filtered_tasks:
            print("没有找到今日或过期的未完成任务")
            return
        
        print(f"找到 {len(filtered_tasks)} 个今日或过期的未完成任务:")
        print("=" * 80)
        print("ID | 标题 | 状态 | 优先级 | 日期 | 分类 | 重复 | 描述")
        print("-" * 80)
        
        for task in filtered_tasks:
            print(format_task_for_display(task))
            
    except Exception as e:
        print(f"错误: 获取任务列表失败 - {e}", file=sys.stderr)
        sys.exit(1)

def list_all_tasks_command(service: TaskService, args):
    """处理list-all命令：列出全部未完成任务（所有时间的以及没有安排时间的任务）"""
    try:
        # 获取所有未完成的任务
        tasks = service.list_tasks(status=["NORMAL"])
        
        # 输出结果
        if not tasks:
            print("没有找到未完成任务")
            return
        
        print(f"找到 {len(tasks)} 个未完成任务:")
        print("=" * 80)
        print("ID | 标题 | 状态 | 优先级 | 日期 | 分类 | 重复 | 描述")
        print("-" * 80)
        
        for task in tasks:
            print(format_task_for_display(task))
            
    except Exception as e:
        print(f"错误: 获取任务列表失败 - {e}", file=sys.stderr)
        sys.exit(1)

def list_tasks_command(service: TaskService, args):
    """处理list命令（兼容命令，等同于list-today）"""
    list_today_tasks_command(service, args)

def create_task_command(service: TaskService, args):
    """处理create命令"""
    # 验证必要参数
    if not args.title:
        print("错误: 必须提供任务标题 (--title)", file=sys.stderr)
        sys.exit(1)
    
    # 创建任务对象
    try:
        task = Task(
            title=args.title,
            description=args.description or "",
            schedule_date=args.date,
            priority=(args.priority or "NONE").upper()
        )
        
        # 如果有分类ID，设置分类
        if args.category_id:
            # 获取所有分类
            categories = service.list_categories()
            category = next((c for c in categories if c.id == args.category_id), None)
            if category:
                task.category = category
            else:
                print(f"警告: 分类ID '{args.category_id}' 不存在，任务将不设置分类", file=sys.stderr)

        if args.repeat:
            task.repeat_flag = args.repeat

        # 创建任务
        created_task = service.create_task(task)
        print(f"创建成功: {created_task.id}")
        print(f"标题: {created_task.title}")
        if created_task.schedule_date:
            print(f"日期: {created_task.schedule_date}")
        print(f"优先级: {created_task.priority}")
        if created_task.repeat_flag:
            print(f"重复: {created_task.repeat_flag}")
        
    except Exception as e:
        print(f"错误: 创建任务失败 - {e}", file=sys.stderr)
        sys.exit(1)

def get_task_command(service: TaskService, args):
    """处理get命令"""
    if not args.task_id:
        print("错误: 必须提供任务ID", file=sys.stderr)
        sys.exit(1)
    
    try:
        task = service.get_task(args.task_id)
        print(format_task_detail(task))
    except Exception as e:
        print(f"错误: 获取任务失败 - {e}", file=sys.stderr)
        sys.exit(1)

def complete_task_command(service: TaskService, args):
    """处理complete命令"""
    if not args.task_id:
        print("错误: 必须提供任务ID", file=sys.stderr)
        sys.exit(1)
    
    try:
        service.complete_task(args.task_id)
        print(f"完成成功: {args.task_id}")
    except Exception as e:
        print(f"错误: 完成任务失败 - {e}", file=sys.stderr)
        sys.exit(1)

def delete_task_command(service: TaskService, args):
    """处理delete命令"""
    if not args.task_id:
        print("错误: 必须提供任务ID", file=sys.stderr)
        sys.exit(1)
    
    try:
        service.delete_task(args.task_id)
        print(f"删除成功: {args.task_id}")
    except Exception as e:
        print(f"错误: 删除任务失败 - {e}", file=sys.stderr)
        sys.exit(1)

def list_categories_command(service: TaskService, args):
    """处理categories命令"""
    try:
        categories = service.list_categories()
        
        if not categories:
            print("没有找到分类")
            return
        
        print(f"找到 {len(categories)} 个分类:")
        print("=" * 50)
        print("ID | 名称 | 排序")
        print("-" * 50)
        
        for category in categories:
            print(f"{category.id} | {category.name} | {category.sort_order}")
            
    except Exception as e:
        print(f"错误: 获取分类列表失败 - {e}", file=sys.stderr)
        sys.exit(1)

def parse_date(date_str: str) -> Optional[date]:
    """解析日期字符串"""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        print(f"错误: 无效的日期格式 '{date_str}'，请使用 YYYY-MM-DD 格式", file=sys.stderr)
        sys.exit(1)

def main():
    # 检查环境变量
    token, project_id = check_env_vars()
    
    # 创建服务实例
    try:
        service = TaskService(token, project_id)
    except Exception as e:
        print(f"错误: 初始化服务失败 - {e}", file=sys.stderr)
        sys.exit(1)
    
    # 创建主解析器
    parser = argparse.ArgumentParser(
        description="待办任务管理CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # list-today命令：列出当前未完成任务（今日以及过期的任务）
    list_today_parser = subparsers.add_parser("list-today", help="列出当前未完成任务（今日以及过期的任务）")
    
    # list-all命令：列出全部未完成任务（所有时间的以及没有安排时间的任务）
    list_all_parser = subparsers.add_parser("list-all", help="列出全部未完成任务（所有时间的以及没有安排时间的任务）")
    
    # list命令（兼容命令，等同于list-today）
    list_parser = subparsers.add_parser("list", help="列出当前未完成任务（兼容命令，等同于list-today）")
    
    # create命令
    create_parser = subparsers.add_parser("create", help="创建新任务")
    create_parser.add_argument("--title", required=True, help="任务标题")
    create_parser.add_argument("--description", default="", help="任务描述")
    create_parser.add_argument("--date", type=parse_date, help="任务日期 (YYYY-MM-DD)")
    create_parser.add_argument("--priority", choices=["NONE", "LOW", "MEDIUM", "HIGH"],
                             help="任务优先级")
    create_parser.add_argument("--category-id", help="分类ID")
    create_parser.add_argument("--repeat", help="重复规则 (iCalendar RRULE语法, 如 'RRULE:FREQ=DAILY;INTERVAL=1')")
    
    # get命令
    get_parser = subparsers.add_parser("get", help="获取任务详情")
    get_parser.add_argument("task_id", help="任务ID")
    
    # complete命令
    complete_parser = subparsers.add_parser("complete", help="标记任务为已完成")
    complete_parser.add_argument("task_id", help="任务ID")
    
    # delete命令
    delete_parser = subparsers.add_parser("delete", help="删除任务")
    delete_parser.add_argument("task_id", help="任务ID")
    
    # categories命令
    categories_parser = subparsers.add_parser("categories", help="列出所有分类")
    
    # 解析参数
    args = parser.parse_args()
    
    # 如果没有提供命令，显示帮助
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # 执行命令
    try:
        if args.command == "list-today":
            list_today_tasks_command(service, args)
        elif args.command == "list-all":
            list_all_tasks_command(service, args)
        elif args.command == "list":
            list_tasks_command(service, args)  # 兼容命令
        elif args.command == "create":
            create_task_command(service, args)
        elif args.command == "get":
            get_task_command(service, args)
        elif args.command == "complete":
            complete_task_command(service, args)
        elif args.command == "delete":
            delete_task_command(service, args)
        elif args.command == "categories":
            list_categories_command(service, args)
    except KeyboardInterrupt:
        print("\n操作被用户中断", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"错误: 执行命令时发生意外错误 - {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
