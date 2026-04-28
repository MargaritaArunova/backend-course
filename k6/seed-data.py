#!/usr/bin/env python3
"""
Скрипт для автоматического заполнения REST-сервиса тестовыми данными.
Использует библиотеки requests и Faker для генерации реалистичных данных.
"""

import argparse
import requests
import sys
from faker import Faker
import random
from typing import List, Dict, Any
import time

# Инициализация Faker
fake = Faker()

# Настройки по умолчанию
DEFAULT_BASE_URL = 'http://localhost:8080'
DEFAULT_COUNT = 500

class DataSeeder:
    """Класс для заполнения базы данных тестовыми данными."""

    def __init__(self, base_url: str = DEFAULT_BASE_URL):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.created_users = []
        self.created_posts = []
        self.created_comments = []

    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Выполняет HTTP запрос с обработкой ошибок."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"❌ Ошибка при {method} {url}: {e}")
            if hasattr(e.response, 'text'):
                print(f"   Ответ сервера: {e.response.text}")
            raise

    def get_all_entities(self, endpoint: str) -> List[Dict[str, Any]]:
        """Получает все объекты по указанному эндпоинту."""
        try:
            response = self._make_request('GET', endpoint)
            return response.json()
        except Exception as e:
            print(f"⚠ Не удалось получить данные из {endpoint}: {e}")
            return []

    def delete_entity(self, endpoint: str, entity_id: int, parent_id: int = None) -> bool:
        """Удаляет объект по ID."""
        try:
            # Для комментариев используем /posts/{postId}/comments/{commentId}
            if endpoint == 'comments' and parent_id:
                self._make_request('DELETE', f"/posts/{parent_id}/comments/{entity_id}")
            else:
                self._make_request('DELETE', f"{endpoint}/{entity_id}")
            return True
        except Exception:
            return False

    def clear_endpoint(self, endpoint: str, include_related: bool = False):
        """Удаляет все объекты по указанному эндпоинту."""
        print(f"\n🗑️  Очистка данных для /{endpoint}...")

        # Определяем порядок очистки с учетом зависимостей
        if include_related:
            if endpoint == 'users':
                # Благодаря каскадному удалению в JPA, удалять связанные объекты не нужно
                # Они удалятся автоматически
                pass

        # Получаем все объекты
        entities = self.get_all_entities(endpoint)

        if not entities:
            print(f"   ℹ️  Нет данных для удаления в /{endpoint}")
            return

        deleted_count = 0
        failed_count = 0

        for entity in entities:
            entity_id = entity.get('id')
            if entity_id:
                # Для комментариев нужен postId
                parent_id = entity.get('postId') if endpoint == 'comments' else None
                if self.delete_entity(endpoint, entity_id, parent_id):
                    deleted_count += 1
                else:
                    failed_count += 1

        if deleted_count > 0:
            print(f"   ✓ Удалено: {deleted_count} объект(ов)")
        if failed_count > 0:
            print(f"   ⚠ Не удалось удалить: {failed_count} объект(ов)")

    def clear_all_data(self):
        """Удаляет все данные из базы данных в правильном порядке."""
        print("\n" + "="*80)
        print("ОЧИСТКА ВСЕХ ДАННЫХ".center(80))
        print("="*80)

        # Удаляем в порядке зависимостей: сначала зависимые данные, потом основные
        # Благодаря каскадному удалению в JPA, достаточно удалить только users
        # Все связанные posts, comments и likes удалятся автоматически
        self.clear_endpoint('users', include_related=True)

        print("\n" + "="*80)
        print("✓ ОЧИСТКА ЗАВЕРШЕНА".center(80))
        print("="*80)
        print()

    def create_user(self) -> Dict[str, Any]:
        """Создает пользователя с случайными данными."""
        user_data = {
            'nickname': fake.user_name() + str(random.randint(1000, 9999)),
            'email': fake.email()
        }

        try:
            response = self._make_request('POST', '/users', json=user_data)
            user = response.json()
            self.created_users.append(user)
            return user
        except Exception as e:
            print(f"⚠ Ошибка создания пользователя: {e}")
            return None

    def create_post(self, author_id: int) -> Dict[str, Any]:
        """Создает пост для указанного автора."""
        post_data = {
            'text': fake.text(max_nb_chars=500),
            'authorId': author_id
        }

        try:
            response = self._make_request('POST', '/posts', params=post_data)
            post = response.json()
            self.created_posts.append(post)
            return post
        except Exception as e:
            print(f"⚠ Ошибка создания поста: {e}")
            return None

    def create_comment(self, post_id: int, author_id: int) -> Dict[str, Any]:
        """Создает комментарий к посту."""
        comment_params = {
            'text': fake.sentence(),
            'authorId': author_id
        }

        try:
            response = self._make_request('POST', f'/posts/{post_id}/comments', params=comment_params)
            comment = response.json()
            self.created_comments.append(comment)
            return comment
        except Exception as e:
            print(f"⚠ Ошибка создания комментария: {e}")
            return None

    def like_post(self, post_id: int, user_id: int) -> bool:
        """Ставит лайк на пост."""
        try:
            self._make_request('POST', f'/posts/{post_id}/likes', params={'userId': user_id})
            return True
        except Exception:
            return False

    def seed_users(self, count: int):
        """Генерирует указанное количество пользователей."""
        print(f"\n👤 Создание {count} пользователей...")
        created = 0

        for i in range(count):
            if self.create_user():
                created += 1
                if (i + 1) % 50 == 0:
                    print(f"   Создано: {i + 1}/{count}")

        print(f"   ✓ Создано пользователей: {created}")

    def seed_posts(self, count: int):
        """Генерирует указанное количество постов."""
        if not self.created_users:
            print("⚠ Сначала нужно создать пользователей!")
            return

        print(f"\n📝 Создание {count} постов...")
        created = 0

        for i in range(count):
            author = random.choice(self.created_users)
            if self.create_post(author['id']):
                created += 1
                if (i + 1) % 50 == 0:
                    print(f"   Создано: {i + 1}/{count}")

        print(f"   ✓ Создано постов: {created}")

    def seed_comments(self, count: int):
        """Генерирует указанное количество комментариев."""
        if not self.created_posts or not self.created_users:
            print("⚠ Сначала нужно создать пользователей и посты!")
            return

        print(f"\n💬 Создание {count} комментариев...")
        created = 0

        for i in range(count):
            post = random.choice(self.created_posts)
            author = random.choice(self.created_users)
            if self.create_comment(post['id'], author['id']):
                created += 1
                if (i + 1) % 50 == 0:
                    print(f"   Создано: {i + 1}/{count}")

        print(f"   ✓ Создано комментариев: {created}")

    def seed_likes(self, count: int):
        """Генерирует указанное количество лайков."""
        if not self.created_posts or not self.created_users:
            print("⚠ Сначала нужно создать пользователей и посты!")
            return

        print(f"\n❤️  Создание {count} лайков...")
        created = 0
        failed = 0

        for i in range(count):
            post = random.choice(self.created_posts)
            user = random.choice(self.created_users)

            if self.like_post(post['id'], user['id']):
                created += 1
            else:
                failed += 1

            if (i + 1) % 50 == 0:
                print(f"   Обработано: {i + 1}/{count}")

        print(f"   ✓ Создано лайков: {created}")
        if failed > 0:
            print(f"   ⚠ Дубликатов пропущено: {failed}")

    def create_all_entities(self, user_count: int):
        """Создает все сущности: пользователей, посты, комментарии и лайки."""
        print("\n" + "="*80)
        print("СОЗДАНИЕ ВСЕХ СУЩНОСТЕЙ".center(80))
        print("="*80)

        # Создаем пользователей
        self.seed_users(user_count)

        # Создаем посты (в среднем 2-3 поста на пользователя)
        post_count = int(user_count * 2.5)
        self.seed_posts(post_count)

        # Создаем комментарии (в среднем 1-2 комментария на пост)
        comment_count = int(post_count * 1.5)
        self.seed_comments(comment_count)

        # Создаем лайки (в среднем 3-4 лайка на пост)
        like_count = int(post_count * 3.5)
        self.seed_likes(like_count)

        print("\n" + "="*80)
        print("✓ СОЗДАНИЕ ЗАВЕРШЕНО".center(80))
        print("="*80)
        print(f"\nСоздано:")
        print(f"  • Пользователей: {len(self.created_users)}")
        print(f"  • Постов: {len(self.created_posts)}")
        print(f"  • Комментариев: {len(self.created_comments)}")
        print()

    def seed_full_dataset(self, user_count: int):
        """Создает полный набор тестовых данных. (Алиас для create_all_entities)"""
        self.create_all_entities(user_count)

