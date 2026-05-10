"""
滴答清单(Dida365) API的Python客户端库

这个模块提供了一个简单的待办任务抽象，基于滴答清单的公开API。
它封装了滴答清单API的常用操作，提供了类型安全的Python接口。

主要功能：
- 任务管理（创建、读取、更新、删除）
- 任务过滤和查询
- 项目管理和分类管理
- 任务状态和优先级处理

使用前需要：
1. 获取滴答清单API的访问令牌（token）
2. 获取项目ID（project_id）

示例用法：
    >>> from TaskService import TaskService, Task
    >>> service = TaskService(token="your_token", project_id="your_project_id")
    >>> task = Task(title="测试任务", description="这是一个测试")
    >>> created_task = service.create_task(task)
    >>> print(f"创建的任务ID: {created_task.id}")

注意：
- API使用UTC时间存储，中国时区（UTC+8）的日期在API中会显示为前一天的16:00 UTC
- 创建任务时无法直接创建已完成的任务，需要先创建再调用complete_task方法
- 更新任务需要先删除再重新创建

版本: 1.0.0
作者: 自动生成
"""

from datetime import datetime, date, time, timezone
from functools import cache
from typing import Any
from pydantic import BaseModel, Field
from typing import Literal, Annotated
import requests

class TaskCategory(BaseModel):
    """任务分类（滴答清单中的列/column）
    
    属性:
        id: 分类的唯一标识符
        name: 分类名称
        sort_order: 排序顺序
    """
    id: str
    name: str
    sort_order: int


class TaskNormalStatus(BaseModel):
    """任务正常状态
    
    表示任务处于未完成状态。
    """
    status: Literal['NORMAL'] = Field(default='NORMAL', init=False)


class TaskCompletedStatus(BaseModel):
    """任务完成状态
    
    表示任务已完成。
    
    属性:
        completed_at: 任务完成时间
    """
    status: Literal['COMPLETED'] = Field(default='COMPLETED', init=False)
    completed_at: datetime = Field(description='任务完成时间')


type TaskStatus = Annotated[TaskNormalStatus | TaskCompletedStatus, Field(discriminator='status')]
"""任务状态类型：NORMAL（未完成）或 COMPLETED（已完成）"""


type TaskPriority = Literal['NONE', 'LOW', 'MEDIUM', 'HIGH']
"""任务优先级类型：NONE（无）、LOW（低）、MEDIUM（中）、HIGH（高）"""


class Task(BaseModel):
    """任务模型
    
    表示滴答清单中的一个任务。
    
    属性:
        id: 任务ID，创建任务时不需要给定，由API生成
        title: 任务标题，必填
        description: 任务描述，支持markdown格式，可选
        schedule_date: 任务所属日期，为None表示未安排日期
        priority: 任务优先级，默认为'NONE'
        status: 任务状态，默认为TaskNormalStatus
        category: 任务所属分类，为None表示任务未分组
    """
    id: str = Field(default='', description='任务 ID，创建任务时不需要给定')
    title: str = Field(description='任务标题')
    description: str = Field(default='', description='任务描述，支持markdown格式，可省略')
    schedule_date: date | None = Field(default=None, description='任务所属日期，为 None 表示未安排日期')
    repeat_flag: str | None = Field(default=None, description='重复规则，使用iCalendar RRULE语法，如 "RRULE:FREQ=DAILY;INTERVAL=1"')
    priority: TaskPriority = Field(default='NONE', description='任务优先级')
    
    status: TaskStatus = Field(default_factory=TaskNormalStatus, description='任务状态')
    category: TaskCategory | None = Field(default=None, description='任务所属分组，为None表示任务未分组')

