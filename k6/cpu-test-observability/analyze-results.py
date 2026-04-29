#!/usr/bin/env python3
"""
Скрипт для анализа и визуализации результатов observability тестирования.
Анализирует метрики K6 и статистику из логов приложения.
"""

import json
import os
import sys
import re
from pathlib import Path
from typing import Dict, List

try:
    import matplotlib.pyplot as plt
    import pandas as pd
except ImportError:
    print("Требуется установить зависимости: pip install matplotlib pandas")
    sys.exit(1)


def parse_k6_json(file_path: str) -> Dict:
    """Парсит JSON файл с результатами k6."""
    with open(file_path, 'r') as f:
        metrics = {
            'controller_response_time': [],
            'repository_response_time': [],
            'self_like_stats_response_time': [],
            'observability_stats_response_time': [],
            'http_req_duration': []
        }

        for line in f:
            try:
                data = json.loads(line)

                if data.get('type') == 'Point':
                    metric_name = data.get('metric')
                    value = data.get('data', {}).get('value')

                    if metric_name in metrics and value is not None:
                        metrics[metric_name].append(value)

            except json.JSONDecodeError:
                continue

    # Вычисляем статистику
    result = {}
    for metric_name, values in metrics.items():
        if values:
            values_sorted = sorted(values)
            n = len(values_sorted)
            result[metric_name] = {
                'mean': sum(values) / n,
                'p50': values_sorted[int(n * 0.50)],
                'p95': values_sorted[int(n * 0.95)],
                'p99': values_sorted[int(n * 0.99)],
                'max': max(values),
                'min': min(values),
                'count': n
            }
        else:
            result[metric_name] = {
                'mean': 0, 'p50': 0, 'p95': 0, 'p99': 0, 'max': 0, 'min': 0, 'count': 0
            }

    return result


def parse_observability_stats(log_file: str) -> Dict:
    """Парсит статистику observability из логов."""
    stats_file = log_file.replace('.log', '_stats.txt')

    if not os.path.exists(stats_file):
        return {}

    with open(stats_file, 'r') as f:
        content = f.read()

    # Парсим статистику для разных временных окон
    windows = ['SHORT', 'MEDIUM', 'LONG']
    result = {}

    for window in windows:
        window_pattern = rf'--- {window} window \((\d+) seconds\) ---'
        match = re.search(window_pattern, content)

        if not match:
            continue

        window_seconds = int(match.group(1))
        window_key = window.lower()

        # Находим секцию для этого окна
        start_idx = match.end()
        next_window_match = re.search(r'--- \w+ window', content[start_idx:])
        end_idx = start_idx + next_window_match.start() if next_window_match else len(content)

        window_content = content[start_idx:end_idx]

        # Парсим метрики из этой секции
        # Формат: Controller.PostController.getAll: count=123, avg=45.67ms, min=12ms, max=89ms
        metrics_pattern = r'(\S+): count=(\d+), avg=([\d.]+)ms, min=(\d+)ms, max=(\d+)ms'
        metrics = {}

        for match in re.finditer(metrics_pattern, window_content):
            method_name = match.group(1)
            count = int(match.group(2))
            avg = float(match.group(3))
            min_val = int(match.group(4))
            max_val = int(match.group(5))

            metrics[method_name] = {
                'count': count,
                'avg': avg,
                'min': min_val,
                'max': max_val
            }

        if metrics:
            result[window_key] = {
                'window_seconds': window_seconds,
                'metrics': metrics
            }

    return result


def load_results(results_dir: str) -> pd.DataFrame:
    """Загружает все результаты тестов и формирует DataFrame."""
    data = []

    results_path = Path(results_dir)
    for json_file in results_path.glob('cpu_*.json'):
        # Извлекаем CPU из имени файла (cpu_0.5.json или cpu_1.0.json)
        try:
            cpu_str = json_file.stem.replace('cpu_', '')
            cpu = float(cpu_str)

            # Парсим метрики K6
            k6_metrics = parse_k6_json(str(json_file))

            # Парсим observability статистику из логов
            log_file = results_path / 'logs' / f'{json_file.stem}.log'
            obs_stats = parse_observability_stats(str(log_file)) if log_file.exists() else {}

            # Формируем строку данных
            row = {
                'cpu': cpu,
                'controller_p95': k6_metrics.get('controller_response_time', {}).get('p95', 0),
                'controller_mean': k6_metrics.get('controller_response_time', {}).get('mean', 0),
                'repository_p95': k6_metrics.get('repository_response_time', {}).get('p95', 0),
                'repository_mean': k6_metrics.get('repository_response_time', {}).get('mean', 0),
                'self_like_stats_p95': k6_metrics.get('self_like_stats_response_time', {}).get('p95', 0),
                'self_like_stats_mean': k6_metrics.get('self_like_stats_response_time', {}).get('mean', 0),
                'observability_stats_p95': k6_metrics.get('observability_stats_response_time', {}).get('p95', 0),
                'observability_stats_mean': k6_metrics.get('observability_stats_response_time', {}).get('mean', 0),
                'overall_p95': k6_metrics.get('http_req_duration', {}).get('p95', 0),
                'overall_mean': k6_metrics.get('http_req_duration', {}).get('mean', 0),
            }

            # Добавляем статистику observability (для среднего окна)
            if 'medium' in obs_stats:
                row['obs_internal_stats'] = obs_stats['medium']

            data.append(row)

        except (ValueError, IndexError) as e:
            print(f"Пропуск файла {json_file}: {e}")
            continue

    if not data:
        print("Не найдено данных для анализа")
        return pd.DataFrame()

    df = pd.DataFrame(data)
    df = df.sort_values('cpu')

    return df


