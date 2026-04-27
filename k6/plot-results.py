#!/usr/bin/env python3
"""
Скрипт для генерации графиков результатов k6 тестирования.
Строит график зависимости среднего времени отклика от количества VUs.
"""

import json
import os
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

def load_results(results_dir='k6/results'):
    """Загружает результаты тестов из JSON файлов."""
    results = []
    results_path = Path(results_dir)

    if not results_path.exists():
        print(f"❌ Директория с результатами не найдена: {results_dir}")
        return results

    # Ищем файлы result_*vus.json
    result_files = sorted(results_path.glob('result_*vus.json'))

    if not result_files:
        print(f"❌ Файлы с результатами не найдены в {results_dir}")
        print("   Убедитесь, что вы запустили тесты командой: ./k6/run-tests.sh")
        return results

    for file_path in result_files:
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                results.append(data)
                print(f"✓ Загружен файл: {file_path.name}")
        except Exception as e:
            print(f"⚠ Ошибка при чтении {file_path.name}: {e}")

    return results

def plot_response_time_vs_load(results, output_file='k6/results/response_time_vs_load.png'):
    """Строит график зависимости времени отклика от нагрузки."""
    if not results:
        print("❌ Нет данных для построения графика")
        return

    # Сортируем результаты по количеству VUs
    results = sorted(results, key=lambda x: x['vus'])

    # Извлекаем данные
    vus = [r['vus'] for r in results]
    avg_durations = [r['avg_duration'] for r in results]
    p95_durations = [r['p95_duration'] for r in results]

    # Создаем график
    plt.figure(figsize=(12, 8))

    # График средних значений
    plt.subplot(2, 1, 1)
    plt.plot(vus, avg_durations, marker='o', linewidth=2, markersize=8, color='#2E86AB', label='Avg Response Time')
    plt.fill_between(vus, 0, avg_durations, alpha=0.3, color='#2E86AB')
    plt.xlabel('Virtual Users (VUs)', fontsize=12, fontweight='bold')
    plt.ylabel('Avg Response Time (ms)', fontsize=12, fontweight='bold')
    plt.title('Average Response Time vs Load', fontsize=14, fontweight='bold', pad=20)
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.legend(fontsize=10)

    # Добавляем значения на точки
    for i, (x, y) in enumerate(zip(vus, avg_durations)):
        plt.annotate(f'{y:.2f}ms',
                    xy=(x, y),
                    xytext=(0, 10),
                    textcoords='offset points',
                    ha='center',
                    fontsize=9,
                    bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.7))

    # График P95
    plt.subplot(2, 1, 2)
    plt.plot(vus, p95_durations, marker='s', linewidth=2, markersize=8, color='#F24236', label='P95 Response Time')
    plt.fill_between(vus, 0, p95_durations, alpha=0.3, color='#F24236')
    plt.xlabel('Virtual Users (VUs)', fontsize=12, fontweight='bold')
    plt.ylabel('P95 Response Time (ms)', fontsize=12, fontweight='bold')
    plt.title('P95 Response Time vs Load', fontsize=14, fontweight='bold', pad=20)
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.legend(fontsize=10)

    # Добавляем значения на точки
    for i, (x, y) in enumerate(zip(vus, p95_durations)):
        plt.annotate(f'{y:.2f}ms',
                    xy=(x, y),
                    xytext=(0, 10),
                    textcoords='offset points',
                    ha='center',
                    fontsize=9,
                    bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.7))

    plt.tight_layout()

    # Сохраняем график
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\n✓ График сохранен: {output_file}")

    # Показываем график
    plt.show()

def plot_combined_metrics(results, output_file='k6/results/combined_metrics.png'):
    """Строит комбинированный график всех метрик."""
    if not results:
        print("❌ Нет данных для построения графика")
        return

    results = sorted(results, key=lambda x: x['vus'])

    vus = [r['vus'] for r in results]
    avg_durations = [r['avg_duration'] for r in results]
    min_durations = [r['min_duration'] for r in results]
    max_durations = [r['max_duration'] for r in results]
    p95_durations = [r['p95_duration'] for r in results]

    plt.figure(figsize=(14, 8))

    plt.plot(vus, avg_durations, marker='o', linewidth=2, markersize=8, label='Avg', color='#2E86AB')
    plt.plot(vus, p95_durations, marker='s', linewidth=2, markersize=8, label='P95', color='#F24236')
    plt.plot(vus, min_durations, marker='^', linewidth=1.5, markersize=6, label='Min', color='#06A77D', linestyle='--')
    plt.plot(vus, max_durations, marker='v', linewidth=1.5, markersize=6, label='Max', color='#F6AE2D', linestyle='--')

    plt.xlabel('Virtual Users (VUs)', fontsize=12, fontweight='bold')
    plt.ylabel('Response Time (ms)', fontsize=12, fontweight='bold')
    plt.title('Response Time Metrics vs Load', fontsize=14, fontweight='bold', pad=20)
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.legend(fontsize=11)

    # Сохраняем график
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ График сохранен: {output_file}")

    plt.show()

def print_summary_table(results):
    """Выводит таблицу с результатами."""
    if not results:
        return

    results = sorted(results, key=lambda x: x['vus'])

    print("\n" + "="*80)
    print("SUMMARY TABLE".center(80))
    print("="*80)
    print(f"{'VUs':<10} {'Avg (ms)':<15} {'P95 (ms)':<15} {'Min (ms)':<15} {'Max (ms)':<15}")
    print("-"*80)

    for r in results:
        print(f"{r['vus']:<10} "
              f"{r['avg_duration']:<15.2f} "
              f"{r['p95_duration']:<15.2f} "
              f"{r['min_duration']:<15.2f} "
              f"{r['max_duration']:<15.2f}")

    print("="*80 + "\n")

def main():
    """Основная функция."""
    print("\n" + "="*80)
    print("K6 Load Test Results - Chart Generator".center(80))
    print("="*80 + "\n")

    # Загружаем результаты
    results = load_results()

    if not results:
        print("\n⚠ Запустите сначала тесты командой: ./k6/run-tests.sh")
        return

    print(f"\n✓ Загружено результатов: {len(results)}")

    # Выводим таблицу
    print_summary_table(results)

    # Строим графики
    print("Генерация графиков...")
    plot_response_time_vs_load(results)
    plot_combined_metrics(results)

    print("\n✓ Все графики успешно созданы!")
    print("="*80 + "\n")

if __name__ == '__main__':
    main()
