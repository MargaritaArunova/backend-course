package com.backend.course.repository;

import com.backend.course.model.Post;
import org.springframework.stereotype.Repository;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicLong;

@Repository
public class PostRepository {

    private final Map<Long, Post> storage = new ConcurrentHashMap<>();
    private final AtomicLong idGenerator = new AtomicLong(0);

    public Post save(Post post) {
        if (post.getId() == null) {
            post.setId(idGenerator.incrementAndGet());
        }
        storage.put(post.getId(), post);
        return post;
    }

    public Optional<Post> findById(Long id) {
        return Optional.ofNullable(storage.get(id));
    }

    public List<Post> findAll() {
        return new ArrayList<>(storage.values());
    }

    public void deleteById(Long id) {
        storage.remove(id);
    }

    public void delete(Post post) {
        storage.remove(post.getId());
    }

    public boolean existsById(Long id) {
        return storage.containsKey(id);
    }

    public long count() {
        return storage.size();
    }

    public List<Post> findByAuthorId(Long authorId) {
        return storage.values().stream()
                .filter(post -> post.getAuthorId().equals(authorId))
                .toList();
    }
}