def plot_k6_results(df: pd.DataFrame, output_dir: str):
    """Строит графики K6 метрик."""
    if df.empty:
        print("Нет данных для построения графиков")
        return

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    plt.style.use('seaborn-v0_8-darkgrid')

    # График 1: P95 время отклика по типам операций
    fig, ax = plt.subplots(figsize=(12, 6))

    metrics = [
        ('controller_p95', 'Controller Operations'),
        ('repository_p95', 'Repository Operations'),
        ('self_like_stats_p95', 'Self-Like Stats'),
        ('observability_stats_p95', 'Observability Stats'),
    ]

    for metric, label in metrics:
        if metric in df.columns and df[metric].sum() > 0:
            ax.plot(df['cpu'], df[metric], marker='o', linewidth=2, label=label, markersize=8)

    ax.set_xlabel('CPU cores', fontsize=12)
    ax.set_ylabel('Response Time P95 (ms)', fontsize=12)
    ax.set_title('Response Time P95 vs CPU Cores (Different Operation Types)', fontsize=14, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(f'{output_dir}/cpu_vs_operations_p95.png', dpi=300)
    print(f"График сохранен: {output_dir}/cpu_vs_operations_p95.png")
    plt.close()

    # График 2: Среднее время отклика
    fig, ax = plt.subplots(figsize=(12, 6))

    metrics_mean = [
        ('controller_mean', 'Controller Operations'),
        ('repository_mean', 'Repository Operations'),
        ('self_like_stats_mean', 'Self-Like Stats'),
        ('observability_stats_mean', 'Observability Stats'),
    ]

    for metric, label in metrics_mean:
        if metric in df.columns and df[metric].sum() > 0:
            ax.plot(df['cpu'], df[metric], marker='s', linewidth=2, label=label, markersize=8)

    ax.set_xlabel('CPU cores', fontsize=12)
    ax.set_ylabel('Mean Response Time (ms)', fontsize=12)
    ax.set_title('Mean Response Time vs CPU Cores (Different Operation Types)', fontsize=14, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(f'{output_dir}/cpu_vs_operations_mean.png', dpi=300)
    print(f"График сохранен: {output_dir}/cpu_vs_operations_mean.png")
    plt.close()

    # График 3: Общий P95
    fig, ax = plt.subplots(figsize=(10, 6))

    ax.plot(df['cpu'], df['overall_p95'], marker='o', linewidth=3, color='red', markersize=10, label='Overall P95')
    ax.plot(df['cpu'], df['overall_mean'], marker='s', linewidth=3, color='blue', markersize=10, label='Overall Mean')

    ax.set_xlabel('CPU cores', fontsize=12)
    ax.set_ylabel('Response Time (ms)', fontsize=12)
    ax.set_title('Overall Response Time vs CPU Cores', fontsize=14, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(f'{output_dir}/cpu_vs_overall_response.png', dpi=300)
    print(f"График сохранен: {output_dir}/cpu_vs_overall_response.png")
    plt.close()


def print_summary(df: pd.DataFrame):
    """Выводит сводную таблицу результатов."""
    if df.empty:
        return

    print("\n" + "="*100)
    print("СВОДНАЯ СТАТИСТИКА K6 МЕТРИК")
    print("="*100)

    print(f"\n{'CPU':>6} | {'Overall P95':>12} | {'Controller P95':>14} | {'Repository P95':>14} | {'Self-Like P95':>13}")
    print("-" * 100)

    for _, row in df.iterrows():
        print(f"{row['cpu']:>6.1f} | {row['overall_p95']:>10.2f} ms | "
              f"{row['controller_p95']:>12.2f} ms | {row['repository_p95']:>12.2f} ms | "
              f"{row['self_like_stats_p95']:>11.2f} ms")


def print_observability_stats(results_dir: str):
    """Выводит статистику observability из логов."""
    logs_dir = Path(results_dir) / 'logs'

    if not logs_dir.exists():
        return

    print("\n" + "="*100)
    print("OBSERVABILITY СТАТИСТИКА ИЗ ЛОГОВ")
    print("="*100)

    for stats_file in sorted(logs_dir.glob('cpu_*_stats.txt')):
        cpu = stats_file.stem.replace('cpu_', '').replace('_stats', '')

        print(f"\n>>> CPU: {cpu} cores")
        print("-" * 100)

        with open(stats_file, 'r') as f:
            content = f.read()
            # Выводим первые 100 строк статистики
            lines = content.split('\n')[:100]
            print('\n'.join(lines))


def main():
    """Основная функция."""
    results_dir = './results'
    output_dir = './results/graphs'

    if not os.path.exists(results_dir):
        print(f"Директория с результатами не найдена: {results_dir}")
        sys.exit(1)

    print("Загрузка результатов тестов...")
    df = load_results(results_dir)

    if df.empty:
        print("Нет данных для анализа")
        sys.exit(1)

    print(f"Загружено {len(df)} результатов тестов")

    # Сохраняем DataFrame в CSV
    csv_path = f'{output_dir}/statistics.csv'
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    df.to_csv(csv_path, index=False)
    print(f"Статистика сохранена: {csv_path}")

    # Выводим сводную статистику
    print_summary(df)

    # Выводим observability статистику
    print_observability_stats(results_dir)

    # Строим графики
    print("\nПостроение графиков...")
    plot_k6_results(df, output_dir)

    print("\n" + "="*100)
    print("Анализ завершен!")
    print("="*100)


if __name__ == '__main__':
    main()