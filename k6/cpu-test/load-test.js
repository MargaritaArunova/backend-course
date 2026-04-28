import http from 'k6/http';
import { check, sleep } from 'k6';
import { Trend } from 'k6/metrics';

// Кастомные метрики для отслеживания времени отклика
const readResponseTime = new Trend('read_response_time');
const writeResponseTime = new Trend('write_response_time');

// Параметры теста
const BASE_URL = __ENV.BASE_URL || 'http://localhost:8080';
const WRITE_RATIO = parseFloat(__ENV.WRITE_RATIO || '0.5'); // Доля операций записи (0.05, 0.5, 0.95)
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
    thresholds: {
        http_req_failed: ['rate<0.1'], // менее 10% ошибок
        http_req_duration: ['p(95)<2000'], // 95% запросов быстрее 2s
    },
};

// Кэш для пользователей и постов
let userIds = [];
let postIds = [];

export function setup() {
    console.log(`Starting test with WRITE_RATIO=${WRITE_RATIO}, VUS=${VUS}, DURATION=${DURATION}`);

    // Предзаполняем базу пользователями и постами для операций чтения
    const initialUsers = 300;

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

    console.log(`Setup complete: ${userIds.length} users`);

    return { userIds, postIds };
}

export default function(data) {
    // Используем данные из setup
    if (data.userIds) userIds = data.userIds;
    if (data.postIds) postIds = data.postIds;

    const isWrite = Math.random() < WRITE_RATIO;

    if (isWrite) {
        // Операция записи
        performWrite();
    } else {
        // Операция чтения
        performRead();
    }

    sleep(0.1); // Небольшая пауза между запросами
}

function performWrite() {
    const operation = Math.random();

    // Создание пользователя (40% операций записи)
    const timestamp = Date.now();
    const res = http.post(`${BASE_URL}/users`, JSON.stringify({
        nickname: `user_${timestamp}_${Math.random().toString(36).substring(7)}`,
        email: `user_${timestamp}_${Math.random().toString(36).substring(7)}@test.com`
    }), {
        headers: { 'Content-Type': 'application/json' },
    });

    writeResponseTime.add(res.timings.duration);

    check(res, {
        'create user status is 200': (r) => r.status === 200 || r.status === 201,
    });

    if (res.status === 200 || res.status === 201) {
        const user = JSON.parse(res.body);
        userIds.push(user.id);
    }
}

function performRead() {
    const operation = Math.random();
    // Получение всех пользователей (50% операций чтения)
    const res = http.get(`${BASE_URL}/users`);

    readResponseTime.add(res.timings.duration);

    check(res, {
        'get users status is 200': (r) => r.status === 200,
    });
}

export function teardown(data) {
    console.log('Test completed');
}