def main():
    """Основная функция."""
    parser = argparse.ArgumentParser(
        description='Заполнение REST-сервиса тестовыми данными',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  # Создать все сущности (пользователи, посты, комментарии, лайки)
  python3 seed-data.py --create-all --count 500

  # Очистить все данные
  python3 seed-data.py --clear-all

  # Создать 100 пользователей и связанные данные
  python3 seed-data.py --endpoint users --count 100

  # Очистить только посты
  python3 seed-data.py --endpoint posts --clear

  # Очистить и создать заново все данные
  python3 seed-data.py --clear-all --create-all --count 500
        """
    )

    parser.add_argument(
        '--count',
        type=int,
        default=DEFAULT_COUNT,
        help=f'Количество создаваемых объектов (по умолчанию: {DEFAULT_COUNT})'
    )

    parser.add_argument(
        '--endpoint',
        type=str,
        choices=['users', 'posts', 'comments', 'likes'],
        help='API-эндпоинт для заполнения данными'
    )

    parser.add_argument(
        '--clear',
        action='store_true',
        help='Удалить все существующие данные для указанного эндпоинта'
    )

    parser.add_argument(
        '--clear-all',
        action='store_true',
        help='Удалить все данные из базы данных'
    )

    parser.add_argument(
        '--create-all',
        action='store_true',
        help='Создать все сущности (пользователи, посты, комментарии, лайки)'
    )

    parser.add_argument(
        '--base-url',
        type=str,
        default=DEFAULT_BASE_URL,
        help=f'Базовый URL API (по умолчанию: {DEFAULT_BASE_URL})'
    )

    args = parser.parse_args()

    # Проверяем валидность аргументов
    if not args.clear_all and not args.create_all and not args.endpoint:
        parser.error("Требуется указать --endpoint, --clear-all или --create-all")

    # Проверяем доступность сервиса
    try:
        response = requests.get(f"{args.base_url}/users", timeout=5)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"❌ Не удалось подключиться к {args.base_url}")
        print(f"   Ошибка: {e}")
        print("\n💡 Убедитесь, что сервис запущен!")
        sys.exit(1)

    seeder = DataSeeder(args.base_url)

    # Очистка всех данных
    if args.clear_all:
        seeder.clear_all_data()
        # Если указан только --clear-all без --create-all, завершаем
        if not args.create_all:
            return

    # Создание всех сущностей
    if args.create_all:
        seeder.create_all_entities(args.count)
        return

    # Очистка отдельного эндпоинта
    if args.clear and args.endpoint:
        seeder.clear_endpoint(args.endpoint, include_related=True)
        return

    # Заполнение данных для отдельного эндпоинта
    if args.endpoint == 'users':
        # Для users создаем полный набор данных
        seeder.create_all_entities(args.count)

    elif args.endpoint == 'posts':
        # Загружаем существующих пользователей
        seeder.created_users = seeder.get_all_entities('users')
        if not seeder.created_users:
            print("❌ Нет пользователей! Сначала создайте пользователей.")
            sys.exit(1)
        seeder.seed_posts(args.count)

    elif args.endpoint == 'comments':
        # Загружаем существующих пользователей и посты
        seeder.created_users = seeder.get_all_entities('users')
        seeder.created_posts = seeder.get_all_entities('posts')
        if not seeder.created_users or not seeder.created_posts:
            print("❌ Нет пользователей или постов! Сначала создайте их.")
            sys.exit(1)
        seeder.seed_comments(args.count)

    elif args.endpoint == 'likes':
        # Загружаем существующих пользователей и посты
        seeder.created_users = seeder.get_all_entities('users')
        seeder.created_posts = seeder.get_all_entities('posts')
        if not seeder.created_users or not seeder.created_posts:
            print("❌ Нет пользователей или постов! Сначала создайте их.")
            sys.exit(1)
        seeder.seed_likes(args.count)

if __name__ == '__main__':
    main()