class TaskService:
    """滴答清单API服务类
    
    提供对滴答清单API的封装，简化任务管理操作。
    
    属性:
        DIDA_ENDPOINT: 滴答清单API的基础端点
    """
    DIDA_ENDPOINT = 'https://dida365.com/open/v1'
    
    @classmethod
    def build_header(cls, token: str):
        """构建API请求头
        
        Args:
            token: 滴答清单API访问令牌
            
        Returns:
            dict: 包含Authorization和User-Agent的请求头
        """
        return {
            'Authorization': f'Bearer {token}',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0'
        }
    
    def __init__(
        self,
        token: str,
        project_id: str,
    ) -> None:
        """初始化TaskService
        
        Args:
            token: 滴答清单API访问令牌
            project_id: 项目ID，任务将属于此项目
            
        Raises:
            ValueError: 如果token或project_id为空
        """
        if not token:
            raise ValueError("token不能为空")
        if not project_id:
            raise ValueError("project_id不能为空")
            
        self._headers = self.build_header(token)
        self._project_id = project_id
    
    @classmethod
    def projects(cls, token: str) -> dict[str, str]:
        """获取用户的所有项目
        
        这是一个类方法，帮助用户在不知道project_id时获取项目列表。
        
        Args:
            token: 滴答清单API访问令牌
            
        Returns:
            dict[str, str]: 项目ID到项目名称的映射
            
        Raises:
            requests.HTTPError: 如果API请求失败
        """
        resp = requests.get(f'{cls.DIDA_ENDPOINT}/project', headers=cls.build_header(token))
        resp.raise_for_status()
        projs = resp.json()
        return {i['id']: i['name'] for i in projs}
    
    def list_tasks(
        self, 
        status: list[Literal['NORMAL', 'COMPLETED']] | None = None, 
        priority: list[TaskPriority] | None = None,
        start_date_inclusive: date | None = None, 
        end_date_inclusive: date | None = None,
    ) -> list[Task]:
        """根据指定条件查询任务
        
        支持按状态、优先级、日期范围过滤任务。
        
        Args:
            status: 任务状态列表，可选值为'NORMAL'或'COMPLETED'
            priority: 任务优先级列表，可选值为'NONE'、'LOW'、'MEDIUM'、'HIGH'
            start_date_inclusive: 开始日期（包含），过滤任务开始日期大于等于此日期的任务
            end_date_inclusive: 结束日期（包含），过滤任务开始日期小于等于此日期的任务
            
        Returns:
            list[Task]: 符合条件的任务列表
            
        Raises:
            requests.HTTPError: 如果API请求失败
            
        Note:
            - 日期过滤使用UTC时间，中国时区（UTC+8）的日期在API中会显示为前一天的16:00 UTC
            - 如果不提供任何过滤条件，返回所有任务
        """
        def format_date(d: date):
            return datetime.combine(d, time.min).astimezone().strftime('%Y-%m-%dT%H:%M:%S.%f%z')
        
        PRIORITY_MAP: dict[TaskPriority, int] = {'NONE': 0, 'LOW': 1, 'MEDIUM': 3, 'HIGH': 5}
        STATUS_MAP = {'NORMAL': 0, 'COMPLETED': 2}
        body = {}
        body['projectIds'] = [self._project_id]
        if start_date_inclusive:
            body['startDate'] = format_date(start_date_inclusive)
        if end_date_inclusive:
            body['endDate'] = format_date(end_date_inclusive)
            
        body['priority'] = [PRIORITY_MAP[i] for i in priority] if priority else list(PRIORITY_MAP.values())
        body['status'] = [STATUS_MAP[i] for i in status] if status else list(STATUS_MAP.values())
        resp = requests.post(f'{self.DIDA_ENDPOINT}/task/filter', headers=self._headers, json=body)
        resp.raise_for_status()
        return [self._dida_task_to_task(i) for i in resp.json()]
        
    def get_task(self, task_id: str) -> Task:
        """根据任务ID获取任务详情
        
        Args:
            task_id: 任务ID
            
        Returns:
            Task: 任务对象
            
        Raises:
            requests.HTTPError: 如果API请求失败或任务不存在
        """
        resp = requests.get(f'{self.DIDA_ENDPOINT}/project/{self._project_id}/task/{task_id}', headers=self._headers)
        resp.raise_for_status()
        return self._dida_task_to_task(resp.json())
    
    def create_task(self, task: Task) -> Task:
        """创建新任务
        
        注意：创建任务时无法直接创建已完成的任务，会视为未完成。
        如果要更新任务，需要先删除再重新创建。
        
        Args:
            task: 要创建的任务对象（不需要提供id）
            
        Returns:
            Task: 创建后的任务对象（包含生成的id）
            
        Raises:
            requests.HTTPError: 如果API请求失败
            ValueError: 如果任务对象无效
        """
        resp = requests.post(f'{self.DIDA_ENDPOINT}/task', headers=self._headers, json=self._task_to_dida_task(task))
        resp.raise_for_status()
        return self._dida_task_to_task(resp.json())

    @cache
    def list_categories(self) -> list[TaskCategory]:
        """获取项目中的所有分类（列）
        
        分类在滴答清单中称为"列"（column）。
        
        Returns:
            list[TaskCategory]: 分类列表
            
        Raises:
            requests.HTTPError: 如果API请求失败
        """
        resp = requests.get(f'{self.DIDA_ENDPOINT}/project/{self._project_id}/data', headers=self._headers)
        resp.raise_for_status()
        return [TaskCategory(id=i['id'], name=i['name'], sort_order=i['sortOrder']) for i in resp.json()['columns']]
    
    def delete_task(self, task_id: str):
        """删除任务
        
        Args:
            task_id: 要删除的任务ID
            
        Raises:
            requests.HTTPError: 如果API请求失败或任务不存在
        """
        resp = requests.delete(f'{self.DIDA_ENDPOINT}/project/{self._project_id}/task/{task_id}', headers=self._headers)
        resp.raise_for_status()
        return 
        
    def complete_task(self, task_id: str):
        """标记任务为已完成
        
        Args:
            task_id: 要完成的任务ID
            
        Raises:
            requests.HTTPError: 如果API请求失败或任务不存在
        """
        resp = requests.post(f'{self.DIDA_ENDPOINT}/project/{self._project_id}/task/{task_id}/complete', headers=self._headers)
        resp.raise_for_status()
        return 
    
    def _dida_task_to_task(self, dida_task: dict[str, Any]) -> Task:
        """将滴答清单API返回的任务数据转换为Task对象
        
        这是一个内部方法，用于将API返回的原始JSON数据转换为类型安全的Task对象。
        处理状态、优先级、日期和分类的映射。
        
        Args:
            dida_task: 滴答清单API返回的任务数据字典
            
        Returns:
            Task: 转换后的Task对象
            
        Note:
            - 处理时区转换：API返回UTC时间，转换为本地时区
            - 优先级映射：0->NONE, 1->LOW, 3->MEDIUM, 5->HIGH
            - 状态映射：0->NORMAL, 2->COMPLETED
        """
        # 处理状态
        status_value = dida_task.get('status', 0)
        if status_value == 2:  # Completed
            completed_time = dida_task.get('completedTime')
            if completed_time:
                # 解析日期时间字符串，只取日期部分
                status = TaskCompletedStatus(completed_at=datetime.strptime(completed_time, "%Y-%m-%dT%H:%M:%S.%f%z"))
            else:
                # 如果没有完成时间，使用当前日期
                status = TaskCompletedStatus(completed_at=datetime.now().astimezone(timezone.utc))
        else:  # Normal
            status = TaskNormalStatus()
        
        # 处理优先级映射
        priority_map = {
            0: 'NONE',    # None -> LOW
            1: 'LOW',    # Low -> LOW
            3: 'MEDIUM', # Medium -> MEDIUM
            5: 'HIGH'    # High -> HIGH
        }
        priority_value = dida_task.get('priority', 0)
        priority = priority_map.get(priority_value, 'LOW')
        
        # 处理日期
        schedule_date = None
        start_date = dida_task.get('startDate')
        if start_date:
            try:
                # 解析日期时间字符串，只取日期部分
                schedule_date = datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%S.%f%z").astimezone().date()
            except (ValueError, TypeError):
                schedule_date = None
        
        repeat_flag = dida_task.get('repeatFlag')

        category = next((i for i in self.list_categories() if i.id == column_id), None) if (column_id := dida_task.get('columnId')) else None
        
        # 构建 Task 对象
        return Task(
            id=dida_task.get('id', ''),
            title=dida_task.get('title', ''),
            description=dida_task.get('content', '') or dida_task.get('desc', ''),
            schedule_date=schedule_date,
            repeat_flag=repeat_flag,
            priority=priority, # type: ignore
            status=status,
            category=category
        )

    def _task_to_dida_task(self, task: Task) -> dict[str, Any]:
        """将Task对象转换为滴答清单API所需的任务数据格式
        
        这是一个内部方法，用于将Task对象转换为API所需的JSON格式。
        处理优先级、状态、日期和分类的逆向映射。
        
        Args:
            task: 要转换的Task对象
            
        Returns:
            dict[str, Any]: 滴答清单API所需的任务数据格式
            
        Note:
            - 日期转换为UTC时间：本地日期转换为UTC时间字符串
            - 优先级逆向映射：NONE->0, LOW->1, MEDIUM->3, HIGH->5
            - 状态逆向映射：NORMAL->0, COMPLETED->2
        """
        dida_task = {
            'title': task.title,
            'content': task.description,
            'priority': {
                'NONE': 0,
                'LOW': 1,
                'MEDIUM': 3,
                'HIGH': 5
            }.get(task.priority, 0),
            'status': 2 if isinstance(task.status, TaskCompletedStatus) else 0,
        }
        
        # 添加 ID（如果存在）
        if task.id:
            dida_task['id'] = task.id
        
        # 处理日期
        if task.schedule_date:
            used_date = datetime.combine(task.schedule_date, time.min).astimezone().astimezone(timezone.utc)
            dida_task['isAllDay'] = True
            # 将日期转换为滴答清单的日期时间格式
            dida_task['startDate'] = f"{used_date.strftime('%Y-%m-%dT%H:%M:%S.%f%z')}"
            dida_task['dueDate'] = f"{used_date.strftime('%Y-%m-%dT%H:%M:%S.%f%z')}"

        if task.repeat_flag:
            dida_task['repeatFlag'] = task.repeat_flag

        # 处理分类
        dida_task['projectId'] = self._project_id
        
        # 处理完成状态
        if isinstance(task.status, TaskCompletedStatus):
            # 将日期转换为滴答清单的日期时间格式
            dida_task['completedTime'] = f"{task.status.completed_at.strftime('%Y-%m-%dT%H:%M:%S.%f%z')}"

        if category := task.category:
            dida_task['columnId'] = category.id
        return dida_task
