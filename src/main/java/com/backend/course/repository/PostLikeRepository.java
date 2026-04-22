package com.backend.course.repository;

import com.backend.course.model.PostLike;
import org.springframework.stereotype.Repository;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicLong;

@Repository
public class PostLikeRepository {

    private final Map<Long, PostLike> storage = new ConcurrentHashMap<>();
    private final AtomicLong idGenerator = new AtomicLong(0);

    public PostLike save(PostLike postLike) {
        if (postLike.getId() == null) {
            postLike.setId(idGenerator.incrementAndGet());
        }
        storage.put(postLike.getId(), postLike);
        return postLike;
    }

    public Optional<PostLike> findById(Long id) {
        return Optional.ofNullable(storage.get(id));
    }

    public List<PostLike> findAll() {
        return new ArrayList<>(storage.values());
    }

    public void deleteById(Long id) {
        storage.remove(id);
    }

    public void delete(PostLike postLike) {
        storage.remove(postLike.getId());
    }

    public boolean existsById(Long id) {
        return storage.containsKey(id);
    }

    public long count() {
        return storage.size();
    }

    public Optional<PostLike> findByUserIdAndPostId(Long userId, Long postId) {
        return storage.values().stream()
                .filter(like -> like.getUserId().equals(userId) && like.getPostId().equals(postId))
                .findFirst();
    }

    public List<PostLike> findByPostId(Long postId) {
        return storage.values().stream()
                .filter(like -> like.getPostId().equals(postId))
                .toList();
    }

    public List<SelfLikeStats> findSelfLikeStats() {
        Map<Long, SelfLikeStatsImpl> statsMap = new HashMap<>();

        storage.values().stream()
                .filter(like -> like.getUserId().equals(like.getPostId()))
                .forEach(like -> {
                    Long userId = like.getUserId();
                    statsMap.computeIfAbsent(userId, id -> new SelfLikeStatsImpl(
                            userId,
                            0L
                    )).incrementSelfLikes();
                });

        return new ArrayList<>(statsMap.values());
    }

    public interface SelfLikeStats {
        Long getUserId();

        Long getSelfLikes();
    }

    private static class SelfLikeStatsImpl implements SelfLikeStats {
        private final Long userId;
        private Long selfLikes;

        public SelfLikeStatsImpl(Long userId, Long selfLikes) {
            this.userId = userId;
            this.selfLikes = selfLikes;
        }

        @Override
        public Long getUserId() {
            return userId;
        }

        @Override
        public Long getSelfLikes() {
            return selfLikes;
        }

        public void incrementSelfLikes() {
            this.selfLikes++;
        }
    }
}

