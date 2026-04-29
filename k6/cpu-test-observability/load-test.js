import http from 'k6/http';
import { check, sleep } from 'k6';
import { Trend } from 'k6/metrics';

// Кастомные метрики для отслеживания времени отклика различных операций
const controllerResponseTime = new Trend('controller_response_time');
const repositoryResponseTime = new Trend('repository_response_time');
const selfLikeStatsResponseTime = new Trend('self_like_stats_response_time');
const observabilityStatsResponseTime = new Trend('observability_stats_response_time');

// Параметры теста
const BASE_URL = __ENV.BASE_URL || 'http://localhost:8080';
const VUS = parseInt(__ENV.VUS || '50'); // Количество виртуальных пользователей
const DURATION = __ENV.DURATION || '5m'; // Длительность теста

export const options = {
    scenarios: {
        constant_load: {
            executor: 'constant-vus',
            vus: VUS,
            duration: DURATION,
        },
    },
   //thresholds: {
   //    http_req_failed: ['rate<0.1'], // менее 10% ошибок
   //},
};

// Кэш для пользователей и постов
let userIds = [];
let postIds = [];

export function setup() {
    console.log(`Starting observability test with VUS=${VUS}, DURATION=${DURATION}`);

    // Предзаполняем базу пользователями и постами
    const initialUsers = 100;
    const postsPerUser = 2;

    console.log(`Creating ${initialUsers} initial users...`);
    for (let i = 0; i < initialUsers; i++) {
        const res = http.post(`${BASE_URL}/users`, JSON.stringify({
            nickname: `setup_user_${i}_${Date.now()}`,
            email: `setup_user_${i}_${Date.now()}@test.com`
        }), {
            headers: { 'Content-Type': 'application/json' },
        });

        if (res.status === 200 || res.status === 201) {
            const user = JSON.parse(res.body);
            userIds.push(user.id);
        }
    }

    console.log(`Creating posts for users...`);
    for (let userId of userIds) {
        for (let j = 0; j < postsPerUser; j++) {
            const res = http.post(`${BASE_URL}/posts?authorId=${userId}&text=Test post ${j}`, null, {
                headers: { 'Content-Type': 'application/json' },
            });

            if (res.status === 200 || res.status === 201) {
                const post = JSON.parse(res.body);
                postIds.push(post.id);
            }
        }
    }

    console.log(`Setup complete: ${userIds.length} users, ${postIds.length} posts`);

    return { userIds, postIds };
}

export default function(data) {
    // Используем данные из setup
    if (data.userIds) userIds = data.userIds;
    if (data.postIds) postIds = data.postIds;

    // Случайный выбор операции
    const operation = Math.random();

    if (operation < 0.3) {
        // 30% - Операции с контроллерами (чтение)
        performControllerOperation();
    } else if (operation < 0.5) {
        // 20% - Операции с контроллерами (запись)
        performControllerWrite();
    } else if (operation < 0.7) {
        // 20% - Запрос статистики self-likes (тяжелый запрос к БД)
        performSelfLikeStatsOperation();
    } else if (operation < 0.85) {
        // 15% - Операции с лайками
        performLikeOperation();
    } else {
        // 15% - Запрос observability статистики
        performObservabilityStatsOperation();
    }

    sleep(0.1); // Небольшая пауза между запросами
}

function performControllerOperation() {
    // Чтение пользователей
    const res = http.get(`${BASE_URL}/users`);

    controllerResponseTime.add(res.timings.duration);

    check(res, {
        'get users status is 200': (r) => r.status === 200,
    });
}

function performControllerWrite() {
    // Создание нового пользователя
    const timestamp = Date.now();
    const res = http.post(`${BASE_URL}/users`, JSON.stringify({
        nickname: `user_${timestamp}_${Math.random().toString(36).substring(7)}`,
        email: `user_${timestamp}_${Math.random().toString(36).substring(7)}@test.com`
    }), {
        headers: { 'Content-Type': 'application/json' },
    });

    controllerResponseTime.add(res.timings.duration);

    check(res, {
        'create user status is 200': (r) => r.status === 200 || r.status === 201,
    });

    if (res.status === 200 || res.status === 201) {
        const user = JSON.parse(res.body);
        userIds.push(user.id);
    }
}

function performSelfLikeStatsOperation() {
    // Запрос статистики self-likes (метод с аспектом)
    const res = http.get(`${BASE_URL}/statistics/self-likes`);

    selfLikeStatsResponseTime.add(res.timings.duration);

    check(res, {
        'get self-like stats status is 200': (r) => r.status === 200,
    });
}

function performLikeOperation() {
    if (postIds.length === 0 || userIds.length === 0) {
        return;
    }

    const randomPostId = postIds[Math.floor(Math.random() * postIds.length)];
    const randomUserId = userIds[Math.floor(Math.random() * userIds.length)];

    // 50% лайк, 50% анлайк
    if (Math.random() < 0.5) {
        const res = http.post(`${BASE_URL}/posts/${randomPostId}/likes?userId=${randomUserId}`);

        repositoryResponseTime.add(res.timings.duration);

        check(res, {
            'like post status is 200': (r) => r.status === 200 || r.status === 204,
        });
    } else {
        const res = http.del(`${BASE_URL}/posts/${randomPostId}/likes?userId=${randomUserId}`);

        repositoryResponseTime.add(res.timings.duration);

        check(res, {
            'unlike post status is 200': (r) => r.status === 200 || r.status === 204,
        });
    }
}

function performObservabilityStatsOperation() {
    // Запрос статистики observability (короткое, среднее или длинное окно)
    const endpoints = [
        '/observability/stats/short',
        '/observability/stats/medium',
        '/observability/stats/long'
    ];

    const endpoint = endpoints[Math.floor(Math.random() * endpoints.length)];
    const res = http.get(`${BASE_URL}${endpoint}`);

    observabilityStatsResponseTime.add(res.timings.duration);

    check(res, {
        'get observability stats status is 200': (r) => r.status === 200,
    });
}

export function teardown(data) {
    console.log('Test completed');
    console.log(`Final counts: ${userIds.length} users, ${postIds.length} posts`);
}
