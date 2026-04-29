import http from 'k6/http';
import { check, sleep } from 'k6';
import { Counter } from 'k6/metrics';

// Настраиваемые параметры
const BASE_URL = __ENV.BASE_URL || 'http://localhost:8080';
const POST_USERS_RATIO = parseFloat(__ENV.POST_USERS_RATIO || '0.5'); // По умолчанию 50%
const GET_STATS_RATIO = 1 - POST_USERS_RATIO;

// Метрики
const postUsersCounter = new Counter('post_users_requests');
const getStatsCounter = new Counter('get_stats_requests');

// Опции для теста (можно переопределить через --vus и --duration)
export const options = {
    vus: parseInt(__ENV.VUS || '10'),
    duration: __ENV.DURATION || '30s',
    thresholds: {
        http_req_duration: ['p(95)<500'], // 95% запросов должны быть быстрее 500ms
        http_req_failed: ['rate<0.1'], // Менее 10% ошибок
    },
};

// Генератор случайных данных
function generateUser() {
    const random = Math.random().toString(36).substring(7);
    const timestamp = Date.now();
    return {
        nickname: `user_${random}_${timestamp}`,
        email: `${random}_${timestamp}@test.com`
    };
}

export default function () {
    // TODO: разделить на два пула, убрать random
    const randomValue = Math.random();

    if (randomValue < POST_USERS_RATIO) {
        // POST /users - Создание пользователя
        const userData = generateUser();
        const postResponse = http.post(
            `${BASE_URL}/users`,
            JSON.stringify(userData),
            {
                headers: { 'Content-Type': 'application/json' },
                tags: { name: 'CreateUser' }
            }
        );

        check(postResponse, {
            'POST /users status 200': (r) => r.status === 200,
            'POST /users response has id': (r) => {
                try {
                    const body = JSON.parse(r.body);
                    return body.id !== undefined;
                } catch (e) {
                    return false;
                }
            }
        });

        postUsersCounter.add(1);
    } else {
        // GET /statistics/self-likes - Получение статистики
        const getResponse = http.get(
            `${BASE_URL}/statistics/self-likes`,
            {
                tags: { name: 'GetSelfLikes' }
            }
        );

        check(getResponse, {
            'GET /statistics/self-likes status 200': (r) => r.status === 200,
            'GET /statistics/self-likes response is array': (r) => {
                try {
                    const body = JSON.parse(r.body);
                    return Array.isArray(body);
                } catch (e) {
                    return false;
                }
            }
        });

        getStatsCounter.add(1);
    }

    // Небольшая пауза между запросами для имитации реального поведения
    sleep(0.1);
}

// Функция для отображения результатов в конце теста
export function handleSummary(data) {
    const avgDuration = data.metrics.http_req_duration.values.avg;
    const p95Duration = data.metrics.http_req_duration.values['p(95)'];
    const maxDuration = data.metrics.http_req_duration.values.max;
    const minDuration = data.metrics.http_req_duration.values.min;
    const vus = options.vus;

    console.log(`\n=== Test Summary ===`);
    console.log(`VUs: ${vus}`);
    console.log(`Avg Response Time: ${avgDuration.toFixed(2)} ms`);
    console.log(`P95 Response Time: ${p95Duration.toFixed(2)} ms`);
    console.log(`Min Response Time: ${minDuration.toFixed(2)} ms`);
    console.log(`Max Response Time: ${maxDuration.toFixed(2)} ms`);

    return {
        'stdout': JSON.stringify(data, null, 2),
        [`k6/results/result_${vus}vus.json`]: JSON.stringify({
            vus: vus,
            avg_duration: avgDuration,
            p95_duration: p95Duration,
            max_duration: maxDuration,
            min_duration: minDuration,
            total_requests: data.metrics.http_reqs.values.count,
            failed_requests: data.metrics.http_req_failed.values.passes || 0
        }, null, 2)
    };
}
