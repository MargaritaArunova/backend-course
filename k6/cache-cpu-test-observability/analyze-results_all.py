#!/usr/bin/env python3
"""
Скрипт для анализа и визуализации результатов CPU тестирования.
Строит графики зависимости времени отклика от количества CPU.
"""

import json
import csv
import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple

try:
    import matplotlib.pyplot as plt
    import pandas as pd
except ImportError:
    print("Требуется установить зависимости: pip install matplotlib pandas")
    sys.exit(1)


def parse_k6_json(file_path: str) -> Dict:
    """Парсит JSON файл с результатами k6."""
    with open(file_path, 'r') as f:
        # k6 выводит JSON построчно
        metrics = {
            'read_response_time': [],
            'write_response_time': [],
            'http_req_duration': []
        }

        for line in f:
            try:
                data = json.loads(line)

                # Извлекаем метрики
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
                'count': n
            }
        else:
            result[metric_name] = {
                'mean': 0, 'p50': 0, 'p95': 0, 'p99': 0, 'max': 0, 'count': 0
            }

    return result


def load_results(results_dir: str) -> pd.DataFrame:
    """Загружает все результаты тестов и формирует DataFrame."""
    data = []

    results_path = Path(results_dir)
    for json_file in results_path.glob('cpu_*.json'):
        # Извлекаем CPU и ratio из имени файла
        # Формат: cpu_0.5_ratio_5_95.json
        parts = json_file.stem.split('_')
        try:
            cpu_idx = parts.index('cpu') + 1
            ratio_idx = parts.index('ratio') + 1

            cpu = float(parts[cpu_idx])
            ratio_label = '_'.join(parts[ratio_idx:])

            # Парсим метрики
            metrics = parse_k6_json(str(json_file))

            # Добавляем данные
            data.append({
                'cpu': cpu,
                'ratio_label': ratio_label,
                'read_p95': metrics.get('read_response_time', {}).get('p95', 0),
                'write_p95': metrics.get('write_response_time', {}).get('p95', 0),
                'overall_p95': metrics.get('http_req_duration', {}).get('p95', 0),
                'read_mean': metrics.get('read_response_time', {}).get('mean', 0),
                'write_mean': metrics.get('write_response_time', {}).get('mean', 0),
                'overall_mean': metrics.get('http_req_duration', {}).get('mean', 0),
            })

        except (ValueError, IndexError) as e:
            print(f"Пропуск файла {json_file}: {e}")
            continue

    if not data:
        print("Не найдено данных для анализа")
        return pd.DataFrame()

    df = pd.DataFrame(data)
    df = df.sort_values(['ratio_label', 'cpu'])

    return df


def plot_results(df: pd.DataFrame, output_dir: str):
    """Строит графики зависимости времени отклика от CPU."""
    if df.empty:
        print("Нет данных для построения графиков")
        return

    # Создаем директорию для графиков
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Настройка стилей
    plt.style.use('seaborn-v0_8-darkgrid')

    # График 1: P95 время отклика для разных соотношений
    fig, ax = plt.subplots(figsize=(12, 6))

    for ratio_label in df['ratio_label'].unique():
        ratio_data = df[df['ratio_label'] == ratio_label]
        ax.plot(
            ratio_data['cpu'],
            ratio_data['overall_p95'],
            marker='o',
            linewidth=2,
            label=f'Write/Read: {ratio_label.replace("_", "/")}',
            markersize=8
        )

    ax.set_xlabel('CPU cores', fontsize=12)
    ax.set_ylabel('Response Time P95 (ms)', fontsize=12)
    ax.set_title('Response Time P95 vs CPU Cores (Different Write/Read Ratios)', fontsize=14, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(f'{output_dir}/cpu_vs_response_time_p95.png', dpi=300)
    print(f"График сохранен: {output_dir}/cpu_vs_response_time_p95.png")
    plt.close()

    # График 2: Среднее время отклика
    fig, ax = plt.subplots(figsize=(12, 6))

    for ratio_label in df['ratio_label'].unique():
        ratio_data = df[df['ratio_label'] == ratio_label]
        ax.plot(
            ratio_data['cpu'],
            ratio_data['overall_mean'],
            marker='s',
            linewidth=2,
            label=f'Write/Read: {ratio_label.replace("_", "/")}',
            markersize=8
        )

    ax.set_xlabel('CPU cores', fontsize=12)
    ax.set_ylabel('Mean Response Time (ms)', fontsize=12)
    ax.set_title('Mean Response Time vs CPU Cores (Different Write/Read Ratios)', fontsize=14, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(f'{output_dir}/cpu_vs_response_time_mean.png', dpi=300)
    print(f"График сохранен: {output_dir}/cpu_vs_response_time_mean.png")
    plt.close()

    # График 3: Сравнение read vs write для каждого соотношения
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    for idx, ratio_label in enumerate(sorted(df['ratio_label'].unique())):
        ratio_data = df[df['ratio_label'] == ratio_label]

        axes[idx].plot(
            ratio_data['cpu'],
            ratio_data['read_p95'],
            marker='o',
            linewidth=2,
            label='Read P95',
            color='blue',
            markersize=8
        )

        axes[idx].plot(
            ratio_data['cpu'],
            ratio_data['write_p95'],
            marker='s',
            linewidth=2,
            label='Write P95',
            color='red',
            markersize=8
        )

        axes[idx].set_xlabel('CPU cores', fontsize=10)
        axes[idx].set_ylabel('Response Time P95 (ms)', fontsize=10)
        axes[idx].set_title(f'Write/Read: {ratio_label.replace("_", "/")}', fontsize=12, fontweight='bold')
        axes[idx].legend(fontsize=9)
        axes[idx].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(f'{output_dir}/cpu_vs_read_write_comparison.png', dpi=300)
    print(f"График сохранен: {output_dir}/cpu_vs_read_write_comparison.png")
    plt.close()

    # Сохраняем статистику в CSV
    csv_path = f'{output_dir}/statistics.csv'
    df.to_csv(csv_path, index=False)
    print(f"Статистика сохранена: {csv_path}")


def print_summary(df: pd.DataFrame):
    """Выводит сводную таблицу результатов."""
    if df.empty:
        return

    print("\n" + "="*80)
    print("СВОДНАЯ СТАТИСТИКА")
    print("="*80)

    for ratio_label in sorted(df['ratio_label'].unique()):
        print(f"\nWrite/Read: {ratio_label.replace('_', '/')}")
        print("-" * 60)
        ratio_data = df[df['ratio_label'] == ratio_label]

        print(f"{'CPU':>6} | {'Overall P95':>12} | {'Read P95':>10} | {'Write P95':>10}")
        print("-" * 60)

        for _, row in ratio_data.iterrows():
            print(f"{row['cpu']:>6.1f} | {row['overall_p95']:>10.2f} ms | "
                  f"{row['read_p95']:>8.2f} ms | {row['write_p95']:>8.2f} ms")


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

    # Выводим сводную статистику
    print_summary(df)

    # Строим графики
    print("\nПостроение графиков...")
    plot_results(df, output_dir)

    print("\n" + "="*80)
    print("Анализ завершен!")
    print("="*80)


if __name__ == '__main__':
    main()