from typing import Optional, List, Dict, Any, Union
from enum import Enum
import aiohttp
from datetime import datetime
import json
from dataclasses import dataclass


class APIError(Exception):
    """Базовый класс для ошибок API"""

    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Dict] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class TaskStatus(Enum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class UserType(Enum):
    EXECUTOR = "executor"
    MANAGER = "manager"
    ADMIN = "admin"
    REG = "regestration"


@dataclass
class APIResponse:
    """Класс для структурированного ответа API"""
    success: bool
    data: Optional[Union[Dict, List]] = None
    message: Optional[str] = None
    error: Optional[str] = None


class TaskManagementAPI:
    """Клиент API для управления задачами"""

    def __init__(self, base_url: str, timeout: int = 30):
        """
        Инициализация клиента API

        Args:
            base_url: Базовый URL API
            timeout: Таймаут запросов в секундах
        """
        self.base_url = base_url.rstrip('/')
        self.session: Optional[aiohttp.ClientSession] = None
        self.timeout = aiohttp.ClientTimeout(total=timeout)

    async def __aenter__(self):
        """Поддержка контекстного менеджера"""
        await self._ensure_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Закрытие сессии при выходе из контекстного менеджера"""
        await self.close()

    async def _ensure_session(self):
        """Создание сессии если она не существует"""
        if self.session is None:
            self.session = aiohttp.ClientSession(
                headers={'Content-Type': 'application/json'},
                timeout=self.timeout
            )

    async def close(self):
        """Закрытие сессии"""
        if self.session:
            await self.session.close()
            self.session = None

    async def _request(
            self,
            method: str,
            endpoint: str,
            **kwargs
    ) -> APIResponse:
        """
        Выполнение HTTP-запроса

        Args:
            method: HTTP-метод
            endpoint: Эндпоинт API
            **kwargs: Дополнительные параметры запроса

        Returns:
            APIResponse: Структурированный ответ API

        Raises:
            APIError: При ошибке запроса
        """
        await self._ensure_session()
        try:
            async with self.session.request(
                    method,
                    f"{self.base_url}{endpoint}",
                    **kwargs
            ) as response:
                response_data = await response.json()

                if not response.ok:
                    raise APIError(
                        message=response_data.get('detail', 'Unknown error'),
                        status_code=response.status,
                        response_data=response_data
                    )

                return APIResponse(
                    success=True,
                    data=response_data.get('data'),
                    message=response_data.get('message')
                )
        except aiohttp.ClientError as e:
            raise APIError(f"Network error: {str(e)}")
        except json.JSONDecodeError:
            raise APIError("Invalid JSON response")

    # Users

    async def get_all_users(self) -> List[dict]:
        """Получение списка всех пользователей"""
        try:
            response = await self._request('GET', '/users/all/list')
            return response.data
        except Exception as e:
            return str(e)

    async def update_user_type(self, user_id: int, new_type: str) -> dict:
        """Изменение типа пользователя"""
        return await self._request(
            'PUT',
            f'/users/{user_id}/type',
            json={"new_type": new_type}
        )

    async def get_user(self, user_id: int) -> Optional[Dict]:
        """
        Получение информации о пользователе

        Args:
            user_id: ID пользователя

        Returns:
            Dict: Информация о пользователе или None если пользователь не найден
        """
        try:
            response = await self._request('GET', f'/users/{user_id}')
            return response.data
        except APIError as e:
            if e.status_code == 404:
                return None
            raise

    async def register_user(
            self,
            user_id: int,
            name: str,
            user_type: Union[UserType, str] = UserType.EXECUTOR,
            username: Optional[str] = None
    ) -> Dict:
        """
        Регистрация нового пользователя

        Args:
            user_id: ID пользователя
            name: Имя пользователя
            user_type: Тип пользователя
            username: Имя пользователя (опционально)

        Returns:
            Dict: Информация о созданном пользователе
        """
        if isinstance(user_type, UserType):
            user_type = user_type.value

        data = {
            "user_id": user_id,
            "name": name,
            "type": user_type,
            "user_name": username
        }
        response = await self._request('POST', '/users/', json=data)
        return response.data

    # Tasks
    async def ban_user(self, user_id: int) -> Dict:
        """
        Блокировка пользователя

        Args:
            user_id: ID пользователя

        Returns:
            Dict: Результат операции
        """
        response = await self._request('POST', f'/users/{user_id}/ban')
        return response.data

    async def unban_user(self, user_id: int) -> Dict:
        """
        Разблокировка пользователя

        Args:
            user_id: ID пользователя

        Returns:
            Dict: Результат операции
        """
        response = await self._request('POST', f'/users/{user_id}/unban')
        return response.data

    async def check_ban_status(self, user_id: int) -> Dict:
        """
        Проверка статуса блокировки пользователя

        Args:
            user_id: ID пользователя

        Returns:
            Dict: Информация о статусе блокировки
        """
        response = await self._request('GET', f'/users/{user_id}/ban-status')
        return response.data

    async def update_task_with_details(
            self,
            task_id: int,
            status: str,
            completion_note: Optional[str] = None
    ) -> Dict:
        """
        Обновление задачи с дополнительными деталями

        Args:
            task_id: ID задачи
            status: Новый статус задачи
            completion_note: Примечание о выполнении (опционально)

        Returns:
            Dict: Обновленная информация о задаче
        """
        data = {
            "status": status,
            "completion_note": completion_note
        }
        response = await self._request('PUT', f'/tasks/{task_id}', json=data)
        return response.data
    async def update_task_status(
            self,
            task_id: int,
            user_id: int,
            status: str,
            comment: Optional[str] = None
    ) -> Dict:
        """
        Обновление статуса работы над задачей

        Args:
            task_id: ID задачи
            user_id: ID пользователя
            status: Новый статус
            comment: Комментарий к обновлению статуса (опционально)

        Returns:
            Dict: Результат операции
        """
        data = {
            "status": status,
            "comment": comment
        }
        response = await self._request(
            'POST',
            f'/tasks/{task_id}/status',
            json=data,
            params={'user_id': user_id}
        )
        return response.data

    async def cancel_task(
            self,
            task_id: int,
            user_id: int,
            reason: str = ''
    ) -> Dict:
        """
        Отмена выполнения задачи

        Args:
            task_id: ID задачи
            user_id: ID пользователя
            reason: Причина отмены

        Returns:
            Dict: Результат операции
        """
        response = await self._request(
            'POST',
            f'/tasks/{task_id}/cancel',
            params={
                'user_id': user_id,
                'reason': reason
            }
        )
        return response.data

    async def complete_task(
            self,
            task_id: int,
            user_id: int,
            completion_note: str = '',
            attachments: Optional[List[Dict]] = None
    ) -> Dict:
        """
        Завершение задачи

        Args:
            task_id: ID задачи
            user_id: ID пользователя
            completion_note: Заметка о завершении
            attachments: Список вложений (опционально)

        Returns:
            Dict: Результат операции
        """
        data = {
            "completion_note": completion_note,
            "attachments": attachments or []
        }
        response = await self._request(
            'POST',
            f'/tasks/{task_id}/complete',
            json=data,
            params={'user_id': user_id}
        )
        return response.data

    async def get_completed_tasks(self) -> List[Dict]:
        """Получение завершенных задач"""
        response = await self._request('GET', '/tasks/completed')
        return response.data

    async def get_incomplete_tasks(self) -> List[Dict]:
        """Получение незавершенных задач"""
        response = await self._request('GET', '/tasks/incomplete')
        return response.data

    async def get_all_tasks(self) -> List[Dict]:
        """Получение всех задач"""
        response = await self._request('GET', '/tasks/all')
        return response.data

    async def get_tasks_by_status(self, status: str) -> List[Dict]:
        """
        Получение задач по статусу

        Args:
            status: Статус задач для фильтрации

        Returns:
            List[Dict]: Список задач с указанным статусом
        """
        response = await self._request('GET', f'/tasks/by-status/{status}')
        return response.data

    async def get_task_history(
            self,
            task_id: int
    ) -> List[Dict]:
        """
        Получение истории работы над задачей

        Args:
            task_id: ID задачи

        Returns:
            List[Dict]: История изменений задачи
        """
        try:
            response = await self._request('GET', f'/tasks/{task_id}/history')
            return response.data
        except APIError as e:
            if e.status_code == 404:
                return []
            raise

    async def get_users_by_type(
            self,
            user_type: Union[UserType, str]
    ) -> List[Dict]:
        """
        Получение списка пользователей определенного типа

        Args:
            user_type: Тип пользователя

        Returns:
            List[Dict]: Список пользователей
        """
        if isinstance(user_type, UserType):
            user_type = user_type.value

        response = await self._request('GET', f'/users/by-type/{user_type}')
        return response.data

    async def get_task(self, task_id: int) -> Optional[Dict]:
        """
        Получение информации о задаче по ID

        Args:
            task_id: ID задачи

        Returns:
            Dict: Информация о задаче или None если задача не найдена
        """
        try:
            response = await self._request('GET', f'/tasks/{task_id}/full')
            return response.data
        except APIError as e:
            if e.status_code == 404:
                return None
            raise

    async def update_task(
            self,
            task_id: int,
            status: Union[TaskStatus, str],
            completion_note: Optional[str] = None
    ) -> Dict:
        """
        Обновление статуса задачи

        Args:
            task_id: ID задачи
            status: Новый статус задачи
            completion_note: Примечание о выполнении (опционально)

        Returns:
            Dict: Обновленная информация о задаче
        """
        if isinstance(status, TaskStatus):
            status = status.value

        data = {
            "status": status,
            "completion_note": completion_note
        }

        response = await self._request('PUT', f'/tasks/{task_id}', json=data)
        return response.data

    async def get_task_attachments(self, task_id: int) -> List[Dict]:
        """
        Получение списка вложений задачи

        Args:
            task_id: ID задачи

        Returns:
            List[Dict]: Список вложений задачи
        """
        response = await self._request('GET', f'/attachments/task/{task_id}')
        return response.data

    async def take_task(self, task_id: int, user_id: int) -> Dict:
        """
        Взять задачу на выполнение

        Args:
            task_id: ID задачи
            user_id: ID пользователя, берущего задачу

        Returns:
            Dict: Результат операции
        """
        response = await self._request('POST', f'/tasks/{task_id}/take',
                                       params={'user_id': user_id})
        return response.data

    async def get_group_tasks(self, group_id: int) -> List[Dict]:
        """
        Получение списка задач группы

        Args:
            group_id: ID группы

        Returns:
            List[Dict]: Список задач группы
        """
        response = await self._request('GET', f'/tasks/group/{group_id}')
        return response.data
    async def create_task(
            self,
            task_message: str,
            created_by: int,
            group_id: int,
            priority: Optional[int] = None,
            due_date: Optional[datetime] = None
    ) -> Dict:
        """
        Создание новой задачи

        Args:
            task_message: Текст задачи
            created_by: ID создателя
            group_id: ID группы
            priority: Приоритет задачи (опционально)
            due_date: Срок выполнения (опционально)

        Returns:
            Dict: Информация о созданной задаче
        """
        data = {
            "task_message": task_message,
            "created_by": created_by,
            "group_id": group_id
        }

        if priority is not None:
            data["priority"] = priority
        if due_date is not None:
            data["due_date"] = due_date.isoformat()

        response = await self._request('POST', '/tasks/', json=data)
        return response.data

    async def get_my_tasks(
            self,
            user_id: int,
            status: Optional[Union[TaskStatus, str]] = None,
            page: int = 1,
            page_size: int = 50
    ) -> List[Dict]:
        """
        Получение списка задач пользователя

        Args:
            user_id: ID пользователя
            status: Статус задач для фильтрации
            page: Номер страницы
            page_size: Размер страницы

        Returns:
            List[Dict]: Список задач
        """
        params = {
            'user_id': str(user_id),
            'page': str(page),
            'page_size': str(page_size)
        }

        if status:
            if isinstance(status, TaskStatus):
                status = status.value
            params['status'] = status

        response = await self._request('GET', '/tasks/my', params=params)
        return response.data

    # Groups
    async def assign_group_to_creator(self, user_id: int, group_id: int) -> dict:
        """Назначение группы создателю"""
        return await self._request('POST', f'/users/{user_id}/groups/{group_id}')

    async def remove_group_from_creator(self, user_id: int, group_id: int) -> dict:
        """Удаление группы у создателя"""
        return await self._request('DELETE', f'/users/{user_id}/groups/{group_id}')

    async def get_creator_groups(self, user_id: int) -> List[dict]:
        """Получение списка групп создателя"""
        response = await self._request('GET', f'/users/{user_id}/groups')
        return response.data

    async def get_all_groups(self) -> List[dict]:
        """Получение списка всех групп"""
        response = await self._request('GET', '/groups/')
        return response.data

    async def get_active_groups(self) -> List[dict]:
        """Получение списка активных групп"""
        response = await self._request('GET', '/groups/active')
        return response.data

    async def get_group(self, group_id: int) -> Optional[dict]:
        """Получение информации о конкретной группе"""
        try:
            response = await self._request('GET', f'/groups/{group_id}')
            return response.data
        except Exception:
            return None

        # Tasks

    async def add_attachemnt(
            self,
            task_id: int,
            file_id: str,
            file_type: str,
            file_name: Optional[str] = "",
            local_path: Optional[str] = ""
    ) -> Dict:
        """
        Добавление вложения

        Args:
            task_id: ID задачи
            file_id: ID файла
            file_type: тип файла
            file_name: имя файла (опционально)
            local_path: локальный путь (опционально)

        Returns:
            Dict: Информация о созданной задаче
        """
        data = {
            "task_id": task_id,
            "file_id": file_id,
            "file_type": file_type,
            "file_name": file_name,
            "local_path": local_path

        }
        response = await self._request('POST', '/attachments/', json=data)
        return response.data

    async def create_group(self, group_id: int, title: str, is_active: bool = True) -> dict:
        """Добавление новой группы"""
        data = {
            "group_id": group_id,
            "title": title,
            "is_active": is_active
        }
        print("Отправляемые данные:", data)  # для отладки
        return await self._request('POST', '/groups/', json=data)

    async def update_group_status(self, group_id: int, is_active: bool) -> dict:
        """Изменение статуса группы"""
        return await self._request(
            'PUT',
            f'/groups/{group_id}/status',
            json={"is_active": is_active}
        )